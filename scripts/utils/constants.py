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
