"""Envelope encryption helpers backed by OpenSSL ML-KEM-768.

This module uses ML-KEM only for wrapping a fresh symmetric content-encryption key (CEK).
Payload encryption remains classical symmetric cryptography (AES-GCM), which is the intended
construction for a KEM-based envelope scheme.
"""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import subprocess
from typing import Sequence


@dataclass(slots=True)
class KemEnvelope:
    ciphertext_path: str
    wrapped_key_path: str
    algorithm: str = "ML-KEM-768"



def _run(cmd: Sequence[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, capture_output=True)


def encapsulate_shared_secret(public_key_path: str | Path,
                              wrapped_key_path: str | Path,
                              shared_secret_path: str | Path,
                              openssl_bin: str = "openssl") -> KemEnvelope:
    cmd = [
        openssl_bin,
        "pkeyutl",
        "-encap",
        "-inkey",
        str(public_key_path),
        "-pubin",
        "-out",
        str(wrapped_key_path),
        "-secret",
        str(shared_secret_path),
    ]
    _run(cmd)
    return KemEnvelope(ciphertext_path=str(wrapped_key_path), wrapped_key_path=str(shared_secret_path))


def decapsulate_shared_secret(private_key_path: str | Path,
                              wrapped_key_path: str | Path,
                              shared_secret_path: str | Path,
                              openssl_bin: str = "openssl") -> Path:
    cmd = [
        openssl_bin,
        "pkeyutl",
        "-decap",
        "-inkey",
        str(private_key_path),
        "-in",
        str(wrapped_key_path),
        "-secret",
        str(shared_secret_path),
    ]
    _run(cmd)
    return Path(shared_secret_path)
