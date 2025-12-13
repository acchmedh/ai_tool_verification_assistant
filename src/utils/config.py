"""Configuration loading utilities for prompts, models, and path constants."""
from pathlib import Path
import yaml
from typing import Any

ROOT = Path(".")
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
PROMPTS_PATH = CONFIG_DIR / "prompts.yaml"
MODELS_PATH = CONFIG_DIR / "models.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    """Loads and parses a YAML file.
    
    Args:
        path: Path to the YAML file to load
    
    Returns:
        Dictionary containing the parsed YAML content
    """
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompts() -> dict[str, Any]:
    """Loads prompt templates from prompts.yaml configuration file.
    
    Returns:
        Dictionary containing prompt templates
    """
    return load_yaml(PROMPTS_PATH)


def load_models() -> dict[str, Any]:
    """Loads model configurations from models.yaml configuration file.
    
    Returns:
        Dictionary containing model configurations
    """
    return load_yaml(MODELS_PATH)


def load_generator_config(prompt_key: str, model_key: str) -> dict[str, Any]:
    """Loads configuration for a generator script (prompts and models).
    
    This is a generic function that loads both prompts and models, then extracts
    the relevant sections based on the provided keys.
    
    Args:
        prompt_key: Key to extract from prompts config (e.g., "toc_generation", "tool_info_generation")
        model_key: Key to extract from models config (e.g., "toc_model", "tool_info")
    
    Returns:
        Dictionary containing the merged configuration with keys:
        - SYSTEM: System prompt from prompts config
        - USER_TEMPLATE: User template from prompts config
        - MODEL_NAME: Model name from models config
        - TEMPERATURE: Temperature from models config (if available)
    """
    prompts = load_prompts()
    models = load_models()
    
    prompt_config = prompts[prompt_key]
    model_config = models[model_key]
    
    config = {
        "SYSTEM": prompt_config["system"],
        "USER_TEMPLATE": prompt_config["user_template"],
        "MODEL_NAME": model_config["name"],
    }
    
    # Add temperature if it exists in model config
    if "temperature" in model_config:
        config["TEMPERATURE"] = model_config["temperature"]
    
    return config




















