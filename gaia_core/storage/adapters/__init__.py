"""Storage adapters: filesystem surface layer for the dual-plane substrate.

Adapters translate the in-process substrate API into OS-level interfaces:

  fuse_mount      -- FUSE daemon that mounts projection views as real paths
  overlay_runtime -- system/data plane split (read-only system + writable data)

Neither adapter is required for the substrate to function in-process.
They are activated at boot by the platform layer when the OS environment
supports FUSE (Linux with libfuse3) and overlayfs.
"""
from gaia_core.storage.adapters.fuse_mount import GaiaFuseMount
from gaia_core.storage.adapters.overlay_runtime import OverlayRuntime

__all__ = ["GaiaFuseMount", "OverlayRuntime"]
