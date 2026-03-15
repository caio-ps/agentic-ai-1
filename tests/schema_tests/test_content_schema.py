import json

import pytest

from src.core.schema_validator import SchemaValidationError
from src.core.schema_validator import validate_schema
from src.core.schemas import SITE_STRUCTURE_SCHEMA


def test_content_schema_accepts_valid_agent_output(
    site_structure_json: str,
) -> None:
    agent_output = json.loads(site_structure_json)

    validate_schema(agent_output, SITE_STRUCTURE_SCHEMA)


def test_content_schema_rejects_invalid_agent_output(
    site_structure_json: str,
) -> None:
    agent_output = json.loads(site_structure_json)
    agent_output["site_structure"]["pages"][0]["sections"][0]["supporting_points"] = []

    with pytest.raises(SchemaValidationError):
        validate_schema(agent_output, SITE_STRUCTURE_SCHEMA)
