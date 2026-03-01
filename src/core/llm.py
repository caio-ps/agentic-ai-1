import os
from typing import Any

from openai import OpenAI


class LLM:
    """Minimal OpenAI wrapper used by agents."""

    def __init__(self, model: str = "gpt-4o") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(
        self,
        system_prompt: str,
        user_input: str,
        tools: list[dict[str, Any]] | None = None,
    ) -> str:
        request: dict[str, Any] = {
            "model": self.model,
            "input": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        }
        if tools:
            request["tools"] = tools

        response = self.client.responses.create(**request)
        return (response.output_text or "").strip()
