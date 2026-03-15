import json

from src.agents.content_designer import ContentDesignerAgent
from src.core.mock_llm import MockLLM
from src.core.schema_validator import validate_schema
from src.core.schemas import SITE_STRUCTURE_SCHEMA


def test_content_designer_returns_valid_site_structure(
    site_structure_json: str,
) -> None:
    agent = ContentDesignerAgent(llm=MockLLM([site_structure_json]))

    result = agent.run("structured inputs")

    parsed = json.loads(result)
    validate_schema(parsed, SITE_STRUCTURE_SCHEMA)
    assert parsed["site_structure"]["pages"][0]["sections"]
