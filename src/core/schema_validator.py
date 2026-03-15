import json
import logging
from typing import Any

from jsonschema import Draft202012Validator
from jsonschema import ValidationError

logger = logging.getLogger(__name__)


class SchemaValidationError(ValueError):
    """Raised when data fails JSON Schema validation."""


def validate_schema(data: Any, schema: dict[str, Any]) -> None:
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(data), key=lambda error: list(error.absolute_path))
    if not errors:
        return

    first_error = errors[0]
    path = ".".join(str(part) for part in first_error.absolute_path) or "<root>"
    logger.error("Schema validation failed at %s: %s", path, first_error.message)
    logger.error("Invalid output for debugging:\n%s", _format_debug_output(data))
    raise SchemaValidationError(f"Schema validation failed at {path}: {first_error.message}")


def _format_debug_output(data: Any) -> str:
    try:
        return json.dumps(data, indent=2, ensure_ascii=True)
    except TypeError:
        return repr(data)
