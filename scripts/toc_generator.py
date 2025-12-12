import json
import re
import sys
from pathlib import Path
from jsonschema import validate, ValidationError

# Add project root to path for imports
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.utils.config import DATA_DIR, load_prompts, load_models
from src.utils.constants import TOC_SCHEMA
from src.utils.openai_client import get_openai_client

client = get_openai_client()

prompts = load_prompts()
TOC_SYSTEM = prompts["toc_generation"]["system"]
TOC_USER_TEMPLATE = prompts["toc_generation"]["user_template"]

models = load_models()
MODEL_NAME = models['toc_model']['name']
TEMPERATURE = models['toc_model']['temperature']


def call_toc_model(tool_info: dict, document_type: str) -> str:
    """Calls the LLM API to generate a TOC JSON.
    
    Args:
        tool_info: Dictionary containing tool metadata (name, category, user_base, etc.)
        document_type: Type of document to generate TOC for (e.g., "privacy_policy", "terms_of_service")
    
    Returns:
        str: Raw text response from the LLM containing the TOC JSON
    """
    user_prompt = TOC_USER_TEMPLATE.format(
        tool_info_json=json.dumps(tool_info, ensure_ascii=False, indent=2),
        document_type=document_type
    )
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": TOC_SYSTEM},
            {"role": "user", "content": user_prompt}
        ],
        temperature=TEMPERATURE
    )
    return resp.choices[0].message.content


def extract_json(text: str):
    """Extracts JSON object from text, trying direct parse first, then searching for JSON patterns."""
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


def validate_and_save_toc(raw_text: str, out_path: Path):
    """Extracts JSON from LLM response, validates it against TOC_SCHEMA, and saves to file."""
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


def generate_all_tocs(model_name="l2-gpt-4o"):
    """Main function that iterates through all tool folders and generates TOC files for each document type."""
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
            raw = call_toc_model(tool_info, doc)

            # Validate & save TOC JSON
            try:
                validate_and_save_toc(raw, out_file)
                print(f"Saved TOC: {out_file}")
            except json.JSONDecodeError:
                print(f"Failed to parse TOC JSON for {tool_folder.name} / {doc}")


if __name__ == '__main__':
    # generate_all_tocs()
    print(prompts)
    print(models)
