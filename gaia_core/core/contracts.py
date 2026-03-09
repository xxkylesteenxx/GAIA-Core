from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List


@dataclass(slots=True)
class CoreMessage:
    source: str
    target: str
    kind: str
    payload: Dict[str, Any]


@dataclass(slots=True)
class CoreResponse:
    target: str
    accepted: bool
    summary: str
    payload: Dict[str, Any]
    warnings: List[str]
