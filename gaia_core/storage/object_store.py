"""object_store -- thin re-export shim for spec name compatibility.

The implementation lives in ``gaia_core.storage.substrate`` as
``ObjectSubstrate``.  This module re-exports it under the name
``ObjectStore`` so that code citing the spec filename works as an
import path, and so that future callers can migrate to either name.

Spec reference
--------------
GAIA_Dual_Plane_Storage_and_Meta_File_System_Spec_v1.0.md lists
``object_store.py`` in the file plan.  The implementation landed as
``substrate.py`` to reflect that the module owns the full dual-plane
substrate, not just the object layer.  Both names are now valid.
"""
from __future__ import annotations

from gaia_core.storage.substrate import ObjectSubstrate as ObjectSubstrate  # noqa: F401

# Alias the canonical implementation class under the spec name.
ObjectStore = ObjectSubstrate

__all__ = ["ObjectStore", "ObjectSubstrate"]
