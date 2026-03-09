from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict

from gaia_core.models import CheckpointManifest, utcnow


class CheckpointStore:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        payload: Dict[str, Any],
        identity_fingerprint: str,
        registered_cores: list[str],
        event_count: int,
        workspace_epoch: int,
    ) -> CheckpointManifest:
        checkpoint_id = f"ckpt_{uuid.uuid4().hex[:12]}"
        checkpoint_dir = self.root / checkpoint_id
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
        manifest = CheckpointManifest(
            checkpoint_id=checkpoint_id,
            created_at=utcnow(),
            identity_root_fingerprint=identity_fingerprint,
            registered_cores=registered_cores,
            event_count=event_count,
            workspace_epoch=workspace_epoch,
            notes=["bootstrap checkpoint"],
        )
        (checkpoint_dir / "manifest.json").write_text(json.dumps({
            "checkpoint_id":            manifest.checkpoint_id,
            "created_at":               manifest.created_at.isoformat(),
            "identity_root_fingerprint": manifest.identity_root_fingerprint,
            "registered_cores":         manifest.registered_cores,
            "event_count":              manifest.event_count,
            "workspace_epoch":          manifest.workspace_epoch,
            "notes":                    manifest.notes,
        }, indent=2), encoding="utf-8")
        (checkpoint_dir / "state.json").write_text(
            json.dumps(payload, indent=2, default=str), encoding="utf-8"
        )
        return manifest

    def latest(self) -> Path | None:
        checkpoints = sorted(self.root.glob("ckpt_*"))
        return checkpoints[-1] if checkpoints else None
