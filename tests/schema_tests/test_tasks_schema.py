import json

import pytest

from src.core.schema_validator import SchemaValidationError
from src.core.schema_validator import validate_schema
from src.core.schemas import DEVELOPMENT_TASKS_SCHEMA


def test_tasks_schema_accepts_valid_agent_output(
    development_tasks_json: str,
) -> None:
    agent_output = json.loads(development_tasks_json)

    validate_schema(agent_output, DEVELOPMENT_TASKS_SCHEMA)


def test_tasks_schema_rejects_invalid_agent_output(
    development_tasks_json: str,
) -> None:
    agent_output = json.loads(development_tasks_json)
    del agent_output["tasks"][0]["description"]

    with pytest.raises(SchemaValidationError):
        validate_schema(agent_output, DEVELOPMENT_TASKS_SCHEMA)
