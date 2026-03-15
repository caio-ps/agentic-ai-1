NON_EMPTY_STRING = {
    "type": "string",
    "minLength": 1,
}

NON_EMPTY_STRING_ARRAY = {
    "type": "array",
    "items": NON_EMPTY_STRING,
    "minItems": 1,
}

COMPETITOR_PATTERN_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "platform": NON_EMPTY_STRING,
        "key_features": NON_EMPTY_STRING,
        "website": NON_EMPTY_STRING,
    },
    "required": ["platform", "key_features"],
}

RESEARCH_OUTPUT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["strategic_insights", "knowledge_base"],
    "properties": {
        "strategic_insights": {
            "type": "object",
            "additionalProperties": False,
            "required": ["competitor_patterns", "seo_keywords", "messaging_patterns"],
            "properties": {
                "competitor_patterns": {
                    "type": "array",
                    "minItems": 1,
                    "items": COMPETITOR_PATTERN_SCHEMA,
                },
                "seo_keywords": NON_EMPTY_STRING_ARRAY,
                "messaging_patterns": NON_EMPTY_STRING_ARRAY,
            },
        },
        "knowledge_base": {
            "type": "object",
            "additionalProperties": False,
            "required": ["topics"],
            "properties": {
                "topics": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["topic", "summary", "key_points", "facts", "sources"],
                        "properties": {
                            "topic": NON_EMPTY_STRING,
                            "summary": NON_EMPTY_STRING,
                            "key_points": NON_EMPTY_STRING_ARRAY,
                            "facts": NON_EMPTY_STRING_ARRAY,
                            "sources": NON_EMPTY_STRING_ARRAY,
                        },
                    },
                }
            },
        },
    },
}

__all__ = [
    "COMPETITOR_PATTERN_SCHEMA",
    "RESEARCH_OUTPUT_SCHEMA",
]
