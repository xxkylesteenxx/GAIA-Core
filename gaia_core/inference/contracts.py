from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping


class TaskType(StrEnum):
    GENERATE = "generate"
    EMBED = "embed"
    RERANK = "rerank"
    CLASSIFY = "classify"
    SUMMARIZE = "summarize"
    ROUTE = "route"
    POLICY_EVAL = "policy_eval"


class RuntimeBackend(StrEnum):
    MOCK = "mock"
    LLAMA_CPP = "llama.cpp"
    VLLM = "vllm"
    TRITON = "triton"
    REMOTE_HTTP = "remote_http"


@dataclass(slots=True, frozen=True)
class InferRequest:
    schema_version: str = "1.0"
    request_id: str = ""
    core_id: str = ""
    task_type: TaskType = TaskType.GENERATE
    backend: RuntimeBackend | None = None

    model_id: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)
    context: Mapping[str, Any] = field(default_factory=dict)
    routing_hints: Mapping[str, Any] = field(default_factory=dict)

    timeout_ms: int = 30_000
    priority: int = 100
    max_tokens: int | None = None
    temperature: float | None = None


@dataclass(slots=True, frozen=True)
class InferResponse:
    schema_version: str = "1.0"
    request_id: str = ""
    accepted: bool = True

    core_id: str = ""
    task_type: TaskType = TaskType.GENERATE
    backend: RuntimeBackend = RuntimeBackend.MOCK
    model_id: str | None = None

    result: Mapping[str, Any] = field(default_factory=dict)
    usage: Mapping[str, Any] = field(default_factory=dict)
    latency_ms: int = 0

    error_code: str | None = None
    error_message: str | None = None
