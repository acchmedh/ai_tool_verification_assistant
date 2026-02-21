import json
import random
import sys
from pathlib import Path

# Add project root to a path for imports
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
DATA_DIR = ROOT / "data"

from scripts.utils.generation_config import load_generator_config, load_dataset_config
from scripts.utils.json_utils import extract_json
from src.utils.openai_client import get_openai_client

client = get_openai_client()

# Load dataset config
dataset_config = load_dataset_config()
CATEGORIES = dataset_config["categories"]
USER_BASES = dataset_config["user_bases"]
DOCUMENT_TYPES = dataset_config["document_types"]
NUMBER_OF_TOOLS = dataset_config["number_of_tools"]
DOCS_PER_TOOL = dataset_config["docs_per_tool"]

# Load tool info generation config
config = load_generator_config('tool_info_generation')
SYSTEM = config["system"]
USER_TEMPLATE = config["user_template"]
MODEL_NAME = config["model_name"]


def sanitize_folder_name(tool_name: str) -> str:
    """Converts tool name to valid folder name (removes special chars, spaces to underscores).

        Args:
            tool_name: Original tool name from LLM

        Returns:
            str: Sanitized folder name
        """
    sanitized = "".join(c if c.isalnum() or c in (' ', '_', '-') else '' for c in tool_name)
    sanitized = sanitized.replace(' ', '_')
    return sanitized


def generate_tool_info_with_name(category: str, user_base: str) -> dict:
    """Calls the LLM API to generate a tool info including creative name.

    Args:
        category: The category of the tool.
        user_base: The intended user base for the tool.

    Returns:
        dict: Parsed JSON object containing name, purpose, category, user_base.

    Raises:
        ValueError: If the response cannot be parsed as JSON or lacks required fields.

    """
    user_prompt = USER_TEMPLATE.format(
        name="<generate_creative_name>",
        category=category,
        user_base=user_base
    )

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user_prompt}
        ]
    )

    content = response.choices[0].message.content.strip()

    result = extract_json(content)
    if result is None:
        raise ValueError(f"Failed to extract JSON from LLM response: {content[:100]}...")
    return result


def generate_tool() -> None:
    """Generates a tool with creative name, folder, and info file.

    Creates:
    - Folder: data/{sanitized_tool_name}/
    - File: data/{sanitized_tool_name}/{sanitized_tool_name}_info.json

    Args:
        tool_index: Index for fallback naming if generation fails.
    """
    category = random.choice(CATEGORIES)
    user_base = random.choice(USER_BASES)
    document_types = random.sample(DOCUMENT_TYPES, DOCS_PER_TOOL)

    description = generate_tool_info_with_name(category, user_base)
    tool_name = description["name"]

    # Sanitize the tool name for the folder
    folder_name = sanitize_folder_name(tool_name)
    print(f"  Generated tool: {folder_name}")

    # Create folder
    tool_folder = DATA_DIR / folder_name
    tool_folder.mkdir(parents=True, exist_ok=True)

    # Prepare tool info
    tool_info = {
        "description": description,
        "document_types": document_types,
    }

    # Save as {tool_name}_info.json
    info_file_name = f"{folder_name}_info.json"
    tool_info_path = tool_folder / info_file_name
    tool_info_path.write_text(json.dumps(tool_info, indent=2), encoding="utf-8")

    print(f"✓ Created {tool_folder.name}/{info_file_name}")



def generate_tools() -> None:
    for i in range(NUMBER_OF_TOOLS):
        try:
            print(f"Generating Tool {i+1}...")
            generate_tool()
            print()
        except Exception as e:
            print(f"✗ Failed to generate Tool {i}: {e}\n")


if __name__ == "__main__":
    generate_tools()
