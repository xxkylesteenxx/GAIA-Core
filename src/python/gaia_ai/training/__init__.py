"""Training hooks for GAIA AI — auditable event emission only.

No autonomous online fine-tuning. No live model mutation.
All events are append-only records requiring explicit approval.
"""

from .fine_tune_hooks import FineTuneEmitter, FinetuneEvent, FinetuneEventType, InMemoryEventSink

__all__ = [
    "FineTuneEmitter",
    "FinetuneEvent",
    "FinetuneEventType",
    "InMemoryEventSink",
]
