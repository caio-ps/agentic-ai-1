from src.agents.product_manager import ProductManagerAgent
from src.core.mock_llm import MockLLM
from src.core.schema_validator import validate_schema
from src.core.schemas import PRODUCT_REQUIREMENTS_SCHEMA

from tests.conftest import assert_product_requirements_document

def test_product_manager_returns_structured_requirements(
    product_requirements_output: str,
) -> None:
    agent = ProductManagerAgent(llm=MockLLM([product_requirements_output]))

    result = agent.run("Build a cryptocurrency education website")

    validate_schema(result, PRODUCT_REQUIREMENTS_SCHEMA)
    assert_product_requirements_document(result)
