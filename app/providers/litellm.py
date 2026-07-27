"""
LiteLLM provider for multi-model support.

This provider allows using any LiteLLM-supported model (OpenAI, Claude, etc.).
"""

from typing import Any, Optional
import litellm
from app.kernel.provider import Provider


class LiteLLMProvider(Provider):
    """Provider for any LiteLLM-supported model."""

    def __init__(self, model_id: str, api_base: Optional[str] = None):
        """
        Initialize the LiteLLM provider.

        Args:
            model_id: The model ID (e.g., "gpt-4", "claude-3-opus", "ollama/qwen2")
            api_base: Optional API base URL (for self-hosted or alternative endpoints)
        """
        super().__init__(f"litellm_{model_id}")
        self.model_id = model_id
        self.api_base = api_base

    async def call(self, prompt: str, **kwargs: Any) -> str:
        """
        Call the model via LiteLLM.

        Args:
            prompt: The prompt to send to the model
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            The model's response

        Raises:
            Exception: If the call fails
        """
        try:
            call_kwargs = {
                "model": self.model_id,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 2000),
                "timeout": kwargs.get("timeout", 120),
            }

            if self.api_base:
                call_kwargs["api_base"] = self.api_base

            response = litellm.completion(**call_kwargs)

            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"LiteLLM call failed: {str(e)}")

