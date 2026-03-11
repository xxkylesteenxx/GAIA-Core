"""Triton Inference Server backend — perception / embedding / classifier.

Dependency: tritonclient[http] (optional, guarded import)
Used by ATLAS, TERRA, AQUA, AERO, VITA cores.
"""
from __future__ import annotations

import logging
import time
from typing import Any

import numpy as np  # type: ignore

from gaia_core.inference.contracts import InferBackend, InferRequest, InferResponse

log = logging.getLogger(__name__)

try:
    import tritonclient.http as triton_http  # type: ignore
    _TRITON_AVAILABLE = True
except ImportError:
    _TRITON_AVAILABLE = False
    triton_http = None  # type: ignore


class TritonBackend:
    """Triton Inference Server backend for embedding + classifier workloads."""

    def __init__(self, url: str = "localhost:8000", model_name: str | None = None) -> None:
        if not _TRITON_AVAILABLE:
            raise ImportError("tritonclient[http] is required. Run: pip install tritonclient[http]")
        self._client = triton_http.InferenceServerClient(url=url)
        self._default_model = model_name

    def infer(self, request: InferRequest) -> InferResponse:
        model_name = self._default_model or request.model_id
        t0 = time.monotonic()
        # Encode prompt as bytes tensor — model-specific preprocessing expected upstream
        input_data = np.array([[request.prompt.encode()]], dtype=object)
        infer_input = triton_http.InferInput("INPUT", input_data.shape, "BYTES")
        infer_input.set_data_from_numpy(input_data)
        result = self._client.infer(model_name=model_name, inputs=[infer_input])
        latency_ms = (time.monotonic() - t0) * 1000
        output: Any = result.as_numpy("OUTPUT")
        text = output[0][0].decode() if output is not None else ""
        return InferResponse(
            text=text,
            model_id=request.model_id,
            backend=InferBackend.TRITON,
            latency_ms=latency_ms,
        )
