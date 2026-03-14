"""End-to-end demo of the GAIA AI inference and RAG pipeline.

Run with:
    python -m gaia_ai.examples.demo_pipeline

Uses StubAdapter throughout — no live model server required.
"""

from __future__ import annotations

import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

from gaia_ai.embeddings import EmbeddingEngine
from gaia_ai.rag import Document, RAGPipeline
from gaia_ai.registry import Locality, ModelProfile, ModelProfileRegistry
from gaia_ai.robustness import RobustnessScanner
from gaia_ai.router import InferenceRequest, InferenceRouter, TaskMode
from gaia_ai.serving import StubAdapter
from gaia_ai.training import FineTuneEmitter


async def main() -> None:
    print("\n=== GAIA AI Demo Pipeline ===")

    # 1. Registry
    registry = ModelProfileRegistry()
    registry.register(ModelProfile(
        model_id="local-chat",
        locality=Locality.LOCAL_FAST,
        context_window=4096,
        capability_tags=["chat", "completion"],
        approved=True,
    ))
    registry.register(ModelProfile(
        model_id="local-embed",
        locality=Locality.LOCAL_EMBEDDING,
        context_window=512,
        capability_tags=["embedding"],
        approved=True,
    ))
    print(f"\n[1] Registry: {registry.model_ids}")

    # 2. Router
    adapter = StubAdapter(response="[GAIA-STUB]")
    router  = InferenceRouter(registry, {"local-chat": adapter, "local-embed": adapter})
    resp    = await router.route(InferenceRequest(
        prompt="What is the current ocean heat content?",
        task_mode=TaskMode.CHAT,
        private_data=True,
    ))
    print(f"\n[2] Router response: model={resp.model_id} locality={resp.locality}")
    print(f"    content: {resp.content[:80]}")

    # 3. RAG pipeline
    engine = EmbeddingEngine()
    rag    = RAGPipeline(engine, adapter, top_k=2)
    await rag.ingest([
        Document("d1", "GAIA monitors ocean heat content via AQUA core."),
        Document("d2", "Arctic ice loss accelerates permafrost thaw cycles."),
        Document("d3", "Soil moisture anomalies are tracked by TERRA core."),
        Document("d4", "Energy system efficiency is optimised by ETA core."),
    ])
    rag_result = await rag.query("What drives ocean heat uptake?")
    print(f"\n[3] RAG answer: {rag_result.answer[:80]}")
    print(f"    Retrieved {len(rag_result.chunks)} chunk(s):")
    for chunk in rag_result.chunks:
        print(f"      [{chunk.doc_id}] score={chunk.score:.3f} {chunk.content[:60]}")

    # 4. Fine-tune event emission
    emitter = FineTuneEmitter()
    event   = emitter.emit_preference(
        model_id="local-chat",
        source="GUARDIAN",
        prompt="Is deforestation increasing?",
        chosen="Yes, according to TERRA core data, deforestation rates rose 12% last year.",
        rejected="I don't have that information.",
    )
    print(f"\n[4] Fine-tune event: {event.event_type.value} approved={event.approved}")
    print(f"    Pending approval: {len(emitter.sink.pending_approval())} event(s)")

    # 5. Robustness scan
    scanner = RobustnessScanner(adapter)
    report  = await scanner.run("local-chat")
    print(f"\n[5] Robustness scan: {report.total} probes — "
          f"{report.pass_count} pass / {report.fail_count} fail / "
          f"{report.inconclusive_count} inconclusive")

    print("\n=== Demo complete ===")


if __name__ == "__main__":
    asyncio.run(main())
