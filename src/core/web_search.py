import os

from openai import OpenAI


class WebSearchService:
    """Reusable web search service powered by OpenAI tool calling."""

    def __init__(self, model: str = "gpt-4o") -> None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is not set.")

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def search(self, query: str) -> str:
        response = self.client.responses.create(
            model=self.model,
            tools=[{"type": "web_search_preview"}],
            input=[
                {
                    "role": "system",
                    "content": (
                        "Use web search and return only structured raw search results. "
                        "For each result include exactly: Title, URL, Short summary. "
                        "Do not include conclusions, recommendations, or analysis."
                    ),
                },
                {"role": "user", "content": query},
            ],
        )
        return (response.output_text or "").strip()
