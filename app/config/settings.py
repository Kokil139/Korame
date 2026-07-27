"""
Configuration management for Korame.

Loads settings from environment variables and .env file.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Global settings for Korame."""

    # API Configuration
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    debug: bool = Field(default=False, alias="DEBUG")

    # Ollama Configuration
    ollama_url: str = Field(default="http://localhost:11434", alias="OLLAMA_URL")
    ollama_model: str = Field(default="qwen3:8b", alias="OLLAMA_MODEL")

    # Logging
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    # LiteLLM
#     litellm_log: str = Field(default="INFO", alias="LITELLM_LOG")

    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get the global settings instance."""
    return Settings()

