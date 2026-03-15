import json

from src.agents.designer import DesignerAgent
from src.core.mock_llm import MockLLM
from src.core.schema_validator import validate_schema
from src.core.schemas import DESIGN_SPEC_SCHEMA


def test_designer_returns_valid_design_spec(
    design_spec_json: str,
) -> None:
    agent = DesignerAgent(llm=MockLLM([design_spec_json]))

    result = agent.run("structured inputs")

    parsed = json.loads(result)
    validate_schema(parsed, DESIGN_SPEC_SCHEMA)
    assert len(parsed["images"]) == 3
