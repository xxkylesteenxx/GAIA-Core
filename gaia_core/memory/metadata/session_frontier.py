"""Session causal frontier tracker.

Tracks per-session read/write frontiers to enforce:
  - Read-your-writes: a session always sees its own writes
  - Monotonic reads: a session never goes backwards
  - Monotonic writes: writes from a session are ordered

Each session maintains a frontier HLC timestamp.
Visibility checks compare atom HLC against the session frontier.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from threading import Lock

from gaia_core.memory.hlc import HLCTimestamp

log = logging.getLogger(__name__)


@dataclass
class SessionState:
    session_id: str
    read_frontier: HLCTimestamp | None = None
    write_frontier: HLCTimestamp | None = None
    written_atom_ids: list[str] = field(default_factory=list)


class SessionFrontier:
    """Thread-safe per-session causal frontier registry."""

    def __init__(self) -> None:
        self._sessions: dict[str, SessionState] = {}
        self._lock = Lock()

    def get_or_create(self, session_id: str) -> SessionState:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionState(session_id=session_id)
            return self._sessions[session_id]

    def record_write(self, session_id: str, atom_id: str, hlc: HLCTimestamp) -> None:
        """Record that this session wrote atom_id at hlc."""
        with self._lock:
            s = self._sessions.setdefault(session_id, SessionState(session_id=session_id))
            if s.write_frontier is None or hlc > s.write_frontier:
                s.write_frontier = hlc
            if s.read_frontier is None or hlc > s.read_frontier:
                s.read_frontier = hlc  # read-your-writes
            s.written_atom_ids.append(atom_id)

    def record_read(self, session_id: str, hlc: HLCTimestamp) -> None:
        """Advance the session read frontier. Enforces monotonic reads."""
        with self._lock:
            s = self._sessions.setdefault(session_id, SessionState(session_id=session_id))
            if s.read_frontier is None or hlc > s.read_frontier:
                s.read_frontier = hlc

    def is_visible(self, session_id: str, atom_hlc: HLCTimestamp, atom_id: str) -> bool:
        """Return True if atom is visible to this session.

        Always visible if: written by this session, or atom_hlc <= read_frontier.
        """
        with self._lock:
            s = self._sessions.get(session_id)
            if s is None:
                return True  # unknown session — open policy
            if atom_id in s.written_atom_ids:
                return True  # read-your-writes
            if s.read_frontier is None:
                return True
            return atom_hlc <= s.read_frontier

    def close(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)
