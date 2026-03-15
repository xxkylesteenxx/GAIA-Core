"""Mount controller for the GAIA FUSE meta-overlay projection filesystem.

This module manages the lifecycle of the FUSE daemon process:
  mount()   -- spawn the daemon and mount /gaia/views
  unmount() -- cleanly unmount and terminate the daemon
  status()  -- return current mount state

The actual filesystem logic lives in fuse_daemon.py.  This module is the
shell that entrypoints and systemd units call.
"""
from __future__ import annotations

import logging
import os
import signal
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_MOUNT_POINT = Path("/gaia/views")
DEFAULT_STATE_ROOT = Path(".gaia_state")


@dataclass
class MountState:
    mounted: bool = False
    mount_point: Path = DEFAULT_MOUNT_POINT
    state_root: Path = DEFAULT_STATE_ROOT
    pid: Optional[int] = None
    error: Optional[str] = None


class MetaOverlayMount:
    """Controls mount/unmount of the GAIA projection FUSE filesystem."""

    def __init__(
        self,
        mount_point: Path = DEFAULT_MOUNT_POINT,
        state_root: Path = DEFAULT_STATE_ROOT,
    ) -> None:
        self.mount_point = mount_point
        self.state_root = state_root
        self._proc: Optional[subprocess.Popen] = None

    def mount(self) -> MountState:
        """Create the mount point and launch the FUSE daemon."""
        self.mount_point.mkdir(parents=True, exist_ok=True)

        daemon_script = Path(__file__).parent / "fuse_daemon.py"
        if not daemon_script.exists():
            return MountState(
                mounted=False,
                mount_point=self.mount_point,
                state_root=self.state_root,
                error=f"fuse_daemon.py not found at {daemon_script}",
            )

        try:
            self._proc = subprocess.Popen(
                [
                    "python3",
                    str(daemon_script),
                    "--mount", str(self.mount_point),
                    "--state-root", str(self.state_root),
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            logger.info(
                "MetaOverlay FUSE daemon launched. pid=%d mount=%s",
                self._proc.pid,
                self.mount_point,
            )
            return MountState(
                mounted=True,
                mount_point=self.mount_point,
                state_root=self.state_root,
                pid=self._proc.pid,
            )
        except Exception as exc:
            logger.error("MetaOverlay mount failed: %s", exc)
            return MountState(
                mounted=False,
                mount_point=self.mount_point,
                state_root=self.state_root,
                error=str(exc),
            )

    def unmount(self) -> None:
        """Unmount the FUSE filesystem and terminate the daemon."""
        try:
            subprocess.run(
                ["fusermount", "-u", str(self.mount_point)],
                check=False,
            )
        except FileNotFoundError:
            pass
        if self._proc and self._proc.poll() is None:
            self._proc.send_signal(signal.SIGTERM)
            try:
                self._proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self._proc.kill()
        logger.info("MetaOverlay FUSE daemon stopped.")

    def status(self) -> MountState:
        running = self._proc is not None and self._proc.poll() is None
        return MountState(
            mounted=running,
            mount_point=self.mount_point,
            state_root=self.state_root,
            pid=self._proc.pid if running else None,
        )
