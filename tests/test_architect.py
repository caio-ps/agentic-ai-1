import json

from src.agents.architect import ArchitectAgent
from src.core.mock_llm import MockLLM
from src.core.schema_validator import validate_schema
from src.core.schemas import ARCHITECTURE_SPEC_SCHEMA


def test_architect_returns_valid_architecture_spec(
    architecture_spec_json: str,
) -> None:
    agent = ArchitectAgent(llm=MockLLM([architecture_spec_json]))

    result = agent.run("structured inputs")

    parsed = json.loads(result)
    validate_schema(parsed, ARCHITECTURE_SPEC_SCHEMA)
    assert parsed["architecture_spec"]["project_structure"]
