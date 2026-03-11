"""Replay bootstrap orchestrator for GAIA node restore.

Full restore sequence:
  1. Connect to JetStream and etcd.
  2. Replay GAIA.CAUSAL stream to reconstruct the causal event log.
  3. Read the continuity head pointer from etcd.
  4. Fetch the latest checkpoint from MinIO.
  5. Return a ReplayResult with all recovered state for the caller.

This is the canonical path for:
  - node restart after crash,
  - new node joining an existing GAIA cluster,
  - audit/forensic replay of past state.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class ReplayResult:
    """Output of a completed replay bootstrap."""
    node_id: str
    continuity_head: int | None         # latest checkpoint sequence from etcd
    checkpoint_data: bytes | None        # raw checkpoint bytes from MinIO
    causal_events: list[Any] = field(default_factory=list)  # verified CausalEvents
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True if bootstrap completed without errors."""
        return len(self.errors) == 0

    def summary(self) -> dict:
        return {
            "node_id": self.node_id,
            "continuity_head": self.continuity_head,
            "checkpoint_bytes": len(self.checkpoint_data) if self.checkpoint_data else 0,
            "causal_events_replayed": len(self.causal_events),
            "errors": self.errors,
            "ok": self.ok,
        }


class ReplayBootstrap:
    """Orchestrates full node restore from JetStream + etcd + MinIO."""

    def __init__(
        self,
        jetstream_log: Any,    # JetStreamLog
        etcd_registry: Any,    # EtcdRegistry
        minio_store: Any,      # MinioStore
    ) -> None:
        self._wal = jetstream_log
        self._etcd = etcd_registry
        self._minio = minio_store

    async def run(self, node_id: str, stream: str = "GAIA.CAUSAL") -> ReplayResult:
        """Execute the full bootstrap sequence for the given node.

        Args:
            node_id: The GAIA node identifier to restore.
            stream:  JetStream stream to replay (default: GAIA.CAUSAL).

        Returns:
            ReplayResult with all recovered state.
        """
        result = ReplayResult(node_id=node_id)

        # Step 1 — Replay causal WAL
        log.info("[%s] Step 1: Replaying causal stream '%s'", node_id, stream)
        try:
            result.causal_events = await self._wal.replay(stream)
            log.info(
                "[%s] Replayed %d verified events",
                node_id, len(result.causal_events),
            )
        except Exception as exc:
            msg = f"WAL replay failed: {exc}"
            log.error("[%s] %s", node_id, msg)
            result.errors.append(msg)

        # Step 2 — Reconstruct continuity head from etcd
        log.info("[%s] Step 2: Reading continuity head from etcd", node_id)
        try:
            result.continuity_head = self._etcd.get_head(node_id)
            log.info("[%s] Continuity head = %s", node_id, result.continuity_head)
        except Exception as exc:
            msg = f"etcd head read failed: {exc}"
            log.error("[%s] %s", node_id, msg)
            result.errors.append(msg)

        # Step 3 — Restore checkpoint from MinIO
        if result.continuity_head is not None:
            log.info(
                "[%s] Step 3: Fetching checkpoint seq=%d from MinIO",
                node_id, result.continuity_head,
            )
            try:
                result.checkpoint_data = self._minio.get_checkpoint(
                    node_id, result.continuity_head
                )
                log.info(
                    "[%s] Checkpoint fetched: %d bytes",
                    node_id, len(result.checkpoint_data),
                )
            except Exception as exc:
                msg = f"MinIO checkpoint fetch failed (seq={result.continuity_head}): {exc}"
                log.error("[%s] %s", node_id, msg)
                result.errors.append(msg)
        else:
            log.warning("[%s] No continuity head found — skipping checkpoint restore", node_id)

        if result.ok:
            log.info("[%s] Replay bootstrap COMPLETE: %s", node_id, result.summary())
        else:
            log.warning("[%s] Replay bootstrap PARTIAL: %s", node_id, result.summary())

        return result
