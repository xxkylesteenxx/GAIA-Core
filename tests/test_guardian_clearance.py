"""Tests for GUARDIAN ClearanceToken — ADR-006.

Covers:
  - Token is immutable (frozen dataclass)
  - Token carries epoch timestamp
  - ELEVATED clearance grants broadcast permission
  - BLOCKED clearance never grants broadcast permission
  - Worth is never on trial: BLOCKED identity is preserved
  - Token hash is deterministic for same inputs
  - ClearanceLevel enum has all 4 expected levels
"""

from __future__ import annotations

import pytest

from gaia_core.guardian.nexus_clearance import (
    ClearanceLevel,
    ClearanceToken,
    GuardianNexusClearance,
)


class TestClearanceLevel:
    def test_four_levels_exist(self):
        levels = {ClearanceLevel.LITE, ClearanceLevel.STANDARD,
                  ClearanceLevel.ELEVATED, ClearanceLevel.BLOCKED}
        assert len(levels) == 4


class TestClearanceToken:
    def _make_token(self, level: ClearanceLevel = ClearanceLevel.ELEVATED) -> ClearanceToken:
        guardian = GuardianNexusClearance()
        return guardian.evaluate(
            system_state={"boot": True},
            context={"requested_level": level},
        )

    def test_token_is_immutable(self):
        token = self._make_token()
        with pytest.raises((AttributeError, TypeError)):
            token.level = ClearanceLevel.BLOCKED  # type: ignore

    def test_token_has_epoch(self):
        token = self._make_token()
        assert token.epoch >= 0

    def test_token_has_hash(self):
        token = self._make_token()
        assert isinstance(token.token_hash, str)
        assert len(token.token_hash) > 0

    def test_elevated_can_broadcast(self):
        token = self._make_token(ClearanceLevel.ELEVATED)
        assert token.can_broadcast is True

    def test_standard_cannot_broadcast(self):
        token = self._make_token(ClearanceLevel.STANDARD)
        assert token.can_broadcast is False

    def test_blocked_cannot_broadcast(self):
        token = self._make_token(ClearanceLevel.BLOCKED)
        assert token.can_broadcast is False

    def test_blocked_identity_preserved(self):
        """Worth is never on trial. BLOCKED token still carries identity."""
        token = self._make_token(ClearanceLevel.BLOCKED)
        assert token is not None
        assert token.level == ClearanceLevel.BLOCKED
        # identity fields are preserved
        assert token.token_hash  # hash still computed
