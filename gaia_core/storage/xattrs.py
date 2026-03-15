"""POSIX extended-attribute helpers for GAIA substrate objects.

xattrs are the inode-local metadata layer.  Keep values compact:
- identifiers, kind tags, trust levels, policy class labels.
Do NOT store full semantic records here; use semantic_index.py for that.

Namespace conventions
----------------------
user.gaia.*       -- application-visible identity and kind metadata
trusted.gaia.*    -- kernel-trusted provenance and origin metadata (root-write)
security.gaia.*   -- MAC / policy labels (SELinux / AppArmor / GAIA-policy)

Fallback behaviour
------------------
When the underlying filesystem does not support xattrs (tmpfs without
mount options, some network filesystems) all operations become no-ops so
the rest of the storage layer continues to function.
"""
from __future__ import annotations

import errno
import os
from pathlib import Path
from typing import Dict, Optional

# GAIA xattr key constants
KEY_OBJECT_ID = "user.gaia.object_id"
KEY_KIND = "user.gaia.kind"
KEY_TRUST_LEVEL = "trusted.gaia.trust_level"
KEY_ORIGIN_CORE = "trusted.gaia.origin_core"
KEY_POLICY_CLASS = "security.gaia.policy_class"


def _path(p: Path | str) -> bytes:
    return os.fsencode(str(p))


def set_xattr(path: Path | str, key: str, value: str) -> bool:
    """Write a single xattr; returns False if xattrs are unsupported."""
    try:
        os.setxattr(_path(path), key.encode(), value.encode())  # type: ignore[attr-defined]
        return True
    except (OSError, AttributeError) as exc:
        if isinstance(exc, OSError) and exc.errno not in (
            errno.ENOTSUP,
            errno.EOPNOTSUPP,
            errno.EACCES,
        ):
            raise
        return False


def get_xattr(path: Path | str, key: str) -> Optional[str]:
    """Read a single xattr; returns None when absent or unsupported."""
    try:
        raw = os.getxattr(_path(path), key.encode())  # type: ignore[attr-defined]
        return raw.decode()
    except (OSError, AttributeError):
        return None


def annotate_object(
    path: Path | str,
    *,
    object_id: str,
    kind: str,
    trust_level: str = "standard",
    origin_core: str = "GAIA",
    policy_class: str = "default",
) -> Dict[str, bool]:
    """Write all standard GAIA xattrs for a substrate object in one call."""
    results = {
        KEY_OBJECT_ID: set_xattr(path, KEY_OBJECT_ID, object_id),
        KEY_KIND: set_xattr(path, KEY_KIND, kind),
        KEY_TRUST_LEVEL: set_xattr(path, KEY_TRUST_LEVEL, trust_level),
        KEY_ORIGIN_CORE: set_xattr(path, KEY_ORIGIN_CORE, origin_core),
        KEY_POLICY_CLASS: set_xattr(path, KEY_POLICY_CLASS, policy_class),
    }
    return results


def read_all_gaia_xattrs(path: Path | str) -> Dict[str, str]:
    """Return a dict of all user.gaia.* / trusted.gaia.* / security.gaia.* attrs."""
    try:
        raw_keys: list[bytes] = os.listxattr(_path(path))  # type: ignore[attr-defined]
    except (OSError, AttributeError):
        return {}
    result: Dict[str, str] = {}
    for raw_key in raw_keys:
        key = raw_key.decode(errors="replace")
        if key.startswith(("user.gaia.", "trusted.gaia.", "security.gaia.")):
            val = get_xattr(path, key)
            if val is not None:
                result[key] = val
    return result
