"""Dual-plane object substrate: raw storage + semantic annotation.

ObjectSubstrate is the primary write path for all substrate objects.
Every write:
  1. Stores the raw bytes / file into the objects/ content tree.
  2. Writes compact xattrs onto the file for inode-local identity.
  3. Inserts a SemanticRecord into the SemanticIndex for rich metadata.

This is the module that bootstrap.py uses to initialise the expanded
.gaia_state layout.  It deliberately does not import from bootstrap.py
to avoid circular dependencies.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Optional

from gaia_core.storage.object_id import ObjectID, ObjectKind, generate_object_id
from gaia_core.storage.semantic_index import SemanticIndex, SemanticRecord
from gaia_core.storage.xattrs import annotate_object


class ObjectSubstrate:
    """Content-addressed object store with dual-plane semantic annotation."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self.objects_dir = root / "objects"
        self.semantic_dir = root / "semantic"
        self.views_dir = root / "views"

        for d in (self.objects_dir, self.semantic_dir, self.views_dir):
            d.mkdir(parents=True, exist_ok=True)

        self.index = SemanticIndex(self.semantic_dir / "index.jsonl")

    # ------------------------------------------------------------------
    # Write path
    # ------------------------------------------------------------------

    def put(
        self,
        data: bytes,
        kind: ObjectKind,
        *,
        ontology_type: str = "gaia:unknown",
        trust_level: str = "standard",
        origin_core: str = "GAIA",
        policy_class: str = "default",
        tenant_id: Optional[str] = None,
        node_id: Optional[str] = None,
        core_scope: Optional[str] = None,
        retrieval_tags: Optional[list] = None,
        provenance_chain: Optional[list] = None,
        causal_parents: Optional[list] = None,
    ) -> ObjectID:
        """Write *data* into the substrate and return its ObjectID."""
        oid = generate_object_id(data, kind)

        # 1. Raw bytes to objects/
        obj_path = self._object_path(oid)
        obj_path.parent.mkdir(parents=True, exist_ok=True)
        if not obj_path.exists():
            obj_path.write_bytes(data)

        # 2. Compact inode xattrs
        annotate_object(
            obj_path,
            object_id=str(oid),
            kind=kind.value,
            trust_level=trust_level,
            origin_core=origin_core,
            policy_class=policy_class,
        )

        # 3. Rich semantic record
        record = SemanticRecord(
            object_id=str(oid),
            kind=kind.value,
            ontology_type=ontology_type,
            provenance_chain=provenance_chain or [],
            causal_parents=causal_parents or [],
            retrieval_tags=retrieval_tags or [],
            trust_level=trust_level,
            tenant_id=tenant_id,
            node_id=node_id,
            core_scope=core_scope,
        )
        self.index.put(record)

        return oid

    # ------------------------------------------------------------------
    # Read path
    # ------------------------------------------------------------------

    def get_bytes(self, oid: ObjectID) -> Optional[bytes]:
        p = self._object_path(oid)
        return p.read_bytes() if p.exists() else None

    def get_record(self, oid: ObjectID) -> Optional[SemanticRecord]:
        return self.index.get(str(oid))

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _object_path(self, oid: ObjectID) -> Path:
        # 2-char sharding on content hash prefix (git-style)
        shard = oid.content_hash[:2]
        return self.objects_dir / shard / oid.content_hash
