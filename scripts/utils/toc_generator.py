import json
import sys
from pathlib import Path
from jsonschema import validate, ValidationError

# Add project root to path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.utils.generation_config import DATA_DIR, load_generator_config
from scripts.utils.constants import TOC_SCHEMA, TOC_RESPONSE_FORMAT
from src.utils.openai_client import get_openai_client

client = get_openai_client()

config = load_generator_config("toc_generation", "toc_model")
TOC_SYSTEM = config["system"]
TOC_USER_TEMPLATE = config["user_template"]
MODEL_NAME = config["model_name"]
TEMPERATURE = config["temperature"]


def call_toc_model(tool_info: dict, document_type: str) -> dict:
    """Calls the LLM API to generate a TOC using structured outputs.

    The API is given a JSON schema so the model returns guaranteed valid JSON
    conforming to the TOC structure (no regex or best-effort parsing).

    Args:
        tool_info: Dictionary containing tool metadata (name, category, user_base, etc.)
        document_type: Type of document to generate TOC for (e.g., "privacy_policy", "terms_of_service")

    Returns:
        dict: Parsed TOC object (title, sections) from the structured output.

    Raises:
        ValueError: If the model refused or content is missing.
    """
    user_prompt = TOC_USER_TEMPLATE.format(
        tool_info_json=json.dumps(tool_info, ensure_ascii=False, indent=2),
        document_type=document_type,
    )
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": TOC_SYSTEM},
            {"role": "user", "content": user_prompt},
        ],
        temperature=TEMPERATURE,
        response_format=TOC_RESPONSE_FORMAT,
    )
    message = response.choices[0].message
    if getattr(message, "refusal", None):
        raise ValueError(f"Model refused to generate TOC: {message.refusal}")
    content = message.content
    if not content or not content.strip():
        raise ValueError("Empty content in model output")
    obj = json.loads(content)
    return obj


def validate_and_save_toc(toc_obj: dict, out_path: Path) -> dict:
    """Validates TOC against TOC_SCHEMA and saves to file.

    Args:
        toc_obj: TOC dictionary from structured output (already valid JSON shape).
        out_path: Path where the validated TOC JSON will be saved.

    Returns:
        dict: Validated TOC dictionary that was saved to file.

    Raises:
        ValueError: If schema validation fails.
    """
    try:
        validate(instance=toc_obj, schema=TOC_SCHEMA)
    except ValidationError as e:
        raise ValueError(f"TOC JSON failed schema validation: {e.message}")
    out_path.write_text(json.dumps(toc_obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return toc_obj


def generate_all_tocs() -> None:
    """Main function that iterates through all tool folders and generates TOC files for each document type.

    Processes all tool directories in the data folder, reads their tool_info.json files,
    and generates Table of Contents (TOC) JSON files for each document type specified
    in the tool's configuration. The generated TOC files are validated against TOC_SCHEMA
    before being saved.

    The function will skip tool folders that:
    - Don't contain a tool_info.json file
    - Don't have any document_types specified

    Generated TOC files are saved as `toc_{document_type}.json` in each tool's directory.
    """
    for tool_folder in sorted(DATA_DIR.iterdir()):
        if not tool_folder.is_dir():
            continue
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
            try:
                toc_obj = call_toc_model(tool_info, doc)
                validate_and_save_toc(toc_obj, out_file)
                print(f"Saved TOC: {out_file}")
            except (ValueError, json.JSONDecodeError) as e:
                print(f"Failed to generate or save TOC for {tool_folder.name} / {doc}: {e}")


if __name__ == "__main__":
    generate_all_tocs()
