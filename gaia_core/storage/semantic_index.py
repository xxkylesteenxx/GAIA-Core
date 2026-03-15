"""Semantic index: the rich metadata plane for GAIA substrate objects.

This module owns everything that is too large or too relational to live in
an inode xattr:
  - ontology type
  - provenance chain (ordered list of ancestor object IDs)
  - causal parents (event-causal graph edges)
  - embedding references (vector store pointers)
  - retrieval tags
  - actuation constraints
  - tenant / node / core scope

The backing store is intentionally simple at this stage: a JSON-lines file
that can be trivially replaced with SQLite, DuckDB, or a graph DB later.
The public API (SemanticIndex) will remain stable across backend changes.
"""
from __future__ import annotations

import json
import threading
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class SemanticRecord:
    object_id: str
    kind: str
    ontology_type: str = "gaia:unknown"
    provenance_chain: List[str] = field(default_factory=list)
    causal_parents: List[str] = field(default_factory=list)
    embedding_refs: List[str] = field(default_factory=list)
    retrieval_tags: List[str] = field(default_factory=list)
    actuation_constraints: List[str] = field(default_factory=list)
    tenant_id: Optional[str] = None
    node_id: Optional[str] = None
    core_scope: Optional[str] = None
    trust_level: str = "standard"
    extra: Dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "SemanticRecord":
        known = {f.name for f in cls.__dataclass_fields__.values()}  # type: ignore[attr-defined]
        extra = {k: v for k, v in d.items() if k not in known}
        base = {k: v for k, v in d.items() if k in known}
        base["extra"] = {**base.get("extra", {}), **extra}
        return cls(**base)


class SemanticIndex:
    """Append-friendly, thread-safe JSONL-backed semantic metadata store."""

    def __init__(self, index_path: Path) -> None:
        self._path = index_path
        self._lock = threading.Lock()
        self._cache: Dict[str, SemanticRecord] = {}
        self._load()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load(self) -> None:
        if not self._path.exists():
            return
        with self._lock:
            with self._path.open() as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        rec = SemanticRecord.from_dict(json.loads(line))
                        self._cache[rec.object_id] = rec
                    except (json.JSONDecodeError, TypeError):
                        continue

    def _append(self, record: SemanticRecord) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        with self._path.open("a") as fh:
            fh.write(json.dumps(record.to_dict()) + "\n")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def put(self, record: SemanticRecord) -> None:
        """Insert or overwrite a semantic record."""
        with self._lock:
            self._cache[record.object_id] = record
            self._append(record)

    def get(self, object_id: str) -> Optional[SemanticRecord]:
        with self._lock:
            return self._cache.get(object_id)

    def query_by_kind(self, kind: str) -> List[SemanticRecord]:
        with self._lock:
            return [r for r in self._cache.values() if r.kind == kind]

    def query_by_core(self, core_scope: str) -> List[SemanticRecord]:
        with self._lock:
            return [r for r in self._cache.values() if r.core_scope == core_scope]

    def query_by_tenant(self, tenant_id: str) -> List[SemanticRecord]:
        with self._lock:
            return [r for r in self._cache.values() if r.tenant_id == tenant_id]

    def query_by_trust(self, trust_level: str) -> List[SemanticRecord]:
        with self._lock:
            return [r for r in self._cache.values() if r.trust_level == trust_level]

    def query_by_tag(self, tag: str) -> List[SemanticRecord]:
        with self._lock:
            return [r for r in self._cache.values() if tag in r.retrieval_tags]

    def all_records(self) -> List[SemanticRecord]:
        with self._lock:
            return list(self._cache.values())

    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)
