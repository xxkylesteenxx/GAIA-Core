"""GAIA Holographic Memory Stack.

Multi-tier associative memory fabric:
  L0  In-process atom cache
  L1  FAISS HNSW hot index (in-memory)
  L2  DiskANN capacity index (NVMe-backed stub)
  L3  MinIO + JetStream + etcd distributed fabric (via gaia_core.storage)

Canonical truth lives in the causal WAL + object store.
Indexes are rebuildable projections.

Public surface:
  MemoryAtom          — the unit of stored memory
  MemorySearchResult  — ranked retrieval result
  CausalEnvelope      — HLC-stamped causal metadata wrapper
  HybridLogicalClock  — HLC service
  FaissHnswService    — hot-tier HNSW index
  DiskANNService      — capacity-tier stub
  SessionFrontier     — per-session causal frontier tracker
  DependencyResolver  — causal dependency checker
  FederatedSearch     — tier-aware retrieval router
  VisibilityFilter    — causal visibility gate
  MemoryIngest        — ingestion pipeline
"""
from gaia_core.memory.contracts import MemoryAtom, MemorySearchResult
from gaia_core.memory.causal_envelope import CausalEnvelope
from gaia_core.memory.hlc import HybridLogicalClock
from gaia_core.memory.hot_index.faiss_hnsw_service import FaissHnswService
from gaia_core.memory.capacity_index.diskann_service import DiskANNService
from gaia_core.memory.metadata.session_frontier import SessionFrontier
from gaia_core.memory.metadata.dependency_resolver import DependencyResolver
from gaia_core.memory.retrieval.federated_search import FederatedSearch
from gaia_core.memory.retrieval.visibility_filter import VisibilityFilter
from gaia_core.memory.ingestion.memory_ingest import MemoryIngest

__all__ = [
    "MemoryAtom",
    "MemorySearchResult",
    "CausalEnvelope",
    "HybridLogicalClock",
    "FaissHnswService",
    "DiskANNService",
    "SessionFrontier",
    "DependencyResolver",
    "FederatedSearch",
    "VisibilityFilter",
    "MemoryIngest",
]
