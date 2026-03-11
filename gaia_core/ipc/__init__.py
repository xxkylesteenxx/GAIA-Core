"""GAIA Inter-Process Communication Transport Stack.

Three-tier IPC fabric:
  L1  memfd shared memory rings (same-host zero-copy)
  L2  Unix domain sockets + io_uring (same-host async)
  L3  gRPC + Protobuf (cross-host typed contracts)
  L4  Causal broadcast + vector clocks (distributed ordering)

Public surface:
  GaiaEnvelope          — base message contract with causal clock
  VectorClockService    — per-node vector clock management
  CausalBroadcast       — causal delivery with holdback queue
  MemfdRing             — shared memory ring buffer (same-host)
  NexusSyncService      — gRPC NexusSync stub
  GuardianPolicyService — gRPC GuardianPolicy stub
  IpcObservability      — IPC metrics and instrumentation
"""
from gaia_core.ipc.contracts import GaiaEnvelope, DataClass, MessagePriority
from gaia_core.ipc.causal.vector_clock import VectorClockService
from gaia_core.ipc.causal.causal_broadcast import CausalBroadcast
from gaia_core.ipc.local.shm.memfd_ring import MemfdRing
from gaia_core.ipc.grpc.nexus_sync_service import NexusSyncService
from gaia_core.ipc.grpc.guardian_policy_service import GuardianPolicyService
from gaia_core.ipc.observability import IpcObservability

__all__ = [
    "GaiaEnvelope",
    "DataClass",
    "MessagePriority",
    "VectorClockService",
    "CausalBroadcast",
    "MemfdRing",
    "NexusSyncService",
    "GuardianPolicyService",
    "IpcObservability",
]
