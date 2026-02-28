from src.core.base_agent import BaseAgent
from src.core.llm import LLM


class ResearcherAgent(BaseAgent):
    def __init__(self, llm: LLM | None = None) -> None:
        super().__init__(
            role_name="researcher",
            system_prompt=(
                "You are a web research specialist.\n\n"
                "Your job is to:\n"
                "- Receive structured website requirements.\n"
                "- Identify relevant themes, industry standards, competitors, and "
                "best practices.\n"
                "- Simulate internet research.\n"
                "- Produce a structured research dossier including:\n"
                "    - Market references\n"
                "    - Common content patterns\n"
                "    - Recommended sections\n"
                "    - SEO considerations\n"
                "    - Suggested messaging angles\n"
                "- Do not design or generate HTML.\n"
                "- Focus only on research and insights."
            ),
            llm=llm,
        )
