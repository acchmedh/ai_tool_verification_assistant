from pathlib import Path
import yaml
from typing import Any

ROOT = Path(".")
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
PROMPTS_PATH = CONFIG_DIR / "prompts.yaml"
MODELS_PATH = CONFIG_DIR / "models.yaml"

def load_yaml(path: Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_prompts() -> dict[str, Any]:
    return load_yaml(PROMPTS_PATH)

def load_models() -> dict[str, Any]:
    return load_yaml(MODELS_PATH)
