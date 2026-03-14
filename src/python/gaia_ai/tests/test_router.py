"""Basic regression tests for InferenceRouter.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §4
"""

from __future__ import annotations

import unittest

from gaia_ai.registry import Locality, ModelProfile, ModelProfileRegistry
from gaia_ai.router import InferenceRequest, InferenceRouter, RoutingError, TaskMode
from gaia_ai.serving import StubAdapter


def _registry_with_local() -> ModelProfileRegistry:
    reg = ModelProfileRegistry()
    reg.register(ModelProfile(
        model_id="local-chat",
        locality=Locality.LOCAL_FAST,
        context_window=4096,
        capability_tags=["chat", "completion"],
        approved=True,
    ))
    return reg


class TestRouterRegression(unittest.IsolatedAsyncioTestCase):

    async def test_local_route_selected_for_private_data(self) -> None:
        reg     = _registry_with_local()
        adapter = StubAdapter()
        router  = InferenceRouter(reg, {"local-chat": adapter})
        req     = InferenceRequest(prompt="secret data", private_data=True, task_mode=TaskMode.CHAT)
        resp    = await router.route(req)
        self.assertEqual(resp.model_id, "local-chat")
        self.assertEqual(resp.locality, "local_fast")

    async def test_cloud_denied_for_private_data(self) -> None:
        reg = ModelProfileRegistry()
        reg.register(ModelProfile(model_id="cloud", locality=Locality.CLOUD,
                                  context_window=8192, approved=True))
        router = InferenceRouter(reg)
        with self.assertRaises(RoutingError):
            router.select(InferenceRequest(prompt="secret", private_data=True))

    async def test_unapproved_cloud_not_routed(self) -> None:
        reg = ModelProfileRegistry()
        reg.register(ModelProfile(model_id="gpt-x", locality=Locality.CLOUD,
                                  context_window=8192, approved=False))
        router = InferenceRouter(reg)
        with self.assertRaises(RoutingError):
            router.select(InferenceRequest(prompt="hello"))

    async def test_capability_tag_preferred(self) -> None:
        reg = ModelProfileRegistry()
        reg.register(ModelProfile(model_id="generic", locality=Locality.LOCAL_FAST,
                                  context_window=4096, capability_tags=["chat"], approved=True))
        reg.register(ModelProfile(model_id="coder", locality=Locality.LOCAL_FAST,
                                  context_window=4096, capability_tags=["code"], approved=True))
        router  = InferenceRouter(reg, {"coder": StubAdapter()})
        profile = router.select(InferenceRequest(prompt="write a function", task_mode=TaskMode.CODE))
        self.assertEqual(profile.model_id, "coder")

    async def test_adapter_call_count(self) -> None:
        reg     = _registry_with_local()
        adapter = StubAdapter()
        router  = InferenceRouter(reg, {"local-chat": adapter})
        await router.route(InferenceRequest(prompt="ping", task_mode=TaskMode.CHAT))
        await router.route(InferenceRequest(prompt="pong", task_mode=TaskMode.CHAT))
        self.assertEqual(adapter.call_count, 2)


if __name__ == "__main__":
    unittest.main()
