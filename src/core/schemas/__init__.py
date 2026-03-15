from .architecture_schema import ARCHITECTURE_SPEC_SCHEMA
from .research_schema import RESEARCH_OUTPUT_SCHEMA

NON_EMPTY_STRING = {
    "type": "string",
    "minLength": 1,
}

NON_EMPTY_STRING_ARRAY = {
    "type": "array",
    "items": NON_EMPTY_STRING,
    "minItems": 1,
}

PRODUCT_REQUIREMENTS_SCHEMA = {
    "type": "string",
    "minLength": 1,
    "anyOf": [
        {"pattern": "REQUIREMENTS_READY"},
        {"pattern": r"\?"},
    ],
}

SITE_STRUCTURE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["site_structure"],
    "properties": {
        "site_structure": {
            "type": "object",
            "additionalProperties": False,
            "required": ["pages"],
            "properties": {
                "pages": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["slug", "title", "page_goal", "sections"],
                        "properties": {
                            "slug": {
                                "type": "string",
                                "minLength": 1,
                                "pattern": r"^(\/|[a-z0-9][a-z0-9\/-]*)$",
                            },
                            "title": NON_EMPTY_STRING,
                            "page_goal": NON_EMPTY_STRING,
                            "sections": {
                                "type": "array",
                                "minItems": 1,
                                "items": {
                                    "type": "object",
                                    "additionalProperties": False,
                                    "required": ["heading", "text", "supporting_points"],
                                    "properties": {
                                        "heading": NON_EMPTY_STRING,
                                        "text": NON_EMPTY_STRING,
                                        "supporting_points": NON_EMPTY_STRING_ARRAY,
                                    },
                                },
                            },
                        },
                    },
                }
            },
        }
    },
}

DESIGN_SPEC_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["design_system", "images"],
    "properties": {
        "design_system": {
            "type": "object",
            "additionalProperties": False,
            "required": [
                "color_palette",
                "typography",
                "spacing_system",
                "layout_rules",
                "components",
            ],
            "properties": {
                "color_palette": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": [
                        "primary",
                        "secondary",
                        "accent",
                        "background",
                        "surface",
                        "text_primary",
                        "text_secondary",
                    ],
                    "properties": {
                        "primary": NON_EMPTY_STRING,
                        "secondary": NON_EMPTY_STRING,
                        "accent": NON_EMPTY_STRING,
                        "background": NON_EMPTY_STRING,
                        "surface": NON_EMPTY_STRING,
                        "text_primary": NON_EMPTY_STRING,
                        "text_secondary": NON_EMPTY_STRING,
                    },
                },
                "typography": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["heading_font", "body_font", "scale"],
                    "properties": {
                        "heading_font": NON_EMPTY_STRING,
                        "body_font": NON_EMPTY_STRING,
                        "scale": {
                            "type": "object",
                            "additionalProperties": False,
                            "required": ["h1", "h2", "h3", "body"],
                            "properties": {
                                "h1": NON_EMPTY_STRING,
                                "h2": NON_EMPTY_STRING,
                                "h3": NON_EMPTY_STRING,
                                "body": NON_EMPTY_STRING,
                            },
                        },
                    },
                },
                "spacing_system": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["base_unit", "section_padding", "container_width"],
                    "properties": {
                        "base_unit": NON_EMPTY_STRING,
                        "section_padding": NON_EMPTY_STRING,
                        "container_width": NON_EMPTY_STRING,
                    },
                },
                "layout_rules": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["grid", "max_width", "responsive_breakpoints"],
                    "properties": {
                        "grid": NON_EMPTY_STRING,
                        "max_width": NON_EMPTY_STRING,
                        "responsive_breakpoints": NON_EMPTY_STRING_ARRAY,
                    },
                },
                "components": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["navbar", "hero_section", "feature_cards", "cta_section", "footer"],
                    "properties": {
                        "navbar": NON_EMPTY_STRING,
                        "hero_section": NON_EMPTY_STRING,
                        "feature_cards": NON_EMPTY_STRING,
                        "cta_section": NON_EMPTY_STRING,
                        "footer": NON_EMPTY_STRING,
                    },
                },
            },
        },
        "images": {
            "type": "array",
            "minItems": 3,
            "maxItems": 6,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["filename", "prompt", "alt"],
                "properties": {
                    "filename": {
                        "type": "string",
                        "minLength": 1,
                        "pattern": r"^(?!\/)(?!.*\.\.)[^\\]+\.png$",
                    },
                    "prompt": NON_EMPTY_STRING,
                    "alt": NON_EMPTY_STRING,
                },
            },
        },
    },
}

DEVELOPMENT_TASKS_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["tasks"],
    "properties": {
        "tasks": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["id", "description", "files_involved"],
                "properties": {
                    "id": NON_EMPTY_STRING,
                    "description": NON_EMPTY_STRING,
                    "files_involved": NON_EMPTY_STRING_ARRAY,
                },
            },
        }
    },
}

GENERATED_FILES_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["files"],
    "properties": {
        "files": {
            "type": "object",
            "required": ["index.html", "css/styles.css", "js/main.js"],
            "properties": {
                "index.html": NON_EMPTY_STRING,
                "css/styles.css": NON_EMPTY_STRING,
                "js/main.js": {
                    "type": "string",
                },
            },
            "patternProperties": {
                r"^.+$": {
                    "type": "string",
                }
            },
            "additionalProperties": True,
        }
    },
}

OUTPUT_SCHEMAS = {
    "product_requirements": PRODUCT_REQUIREMENTS_SCHEMA,
    "research_output": RESEARCH_OUTPUT_SCHEMA,
    "site_structure": SITE_STRUCTURE_SCHEMA,
    "architecture_spec": ARCHITECTURE_SPEC_SCHEMA,
    "design_spec": DESIGN_SPEC_SCHEMA,
    "development_tasks": DEVELOPMENT_TASKS_SCHEMA,
    "generated_files": GENERATED_FILES_SCHEMA,
}

__all__ = [
    "ARCHITECTURE_SPEC_SCHEMA",
    "DESIGN_SPEC_SCHEMA",
    "DEVELOPMENT_TASKS_SCHEMA",
    "GENERATED_FILES_SCHEMA",
    "OUTPUT_SCHEMAS",
    "PRODUCT_REQUIREMENTS_SCHEMA",
    "RESEARCH_OUTPUT_SCHEMA",
    "SITE_STRUCTURE_SCHEMA",
]
