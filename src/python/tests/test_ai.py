"""Tests for gaia_ai layer — router, embeddings, RAG, fine-tune hooks, robustness."""

from __future__ import annotations

import asyncio
import unittest

from gaia_ai.embeddings import DeterministicEmbeddingBackend, EmbeddingEngine
from gaia_ai.finetune import FineTuneEmitter, FinetuneEventType
from gaia_ai.rag import Document, RAGPipeline
from gaia_ai.registry import HardwareMinima, Locality, ModelProfile, ModelProfileRegistry
from gaia_ai.robustness import RobustnessScanner, ScanCategory, RobustnessScan
from gaia_ai.router import InferenceRequest, InferenceRouter, RoutingError, TaskMode
from gaia_ai.serving import StubAdapter


class TestModelProfileRegistry(unittest.TestCase):

    def test_register_and_retrieve(self) -> None:
        reg = ModelProfileRegistry()
        profile = ModelProfile(
            model_id="local-fast",
            locality=Locality.LOCAL_FAST,
            context_window=4096,
            capability_tags=["chat", "completion"],
            approved=True,
        )
        reg.register(profile)
        self.assertEqual(reg.get("local-fast").model_id, "local-fast")

    def test_duplicate_raises(self) -> None:
        reg = ModelProfileRegistry()
        p = ModelProfile(model_id="m", locality=Locality.LOCAL_FAST,
                         context_window=2048, approved=True)
        reg.register(p)
        with self.assertRaises(ValueError):
            reg.register(p)

    def test_cloud_deny_by_default(self) -> None:
        reg = ModelProfileRegistry()
        cloud = ModelProfile(model_id="gpt-4", locality=Locality.CLOUD,
                             context_window=128000, approved=False)
        reg.register(cloud)
        approved = reg.all_approved()
        self.assertNotIn(cloud, approved)

    def test_approve_external_route(self) -> None:
        reg = ModelProfileRegistry()
        cloud = ModelProfile(model_id="gpt-4", locality=Locality.CLOUD,
                             context_window=128000, approved=False)
        reg.register(cloud)
        reg.approve("gpt-4")
        self.assertTrue(reg.get("gpt-4").approved)


class TestInferenceRouter(unittest.IsolatedAsyncioTestCase):

    def _make_registry(self) -> ModelProfileRegistry:
        reg = ModelProfileRegistry()
        reg.register(ModelProfile(
            model_id="local-chat",
            locality=Locality.LOCAL_FAST,
            context_window=4096,
            capability_tags=["chat"],
            approved=True,
        ))
        reg.register(ModelProfile(
            model_id="cloud-deep",
            locality=Locality.CLOUD,
            context_window=128000,
            capability_tags=["chat", "code"],
            approved=False,  # deny-by-default
        ))
        return reg

    async def test_routes_to_local_for_private_data(self) -> None:
        reg = self._make_registry()
        adapter = StubAdapter()
        router = InferenceRouter(reg, {"local-chat": adapter})
        req = InferenceRequest(prompt="secret", private_data=True, task_mode=TaskMode.CHAT)
        resp = await router.route(req)
        self.assertEqual(resp.model_id, "local-chat")
        self.assertEqual(resp.locality, "local_fast")

    async def test_denies_cloud_for_private_data(self) -> None:
        reg = ModelProfileRegistry()
        reg.register(ModelProfile(model_id="cloud", locality=Locality.CLOUD,
                                  context_window=8192, approved=True))
        router = InferenceRouter(reg)
        req = InferenceRequest(prompt="secret", private_data=True)
        with self.assertRaises(RoutingError):
            router.select(req)

    async def test_routing_error_without_adapter(self) -> None:
        reg = self._make_registry()
        router = InferenceRouter(reg)  # no adapter bound
        req = InferenceRequest(prompt="hello", task_mode=TaskMode.CHAT)
        with self.assertRaises(RoutingError):
            await router.route(req)


class TestEmbeddingEngine(unittest.IsolatedAsyncioTestCase):

    async def test_encode_returns_correct_shape(self) -> None:
        engine = EmbeddingEngine(DeterministicEmbeddingBackend(dim=64))
        vectors = await engine.encode(["hello", "world"])
        self.assertEqual(len(vectors), 2)
        self.assertEqual(len(vectors[0]), 64)

    async def test_encode_is_deterministic(self) -> None:
        engine = EmbeddingEngine(DeterministicEmbeddingBackend(dim=64))
        v1 = await engine.encode_one("gaia")
        v2 = await engine.encode_one("gaia")
        self.assertEqual(v1, v2)

    async def test_different_texts_differ(self) -> None:
        engine = EmbeddingEngine(DeterministicEmbeddingBackend(dim=64))
        v1 = await engine.encode_one("apple")
        v2 = await engine.encode_one("orange")
        self.assertNotEqual(v1, v2)


class TestRAGPipeline(unittest.IsolatedAsyncioTestCase):

    async def test_ingest_and_query(self) -> None:
        engine  = EmbeddingEngine(DeterministicEmbeddingBackend(dim=64))
        adapter = StubAdapter(response="[ANSWER]")
        rag     = RAGPipeline(engine, adapter, top_k=2)

        await rag.ingest([
            Document("d1", "The ocean absorbs heat from the atmosphere."),
            Document("d2", "Soil moisture affects plant transpiration rates."),
            Document("d3", "Arctic ice loss accelerates permafrost thaw."),
        ])

        result = await rag.query("What drives ocean heat uptake?")
        self.assertFalse(result.bypassed)
        self.assertLessEqual(len(result.chunks), 2)
        self.assertIn("[ANSWER]", result.answer)

    async def test_bypass_skips_retrieval(self) -> None:
        engine  = EmbeddingEngine()
        adapter = StubAdapter()
        rag     = RAGPipeline(engine, adapter)
        result  = await rag.query("anything", bypass_retrieval=True)
        self.assertTrue(result.bypassed)
        self.assertEqual(result.chunks, [])


class TestFineTuneEmitter(unittest.TestCase):

    def test_emit_creates_event(self) -> None:
        emitter = FineTuneEmitter()
        event = emitter.emit_preference(
            model_id="local-chat", source="GUARDIAN",
            prompt="Is this safe?",
            chosen="Yes, with care.",
            rejected="Sure, no problem!",
        )
        self.assertEqual(event.event_type, FinetuneEventType.PREFERENCE_SIGNAL)
        self.assertFalse(event.approved)
        self.assertEqual(emitter.sink.count, 1)

    def test_pending_events_require_approval(self) -> None:
        emitter = FineTuneEmitter()
        emitter.emit_correction(
            model_id="m", source="SOPHIA",
            prompt="p", original="wrong", corrected="right",
        )
        self.assertEqual(len(emitter.sink.pending_approval()), 1)


class TestRobustnessScanner(unittest.IsolatedAsyncioTestCase):

    async def test_builtin_probes_run(self) -> None:
        adapter = StubAdapter(response="I cannot help with that.")
        scanner = RobustnessScanner(adapter)
        report  = await scanner.run("stub-model")
        self.assertGreater(report.total, 0)
        self.assertIsNotNone(report.pass_count + report.fail_count + report.inconclusive_count)

    async def test_custom_probe(self) -> None:
        adapter = StubAdapter(response="safe response")
        scanner = RobustnessScanner(adapter)
        scanner.add_probe(RobustnessScan(
            scan_id="custom-001",
            category=ScanCategory.CUSTOM,
            prompt="test probe",
            assertion=lambda r: "safe" in r,
        ))
        report = await scanner.run("stub-model", include_builtin=False)
        self.assertEqual(report.total, 1)
        self.assertEqual(report.pass_count, 1)


if __name__ == "__main__":
    unittest.main()
