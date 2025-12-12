import os
import json
import re
import time
from pathlib import Path
from jsonschema import validate, ValidationError
from dotenv import load_dotenv
from openai import OpenAI

# Load env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found")

client = OpenAI(api_key=api_key)

ROOT = Path(".")
DATA_DIR = ROOT / "data"
CONFIG_DIR = ROOT / "config"
PROMPTS_PATH = CONFIG_DIR / "prompts.yaml"

TOC_SCHEMA = {
  "type": "object",
  "required": ["title", "sections"],
  "properties": {
    "title": {"type": "string"},
    "sections": {
      "type": "array",
      "items": {"$ref": "#/definitions/section"}
    }
  },
  "definitions": {
    "section": {
      "type": "object",
      "required": ["title"],
      "properties": {
        "title": {"type": "string"},
        "page": {"type": "integer"},
        "id": {"type": "string"},
        "subsections": {
          "type": "array",
          "items": {"$ref": "#/definitions/section"}
        }
      }
    }
  }
}

import yaml
def load_prompts():
    p = PROMPTS_PATH
    if not p.exists():
        raise FileNotFoundError(f"{p} not found. Create config/prompts.yaml")
    with open(p, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

prompts = load_prompts()
TOC_SYSTEM = prompts["toc_generation"]["system"]
TOC_USER_TEMPLATE = prompts["toc_generation"]["user_template"]

def extract_json(text: str):
    text = text.strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    matches = re.finditer(r"\{.*\}", text, re.DOTALL)
    for m in matches:
        candidate = m.group(0)
        try:
            return json.loads(candidate)
        except Exception:
            continue
    return None

def call_toc_model(tool_info: dict, document_type: str, model_name="l2-gpt-4o", temperature=0.3, attempts=3, backoff=1.5):
    user_prompt = TOC_USER_TEMPLATE.format(
        tool_info_json=json.dumps(tool_info, ensure_ascii=False, indent=2),
        document_type=document_type
    )
    last_err = None
    for attempt in range(1, attempts+1):
        try:
            resp = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": TOC_SYSTEM},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature
            )
            raw = resp.choices[0].message.content
            return raw
        except Exception as e:
            last_err = e
            time.sleep(backoff * attempt)
    raise RuntimeError("LLM call failed") from last_err

def validate_and_save_toc(raw_text: str, out_path: Path):
    obj = extract_json(raw_text)
    if obj is None:
        raise ValueError("No JSON object found in model output")
    try:
        validate(instance=obj, schema=TOC_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"TOC JSON failed schema validation: {e.message}")
    # Save pretty JSON
    out_path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return obj

def generate_all_tocs(model_name="l2-gpt-4o", temperature=0.3, attempts=3):
    # iterate tool folders
    for tool_folder in sorted(DATA_DIR.iterdir()):
        if not tool_folder.is_dir(): continue
        tool_info_path = tool_folder / "tool_info.json"
        if not tool_info_path.exists():
            print(f"Skipping {tool_folder} (no tool_info.json)")
            continue
        tool_info = json.loads(tool_info_path.read_text(encoding="utf-8"))
        docs = tool_info.get("document_types") or []
        if not docs:
            print(f"No document_types for {tool_folder}, skipping")
            continue

        for doc in docs:
            out_file = tool_folder / f"toc_{doc}.json"
            print(f"Generating TOC for {tool_folder.name} / {doc} ...")
            raw = call_toc_model(tool_info, doc, model_name=model_name, temperature=temperature, attempts=attempts)

            # Validate & save TOC JSON
            try:
                validate_and_save_toc(raw, out_file)
                print(f"Saved TOC: {out_file}")
            except json.JSONDecodeError:
                print(f"Failed to parse TOC JSON for {tool_folder.name} / {doc}")


if __name__ == '__main__':
    generate_all_tocs()