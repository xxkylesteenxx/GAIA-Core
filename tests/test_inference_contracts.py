"""Unit tests for gaia_core.inference.contracts and router."""
import pytest
from gaia_core.inference.contracts import InferBackend, InferRequest, InferResponse
from gaia_core.inference.router import InferRouter, _resolve_backend


def test_infer_request_defaults():
    req = InferRequest(prompt="hello", model_id="nexus-7b-q4")
    assert req.max_tokens == 512
    assert req.temperature == 0.7
    assert req.stream is False
    assert req.backend is None


def test_infer_request_explicit_backend():
    req = InferRequest(prompt="test", model_id="nexus-7b-q4", backend=InferBackend.LLAMA_CPP)
    assert _resolve_backend(req) == InferBackend.LLAMA_CPP


def test_infer_request_explicit_vllm():
    req = InferRequest(prompt="test", model_id="nexus-70b", backend=InferBackend.VLLM)
    assert _resolve_backend(req) == InferBackend.VLLM


def test_infer_response_fields():
    resp = InferResponse(text="output", model_id="nexus-7b-q4", backend=InferBackend.LLAMA_CPP)
    assert resp.text == "output"
    assert resp.backend == InferBackend.LLAMA_CPP
    assert resp.latency_ms == 0.0


def test_router_no_backend_raises():
    router = InferRouter()
    req = InferRequest(prompt="hello", model_id="nexus-7b-q4", backend=InferBackend.LLAMA_CPP)
    with pytest.raises(RuntimeError, match="No backend registered"):
        router.infer(req)


def test_router_with_mock_backend():
    class MockBackend:
        def infer(self, request: InferRequest) -> InferResponse:
            return InferResponse(text="mocked", model_id=request.model_id, backend=InferBackend.LLAMA_CPP)

    router = InferRouter()
    router.register(InferBackend.LLAMA_CPP, MockBackend())
    req = InferRequest(prompt="hello", model_id="nexus-7b-q4", backend=InferBackend.LLAMA_CPP)
    resp = router.infer(req)
    assert resp.text == "mocked"


def test_infer_backend_enum_values():
    assert InferBackend.LLAMA_CPP == "llama_cpp"
    assert InferBackend.VLLM == "vllm"
    assert InferBackend.TRITON == "triton"
