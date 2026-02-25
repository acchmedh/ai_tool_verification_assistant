import sys
import yaml
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
PROMPTS_PATH = CONFIG_DIR / "prompts.yaml"
CHATBOT_CONFIG_PATH = CONFIG_DIR / "chatbot.yaml"


def load_yaml(path: Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_prompts() -> dict[str, Any]:
    return load_yaml(PROMPTS_PATH)["chatbot"]


def load_chatbot_config() -> dict[str, Any]:
    return load_yaml(CHATBOT_CONFIG_PATH)
