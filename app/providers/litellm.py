"""
Deprecated LiteLLM provider.

For the V1 architecture we're using a local Ollama (qwen3:8b) model and the
LiteLLM integration has been removed from the runtime. This module is kept as
an explicit placeholder to avoid accidental imports. Importing the provider
will raise an ImportError signalling it is not available in V1.
"""

from typing import Any, Optional

def __getattr__(name: str) -> Any:  # pragma: no cover - trivial deprecation
    raise ImportError(
        "LiteLLM provider has been removed for V1. Use the OllamaProvider (local qwen3:8b)"
    )

