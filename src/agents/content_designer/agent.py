from src.core.base_agent import BaseAgent
from src.core.llm import LLM


class ContentDesignerAgent(BaseAgent):
    def __init__(self, llm: LLM | None = None) -> None:
        super().__init__(
            role_name="content_designer",
            system_prompt=(
                "You are a content strategist and information architect.\n\n"
                "Your job is to:\n"
                "- Receive structured requirements from ProductManager.\n"
                "- Receive research dossier from Researcher.\n"
                "- Propose a complete website content structure including:\n"
                "    - Page list\n"
                "    - Navigation structure\n"
                "    - Section breakdown per page\n"
                "    - Headline ideas\n"
                "    - Content blocks\n"
                "    - Internal linking strategy\n\n"
                "Output must be structured and organized.\n"
                "Do not generate HTML.\n"
                "Do not generate design specs.\n"
                "Focus only on content structure."
            ),
            llm=llm,
        )
