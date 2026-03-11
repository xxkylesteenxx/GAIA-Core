"""GAIA storage substrate — MinIO + etcd + NATS JetStream.

Write pattern:
  1. jetstream_log  → durable causal WAL (synchronous commit)
  2. minio_store    → durable object materialization (async)
  3. etcd_registry  → head pointer + lease update
"""

from gaia_core.storage.minio_store import MinioStore
from gaia_core.storage.jetstream_log import JetStreamLog
from gaia_core.storage.etcd_registry import EtcdRegistry

__all__ = ["MinioStore", "JetStreamLog", "EtcdRegistry"]
