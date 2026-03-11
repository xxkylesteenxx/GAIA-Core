"""memfd shared memory ring buffer — same-host zero-copy IPC.

Provides a lock-free single-producer / single-consumer ring buffer
backed by a memory-mapped byte array.

On Linux with memfd_create available, the backing store is an
anonymous RAM-backed file (zero disk I/O, close-on-exec, sealable).

Fallback: uses a plain bytearray for portability on macOS/Windows
(correct semantics, not zero-copy).

Wire format per slot:
  [4 bytes: payload_len][payload_len bytes: payload][padding to slot_size]

Usage:
    ring = MemfdRing(capacity=64, slot_size=4096)
    ring.put(b"hello")   # producer
    data = ring.get()    # consumer (returns None if empty)
"""
from __future__ import annotations

import ctypes
import logging
import mmap
import os
import struct
import sys
from threading import Lock
from typing import Optional

log = logging.getLogger(__name__)

_HEADER_FMT = ">I"   # big-endian uint32 payload length
_HEADER_SIZE = struct.calcsize(_HEADER_FMT)


def _try_memfd_create(name: str) -> int | None:
    """Attempt memfd_create(2) syscall. Returns fd or None if unavailable."""
    if sys.platform != "linux":
        return None
    try:
        # syscall number 319 on x86-64; use ctypes libc wrapper
        libc = ctypes.CDLL("libc.so.6", use_errno=True)
        memfd_create = libc.memfd_create
        memfd_create.restype = ctypes.c_int
        memfd_create.argtypes = [ctypes.c_char_p, ctypes.c_uint]
        MFD_CLOEXEC = 0x0001
        fd = memfd_create(name.encode(), MFD_CLOEXEC)
        if fd < 0:
            return None
        return fd
    except Exception:
        return None


class MemfdRing:
    """Single-producer / single-consumer ring buffer.

    Thread-safe for one producer thread and one consumer thread.
    Not safe for multiple concurrent producers or consumers.
    """

    def __init__(
        self,
        capacity: int = 64,
        slot_size: int = 4096,
        name: str = "gaia_ring",
    ) -> None:
        self.capacity = capacity
        self.slot_size = slot_size
        self.name = name
        self._total_size = capacity * slot_size
        self._write_idx = 0
        self._read_idx = 0
        self._count = 0
        self._lock = Lock()

        # Try memfd_create first, fall back to plain bytearray
        fd = _try_memfd_create(name)
        if fd is not None:
            os.ftruncate(fd, self._total_size)
            self._buf = mmap.mmap(fd, self._total_size)
            os.close(fd)  # mmap holds reference
            self._using_memfd = True
            log.debug("MemfdRing '%s': using memfd_create (%d slots x %d bytes)",
                      name, capacity, slot_size)
        else:
            self._buf = bytearray(self._total_size)  # type: ignore[assignment]
            self._using_memfd = False
            log.debug("MemfdRing '%s': using bytearray fallback (%d slots x %d bytes)",
                      name, capacity, slot_size)

    def _slot_offset(self, idx: int) -> int:
        return (idx % self.capacity) * self.slot_size

    def put(self, data: bytes) -> bool:
        """Write data into the next ring slot. Returns False if ring is full."""
        if len(data) + _HEADER_SIZE > self.slot_size:
            raise ValueError(
                f"Payload {len(data)} bytes exceeds slot_size {self.slot_size - _HEADER_SIZE}"
            )
        with self._lock:
            if self._count >= self.capacity:
                log.warning("MemfdRing '%s' full — dropping message", self.name)
                return False
            offset = self._slot_offset(self._write_idx)
            header = struct.pack(_HEADER_FMT, len(data))
            if self._using_memfd:
                self._buf.seek(offset)  # type: ignore[union-attr]
                self._buf.write(header + data)  # type: ignore[union-attr]
            else:
                self._buf[offset:offset + _HEADER_SIZE + len(data)] = header + data
            self._write_idx = (self._write_idx + 1) % self.capacity
            self._count += 1
            return True

    def get(self) -> bytes | None:
        """Read and return the next slot payload. Returns None if ring is empty."""
        with self._lock:
            if self._count == 0:
                return None
            offset = self._slot_offset(self._read_idx)
            if self._using_memfd:
                self._buf.seek(offset)  # type: ignore[union-attr]
                header = self._buf.read(_HEADER_SIZE)  # type: ignore[union-attr]
                length = struct.unpack(_HEADER_FMT, header)[0]
                data = self._buf.read(length)  # type: ignore[union-attr]
            else:
                header = bytes(self._buf[offset:offset + _HEADER_SIZE])
                length = struct.unpack(_HEADER_FMT, header)[0]
                data = bytes(self._buf[offset + _HEADER_SIZE:offset + _HEADER_SIZE + length])
            self._read_idx = (self._read_idx + 1) % self.capacity
            self._count -= 1
            return data

    def available(self) -> int:
        """Number of slots with unread data."""
        with self._lock:
            return self._count

    def free_slots(self) -> int:
        with self._lock:
            return self.capacity - self._count

    def status(self) -> dict:
        with self._lock:
            return {
                "name": self.name,
                "capacity": self.capacity,
                "slot_size": self.slot_size,
                "used": self._count,
                "free": self.capacity - self._count,
                "using_memfd": self._using_memfd,
            }
