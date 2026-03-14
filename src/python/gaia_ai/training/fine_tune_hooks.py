"""Fine-Tuning Hook Emission.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §3, §4, §6

Fine-tuning hooks SHALL emit auditable events rather than
mutating live models inline. No autonomous online fine-tuning,
no direct production-model mutation, no unsafe tool execution.
Training hooks are recorded as events for later reviewed processing.

Two APIs are provided:

  FineTuneHookStore   —  canonical file-persisting store (spec-primary).
                         Writes JSON to disk; used by demo_pipeline.py.

  FineTuneEmitter     —  in-memory event emitter (kept for existing code).
                         Backed by InMemoryEventSink; no disk I/O.

Event types (FinetuneEventType)
-------------------------------
PREFERENCE_SIGNAL  — thumbs up/down or ranked preference pair
CORRECTION         — explicit correction of a model output
DOMAIN_EXAMPLE     — new knowledge-domain example
SAFETY_ANNOTATION  — GUARDIAN-sourced safety signal
CAPABILITY_PROBE   — structured capability evaluation
SFT_PREPARE        — supervised fine-tuning job preparation request
"""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# TrainingEvent  —  canonical flat event (FineTuneHookStore)
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class TrainingEvent:
    """Flat, file-serialisable training event record.

    Used by FineTuneHookStore.  Intentionally minimal — all extra
    context goes in the metadata dict.
    """
    event_type:  str
    model_name:  str
    dataset_ref: str
    metadata:    dict = field(default_factory=dict)


# ---------------------------------------------------------------------------
# FineTuneHookStore  —  canonical file-persisting store
# ---------------------------------------------------------------------------

class FineTuneHookStore:
    """Write auditable TrainingEvent records to disk as JSON.

    Each event is written to a separate file:
      {root}/{model_name}_{event_type}.json

    The root directory is created automatically if it does not exist.
    No training job is launched — events are queued for reviewed
    offline processing.

    Usage::

        hooks = FineTuneHookStore("_artifacts")
        event = hooks.prepare_sft_job(
            model_name="gaia-fast-local",
            dataset_ref="datasets/feedback.jsonl",
            output_dir="runs/sft/gaia-fast-local",
        )
        path = hooks.record(event)
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def record(self, event: TrainingEvent) -> Path:
        """Serialise event to JSON and write to disk; return the path."""
        path = self.root / f"{event.model_name}_{event.event_type}.json"
        path.write_text(json.dumps(asdict(event), indent=2), encoding="utf-8")
        log.info("fine_tune_hooks: recorded %s for '%s' at %s",
                 event.event_type, event.model_name, path)
        return path

    def prepare_sft_job(
        self,
        *,
        model_name:  str,
        dataset_ref: str,
        output_dir:  str,
    ) -> TrainingEvent:
        """Build an SFT preparation TrainingEvent.

        Does not launch a training job — call record() to persist it.
        """
        return TrainingEvent(
            event_type="sft_prepare",
            model_name=model_name,
            dataset_ref=dataset_ref,
            metadata={"output_dir": output_dir},
        )


# ---------------------------------------------------------------------------
# FinetuneEventType  (in-memory emitter schema)
# ---------------------------------------------------------------------------

class FinetuneEventType(str, Enum):
    PREFERENCE_SIGNAL = "preference_signal"
    CORRECTION        = "correction"
    DOMAIN_EXAMPLE    = "domain_example"
    SAFETY_ANNOTATION = "safety_annotation"
    CAPABILITY_PROBE  = "capability_probe"
    SFT_PREPARE       = "sft_prepare"


@dataclass
class FinetuneEvent:
    """Append-only auditable training signal record (in-memory emitter)."""
    event_type: FinetuneEventType
    model_id:   str
    source:     str
    payload:    dict[str, Any]
    approved:   bool = False
    timestamp:  str  = field(default_factory=_now)
    event_id:   str  = field(default_factory=lambda: _now().replace(":", "-"))


# ---------------------------------------------------------------------------
# InMemoryEventSink
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# FineTuneEmitter  (in-memory convenience emitter)
# ---------------------------------------------------------------------------

class FineTuneEmitter:
    """Emit fine-tuning events to a configured sink. No live model is mutated."""

    def __init__(self, sink: InMemoryEventSink | None = None) -> None:
        self._sink = sink or InMemoryEventSink()

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
