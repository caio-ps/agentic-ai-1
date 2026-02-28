import os

from openai import OpenAI


class LLM:
    """Minimal OpenAI wrapper used by agents."""

    def __init__(self, model: str = "gpt-4o") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate(self, system_prompt: str, user_input: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input},
            ],
        )
        return (response.output_text or "").strip()
