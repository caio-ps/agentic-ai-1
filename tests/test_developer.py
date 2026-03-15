from src.agents.developer import DeveloperAgent
from src.core.mock_llm import MockLLM
from src.core.orchestration.orchestrator import Orchestrator


def test_developer_returns_valid_generated_files(
    generated_files_json: str,
) -> None:
    agent = DeveloperAgent(llm=MockLLM([generated_files_json]))

    result = agent.run("structured inputs")

    normalized, error = Orchestrator._validate_generated_files_output(
        stage_name="DeveloperAgent",
        stage_output=result,
    )
    assert error is None
    assert '"index.html"' in normalized
