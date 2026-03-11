"""Circuit breaker for GAIA inference backends.

Prevents cascading failures by tracking consecutive errors per backend
and opening the circuit after a configurable threshold.

States:
  CLOSED  — normal operation, requests pass through
  OPEN    — backend is failing, requests rejected immediately
  HALF_OPEN — probe window, one request allowed through to test recovery
"""
from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from typing import Callable, TypeVar

log = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 3        # consecutive failures before opening
    recovery_timeout_s: float = 30.0  # seconds before attempting half-open probe
    success_threshold: int = 2        # consecutive successes to close from half-open


@dataclass
class CircuitBreakerState:
    state: CircuitState = CircuitState.CLOSED
    consecutive_failures: int = 0
    consecutive_successes: int = 0
    opened_at: float = 0.0
    total_failures: int = 0
    total_successes: int = 0
    total_rejected: int = 0


class CircuitBreaker:
    """Thread-safe circuit breaker for a single backend."""

    def __init__(self, name: str, config: CircuitBreakerConfig | None = None) -> None:
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self._state = CircuitBreakerState()
        self._lock = Lock()

    @property
    def state(self) -> CircuitState:
        return self._state.state

    def is_available(self) -> bool:
        """Returns True if the circuit allows a request through."""
        with self._lock:
            if self._state.state == CircuitState.CLOSED:
                return True
            if self._state.state == CircuitState.OPEN:
                elapsed = time.monotonic() - self._state.opened_at
                if elapsed >= self.config.recovery_timeout_s:
                    log.info("[%s] Circuit entering HALF_OPEN for probe", self.name)
                    self._state.state = CircuitState.HALF_OPEN
                    return True
                self._state.total_rejected += 1
                return False
            # HALF_OPEN — allow one probe through
            return True

    def record_success(self) -> None:
        with self._lock:
            self._state.total_successes += 1
            self._state.consecutive_failures = 0
            if self._state.state == CircuitState.HALF_OPEN:
                self._state.consecutive_successes += 1
                if self._state.consecutive_successes >= self.config.success_threshold:
                    log.info("[%s] Circuit CLOSED after recovery", self.name)
                    self._state.state = CircuitState.CLOSED
                    self._state.consecutive_successes = 0
            elif self._state.state == CircuitState.CLOSED:
                self._state.consecutive_successes += 1

    def record_failure(self) -> None:
        with self._lock:
            self._state.total_failures += 1
            self._state.consecutive_failures += 1
            self._state.consecutive_successes = 0
            if self._state.state in (CircuitState.CLOSED, CircuitState.HALF_OPEN):
                if self._state.consecutive_failures >= self.config.failure_threshold:
                    log.warning(
                        "[%s] Circuit OPEN after %d consecutive failures",
                        self.name, self._state.consecutive_failures,
                    )
                    self._state.state = CircuitState.OPEN
                    self._state.opened_at = time.monotonic()

    def call(self, fn: Callable[[], T]) -> T:
        """Execute fn() guarded by the circuit breaker."""
        if not self.is_available():
            raise RuntimeError(
                f"Circuit breaker OPEN for backend '{self.name}'. "
                f"Retry after {self.config.recovery_timeout_s}s."
            )
        try:
            result = fn()
            self.record_success()
            return result
        except Exception as exc:
            self.record_failure()
            raise exc

    def status(self) -> dict:
        s = self._state
        return {
            "backend": self.name,
            "state": s.state.value,
            "consecutive_failures": s.consecutive_failures,
            "consecutive_successes": s.consecutive_successes,
            "total_failures": s.total_failures,
            "total_successes": s.total_successes,
            "total_rejected": s.total_rejected,
        }
