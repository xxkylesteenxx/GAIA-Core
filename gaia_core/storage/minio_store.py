"""MinIO object store — durable checkpoint and evidence bundle storage.

Dependency: minio (optional, guarded import)
Buckets: gaia-checkpoints, gaia-evidence, gaia-observations,
         gaia-model-manifests, gaia-sync-bundles, gaia-twins
"""
from __future__ import annotations

import hashlib
import io
import json
import logging
from dataclasses import dataclass
from typing import Any

log = logging.getLogger(__name__)

try:
    from minio import Minio  # type: ignore
    from minio.error import S3Error  # type: ignore
    _MINIO_AVAILABLE = True
except ImportError:
    _MINIO_AVAILABLE = False
    Minio = None  # type: ignore
    S3Error = Exception  # type: ignore

GAIA_BUCKETS = [
    "gaia-checkpoints",
    "gaia-evidence",
    "gaia-observations",
    "gaia-model-manifests",
    "gaia-sync-bundles",
    "gaia-twins",
]


@dataclass
class CheckpointMeta:
    """Metadata attached to every stored checkpoint object."""
    node_id: str
    sequence: int
    sha256: str
    size_bytes: int
    timestamp_ns: int


class MinioStore:
    """Thin async-friendly wrapper around the MinIO Python client."""

    def __init__(
        self,
        endpoint: str = "localhost:9000",
        access_key: str = "minioadmin",
        secret_key: str = "minioadmin",
        secure: bool = False,
    ) -> None:
        if not _MINIO_AVAILABLE:
            raise ImportError("minio package is required. Run: pip install minio")
        self._client = Minio(endpoint, access_key=access_key, secret_key=secret_key, secure=secure)

    def ensure_buckets(self) -> None:
        """Create all GAIA buckets if they don't exist."""
        for bucket in GAIA_BUCKETS:
            if not self._client.bucket_exists(bucket):
                self._client.make_bucket(bucket)
                log.info("Created bucket: %s", bucket)

    def put_checkpoint(self, node_id: str, sequence: int, data: bytes) -> CheckpointMeta:
        """Store a checkpoint with digest metadata."""
        sha256 = hashlib.sha256(data).hexdigest()
        import time
        meta = CheckpointMeta(
            node_id=node_id,
            sequence=sequence,
            sha256=sha256,
            size_bytes=len(data),
            timestamp_ns=time.time_ns(),
        )
        object_name = f"{node_id}/{sequence:016d}.ckpt"
        meta_name = f"{node_id}/{sequence:016d}.meta.json"
        self._client.put_object("gaia-checkpoints", object_name, io.BytesIO(data), len(data))
        meta_bytes = json.dumps(meta.__dict__).encode()
        self._client.put_object("gaia-checkpoints", meta_name, io.BytesIO(meta_bytes), len(meta_bytes))
        log.debug("Stored checkpoint: %s sha256=%s", object_name, sha256)
        return meta

    def get_checkpoint(self, node_id: str, sequence: int) -> bytes:
        """Retrieve a checkpoint by node and sequence number."""
        object_name = f"{node_id}/{sequence:016d}.ckpt"
        response = self._client.get_object("gaia-checkpoints", object_name)
        try:
            return response.read()
        finally:
            response.close()
            response.release_conn()

    def put_object(self, bucket: str, key: str, data: bytes, metadata: dict[str, Any] | None = None) -> None:
        """Generic object put for evidence bundles, observations, etc."""
        self._client.put_object(bucket, key, io.BytesIO(data), len(data),
                                metadata=metadata or {})
