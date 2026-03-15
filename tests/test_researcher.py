import json

from src.agents.researcher import ResearcherAgent
from src.core.mock_llm import MockLLM
from src.core.schema_validator import validate_schema
from src.core.schemas import RESEARCH_OUTPUT_SCHEMA


def test_researcher_returns_valid_research_output(
    product_requirements_output: str,
    research_scope_output: str,
    strategic_queries_output: str,
    knowledge_queries_output: str,
    research_output_json: str,
    fake_web_search_service,
) -> None:
    llm = MockLLM(
        [
            research_scope_output,
            strategic_queries_output,
            knowledge_queries_output,
            research_output_json,
        ]
    )
    agent = ResearcherAgent(llm=llm, web_search_service=fake_web_search_service)

    result = agent.run(product_requirements_output)

    parsed = json.loads(result)
    validate_schema(parsed, RESEARCH_OUTPUT_SCHEMA)
    assert parsed["knowledge_base"]["topics"]
    assert len(fake_web_search_service.queries) == 10
