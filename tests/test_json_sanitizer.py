import json

import pytest

from src.core.base_agent import sanitize_llm_output


@pytest.mark.parametrize(
    ("raw_response", "expected"),
    [
        ('{"key": "value"}', {"key": "value"}),
        ('```json\n{"key": "value"}\n```', {"key": "value"}),
        ('```\n{"key": "value"}\n```', {"key": "value"}),
        ('  \n\t{"key": "value"}\n  ', {"key": "value"}),
    ],
)
def test_sanitize_json_response_allows_json_parsing(raw_response: str, expected: dict[str, str]) -> None:
    cleaned = sanitize_llm_output(raw_response)

    assert json.loads(cleaned) == expected
