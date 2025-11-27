"""
Unit tests for configuration management.
"""

import pytest
from pydantic import ValidationError

from src.config import Settings


def test_settings_load_from_env(monkeypatch):
    """Test that settings can be loaded from environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://test.example.com")
    monkeypatch.setenv("DEFAULT_MODEL", "test-model")

    settings = Settings()
    assert settings.openai_api_key == "test-api-key"
    assert settings.openai_base_url == "https://test.example.com"
    assert settings.default_model == "test-model"


def test_settings_validation(monkeypatch):
    """Test that settings validate input ranges."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    # Test temperature validation
    monkeypatch.setenv("TEMPERATURE", "2.5")  # Invalid: > 2.0
    with pytest.raises(ValidationError):
        Settings()

    # Test valid temperature
    monkeypatch.setenv("TEMPERATURE", "1.5")
    settings = Settings()
    assert settings.temperature == 1.5


def test_settings_defaults(monkeypatch):
    """Test that default values are applied correctly."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")

    settings = Settings()
    assert settings.default_model == "l2-gpt-4o-mini"
    assert settings.embedding_model == "l2-text-embedding-3-small"
    assert settings.temperature == 0.7
    assert settings.max_tokens == 2000
