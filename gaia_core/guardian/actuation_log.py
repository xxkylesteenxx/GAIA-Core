"""
GAIA ADR-007 — GUARDIAN Actuation Log
Tamper-evident actuation decision log.
Publishes all GUARDIAN decisions to GAIA.GUARDIAN JetStream stream.
"""
from __future__ import annotations
import hashlib
import json
import logging
import time
from dataclasses import asdict, dataclass, field
from typing import List, Optional
from .approval_gate import ApprovalRecord, ApprovalResult

log = logging.getLogger(__name__)


@dataclass
class LogEntry:
    """
    A single tamper-evident log entry.
    Chained via SHA-256 hash of previous entry (blockchain-lite).
    """
    entry_id: int
    record: ApprovalRecord
    timestamp: float = field(default_factory=time.time)
    prev_hash: str = "0" * 64  # Genesis block
    entry_hash: str = field(default="", init=False)

    def __post_init__(self) -> None:
        self.entry_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        payload = json.dumps({
            "entry_id": self.entry_id,
            "request_id": self.record.request_id,
            "action": self.record.action,
            "risk_level": int(self.record.risk_level),
            "result": str(self.record.result),
            "decided_by": self.record.decided_by,
            "timestamp": self.timestamp,
            "prev_hash": self.prev_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(payload).hexdigest()

    def verify(self) -> bool:
        """Verify entry has not been tampered with."""
        return self.entry_hash == self._compute_hash()


class ActuationLog:
    """
    GUARDIAN tamper-evident actuation decision log.
    In-process chain; production: also publishes to GAIA.GUARDIAN JetStream stream.
    """
    def __init__(self, jetstream_publisher=None) -> None:
        self._entries: List[LogEntry] = []
        self._jetstream = jetstream_publisher  # Optional: nats.js client

    def record(self, approval_record: ApprovalRecord) -> LogEntry:
        """Append a tamper-evident entry to the actuation log."""
        prev_hash = self._entries[-1].entry_hash if self._entries else "0" * 64
        entry = LogEntry(
            entry_id=len(self._entries),
            record=approval_record,
            prev_hash=prev_hash
        )
        self._entries.append(entry)
        log.info(f"[ActuationLog] Entry #{entry.entry_id} recorded: {approval_record.action!r} → {approval_record.result.value}")

        if self._jetstream:
            try:
                self._jetstream.publish(
                    "GAIA.GUARDIAN",
                    json.dumps({
                        "entry_id": entry.entry_id,
                        "entry_hash": entry.entry_hash,
                        "action": approval_record.action,
                        "result": approval_record.result.value,
                        "risk_level": int(approval_record.risk_level),
                        "decided_by": approval_record.decided_by,
                        "timestamp": entry.timestamp
                    }).encode()
                )
            except Exception as e:
                log.warning(f"[ActuationLog] JetStream publish failed: {e}")

        return entry

    def verify_chain(self) -> bool:
        """Verify the entire log chain has not been tampered with."""
        for i, entry in enumerate(self._entries):
            if not entry.verify():
                log.error(f"[ActuationLog] Chain integrity FAILED at entry #{i}.")
                return False
            if i > 0 and entry.prev_hash != self._entries[i-1].entry_hash:
                log.error(f"[ActuationLog] Chain link BROKEN between entries #{i-1} and #{i}.")
                return False
        log.info(f"[ActuationLog] Chain integrity VERIFIED ({len(self._entries)} entries).")
        return True

    def to_json(self) -> str:
        return json.dumps([
            {
                "entry_id": e.entry_id,
                "entry_hash": e.entry_hash,
                "prev_hash": e.prev_hash,
                "action": e.record.action,
                "result": e.record.result.value,
                "risk_level": int(e.record.risk_level),
                "decided_by": e.record.decided_by,
                "timestamp": e.timestamp
            }
            for e in self._entries
        ], indent=2)
