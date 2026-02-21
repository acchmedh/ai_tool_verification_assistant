import json
import sys
from pathlib import Path
from jsonschema import validate, ValidationError

# Add project root to a path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from scripts.utils.generation_config import DATA_DIR, load_generator_config
from scripts.utils.json_utils import extract_json
from scripts.utils.constants import TOC_SCHEMA
from src.utils.openai_client import get_openai_client

client = get_openai_client()

config = load_generator_config('toc_generation', 'toc_model')
TOC_SYSTEM = config["system"]
TOC_USER_TEMPLATE = config["user_template"]
MODEL_NAME = config["model_name"]
TEMPERATURE = config["temperature"]


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
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": TOC_SYSTEM},
            {"role": "user", "content": user_prompt}
        ],
        temperature=TEMPERATURE
    )
    return response.choices[0].message.content


def validate_and_save_toc(raw_text: str, out_path: Path) -> dict:
    """Extracts JSON from LLM response, validates it against TOC_SCHEMA, and saves to file.

    Args:
        raw_text: Raw text response from LLM that should contain JSON
        out_path: Path where the validated TOC JSON will be saved

    Returns:
        dict: Validated TOC dictionary that was saved to file

    Raises:
        ValueError: If JSON extraction fails or schema validation fails
    """
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
    generate_all_tocs()
