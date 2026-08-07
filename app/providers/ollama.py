"""Ollama provider using the local Ollama HTTP API.

This provider calls a locally running Ollama inference server (default
http://localhost:11434) and returns the generated text. The previous
implementation used LiteLLM; for V1 we call Ollama directly via HTTP.
"""

import asyncio
import re
import time
from typing import Any, Optional
import httpx
from app.kernel.provider import Provider
from app.utils import logger

# Some models (notably the Qwen3 family) emit a <think>...</think> reasoning
# block before their actual answer. Left in place, this eats into a bounded
# max_tokens budget and breaks the regex-based parsing agents do on the
# response (numbered lists, STATUS: markers, title extraction, etc.).
_THINK_BLOCK_PATTERN = re.compile(r"<think>.*?</think>", re.DOTALL | re.IGNORECASE)

# Model name substrings that indicate support for Ollama's `think` parameter.
# All other models silently ignore the think kwarg so no 400 is raised.
_THINKING_MODEL_PATTERNS: tuple[str, ...] = ("qwen3",)


def _model_supports_thinking(model: str) -> bool:
    """Return True if this Ollama model understands the ``think`` parameter."""
    model_lower = model.lower()
    return any(pat in model_lower for pat in _THINKING_MODEL_PATTERNS)


class OllamaProvider(Provider):
    """Provider for Ollama models using the Ollama HTTP API.

    Example usage: Ollama running locally at http://localhost:11434
    with model name like "qwen2.5-coder:7b" or "qwen3:8b".

    The ``think`` kwarg passed by agents (``think=True`` for deliberative
    tasks, ``think=False`` for format-constrained code generation) is only
    forwarded to Ollama for models whose names match ``_THINKING_MODEL_PATTERNS``
    (currently the Qwen3 family).  All other models receive no ``think`` field
    so they never return a 400 for an unsupported parameter.
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2.5-coder:7b"):
        super().__init__("ollama")
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._thinking_supported: bool = _model_supports_thinking(model)
        logger.info(
            f"OllamaProvider: model={model}, thinking_supported={self._thinking_supported}"
        )

    async def call(self, prompt: str, **kwargs: Any) -> str:
        """
        Call the local Ollama server's /api/generate endpoint.

        Args:
            prompt: Prompt text to send to Ollama
            **kwargs: Optional generation params: temperature, max_tokens, timeout, max_retries

        Returns:
            The generated text from the model
        """
        # Local CPU inference of an 8B model can genuinely take a few minutes
        # for longer (code-generation) responses, and there's also model-load
        # latency on the first call after Ollama starts or after it's been
        # idle - 120s was too tight and surfaced as "Ollama call failed" for
        # the Developer/Testing agents' longer generations.
        timeout = kwargs.get("timeout", 300)
        max_retries = kwargs.get("max_retries", 1)
        # Only include `think` when the caller requests it AND the model
        # actually supports the thinking API (Qwen3 family).
        # • think=True  + thinking model  → payload["think"] = True
        # • think=True  + non-thinking    → field omitted (model can't use it)
        # • think=False (any model)       → field omitted (Ollama's default)
        # This avoids the HTTP 400 Ollama returns when an unsupported parameter
        # is sent to a model like qwen2.5-coder:7b.
        think_requested: bool = bool(kwargs.get("think", False))
        payload: dict[str, Any] = {
            "model": self.model,
            "prompt": prompt,
            # Non-streaming mode for simplicity
            "stream": False,
            # Generation params belong under "options" for Ollama's /api/generate
            # endpoint. Passing them as top-level fields is silently ignored by
            # Ollama, so temperature/output length were never actually being
            # honored by any agent.
            "options": {
                "num_predict": kwargs.get("max_tokens", 2000),
                "temperature": kwargs.get("temperature", 0.7),
            },
        }
        if think_requested and self._thinking_supported:
            payload["think"] = True

        url = f"{self.base_url}/api/generate"

        last_error: Optional[Exception] = None
        for attempt in range(max_retries + 1):
            attempt_start = time.monotonic()
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    resp = await client.post(url, json=payload)
                    resp.raise_for_status()
                    text = self._strip_thinking(self._extract_text(resp))
                    duration = time.monotonic() - attempt_start
                    # Timed so a slow/hung call can be correlated against GPU
                    # monitoring (temperature/clock/utilization) at the same
                    # timestamp - useful for telling apart genuine model
                    # slowness from thermal throttling or a driver hiccup.
                    logger.info(
                        f"Ollama call to {self.model} succeeded in {duration:.1f}s "
                        f"(attempt {attempt + 1}/{max_retries + 1}, prompt "
                        f"{len(prompt)} chars, response {len(text)} chars)"
                    )
                    return text

            except httpx.HTTPError as e:
                duration = time.monotonic() - attempt_start
                logger.warning(
                    f"Ollama call to {self.model} failed after {duration:.1f}s "
                    f"(attempt {attempt + 1}/{max_retries + 1}): {e}"
                )
                last_error = e
                if attempt < max_retries:
                    # Transient hiccup (cold start, brief timeout) - back off and retry.
                    await asyncio.sleep(2 * (attempt + 1))
                    continue

        raise Exception(f"Ollama call failed after {max_retries + 1} attempt(s): {last_error}")

    @staticmethod
    def _extract_text(resp: httpx.Response) -> str:
        """Pull the generated text out of an Ollama /api/generate response."""
        # Try to parse JSON response first
        content_type = resp.headers.get("content-type", "")
        if "application/json" in content_type:
            data = resp.json()
            # Common keys: 'text', 'response', 'result', 'outputs', 'choices'
            if isinstance(data, dict):
                for key in ("text", "response", "result"):
                    if key in data and isinstance(data[key], str):
                        return data[key]

                # nested outputs/choices
                outputs = data.get("outputs") or data.get("choices")
                if isinstance(outputs, list) and outputs:
                    first = outputs[0]
                    if isinstance(first, dict):
                        for k in ("text", "output", "content"):
                            if k in first and isinstance(first[k], str):
                                return first[k]
                    if isinstance(first, str):
                        return first

            # Fallback to raw text of JSON
            return str(data)

        # If not JSON, return raw text
        return resp.text

    @staticmethod
    def _strip_thinking(text: str) -> str:
        """Remove any <think>...</think> reasoning block(s) before returning the text."""
        return _THINK_BLOCK_PATTERN.sub("", text).strip()
