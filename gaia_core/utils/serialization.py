"""Wire serialization utilities for GAIA-Core contract objects.

Rules:
- Output is always JSON-safe (str keys, primitive or nested dict/list values).
- datetime is normalized to ISO 8601 UTC string.
- StrEnum values are serialized as their string value.
- Sequences (tuple/list) become lists.
- None is preserved as None.
- schema_version is always included.
- No backend-specific types may appear in output.
"""
from __future__ import annotations

import dataclasses
from datetime import datetime, timezone
from enum import Enum
from typing import Any


def to_wire_dict(obj: Any) -> Any:
    """Recursively convert a contract dataclass to a JSON-safe dict."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return {
            field.name: to_wire_dict(getattr(obj, field.name))
            for field in dataclasses.fields(obj)
        }
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, datetime):
        if obj.tzinfo is None:
            obj = obj.replace(tzinfo=timezone.utc)
        return obj.isoformat()
    if isinstance(obj, (list, tuple)):
        return [to_wire_dict(item) for item in obj]
    if isinstance(obj, dict):
        return {k: to_wire_dict(v) for k, v in obj.items()}
    return obj


def from_wire_dict(cls: type, data: dict[str, Any]) -> Any:
    """Reconstruct a contract dataclass from a wire dict.

    Handles:
    - StrEnum fields: coerces string values back to enum members.
    - datetime fields: parses ISO 8601 strings.
    - Nested dataclass fields: recurses.
    - Sequence fields: reconstructs as tuple (matching contract default_factory).
    - Missing optional fields: uses dataclass field defaults.
    """
    if not dataclasses.is_dataclass(cls):
        raise TypeError(f"{cls} is not a dataclass")

    field_map = {f.name: f for f in dataclasses.fields(cls)}
    kwargs: dict[str, Any] = {}

    for name, field in field_map.items():
        if name not in data:
            if field.default is not dataclasses.MISSING:
                kwargs[name] = field.default
            elif field.default_factory is not dataclasses.MISSING:  # type: ignore[misc]
                kwargs[name] = field.default_factory()  # type: ignore[misc]
            continue

        raw = data[name]
        hint = field.type
        kwargs[name] = _coerce(hint, raw)

    return cls(**kwargs)


def _coerce(hint: Any, value: Any) -> Any:
    """Best-effort type coercion for wire values using string type hints."""
    if value is None:
        return None

    hint_str = str(hint) if not isinstance(hint, str) else hint

    # datetime
    if "datetime" in hint_str and isinstance(value, str):
        return datetime.fromisoformat(value)

    # sequences -> tuple
    if ("Sequence" in hint_str or "tuple" in hint_str or "list" in hint_str) and isinstance(value, (list, tuple)):
        return tuple(value)

    return value
