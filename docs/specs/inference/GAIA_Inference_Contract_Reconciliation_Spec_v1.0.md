# GAIA Inference Contract Reconciliation Spec v1.0

## Boundary Compliance Header

**Document ID:** GAIA-SPEC-INF-001  
**Title:** Inference Contract Reconciliation Spec v1.0  
**Status:** Draft v1.0  
**Authority Layer:** Shared substrate contract owned by GAIA-Core  
**Primary Owner:** GAIA-Core  
**Dependent Repos:** GAIA-Server, GAIA-Desktop, GAIA-Laptop, future model-serving surfaces  
**In Scope:** request/response contracts, backend enumeration, task typing, compatibility aliases, router semantics, error semantics  
**Out of Scope:** model quality, sampling policy, scheduler policy, vendor-specific optimization  
**Primary Trigger:** `GAIA-Server` expects `RuntimeBackend` and `TaskType`, but `GAIA-Core` currently exports a different inference contract surface

---

## 1. Problem Statement

The current GAIA inference boundary is split between two incompatible mental models.

### Current GAIA-Core model

Core presently defines:
- `InferBackend`
- `InferRequest(prompt, model_id, backend, max_tokens, temperature, stream, metadata)`
- `InferResponse(text, model_id, backend, prompt_tokens, completion_tokens, latency_ms, metadata)`

This model is compact and LLM-oriented.

### Current GAIA-Server expectation

Server tests expect:
- `RuntimeBackend`
- `TaskType`
- `InferRequest(request_id, core_id, task_type, backend, payload)`
- response fields like `accepted`, `result`, `error_code`, `error_message`

This model is operation-oriented and supports more than simple text generation.

The result is contract drift at the shared substrate boundary.

---

## 2. Decision

GAIA-Core will own the **canonical multi-task inference contract**. The Server model is closer to the needed substrate shape, but the Core model contains useful convenience semantics. The reconciled contract therefore expands Core rather than duplicating two parallel abstractions.

---

## 3. Canonical Types

### 3.1 RuntimeBackend

GAIA-Core **MUST** define a canonical `RuntimeBackend` enum.

Minimum members:
- `AUTO`
- `MOCK`
- `LLAMA_CPP`
- `VLLM`
- `TRITON`
- `OLLAMA` (optional if Desktop/Laptop use it directly)

`InferBackend` may remain as a temporary compatibility alias for one deprecation cycle, but new code must use `RuntimeBackend`.

### 3.2 TaskType

GAIA-Core **MUST** define a canonical `TaskType` enum.

Minimum members:
- `GENERATE`
- `EMBED`
- `CLASSIFY`

Optional future members:
- `RERANK`
- `SUMMARIZE`
- `TRANSCRIBE`
- `DETECT`

### 3.3 InferRequest

Canonical request shape:

```python
@dataclass
class InferRequest:
    request_id: str
    core_id: str
    task_type: TaskType
    backend: RuntimeBackend = RuntimeBackend.AUTO
    payload: dict[str, Any] = field(default_factory=dict)
    model_id: str | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    stream: bool = False
    timeout_ms: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
```

### 3.4 InferResponse

Canonical response shape:

```python
@dataclass
class InferResponse:
    request_id: str
    accepted: bool
    backend: RuntimeBackend
    task_type: TaskType
    result: dict[str, Any] = field(default_factory=dict)
    error_code: str | None = None
    error_message: str | None = None
    prompt_tokens: int = 0
    completion_tokens: int = 0
    latency_ms: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)
```

---

## 4. Convenience Constructors

To preserve ergonomic LLM usage, Core **SHOULD** provide helpers:

- `InferRequest.for_generate(...)`
- `InferRequest.for_embed(...)`
- `InferResponse.text_output(...)`

Example:

```python
InferRequest.for_generate(
    request_id="req-123",
    core_id="SOPHIA",
    prompt="Hello",
    backend=RuntimeBackend.VLLM,
    model_id="llama3",
)
```

This preserves simple generative use without forcing every caller to handcraft payload dictionaries.

---

## 5. Payload Semantics

### 5.1 GENERATE

Payload keys:
- `prompt` required
- `system_prompt` optional
- `history` optional

Response result keys:
- `text` required on success

### 5.2 EMBED

Payload keys:
- `text` or `texts` required

Response result keys:
- `embedding` or `embeddings`

### 5.3 CLASSIFY

Payload keys:
- `text` or structured object

Response result keys:
- `label`
- `scores` optional

---

## 6. Router Semantics

The router contract **MUST** behave as follows:

1. If `backend=AUTO`, router may choose according to policy.
2. If a requested backend is unavailable, router may fall back only if fallback is policy-authorized and the response metadata records the actual backend used.
3. Timeout returns:
   - `accepted=False`
   - `error_code="TIMEOUT"`
4. Backend exception returns:
   - `accepted=False`
   - `error_code="BACKEND_ERROR"`
5. Validation failure returns:
   - `accepted=False`
   - `error_code="INVALID_REQUEST"`

---

## 7. Compatibility Policy

### 7.1 Temporary compatibility alias

For one migration cycle, GAIA-Core may expose:

- `InferBackend = RuntimeBackend`

and may provide request adapters for old callsites.

### 7.2 Prohibited long-term state

The following long-term state is not allowed:

- Core owning one request model,
- Server owning a second request model,
- downstream repos guessing which one is canonical.

The substrate gets one inference contract, not two.

---

## 8. Migration Steps

1. Add `RuntimeBackend` and `TaskType` to `gaia_core.inference.contracts`.
2. Replace or extend current `InferRequest` and `InferResponse` to canonical form.
3. Add compatibility helpers for prompt-based callers.
4. Update `gaia_core.inference.__init__` to export the canonical types.
5. Update GAIA-Server router and tests to use canonical Core types only.
6. Audit Desktop/Laptop model-runner code for assumptions about the old text-only response shape.

---

## 9. Acceptance Criteria

This spec is satisfied when:

1. `GAIA-Server` inference tests pass using only `gaia_core.inference.contracts` public exports.
2. No downstream repo defines a shadow inference contract.
3. Both generate and embed tasks are first-class substrate concepts.
4. Legacy prompt-based callers have a documented migration path.
5. Router error handling is deterministic and test-covered.

---

## 10. Final Decision

Inference is a shared substrate function, not a Server-private API. The contract therefore belongs in Core, but it must be wide enough to support real multi-task routing.

GAIA-Core will own one canonical inference contract with:
- explicit task type,
- explicit runtime backend,
- structured payload/result,
- deterministic error semantics,
- temporary compatibility for legacy prompt-oriented callers.
