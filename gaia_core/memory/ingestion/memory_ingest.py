"""MemoryAtom ingestion pipeline.

Full ingestion sequence for a new MemoryAtom:
  1. Verify content integrity (sha256)
  2. Generate HLC timestamp
  3. Create CausalEnvelope
  4. Embed content (calls embedding_fn, which is injected at construction)
  5. Add to hot-tier FAISS index
  6. Add to capacity-tier DiskANN index
  7. Record session write frontier
  8. Return the fully-populated MemoryAtom

The embedding_fn is intentionally injectable so the pipeline is
backend-agnostic — it can call llama.cpp, vLLM, Triton, or any
other embedding service via the InferRouter.
"""
from __future__ import annotations

import logging
from typing import Callable

from gaia_core.memory.contracts import MemoryAtom
from gaia_core.memory.causal_envelope import CausalEnvelope
from gaia_core.memory.hlc import HybridLogicalClock
from gaia_core.memory.hot_index.faiss_hnsw_service import FaissHnswService
from gaia_core.memory.capacity_index.diskann_service import DiskANNService
from gaia_core.memory.metadata.session_frontier import SessionFrontier

log = logging.getLogger(__name__)

EmbeddingFn = Callable[[str], list[float]]


class MemoryIngest:
    """Orchestrates full MemoryAtom ingestion into the memory fabric."""

    def __init__(
        self,
        hlc: HybridLogicalClock,
        hot_index: FaissHnswService,
        capacity_index: DiskANNService,
        frontier: SessionFrontier,
        embedding_fn: EmbeddingFn,
        node_id: str = "gaia-node-01",
    ) -> None:
        self._hlc = hlc
        self._hot = hot_index
        self._capacity = capacity_index
        self._frontier = frontier
        self._embed = embedding_fn
        self._node_id = node_id

    def ingest(
        self,
        content: str,
        core: str,
        session_id: str = "",
        dependencies: list[str] | None = None,
        tags: list[str] | None = None,
        metadata: dict | None = None,
    ) -> tuple[MemoryAtom, CausalEnvelope]:
        """Ingest a new memory atom. Returns (atom, envelope)."""

        # Step 1 — Create atom
        atom = MemoryAtom(
            content=content,
            core=core,
            tags=tags or [],
            metadata=metadata or {},
        )
        if not atom.verify():
            raise ValueError(f"MemoryAtom content integrity check failed: {atom.atom_id}")

        # Step 2 — Generate HLC timestamp
        hlc_ts = self._hlc.now()

        # Step 3 — Create CausalEnvelope
        envelope = CausalEnvelope(
            atom_id=atom.atom_id,
            node_id=self._node_id,
            core=core,
            hlc_wall_ns=hlc_ts.wall_ns,
            hlc_logical=hlc_ts.logical,
            dependencies=dependencies or [],
        )
        atom.causal_id = envelope.trace_id

        # Step 4 — Embed
        log.debug("Embedding atom %s ...", atom.atom_id)
        atom.embedding = self._embed(content)

        # Step 5 — Hot index
        self._hot.add(atom)

        # Step 6 — Capacity index
        self._capacity.add(atom)

        # Step 7 — Session frontier
        if session_id:
            self._frontier.record_write(
                session_id=session_id,
                atom_id=atom.atom_id,
                hlc=hlc_ts,
            )

        log.info(
            "Ingested atom %s (core=%s, session=%s, hlc=%d/%d)",
            atom.atom_id, core, session_id or "none",
            hlc_ts.wall_ns, hlc_ts.logical,
        )
        return atom, envelope
