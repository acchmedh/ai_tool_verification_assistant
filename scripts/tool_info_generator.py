import os
import json
import random
import re
import sys
from pathlib import Path

# Add project root to path for imports
ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.utils.constants import CATEGORIES, USER_BASES, DOCUMENT_TYPES
from src.utils.openai_client import get_openai_client

client = get_openai_client()


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


def generate_tool_description(name, category, user_base):
    """Call LLM to generate JSON description of a tool"""
    response = client.chat.completions.create(
        model="l2-gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an assistant that generates fictional software tool descriptions. "
                    "Return ONLY JSON with keys: name, purpose, category, user_base."
                )
            },
            {
                "role": "user",
                "content": f"Generate a fictional software tool with name '{name}', category '{category}', and user base '{user_base}'."
            }
        ]
    )

    content = response.choices[0].message.content.strip()
    result = extract_json(content)
    if result is None:
        raise ValueError(f"Failed to extract JSON from LLM response: {content[:100]}...")
    return result


def generate_tool_info(tool_index):
    tool_name = f"Tool_{tool_index}"
    category = random.choice(CATEGORIES)
    user_base = random.choice(USER_BASES)

    document_types = random.sample(DOCUMENT_TYPES, 4)

    description = generate_tool_description(tool_name, category, user_base)

    tool_info = {
        "tool_name": tool_name,
        "category": category,
        "user_base": user_base,
        "document_types": document_types,
        "description": description
    }

    folder = f"data/tool{tool_index}"
    os.makedirs(folder, exist_ok=True)

    with open(f"{folder}/tool_info.json", "w") as f:
        json.dump(tool_info, f, indent=2)
    return tool_info


if __name__ == "__main__":
    for i in range(1, 6):
        info = generate_tool_info(i)
        print(f"Generated tool_info.json for Tool {i}")
