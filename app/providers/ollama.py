"""Ollama provider using the local Ollama HTTP API.

This provider calls a locally running Ollama inference server (default
http://localhost:11434) and returns the generated text. The previous
implementation used LiteLLM; for V1 we call Ollama directly via HTTP.
"""

from typing import Any, Optional
import httpx
from app.kernel.provider import Provider


class OllamaProvider(Provider):
    """Provider for Ollama models using the Ollama HTTP API.

    Example usage: Ollama running locally at http://localhost:11434
    with model name like "qwen3:8b".
    """

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen3:8b"):
        super().__init__("ollama")
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def call(self, prompt: str, **kwargs: Any) -> str:
        """
        Call the local Ollama server's /api/generate endpoint.

        Args:
            prompt: Prompt text to send to Ollama
            **kwargs: Optional generation params: temperature, max_tokens, timeout

        Returns:
            The generated text from the model
        """
        timeout = kwargs.get("timeout", 120)
        payload = {
            "model": self.model,
            "prompt": prompt,
            "max_tokens": kwargs.get("max_tokens", 2000),
            "temperature": kwargs.get("temperature", 0.7),
            # Non-streaming mode for simplicity
            "stream": False,
        }

        url = f"{self.base_url}/api/generate"

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()

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

        except httpx.HTTPError as e:
            raise Exception(f"Ollama call failed: {e}")
