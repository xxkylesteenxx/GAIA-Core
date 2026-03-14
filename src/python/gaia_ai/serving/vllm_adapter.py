"""vLLM serving adapter.

Spec ref: GAIA-AI-INFERENCE-SPEC v1.0 §5

VLLMAdapter calls a vLLM (or any OpenAI-compatible) chat/completions
endpoint using only the Python standard library (urllib + json).
No third-party HTTP client is required.

Typical usage
-------------
    adapter = VLLMAdapter(base_url="http://127.0.0.1:8000/v1")
    result  = adapter.chat(
        model="gaia-fast-local",
        messages=[{"role": "user", "content": "Hello"}],
    )
    print(result.text)

For streaming or async use, bind an httpx / aiohttp client at the
calling layer — this adapter is intentionally sync and dependency-free.
"""

from __future__ import annotations

import json
from urllib import request
from urllib.error import HTTPError, URLError

from gaia_ai.models import GenerationResult


class VLLMAdapter:
    """Sync HTTP adapter for vLLM (OpenAI-compatible) chat/completions.

    Parameters
    ----------
    base_url:
        Base URL of the vLLM server, e.g. ``http://127.0.0.1:8000/v1``.
        Trailing slashes are stripped automatically.
    api_key:
        Bearer token sent in the Authorization header.
        Defaults to ``"local-token"`` for local dev deployments that
        require a token but don't validate its value.
    """

    def __init__(self, base_url: str, api_key: str = "local-token") -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def chat(
        self,
        *,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int = 512,
    ) -> GenerationResult:
        """Call /chat/completions and return a GenerationResult.

        Parameters
        ----------
        model:
            Model name as registered in vLLM, e.g. ``"gaia-fast-local"``.
        messages:
            OpenAI-format message list, e.g.
            ``[{"role": "user", "content": "Hello"}]``.
        max_tokens:
            Maximum number of tokens to generate.

        Raises
        ------
        urllib.error.HTTPError
            If the server returns a non-2xx status code.
        urllib.error.URLError
            If the server is unreachable or the request times out.
        """
        payload = json.dumps(
            {
                "model":      model,
                "messages":   messages,
                "max_tokens": max_tokens,
            }
        ).encode("utf-8")

        req = request.Request(
            f"{self.base_url}/chat/completions",
            data=payload,
            headers={
                "Content-Type":  "application/json",
                "Authorization": f"Bearer {self.api_key}",
            },
            method="POST",
        )

        try:
            with request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            raise HTTPError(
                exc.url, exc.code,
                f"VLLMAdapter: server returned {exc.code} for model '{model}'",
                exc.headers, exc.fp,
            ) from exc
        except URLError as exc:
            raise URLError(
                f"VLLMAdapter: could not reach {self.base_url} — {exc.reason}"
            ) from exc

        text  = data["choices"][0]["message"]["content"]
        usage = data.get("usage", {})

        return GenerationResult(
            text=text,
            model_name=model,
            prompt_tokens=usage.get("prompt_tokens", 0),
            completion_tokens=usage.get("completion_tokens", 0),
            metadata={"backend": "vllm"},
        )
