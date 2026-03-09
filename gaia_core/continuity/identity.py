from __future__ import annotations

import hashlib
import json
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class IdentityRoot:
    backend: str
    private_seed_hex: str
    public_fingerprint: str

    @classmethod
    def create(cls, backend: str = "software-fallback") -> "IdentityRoot":
        seed = secrets.token_bytes(32)  # 256-bit root
        fingerprint = hashlib.sha256(seed).hexdigest()
        return cls(backend=backend, private_seed_hex=seed.hex(), public_fingerprint=fingerprint)

    def persist(self, path: Path) -> None:
        path.write_text(json.dumps({
            "backend": self.backend,
            "private_seed_hex": self.private_seed_hex,
            "public_fingerprint": self.public_fingerprint,
        }, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: Path) -> "IdentityRoot":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(**payload)
