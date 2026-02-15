import os
import json
import random
import sys
from pathlib import Path

# Add project root to a path for imports
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from scripts.utils.generation_config import load_generator_config, load_dataset_config
from scripts.utils.json_utils import extract_json
from src.utils.openai_client import get_openai_client

client = get_openai_client()

# Load generator config
config = load_generator_config('tool_info_generation')
SYSTEM = config["system"]
USER_TEMPLATE = config["user_template"]
MODEL_NAME = config["model_name"]

# Load dataset config
dataset_config = load_dataset_config()
CATEGORIES = dataset_config["categories"]
USER_BASES = dataset_config["user_bases"]
DOCUMENT_TYPES = dataset_config["document_types"]
NUMBER_OF_TOOLS = dataset_config["number_of_tools"]


def generate_tool_description(name: str, category: str, user_base: str) -> dict:
    """Calls the LLM API to generate a tool description in JSON format.

    Args:
        name: The name of the tool.
        category: The category of the tool.
        user_base: The intended user base for the tool.

    Returns:
        dict: Parsed JSON object containing the tool description.

    Raises:
        RuntimeError: If the LLM API call fails.
        ValueError: If the response cannot be parsed as JSON.
    """
    user_prompt = USER_TEMPLATE.format(
        name=name,
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


def generate_tool_info(tool_index: int) -> dict:
    """Generates and saves tool information as a JSON file.

    Randomly selects a category, user base, and document types, then generates a tool description
    using the LLM API. The resulting information is saved to `data/tool{tool_index}/tool_info.json`.

    Args:
        tool_index: Index used to name the tool and output folder.

    Returns:
        dict: Dictionary containing the generated tool information.
    """
    tool_name = f"Tool_{tool_index}"
    category = random.choice(CATEGORIES)
    user_base = random.choice(USER_BASES)
    document_types = random.sample(DOCUMENT_TYPES, 4)

    description = generate_tool_description(tool_name, category, user_base)

    tool_info = {
        "description": description,
        "document_types": document_types,
    }

    folder = f"data/tool{tool_index}"
    os.makedirs(folder, exist_ok=True)

    with open(f"{folder}/tool_info.json", "w") as f:
        json.dump(tool_info, f, indent=2)
    return tool_info


if __name__ == "__main__":
    # Todo merge tool info and tool name inside generate_dataset.py
    print("Number of tools to generate:", NUMBER_OF_TOOLS)
    print(CATEGORIES)
    print(USER_BASES)
    print(DOCUMENT_TYPES)
    print(SYSTEM)
    print(USER_TEMPLATE)
    print(MODEL_NAME)
    for i in range(0, NUMBER_OF_TOOLS):
        # info = generate_tool_info(i)
        print(f"Generated tool_info.json for Tool {i}")
