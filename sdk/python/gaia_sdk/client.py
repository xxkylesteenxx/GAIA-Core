"""GAIA Python SDK — GAPI Client

Layer: L6 — Apps / SDK / Scripting / Plugins
Language: Python

Provides a typed, thin client for the GAIA Platform API (GAPI).
All system interactions go through this broker — never direct syscalls.
"""

from __future__ import annotations
from typing import Optional
import httpx


class GaiaClient:
    """Thin GAPI HTTP/gRPC client for Python apps and plugins."""

    def __init__(
        self,
        base_url: str = "http://localhost:8080",
        api_key: Optional[str] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}

    def healthz(self) -> dict:
        """Check GAPI broker health."""
        response = httpx.get(f"{self.base_url}/healthz", headers=self.headers, timeout=10.0)
        response.raise_for_status()
        return response.json()

    def infer(self, prompt: str, max_tokens: int = 512) -> dict:
        """Submit an inference request through the GAPI broker."""
        response = httpx.post(
            f"{self.base_url}/v1/infer",
            headers=self.headers,
            json={"prompt": prompt, "max_tokens": max_tokens},
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()

    def atlas_query(self, domain: str, query_type: str, location: Optional[dict] = None) -> dict:
        """Query the ATLAS environmental intelligence layer."""
        response = httpx.post(
            f"{self.base_url}/v1/atlas/query",
            headers=self.headers,
            json={"domain": domain, "query_type": query_type, "location": location},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()
