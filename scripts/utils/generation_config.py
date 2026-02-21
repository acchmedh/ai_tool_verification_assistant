"""Configuration loading utilities for prompts, models, and path constants."""

from pathlib import Path
import sys
import yaml
from typing import Any, Optional

# Add project root to Python path
ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = ROOT / "src"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SRC_DIR))

from src.core.settings import settings
from scripts.utils.typings import GeneratorConfig, DatasetConfig

DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
PROMPTS_PATH = CONFIG_DIR / "prompts.yaml"
GENERATION_PATH = CONFIG_DIR / "generation.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    """Loads and parses a YAML file."""
    with open(path, "r", encoding="utf-8") as f:
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
        docs_per_tool=dataset.get("docs_per_tool", 1)
    )


def load_generator_config(prompt_key: str, model_key: Optional[str] = None) -> GeneratorConfig:
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
