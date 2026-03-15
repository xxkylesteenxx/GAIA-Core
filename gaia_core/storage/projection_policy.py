"""Projection policy: rules controlling which identities see which objects.

A ProjectionPolicy specifies a set of filter predicates.  The projection
layer (namespace_views.py / FUSE daemon) consults these rules to decide
which SemanticRecords are visible inside a given view path.

Design notes
------------
- Policies are purely data; they contain no I/O logic.
- The predicate fields use OR semantics within a field and AND semantics
  across fields (i.e. all populated predicates must match).
- An empty predicate list for a field means "match any value".
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from gaia_core.storage.semantic_index import SemanticRecord


@dataclass
class ProjectionPolicy:
    """A named, composable filter over SemanticRecords."""

    name: str
    description: str = ""

    # OR-within-field, AND-across-fields predicate sets
    allowed_kinds: List[str] = field(default_factory=list)
    allowed_cores: List[str] = field(default_factory=list)
    allowed_tenants: List[str] = field(default_factory=list)
    allowed_trust_levels: List[str] = field(default_factory=list)
    required_tags: List[str] = field(default_factory=list)  # record must have ALL

    deny_trust_levels: List[str] = field(default_factory=list)
    deny_kinds: List[str] = field(default_factory=list)

    def matches(self, record: SemanticRecord) -> bool:
        """Return True if *record* should be visible under this policy."""
        # --- deny gates (checked first) ---
        if self.deny_trust_levels and record.trust_level in self.deny_trust_levels:
            return False
        if self.deny_kinds and record.kind in self.deny_kinds:
            return False

        # --- allow filters ---
        if self.allowed_kinds and record.kind not in self.allowed_kinds:
            return False
        if self.allowed_cores and record.core_scope not in self.allowed_cores:
            return False
        if self.allowed_tenants and record.tenant_id not in self.allowed_tenants:
            return False
        if self.allowed_trust_levels and record.trust_level not in self.allowed_trust_levels:
            return False
        if self.required_tags:
            if not all(t in record.retrieval_tags for t in self.required_tags):
                return False

        return True


# ---------------------------------------------------------------------------
# Built-in policy presets
# ---------------------------------------------------------------------------

POLICY_HIGH_TRUST = ProjectionPolicy(
    name="high-trust",
    description="Only objects with trust_level='high' or 'verified'.",
    allowed_trust_levels=["high", "verified"],
)

POLICY_SENSOR_EVENTS = ProjectionPolicy(
    name="sensor-events",
    description="All inbound sensor artifacts.",
    allowed_kinds=["sensor-artifact"],
)

POLICY_OPEN = ProjectionPolicy(
    name="open",
    description="Matches everything; used for unrestricted views.",
)


def filter_records(
    records: list,
    policy: ProjectionPolicy,
) -> list:
    """Apply a policy to a list of SemanticRecords."""
    return [r for r in records if policy.matches(r)]
