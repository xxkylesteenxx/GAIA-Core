# GAIA AI Inference Routing and RAG Pack

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0

This pack provides a Python-first scaffold for:
- Inference routing with privacy-aware route selection
- Model profile registry loading from YAML
- vLLM / OpenAI-compatible serving adapter
- Triton integration placeholder
- Embedding generation scaffold (deterministic + production-ready ABC)
- In-memory vector search and RAG prompt construction
- Fine-tuning event hooks (auditable, append-only, no live mutation)
- Adversarial robustness runner scaffolds for garak and PyRIT

## Layout

```
gaia_ai/
├── __init__.py                      public surface re-exports
├── router.py                        route selection logic
├── registry.py                      ModelProfile + YAML registry loader
├── embeddings.py                    embedding scaffold
├── rag.py                           retrieval and prompt augmentation
├── serving/
│   ├── __init__.py
│   ├── base.py                      ServingAdapter ABC
│   ├── openai_adapter.py            OpenAI-compatible adapter (vLLM / OpenAI API)
│   ├── triton_adapter.py            Triton placeholder adapter
│   └── stub_adapter.py              Deterministic stub for tests
├── training/
│   ├── __init__.py
│   └── fine_tune_hooks.py           Auditable fine-tuning event emission
├── robustness/
│   ├── __init__.py
│   ├── scanner.py                   Core scan runner
│   ├── probes.py                    Built-in probe library
│   ├── garak_bridge.py              garak integration scaffold
│   └── pyrit_bridge.py              PyRIT integration scaffold
├── examples/
│   └── demo_pipeline.py             Runnable end-to-end demo
└── tests/
    └── test_router.py               Basic regression tests
```

## Quick Start

```bash
cd src/python
pip install -e .
```

```python
import asyncio
from gaia_ai import InferenceRouter, ModelProfileRegistry, EmbeddingEngine, RAGPipeline
from gaia_ai.serving import OpenAIAdapter, StubAdapter
from gaia_ai.registry import ModelProfile, Locality
from gaia_ai.rag import Document

async def main():
    # 1. Registry
    registry = ModelProfileRegistry()
    registry.register(ModelProfile(
        model_id="local-chat",
        locality=Locality.LOCAL_FAST,
        context_window=4096,
        capability_tags=["chat"],
        approved=True,
    ))

    # 2. Router + adapter
    adapter = StubAdapter(response="[GAIA]")
    router  = InferenceRouter(registry, {"local-chat": adapter})

    # 3. RAG
    engine = EmbeddingEngine()
    rag    = RAGPipeline(engine, adapter)
    await rag.ingest([Document("d1", "GAIA monitors Earth systems.")])
    result = await rag.query("What does GAIA do?")
    print(result.answer)

asyncio.run(main())
```

Or run the included demo:

```bash
python -m gaia_ai.examples.demo_pipeline
```

## YAML Registry

Model profiles can be loaded from a YAML file:

```yaml
# model_profiles.yaml
models:
  - model_id: local-chat
    locality: local_fast
    context_window: 4096
    capability_tags: [chat, completion]
    approved: true
    endpoint: "http://localhost:8000/v1"
    hardware_minima:
      ram_gb: 8.0
      vram_gb: 6.0
      cpu_cores: 4

  - model_id: gpt-4o
    locality: cloud
    context_window: 128000
    capability_tags: [chat, code, summarisation]
    approved: false   # deny-by-default; call registry.approve("gpt-4o") to enable
```

```python
from gaia_ai.registry import ModelProfileRegistry
registry = ModelProfileRegistry.from_yaml("model_profiles.yaml")
```

## Robustness Scanning

```bash
# Run built-in probes against a local adapter
python -m gaia_ai.robustness.scanner --model-id local-chat

# Run garak scaffold
python -m gaia_ai.robustness.garak_bridge --model-id local-chat

# Run PyRIT scaffold
python -m gaia_ai.robustness.pyrit_bridge --model-id local-chat
```

Robustness scans run independently of the runtime inference path. Results feed
`FineTuneEmitter.emit_safety_annotation()` for reviewed processing.

## Validation

The demo and unit tests execute successfully in the build environment:

```bash
cd src/python
python -m gaia_ai.examples.demo_pipeline
python -m pytest gaia_ai/tests/ -v
```

## Safety and Governance

- No autonomous online fine-tuning
- No direct production-model mutation
- Training hooks are append-only events requiring explicit approval
- External (cloud) routes are deny-by-default
- Private-data requests are hard-blocked from cloud routes by the router
- Robustness scans produce reports only; no feedback loop without human review

---

*Spec ref: GAIA-AI-INFERENCE-SPEC v1.0*  
*Part of GAIA-Core Layer 3 — Python Orchestration*
