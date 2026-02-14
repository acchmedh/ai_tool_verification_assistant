"""Configuration loading utilities for prompts, models, and path constants."""

from pathlib import Path
import yaml
from typing import Any, Optional
from src.config import settings
from src.typings import GeneratorConfig

ROOT = Path(__file__).parent.parent.parent
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


def load_generator_config(prompt_key: str, model_key: Optional[str] = None) -> GeneratorConfig:
    """Loads configuration for a generator script (prompts and models)."""
    prompts = load_prompts()
    generation = load_generation()

    if prompt_key not in prompts:
        raise KeyError(f"Prompt key '{prompt_key}' not found in prompts.yaml")

    prompt_config = prompts[prompt_key]

    config: GeneratorConfig = {
        "SYSTEM": prompt_config["system"],
        "USER_TEMPLATE": prompt_config["user_template"],
        "NUMBER_OF_TOOLS": generation.get("dataset", {}).get("num_tools", 1)
    }

    models = generation.get("models", {})

    if model_key:
        model_config = models[model_key]
        config["MODEL_NAME"] = model_config["name"]
        if "temperature" in model_config:
            config["TEMPERATURE"] = model_config["temperature"]
    else:
        config["MODEL_NAME"] = settings.default_model

    return config
