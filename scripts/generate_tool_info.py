import os
import json
import random

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY not found in environment variables or .env file")

client = OpenAI(api_key=api_key)

CATEGORIES = [
    "Data Processing",
    "AI Analytics",
    "Collaboration",
    "Compliance Monitoring",
    "Security"
]

USER_BASES = [
    "ML engineers",
    "Data analysts",
    "Enterprise IT",
    "Compliance officers",
    "Product managers"
]

DOCUMENT_TYPES = [
    "privacy_policy",
    "terms_of_service",
    "data_processing_agreement",
    "service_level_agreement",
    "security_whitepaper",
    "compliance_and_certifications"
]


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
    print("LLM output:", content)
    return json.loads(content)


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
