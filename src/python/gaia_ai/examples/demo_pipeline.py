"""End-to-end demo: registry → router → RAG → fine-tune hooks.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0

Run from the repo root:
  python -m gaia_ai.examples.demo_pipeline

This script performs no real inference — it exercises the routing,
retrieval, prompt-building, and training-event machinery using only
pure-Python components (HashEmbeddingEngine, InMemoryVectorStore,
FineTuneHookStore). No GPU or network required.

Expected output (names / paths will match the example profile config):
  ROUTE: gaia-deep-cloud https://... High-depth route selected.
  TOP DOCS: ['doc1', 'doc2']
  PROMPT PREVIEW: ...
  TRAINING EVENT: _artifacts/...
"""

from __future__ import annotations

from pathlib import Path

from gaia_ai.embeddings import HashEmbeddingEngine
from gaia_ai.models import InferenceMode, QueryContext
from gaia_ai.rag import RAGPipeline
from gaia_ai.registry import ModelProfileRegistry
from gaia_ai.router import InferenceRouter
from gaia_ai.training.fine_tune_hooks import FineTuneHookStore
from gaia_ai.vector_store import InMemoryVectorStore


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    registry = ModelProfileRegistry.from_yaml(
        root / "gaia_ai" / "config" / "model_profiles.example.yaml"
    )
    router = InferenceRouter(registry)

    query = QueryContext(
        text="Summarize recent hydrology and climate interactions for Texas watersheds.",
        mode=InferenceMode.DEEP,
        latency_budget_ms=5000,
        requires_private_data=False,
    )
    decision = router.decide(query)
    print("ROUTE:", decision.profile.name, decision.endpoint, decision.reason)

    rag = RAGPipeline(HashEmbeddingEngine(dims=16), InMemoryVectorStore())
    rag.index_documents(
        [
            (
                "doc1",
                "Watershed response depends on precipitation intensity, "
                "soil condition, and basin morphology.",
            ),
            (
                "doc2",
                "Higher temperatures can intensify evaporation and change "
                "runoff timing in some basins.",
            ),
            (
                "doc3",
                "Reservoir operations mediate drought and flood response "
                "across managed systems.",
            ),
        ]
    )
    retrieved = rag.retrieve(query, top_k=2)
    prompt = rag.build_augmented_prompt(query, retrieved)
    print("TOP DOCS:", [chunk.doc_id for chunk in retrieved])
    print("PROMPT PREVIEW:", prompt[:220].replace("\n", " "))

    hooks = FineTuneHookStore(root / "_artifacts")
    event = hooks.prepare_sft_job(
        model_name="gaia-fast-local",
        dataset_ref="datasets/curated_feedback.jsonl",
        output_dir="runs/sft/gaia-fast-local",
    )
    path = hooks.record(event)
    print("TRAINING EVENT:", path)


if __name__ == "__main__":
    main()
