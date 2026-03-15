import json

import pytest

from src.core.schema_validator import SchemaValidationError
from src.core.schema_validator import validate_schema
from src.core.schemas import RESEARCH_OUTPUT_SCHEMA


def test_research_schema_accepts_valid_agent_output(
    research_output_json: str,
) -> None:
    agent_output = json.loads(research_output_json)

    validate_schema(agent_output, RESEARCH_OUTPUT_SCHEMA)


def test_research_schema_rejects_invalid_agent_output(
    research_output_json: str,
) -> None:
    agent_output = json.loads(research_output_json)
    del agent_output["knowledge_base"]["topics"][0]["sources"]

    with pytest.raises(SchemaValidationError):
        validate_schema(agent_output, RESEARCH_OUTPUT_SCHEMA)
