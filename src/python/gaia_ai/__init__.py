"""GAIA AI Inference Routing, Serving, Embeddings, RAG, Fine-Tuning, and Robustness.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0

This layer is the semantic and policy orchestration layer above the low-level
compute substrate and virtualisation isolation layer. It is NOT the hard
security boundary — that is GUARDIAN.

Public surface:
  InferenceRouter       — select and execute an inference route
  ModelProfileRegistry  — register and look up model profiles
  EmbeddingEngine       — produce deterministic / production embedding vectors
  RAGPipeline           — retrieval-augmented generation pipeline
  FineTuneEmitter       — emit auditable fine-tune events (no live mutation)
  RobustnessScanner     — adversarial robustness scans
  OpenAIAdapter         — OpenAI-compatible serving adapter
  TritonAdapter         — Triton placeholder adapter
"""

from .embeddings import EmbeddingEngine
from .finetune import FineTuneEmitter
from .rag import RAGPipeline
from .registry import ModelProfile, ModelProfileRegistry
from .robustness import RobustnessScanner
from .router import InferenceRouter
from .serving import OpenAIAdapter, TritonAdapter

__all__ = [
    "EmbeddingEngine",
    "FineTuneEmitter",
    "InferenceRouter",
    "ModelProfile",
    "ModelProfileRegistry",
    "OpenAIAdapter",
    "RAGPipeline",
    "RobustnessScanner",
    "TritonAdapter",
]
