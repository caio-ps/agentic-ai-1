import json

from src.core.base_agent import BaseAgent
from src.core.base_agent import attempt_schema_repair
from src.core.base_agent import sanitize_llm_output
from src.core.mock_llm import MockLLM


def _build_json_agent(schema: dict[str, object], responses: list[str]) -> BaseAgent:
    return BaseAgent(
        role_name="safe_output_test",
        system_prompt="Return structured JSON.",
        llm=MockLLM(responses),
        output_schema=schema,
        output_format="json",
    )


def test_safe_output_layer_handles_json_wrapped_in_markdown() -> None:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["label"],
        "properties": {"label": {"type": "string"}},
    }
    agent = _build_json_agent(schema, ['```json\n{"label": "Header"}\n```'])

    result = agent.run("Generate a label")

    assert json.loads(result) == {"label": "Header"}


def test_safe_output_layer_extracts_json_when_extra_text_exists() -> None:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["label"],
        "properties": {"label": {"type": "string"}},
    }
    agent = _build_json_agent(
        schema,
        ["Here is the JSON you requested:\n\n```json\n{\"label\": \"Header\"}\n```\nThanks!"],
    )

    result = agent.run("Generate a label")

    assert json.loads(result) == {"label": "Header"}


def test_attempt_schema_repair_extracts_string_from_object() -> None:
    schema = {"type": "string"}

    repaired = attempt_schema_repair({"name": "Header", "directory": "components/Header"}, schema)

    assert repaired == "Header"


def test_attempt_schema_repair_wraps_object_when_schema_expects_array() -> None:
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"],
        },
    }

    repaired = attempt_schema_repair({"name": "Header"}, schema)

    assert repaired == [{"name": "Header"}]


def test_safe_output_layer_repairs_object_and_array_mismatches() -> None:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["labels"],
        "properties": {
            "labels": {
                "type": "array",
                "minItems": 1,
                "items": {"type": "string"},
            }
        },
    }
    agent = _build_json_agent(schema, ['{"labels": {"name": "Header"}}'])

    result = agent.run("Generate labels")

    assert json.loads(result) == {"labels": ["Header"]}


def test_safe_output_layer_retries_once_after_validation_failure() -> None:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["label"],
        "properties": {"label": {"type": "string"}},
    }
    llm = MockLLM(
        [
            '{"unexpected": "value"}',
            '{"label": "Recovered"}',
        ]
    )
    agent = BaseAgent(
        role_name="safe_output_test",
        system_prompt="Return structured JSON.",
        llm=llm,
        output_schema=schema,
        output_format="json",
    )

    result = agent.run("Generate a label")

    assert json.loads(result) == {"label": "Recovered"}
    assert len(llm.calls) == 2
    assert "failed schema validation" in str(llm.calls[1]["user_input"]).lower()


def test_sanitize_llm_output_removes_trailing_commas() -> None:
    cleaned = sanitize_llm_output('{"label": "Header",}')

    assert json.loads(cleaned) == {"label": "Header"}
