"""Tests for InferenceRouter (sync decide()) and InferenceRouterAsync.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §4

Two test suites:

  TestInferenceRouterDecide
    — canonical sync router using QueryContext + RouteDecision.
    — Loaded from config/model_profiles.example.yaml where possible;
       also exercises in-memory fixture registries.

  TestInferenceRouterAsyncRegression
    — backward-compat async router (InferenceRouterAsync) kept to
      ensure existing adapter / serving tests continue to pass.
"""

from __future__ import annotations

import unittest
from pathlib import Path

from gaia_ai.models import InferenceMode, ModelProfile, QueryContext
from gaia_ai.registry import ModelProfileRegistry
from gaia_ai.router import (
    InferenceRequest,
    InferenceRouterAsync,
    RoutingError,
    TaskMode,
    InferenceRouter,
)
from gaia_ai.serving import StubAdapter

# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

EXAMPLE_YAML = (
    Path(__file__).resolve().parents[2]
    / "gaia_ai" / "config" / "model_profiles.example.yaml"
)


def _flat_registry(*profiles: ModelProfile) -> ModelProfileRegistry:
    """Build an in-memory registry from flat ModelProfile instances."""
    return ModelProfileRegistry(profiles)


FAST_PROFILE = ModelProfile(
    name="fast-local",
    backend="vllm",
    family="llama",
    locality="local",
    tags=["fast"],
)

DEEP_PROFILE = ModelProfile(
    name="deep-cloud",
    backend="openai_compatible",
    family="hybrid",
    locality="cloud",
    trust_tier="approved_external",
    tags=["deep"],
)

EMBED_PROFILE = ModelProfile(
    name="embed-local",
    backend="sentence_transformers",
    family="embedding",
    locality="local",
    supports_embeddings=True,
    tags=["embedding"],
)


# ---------------------------------------------------------------------------
# TestInferenceRouterDecide  —  canonical sync decide() tests
# ---------------------------------------------------------------------------

class TestInferenceRouterDecide(unittest.TestCase):
    """Tests for InferenceRouter.decide() using the flat ModelProfile schema."""

    # --- integration: load from YAML ---

    def test_router_private_stays_local(self) -> None:
        """Private-data requests must route to a local profile."""
        registry = ModelProfileRegistry.from_yaml(EXAMPLE_YAML)
        router   = InferenceRouter(registry)

        decision = router.decide(
            QueryContext(
                text="Summarize my private medical notes.",
                mode=InferenceMode.DEEP,
                requires_private_data=True,
                latency_budget_ms=3000,
            )
        )
        assert decision.profile.locality == "local"
        assert decision.retrieval_required is True

    def test_deep_route_uses_cloud(self) -> None:
        """DEEP mode with no privacy constraint routes to the cloud deep profile."""
        registry = ModelProfileRegistry.from_yaml(EXAMPLE_YAML)
        router   = InferenceRouter(registry)

        decision = router.decide(
            QueryContext(
                text="Synthesize the latest climate research.",
                mode=InferenceMode.DEEP,
                latency_budget_ms=5000,
            )
        )
        assert "deep" in decision.profile.tags
        assert decision.retrieval_required is True
        assert decision.guard_scan_required is True

    def test_embedding_routes_to_embed_profile(self) -> None:
        """EMBEDDING mode selects supports_embeddings=True profile."""
        registry = ModelProfileRegistry.from_yaml(EXAMPLE_YAML)
        router   = InferenceRouter(registry)

        decision = router.decide(
            QueryContext(text="embed this", mode=InferenceMode.EMBEDDING)
        )
        assert decision.profile.supports_embeddings is True
        assert decision.retrieval_required is False
        assert decision.guard_scan_required is False

    # --- unit: in-memory fixture registries ---

    def test_fast_mode_selects_fast_tag(self) -> None:
        registry = _flat_registry(FAST_PROFILE, DEEP_PROFILE, EMBED_PROFILE)
        router   = InferenceRouter(registry)
        decision = router.decide(
            QueryContext(text="quick answer", mode=InferenceMode.FAST)
        )
        assert decision.profile.name == "fast-local"
        assert decision.retrieval_required is False

    def test_low_latency_budget_selects_fast(self) -> None:
        registry = _flat_registry(FAST_PROFILE, DEEP_PROFILE)
        router   = InferenceRouter(registry)
        decision = router.decide(
            QueryContext(text="hurry", latency_budget_ms=800)
        )
        assert "fast" in decision.profile.tags

    def test_private_excludes_cloud(self) -> None:
        registry = _flat_registry(FAST_PROFILE, DEEP_PROFILE)
        router   = InferenceRouter(registry)
        decision = router.decide(
            QueryContext(text="private", requires_private_data=True)
        )
        assert decision.profile.locality == "local"

    def test_no_embedding_profile_raises(self) -> None:
        registry = _flat_registry(FAST_PROFILE, DEEP_PROFILE)  # no embed profile
        router   = InferenceRouter(registry)
        with self.assertRaises(RoutingError):
            router.decide(QueryContext(text="embed", mode=InferenceMode.EMBEDDING))

    def test_no_fast_profile_raises(self) -> None:
        registry = _flat_registry(EMBED_PROFILE)  # embed only, no fast tag
        router   = InferenceRouter(registry)
        with self.assertRaises(RoutingError):
            router.decide(QueryContext(text="fast", mode=InferenceMode.FAST))

    def test_route_decision_fields(self) -> None:
        registry = _flat_registry(FAST_PROFILE)
        router   = InferenceRouter(registry)
        decision = router.decide(QueryContext(text="hello", mode=InferenceMode.FAST))
        assert decision.endpoint
        assert decision.reason
        assert isinstance(decision.retrieval_required, bool)
        assert isinstance(decision.guard_scan_required, bool)


# ---------------------------------------------------------------------------
# TestInferenceRouterAsyncRegression  —  backward-compat async suite
# ---------------------------------------------------------------------------

class TestInferenceRouterAsyncRegression(unittest.IsolatedAsyncioTestCase):
    """Backward-compat tests for InferenceRouterAsync.

    These use the old InferenceRequest / TaskMode API and the flat
    ModelProfile (name/locality strings) rather than the old Locality enum.
    """

    def _reg_with_local(self) -> ModelProfileRegistry:
        return _flat_registry(
            ModelProfile(
                name="local-chat",
                backend="vllm",
                family="llama",
                locality="local",
                tags=["chat", "fast"],
            )
        )

    async def test_local_route_selected_for_private_data(self) -> None:
        reg     = self._reg_with_local()
        adapter = StubAdapter()
        router  = InferenceRouterAsync(reg, {"local-chat": adapter})
        req     = InferenceRequest(prompt="secret data", private_data=True, task_mode=TaskMode.CHAT)
        resp    = await router.route(req)
        self.assertEqual(resp.model_id, "local-chat")
        self.assertEqual(resp.locality, "local")

    async def test_capability_tag_preferred(self) -> None:
        reg = _flat_registry(
            ModelProfile(name="generic", backend="vllm", family="llama",
                         locality="local", tags=["chat"]),
            ModelProfile(name="coder",   backend="vllm", family="llama",
                         locality="local", tags=["code"]),
        )
        router  = InferenceRouterAsync(reg, {"coder": StubAdapter()})
        profile = router.select(InferenceRequest(prompt="write a function", task_mode=TaskMode.CODE))
        self.assertEqual(profile.name, "coder")

    async def test_adapter_call_count(self) -> None:
        reg     = self._reg_with_local()
        adapter = StubAdapter()
        router  = InferenceRouterAsync(reg, {"local-chat": adapter})
        await router.route(InferenceRequest(prompt="ping", task_mode=TaskMode.CHAT))
        await router.route(InferenceRequest(prompt="pong", task_mode=TaskMode.CHAT))
        self.assertEqual(adapter.call_count, 2)

    async def test_no_adapter_raises_routing_error(self) -> None:
        reg    = self._reg_with_local()
        router = InferenceRouterAsync(reg)  # no adapters bound
        with self.assertRaises(RoutingError):
            await router.route(InferenceRequest(prompt="hello", task_mode=TaskMode.CHAT))


if __name__ == "__main__":
    unittest.main()
