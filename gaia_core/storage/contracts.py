from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping, Protocol, Sequence


@dataclass(slots=True, frozen=True)
class CheckpointRef:
    schema_version: str = "1.0"
    checkpoint_id: str = ""
    node_id: str = ""
    epoch: int = 0

    manifest_uri: str = ""
    payload_uri: str = ""
    state_hash: str = ""
    causal_cursor: str | None = None

    created_at: datetime | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(slots=True, frozen=True)
class EventEnvelope:
    schema_version: str = "1.0"
    event_id: str = ""
    stream: str = ""
    topic: str = ""
    sequence: int = 0

    entity_id: str = ""
    occurred_at: datetime | None = None
    correlation_id: str | None = None
    causation_id: str | None = None

    payload: Mapping[str, Any] = field(default_factory=dict)
    metadata: Mapping[str, Any] = field(default_factory=dict)
    payload_hash: str | None = None


class StorageBackend(Protocol):
    async def write_event(self, envelope: EventEnvelope) -> str: ...
    async def read_events(
        self,
        stream: str,
        after_sequence: int | None = None,
        limit: int = 100,
    ) -> Sequence[EventEnvelope]: ...

    async def put_checkpoint(self, ref: CheckpointRef, payload: bytes) -> CheckpointRef: ...
    async def get_checkpoint(self, checkpoint_id: str) -> tuple[CheckpointRef, bytes]: ...

    async def exists(self, uri: str) -> bool: ...
    async def health(self) -> Mapping[str, Any]: ...
