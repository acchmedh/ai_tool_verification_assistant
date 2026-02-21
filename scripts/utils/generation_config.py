"""Configuration loading utilities for prompts, models, and path constants."""

import sys
from pathlib import Path
from typing import Any

import yaml

# Project root on path first so "scripts" and "src" resolve when run as script
ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC_DIR))

from scripts.utils.typings import DatasetConfig, GeneratorConfig
from src.core.settings import settings

DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
PROMPTS_PATH = CONFIG_DIR / "prompts.yaml"
GENERATION_PATH = CONFIG_DIR / "generation.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    """Loads and parses a YAML file."""
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompts() -> dict[str, Any]:
    """Loads prompt templates from prompts.yaml"""
    return load_yaml(PROMPTS_PATH)


def load_generation() -> dict[str, Any]:
    """Loads generation configuration from generation.yaml"""
    return load_yaml(GENERATION_PATH)


def load_dataset_config() -> DatasetConfig:
    """Loads dataset configuration (categories, user_bases, document_types) from generation.yaml"""
    generation = load_generation()
    dataset = generation.get("dataset", {})

    return DatasetConfig(
        categories=dataset.get("categories", []),
        user_bases=dataset.get("user_bases", []),
        document_types=dataset.get("document_types", []),
        number_of_tools=dataset.get("num_tools", 1),
        docs_per_tool=dataset.get("docs_per_tool", 1),
    )


def load_generator_config(prompt_key: str, model_key: str | None = None) -> GeneratorConfig:
    """Loads configuration for a generator script (prompts and models)."""
    prompts = load_prompts()
    generation = load_generation()

    if prompt_key not in prompts:
        raise KeyError(f"Prompt key '{prompt_key}' not found in prompts.yaml")

    prompt_config = prompts[prompt_key]

    config: GeneratorConfig = {
        "system": prompt_config["system"],
        "user_template": prompt_config["user_template"],
    }

    models = generation.get("models", {})

    if model_key and model_key in models:
        model_config = models[model_key]
        config["model_name"] = model_config["name"]
        if "temperature" in model_config:
            config["temperature"] = model_config["temperature"]
    else:
        config["model_name"] = settings.default_model

    return config
