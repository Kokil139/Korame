"""
Ollama provider using LiteLLM for model abstraction.

This provider handles communication with Ollama.
"""

from typing import Any, Optional
import litellm
from app.kernel.provider import Provider


class OllamaProvider(Provider):
    """Provider for Ollama models via LiteLLM."""

    def __init__(self, base_url: str = "http://localhost:11434", model: str = "qwen2:7b"):
        """
        Initialize the Ollama provider.

        Args:
            base_url: URL where Ollama is running
            model: Model name to use (default: qwen2:7b)
        """
        super().__init__("ollama")
        self.base_url = base_url
        self.model = model
        self.model_id = f"ollama/{model}"

    async def call(self, prompt: str, **kwargs: Any) -> str:
        """
        Call the Ollama model via LiteLLM.

        Args:
            prompt: The prompt to send to the model
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            The model's response

        Raises:
            Exception: If the call fails
        """
        try:
            # Set Ollama base URL for LiteLLM
            response = litellm.completion(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                api_base=self.base_url,
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2000),
                timeout=kwargs.get("timeout", 120),
            )

            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Ollama call failed: {str(e)}")

