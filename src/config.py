"""
Configuration management for the AI Tool Verification Assistant.

This module handles all configuration loading from environment variables
and provides a centralized configuration object.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # OpenAI/LiteLLM Configuration
    openai_api_key: str = Field(..., description="OpenAI/LiteLLM API key")
    openai_base_url: str = Field(
        default="https://litellm.ai.paas.htec.rs",
        description="API base URL",
    )

    # Model Configuration
    default_model: str = Field(
        default="l2-gpt-4o-mini",
        description="Default LLM model",
    )
    embedding_model: str = Field(
        default="l2-text-embedding-3-small",
        description="Embedding model for RAG",
    )

    # LLM Parameters
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="LLM temperature")
    max_tokens: int = Field(default=2000, gt=0, description="Maximum tokens per request")

    # RAG Configuration
    chroma_persist_directory: str = Field(
        default="./rag_store",
        description="ChromaDB persistence directory",
    )
    chunk_size: int = Field(default=1000, gt=0, description="Text chunk size for splitting")
    chunk_overlap: int = Field(default=200, ge=0, description="Chunk overlap size")

    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )
    log_file: str = Field(default="logs/app.log", description="Log file path")

    # Data Configuration
    data_dir: str = Field(default="./data", description="Data directory path")


# Loaded from environment/.env at runtime; type checker cannot detect it.
# Suppress false-positive "unfilled parameter" warning.
settings = Settings()  # type: ignore[call-arg]
