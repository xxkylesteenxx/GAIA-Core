"""GAIA meta-overlay FUSE daemon.

This daemon mounts the GAIA semantic projection filesystem at
/gaia/views (or a configured path) and serves virtual directory
trees derived from the SemanticIndex and NamespaceViewRegistry.

Virtual path layout served
---------------------------
/gaia/views/
  by-core/<CORE_NAME>/<object_id>          -- objects scoped to a core
  by-trust/high/<object_id>                -- high/verified trust objects
  by-kind/sensor-event/<object_id>         -- sensor artifacts
  by-tenant/<TENANT_ID>/<object_id>        -- tenant-scoped objects
  by-planetary-state/<object_id>           -- open planetary view

Each virtual file, when read, returns the JSON-serialised SemanticRecord
for that object.  Raw bytes are available via the substrate read path;
this daemon exposes the semantic metadata layer.

Dependencies
------------
  pip install fusepy          # pure-Python FUSE bindings
  apt install fuse libfuse-dev

Usage
-----
  python3 fuse_daemon.py --mount /gaia/views --state-root .gaia_state
"""
from __future__ import annotations

import argparse
import errno
import json
import logging
import os
import stat
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Graceful import of fuse — daemon works without fusepy for unit-testing.
# ---------------------------------------------------------------------------
try:
    from fuse import FUSE, FuseOSError, Operations  # type: ignore
    _FUSE_AVAILABLE = True
except ImportError:
    _FUSE_AVAILABLE = False
    # Stubs so the module is importable in test environments.
    class Operations:  # type: ignore
        pass
    class FuseOSError(OSError):  # type: ignore
        pass


# ---------------------------------------------------------------------------
# Virtual filesystem tree helpers
# ---------------------------------------------------------------------------

def _build_tree(registry) -> Dict[str, Any]:
    """Materialise the full virtual directory tree as a nested dict.
    Keys are path components; leaf values are SemanticRecord dicts.
    """
    tree: Dict[str, Any] = {}
    for view in registry.list_views():
        # Strip /gaia/views/ prefix
        parts = [p for p in view.virtual_prefix.strip("/").split("/") if p]
        # Skip leading 'gaia/views'
        if parts[:2] == ["gaia", "views"]:
            parts = parts[2:]
        node = tree
        for part in parts:
            node = node.setdefault(part, {})
        # Populate leaf with object_id -> record dict
        for record in registry.enumerate_view(view.view_id):
            node[record.object_id] = record.to_dict()
    return tree


def _resolve(tree: Dict, parts: List[str]) -> Optional[Any]:
    node = tree
    for part in parts:
        if not isinstance(node, dict):
            return None
        node = node.get(part)
        if node is None:
            return None
    return node


# ---------------------------------------------------------------------------
# FUSE Operations implementation
# ---------------------------------------------------------------------------

class GAIAProjectionFS(Operations):  # type: ignore
    """Read-only FUSE filesystem serving GAIA semantic projection views."""

    def __init__(self, state_root: Path) -> None:
        from gaia_core.storage.substrate import ObjectSubstrate
        from gaia_core.storage.namespace_views import build_standard_views
        from gaia_core.bootstrap import DEFAULT_CORES

        self._substrate = ObjectSubstrate(state_root)
        self._registry = build_standard_views(
            index=self._substrate.index,
            core_names=DEFAULT_CORES,
        )
        self._refresh_tree()

    def _refresh_tree(self) -> None:
        self._tree = _build_tree(self._registry)

    # ------------------------------------------------------------------
    # FUSE interface
    # ------------------------------------------------------------------

    def getattr(self, path: str, fh=None):
        self._refresh_tree()
        if path == "/":
            return self._dir_stat()
        parts = [p for p in path.strip("/").split("/") if p]
        node = _resolve(self._tree, parts)
        if node is None:
            raise FuseOSError(errno.ENOENT)
        if isinstance(node, dict) and not self._is_leaf_record(node):
            return self._dir_stat()
        return self._file_stat(self._serialise(node))

    def readdir(self, path: str, fh):
        self._refresh_tree()
        yield "."
        yield ".."
        if path == "/":
            for key in self._tree:
                yield key
            return
        parts = [p for p in path.strip("/").split("/") if p]
        node = _resolve(self._tree, parts)
        if node is None:
            raise FuseOSError(errno.ENOENT)
        if isinstance(node, dict):
            for key in node:
                yield key

    def read(self, path: str, size: int, offset: int, fh):
        parts = [p for p in path.strip("/").split("/") if p]
        node = _resolve(self._tree, parts)
        if node is None:
            raise FuseOSError(errno.ENOENT)
        data = self._serialise(node).encode()
        return data[offset: offset + size]

    def open(self, path: str, flags):
        return 0

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_leaf_record(d: dict) -> bool:
        return "object_id" in d and "kind" in d

    @staticmethod
    def _serialise(node) -> str:
        return json.dumps(node, indent=2, default=str)

    @staticmethod
    def _dir_stat() -> dict:
        return dict(
            st_mode=stat.S_IFDIR | 0o555,
            st_nlink=2,
            st_size=0,
            st_ctime=0, st_mtime=0, st_atime=0,
            st_uid=os.getuid(),
            st_gid=os.getgid(),
        )

    @staticmethod
    def _file_stat(content: str) -> dict:
        return dict(
            st_mode=stat.S_IFREG | 0o444,
            st_nlink=1,
            st_size=len(content.encode()),
            st_ctime=0, st_mtime=0, st_atime=0,
            st_uid=os.getuid(),
            st_gid=os.getgid(),
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="GAIA meta-overlay FUSE daemon")
    parser.add_argument("--mount", default="/gaia/views", help="FUSE mount point")
    parser.add_argument("--state-root", default=".gaia_state", help="GAIA state root")
    parser.add_argument("--foreground", action="store_true", default=True)
    args = parser.parse_args()

    if not _FUSE_AVAILABLE:
        raise SystemExit("fusepy is not installed. Run: pip install fusepy")

    logging.basicConfig(level=logging.INFO)
    state_root = Path(args.state_root)
    mount_point = args.mount

    logger.info("Mounting GAIA projection FS at %s (state=%s)", mount_point, state_root)
    FUSE(
        GAIAProjectionFS(state_root),
        mount_point,
        nothreads=True,
        foreground=args.foreground,
        ro=True,
    )


if __name__ == "__main__":
    main()
