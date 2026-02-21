TOC_SCHEMA = {
    "type": "object",
    "required": ["title", "sections"],
    "properties": {
        "title": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {"$ref": "#/definitions/section"},
        },
    },
    "additionalProperties": False,
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
                    "items": {"$ref": "#/definitions/section"},
                },
            },
            "additionalProperties": False,
        },
    },
}

TOC_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "table_of_contents",
        "strict": True,
        "schema": TOC_SCHEMA,
    },
}

TOOL_INFO_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "tool_info",
        "strict": True,
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "purpose": {"type": "string"},
                "category": {"type": "string"},
                "user_base": {"type": "string"},
            },
            "required": ["name", "purpose", "category", "user_base"],
            "additionalProperties": False,
        },
    },
}
