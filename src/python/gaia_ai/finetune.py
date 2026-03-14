"""Fine-Tuning Hook Emission.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3, §4, §6

Fine-tuning hooks SHALL emit auditable events rather than
mutating live models inline.

This module intentionally avoids autonomous online fine-tuning,
direct production-model mutation, or unsafe tool execution.
Training hooks are recorded as events for later reviewed processing.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

log = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class FinetuneEventType(str, Enum):
    PREFERENCE_SIGNAL  = "preference_signal"   # thumbs up/down, ranking
    CORRECTION         = "correction"           # explicit correction of output
    DOMAIN_EXAMPLE     = "domain_example"       # new knowledge-domain example
    SAFETY_ANNOTATION  = "safety_annotation"    # GUARDIAN-sourced safety signal
    CAPABILITY_PROBE   = "capability_probe"     # structured capability evaluation


@dataclass
class FinetuneEvent:
    """An auditable record of a training signal.

    Events are append-only. Nothing here mutates a live model.
    """
    event_type:  FinetuneEventType
    model_id:    str
    source:      str                   # core_id or external emitter
    payload:     dict[str, Any]
    approved:    bool  = False         # requires explicit approval before training
    timestamp:   str   = field(default_factory=_now)
    event_id:    str   = field(default_factory=lambda: _now().replace(":", "-"))


class EventSink(Exception):
    """Base class for event sink errors."""


class InMemoryEventSink:
    """Append-only in-memory event log.

    Replace with a durable sink (file, database, message queue) for
    production deployments.
    """

    def __init__(self) -> None:
        self._events: list[FinetuneEvent] = []

    def write(self, event: FinetuneEvent) -> None:
        self._events.append(event)

    def all_events(self) -> list[FinetuneEvent]:
        return list(self._events)

    def pending_approval(self) -> list[FinetuneEvent]:
        return [e for e in self._events if not e.approved]

    def approve(self, event_id: str) -> None:
        for event in self._events:
            if event.event_id == event_id:
                event.approved = True
                return
        raise KeyError(f"unknown event_id: {event_id}")

    @property
    def count(self) -> int:
        return len(self._events)


class FineTuneEmitter:
    """Emit fine-tuning events to a configured sink.

    All events are append-only records. No live model is mutated.
    Approval of events for actual training is a separate offline process.

    Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §6
    """

    def __init__(self, sink: InMemoryEventSink | None = None) -> None:
        self._sink = sink or InMemoryEventSink()

    def emit(
        self,
        event_type: FinetuneEventType,
        model_id:   str,
        source:     str,
        payload:    dict[str, Any],
    ) -> FinetuneEvent:
        """Create and record a fine-tune event. Returns the recorded event."""
        event = FinetuneEvent(
            event_type=event_type,
            model_id=model_id,
            source=source,
            payload=payload,
        )
        self._sink.write(event)
        log.info(
            "finetune: emitted %s for model '%s' from '%s'",
            event_type.value, model_id, source,
        )
        return event

    def emit_preference(
        self, model_id: str, source: str,
        prompt: str, chosen: str, rejected: str,
    ) -> FinetuneEvent:
        return self.emit(
            FinetuneEventType.PREFERENCE_SIGNAL, model_id, source,
            {"prompt": prompt, "chosen": chosen, "rejected": rejected},
        )

    def emit_correction(
        self, model_id: str, source: str,
        prompt: str, original: str, corrected: str,
    ) -> FinetuneEvent:
        return self.emit(
            FinetuneEventType.CORRECTION, model_id, source,
            {"prompt": prompt, "original": original, "corrected": corrected},
        )

    def emit_safety_annotation(
        self, model_id: str, source: str,
        prompt: str, output: str, annotation: str,
    ) -> FinetuneEvent:
        return self.emit(
            FinetuneEventType.SAFETY_ANNOTATION, model_id, source,
            {"prompt": prompt, "output": output, "annotation": annotation},
        )

    @property
    def sink(self) -> InMemoryEventSink:
        return self._sink
