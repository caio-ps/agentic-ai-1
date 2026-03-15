import json

import pytest

from src.core.schema_validator import SchemaValidationError
from src.core.schema_validator import validate_schema
from src.core.schemas import DESIGN_SPEC_SCHEMA


def test_design_schema_accepts_valid_agent_output(
    design_spec_json: str,
) -> None:
    agent_output = json.loads(design_spec_json)

    validate_schema(agent_output, DESIGN_SPEC_SCHEMA)


def test_design_schema_rejects_invalid_agent_output(
    design_spec_json: str,
) -> None:
    agent_output = json.loads(design_spec_json)
    agent_output["images"][0]["filename"] = "../hero.png"

    with pytest.raises(SchemaValidationError):
        validate_schema(agent_output, DESIGN_SPEC_SCHEMA)
