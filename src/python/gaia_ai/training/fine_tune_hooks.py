"""Fine-Tuning Hook Emission.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3, §4, §6

Fine-tuning hooks SHALL emit auditable events rather than
mutating live models inline. No autonomous online fine-tuning,
no direct production-model mutation, no unsafe tool execution.
Training hooks are recorded as events for later reviewed processing.

Event types
-----------
PREFERENCE_SIGNAL  — thumbs up/down or ranked preference pair
CORRECTION         — explicit correction of a model output
DOMAIN_EXAMPLE     — new knowledge-domain example
SAFETY_ANNOTATION  — GUARDIAN-sourced safety signal
CAPABILITY_PROBE   — structured capability evaluation
SFT_PREPARE        — supervised fine-tuning job preparation request
                     (dataset reference + output dir; no job is launched
                      inline — event queued for reviewed processing)
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
    PREFERENCE_SIGNAL = "preference_signal"
    CORRECTION        = "correction"
    DOMAIN_EXAMPLE    = "domain_example"
    SAFETY_ANNOTATION = "safety_annotation"
    CAPABILITY_PROBE  = "capability_probe"
    SFT_PREPARE       = "sft_prepare"   # supervised fine-tuning preparation


@dataclass
class FinetuneEvent:
    """Append-only auditable training signal record."""
    event_type: FinetuneEventType
    model_id:   str
    source:     str
    payload:    dict[str, Any]
    approved:   bool = False
    timestamp:  str  = field(default_factory=_now)
    event_id:   str  = field(default_factory=lambda: _now().replace(":", "-"))


class InMemoryEventSink:
    """Append-only in-memory event log.

    Replace with a durable sink (file, DB, message queue) for production.
    """

    def __init__(self) -> None:
        self._events: list[FinetuneEvent] = []

    def write(self, event: FinetuneEvent) -> None:
        self._events.append(event)

    def all_events(self) -> list[FinetuneEvent]:
        return list(self._events)

    def pending_approval(self) -> list[FinetuneEvent]:
        return [e for e in self._events if not e.approved]

    def by_type(self, event_type: FinetuneEventType) -> list[FinetuneEvent]:
        return [e for e in self._events if e.event_type == event_type]

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
    """Emit fine-tuning events to a configured sink. No live model is mutated."""

    def __init__(self, sink: InMemoryEventSink | None = None) -> None:
        self._sink = sink or InMemoryEventSink()

    # ------------------------------------------------------------------ #
    # Core emit                                                            #
    # ------------------------------------------------------------------ #

    def emit(
        self,
        event_type: FinetuneEventType,
        model_id:   str,
        source:     str,
        payload:    dict[str, Any],
    ) -> FinetuneEvent:
        event = FinetuneEvent(event_type=event_type, model_id=model_id,
                              source=source, payload=payload)
        self._sink.write(event)
        log.info("finetune: emitted %s for '%s' from '%s'",
                 event_type.value, model_id, source)
        return event

    # ------------------------------------------------------------------ #
    # Convenience emitters                                                 #
    # ------------------------------------------------------------------ #

    def emit_preference(
        self, model_id: str, source: str,
        prompt: str, chosen: str, rejected: str,
    ) -> FinetuneEvent:
        return self.emit(FinetuneEventType.PREFERENCE_SIGNAL, model_id, source,
                         {"prompt": prompt, "chosen": chosen, "rejected": rejected})

    def emit_correction(
        self, model_id: str, source: str,
        prompt: str, original: str, corrected: str,
    ) -> FinetuneEvent:
        return self.emit(FinetuneEventType.CORRECTION, model_id, source,
                         {"prompt": prompt, "original": original, "corrected": corrected})

    def emit_safety_annotation(
        self, model_id: str, source: str,
        prompt: str, output: str, annotation: str,
    ) -> FinetuneEvent:
        return self.emit(FinetuneEventType.SAFETY_ANNOTATION, model_id, source,
                         {"prompt": prompt, "output": output, "annotation": annotation})

    def emit_sft_prepare(
        self,
        model_id:    str,
        source:      str,
        dataset_ref: str,
        output_dir:  str,
        metadata:    dict[str, Any] | None = None,
    ) -> FinetuneEvent:
        """Emit a supervised fine-tuning preparation event.

        Records the dataset reference and output directory for a proposed
        SFT run. No training job is launched — the event is queued for
        offline reviewed processing.

        Canonical payload shape (GAIA-AI-INFERENCE-SPEC v1.0):
        {
            "event_type":   "sft_prepare",
            "model_name":   <model_id>,
            "dataset_ref":  <path or URI to training dataset>,
            "metadata": {
                "output_dir": <run output directory>,
                ...           <any additional metadata>
            }
        }
        """
        payload: dict[str, Any] = {
            "event_type":  FinetuneEventType.SFT_PREPARE.value,
            "model_name":  model_id,
            "dataset_ref": dataset_ref,
            "metadata":    {"output_dir": output_dir, **(metadata or {})},
        }
        return self.emit(FinetuneEventType.SFT_PREPARE, model_id, source, payload)

    @property
    def sink(self) -> InMemoryEventSink:
        return self._sink
