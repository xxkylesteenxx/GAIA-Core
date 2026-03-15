"""Stable content-addressed object identifiers for the GAIA substrate."""
from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Optional


class ObjectKind(str, Enum):
    IDENTITY = "identity"
    MEMORY_EVENT = "memory-event"
    CHECKPOINT = "checkpoint"
    MODEL_BLOB = "model-blob"
    SENSOR_ARTIFACT = "sensor-artifact"
    SNAPSHOT = "snapshot"
    POLICY = "policy"
    MANIFEST = "manifest"
    SEMANTIC_RECORD = "semantic-record"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ObjectID:
    """Immutable identifier combining a content hash and a stable UUID."""

    kind: ObjectKind
    content_hash: str  # sha256 hex
    uid: str = field(default_factory=lambda: str(uuid.uuid4()))

    @classmethod
    def from_bytes(cls, data: bytes, kind: ObjectKind) -> "ObjectID":
        digest = hashlib.sha256(data).hexdigest()
        return cls(kind=kind, content_hash=digest)

    @classmethod
    def from_file(cls, path: Path, kind: ObjectKind) -> "ObjectID":
        return cls.from_bytes(path.read_bytes(), kind)

    def __str__(self) -> str:
        return f"{self.kind.value}:{self.content_hash[:16]}:{self.uid[:8]}"


def generate_object_id(
    data: Optional[bytes] = None,
    kind: ObjectKind = ObjectKind.UNKNOWN,
) -> ObjectID:
    """Convenience factory. When data is None a random-content hash is used."""
    payload = data if data is not None else uuid.uuid4().bytes
    return ObjectID.from_bytes(payload, kind)
