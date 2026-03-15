NON_EMPTY_STRING = {
    "type": "string",
    "minLength": 1,
}

NON_EMPTY_STRING_ARRAY = {
    "type": "array",
    "items": NON_EMPTY_STRING,
    "minItems": 1,
}

ARCHITECTURE_COMPONENT_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["name", "directory", "files"],
    "properties": {
        "name": NON_EMPTY_STRING,
        "directory": NON_EMPTY_STRING,
        "files": NON_EMPTY_STRING_ARRAY,
    },
}

ARCHITECTURE_ASSET_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "type": NON_EMPTY_STRING,
        "directory": NON_EMPTY_STRING,
        "files": {
            "type": "array",
            "items": NON_EMPTY_STRING,
        },
    },
    "required": ["type", "directory"],
}

ARCHITECTURE_SPEC_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["architecture_spec"],
    "properties": {
        "architecture_spec": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "project_structure",
                "components",
                "css_strategy",
                "javascript_strategy",
                "asset_structure",
            ],
            "properties": {
                "project_structure": NON_EMPTY_STRING_ARRAY,
                "components": {
                    "type": "array",
                    "minItems": 1,
                    "items": ARCHITECTURE_COMPONENT_SCHEMA,
                },
                "css_strategy": NON_EMPTY_STRING,
                "javascript_strategy": NON_EMPTY_STRING,
                "asset_structure": {
                    "type": "array",
                    "minItems": 1,
                    "items": ARCHITECTURE_ASSET_SCHEMA,
                },
            },
        }
    },
}

__all__ = [
    "ARCHITECTURE_ASSET_SCHEMA",
    "ARCHITECTURE_COMPONENT_SCHEMA",
    "ARCHITECTURE_SPEC_SCHEMA",
]
