import json

import pytest

from src.core.schema_validator import SchemaValidationError
from src.core.schema_validator import validate_schema
from src.core.schemas import ARCHITECTURE_SPEC_SCHEMA


def test_architecture_schema_accepts_valid_agent_output(
    architecture_spec_json: str,
) -> None:
    agent_output = json.loads(architecture_spec_json)

    validate_schema(agent_output, ARCHITECTURE_SPEC_SCHEMA)


def test_architecture_schema_rejects_invalid_agent_output(
    architecture_spec_json: str,
) -> None:
    agent_output = json.loads(architecture_spec_json)
    agent_output["architecture_spec"]["components"] = []

    with pytest.raises(SchemaValidationError):
        validate_schema(agent_output, ARCHITECTURE_SPEC_SCHEMA)
