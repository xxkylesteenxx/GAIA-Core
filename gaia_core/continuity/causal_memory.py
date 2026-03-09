from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

from gaia_core.models import CausalEnvelope, MemoryEvent, VectorClock


class CausalMemoryLog:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text("", encoding="utf-8")
        self.clock = VectorClock()

    def append(
        self,
        core: str,
        kind: str,
        payload: Dict[str, Any],
        dependencies: List[str] | None = None,
        tags: List[str] | None = None,
    ) -> MemoryEvent:
        self.clock = self.clock.increment(core)
        event = MemoryEvent(
            event_id=f"evt_{uuid.uuid4().hex[:12]}",
            core=core,
            kind=kind,
            payload=payload,
            envelope=CausalEnvelope(
                emitter=core,
                created_at=datetime.now(timezone.utc),
                vector_clock=self.clock,
                trace_id=uuid.uuid4().hex,
                dependencies=dependencies or [],
            ),
            tags=tags or [],
        )
        row = {
            "event_id": event.event_id,
            "core": event.core,
            "kind": event.kind,
            "payload": event.payload,
            "tags": event.tags,
            "envelope": {
                "emitter": event.envelope.emitter,
                "created_at": event.envelope.created_at.isoformat(),
                "vector_clock": event.envelope.vector_clock.versions,
                "trace_id": event.envelope.trace_id,
                "dependencies": event.envelope.dependencies,
            },
        }
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row) + "\n")
        return event

    def replay(self) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for line in self.path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                items.append(json.loads(line))
        return items
