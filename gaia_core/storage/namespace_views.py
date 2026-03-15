"""Namespace views: logical filesystem projections over the semantic index.

Each ViewDefinition maps a virtual path prefix to a (SemanticIndex, Policy)
pair.  The NamespaceViewRegistry collects all registered views and provides
an enumerate_view() helper that the FUSE daemon (platform/filesystem/
meta_overlay/) will call to list and resolve objects under a virtual path.

Virtual path conventions
-------------------------
/gaia/views/by-core/<CORE_NAME>/
/gaia/views/by-trust/<LEVEL>/
/gaia/views/by-kind/<KIND>/
/gaia/views/by-tenant/<TENANT_ID>/
/gaia/views/by-tag/<TAG>/
/gaia/views/by-planetary-state/
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from gaia_core.storage.projection_policy import ProjectionPolicy, filter_records
from gaia_core.storage.semantic_index import SemanticIndex, SemanticRecord


@dataclass
class ViewDefinition:
    view_id: str
    virtual_prefix: str  # e.g. "/gaia/views/by-core/SOPHIA"
    index: SemanticIndex
    policy: ProjectionPolicy
    description: str = ""
    read_only: bool = True


class NamespaceViewRegistry:
    """Holds all registered views; consulted by the projection / FUSE layer."""

    def __init__(self) -> None:
        self._views: Dict[str, ViewDefinition] = {}

    def register(self, view: ViewDefinition) -> None:
        self._views[view.view_id] = view

    def get(self, view_id: str) -> Optional[ViewDefinition]:
        return self._views.get(view_id)

    def list_views(self) -> List[ViewDefinition]:
        return list(self._views.values())

    def enumerate_view(self, view_id: str) -> List[SemanticRecord]:
        """Return all records visible under *view_id* after policy filtering."""
        view = self._views.get(view_id)
        if view is None:
            return []
        return filter_records(view.index.all_records(), view.policy)

    def resolve_object(self, view_id: str, object_id: str) -> Optional[SemanticRecord]:
        """Resolve a single object ID within a view; returns None if not visible."""
        view = self._views.get(view_id)
        if view is None:
            return None
        record = view.index.get(object_id)
        if record is None:
            return None
        return record if view.policy.matches(record) else None


def build_standard_views(
    index: SemanticIndex,
    core_names: Optional[List[str]] = None,
    tenant_ids: Optional[List[str]] = None,
) -> NamespaceViewRegistry:
    """Bootstrap a NamespaceViewRegistry with the standard GAIA view set."""
    from gaia_core.storage.projection_policy import (
        POLICY_HIGH_TRUST,
        POLICY_OPEN,
        POLICY_SENSOR_EVENTS,
        ProjectionPolicy,
    )

    registry = NamespaceViewRegistry()

    registry.register(ViewDefinition(
        view_id="by-trust-high",
        virtual_prefix="/gaia/views/by-trust/high",
        index=index,
        policy=POLICY_HIGH_TRUST,
        description="High-trust and verified objects only.",
    ))

    registry.register(ViewDefinition(
        view_id="by-kind-sensor",
        virtual_prefix="/gaia/views/by-kind/sensor-event",
        index=index,
        policy=POLICY_SENSOR_EVENTS,
        description="All inbound sensor artifacts.",
    ))

    registry.register(ViewDefinition(
        view_id="planetary",
        virtual_prefix="/gaia/views/by-planetary-state",
        index=index,
        policy=POLICY_OPEN,
        description="Unrestricted planetary-state view.",
    ))

    for core in (core_names or []):
        policy = ProjectionPolicy(
            name=f"core-{core.lower()}",
            allowed_cores=[core],
        )
        registry.register(ViewDefinition(
            view_id=f"by-core-{core.lower()}",
            virtual_prefix=f"/gaia/views/by-core/{core}",
            index=index,
            policy=policy,
            description=f"Objects scoped to core {core}.",
        ))

    for tenant in (tenant_ids or []):
        policy = ProjectionPolicy(
            name=f"tenant-{tenant}",
            allowed_tenants=[tenant],
        )
        registry.register(ViewDefinition(
            view_id=f"by-tenant-{tenant}",
            virtual_prefix=f"/gaia/views/by-tenant/{tenant}",
            index=index,
            policy=policy,
            description=f"Objects scoped to tenant {tenant}.",
        ))

    return registry
