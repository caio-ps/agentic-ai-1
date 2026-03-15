import json

from src.agents.planner import PlannerAgent
from src.core.mock_llm import MockLLM
from src.core.schema_validator import validate_schema
from src.core.schemas import DEVELOPMENT_TASKS_SCHEMA


def test_planner_returns_valid_development_tasks(
    development_tasks_json: str,
) -> None:
    agent = PlannerAgent(llm=MockLLM([development_tasks_json]))

    result = agent.run("structured inputs")

    parsed = json.loads(result)
    validate_schema(parsed, DEVELOPMENT_TASKS_SCHEMA)
    assert parsed["tasks"][0]["files_involved"]
