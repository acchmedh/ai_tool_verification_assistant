"""JSON utility functions for parsing and extracting JSON from text."""
import json
import re
from typing import Any


def extract_json(text: str) -> dict[str, Any] | None:
    """Extracts JSON object from text, trying direct parse first, then searching for JSON patterns.
    
    This function handles cases where JSON might be wrapped in markdown code blocks or
    surrounded by other text. It attempts multiple parsing strategies:
    1. Direct parsing of the entire text
    2. Searching for JSON-like patterns and parsing each match
    
    Args:
        text: Raw text that may contain JSON (possibly wrapped in markdown or extra text)
    
    Returns:
        Parsed JSON object as dictionary, or None if no valid JSON found
    """
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    matches = re.finditer(r"\{.*}", text, re.DOTALL)
    for m in matches:
        candidate = m.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            continue
    return None

