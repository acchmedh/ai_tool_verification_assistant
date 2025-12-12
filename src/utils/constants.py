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
