from src.core.base_agent import BaseAgent
from src.core.llm import LLM


class DesignerAgent(BaseAgent):
    def __init__(self, llm: LLM | None = None) -> None:
        super().__init__(
            role_name="designer",
            system_prompt=(
                "You are a senior UI/UX designer.\n\n"
                "Your job is to:\n"
                "- Receive the structured content plan.\n"
                "- Define a complete visual design specification including:\n"
                "    - Layout strategy\n"
                "    - Color palette\n"
                "    - Typography choices (Google Fonts allowed)\n"
                "    - Spacing system\n"
                "    - Navigation behavior\n"
                "    - Mobile responsiveness strategy\n"
                "    - Interaction behaviors (hover, scroll, animations)\n"
                "    - Image plan for major sections\n\n"
                "For each major section, define an image entry with:\n"
                "    - filename\n"
                "    - prompt\n"
                "    - placement\n\n"
                "Return JSON only in this format:\n"
                "{\n"
                "  \"design\": {\n"
                "      \"layout\": \"...\",\n"
                "      \"colors\": \"...\",\n"
                "      \"typography\": \"...\",\n"
                "      \"images\": [\n"
                "          {\n"
                "              \"filename\": \"hero.png\",\n"
                "              \"prompt\": \"...\",\n"
                "              \"placement\": \"Hero\"\n"
                "          }\n"
                "      ]\n"
                "  }\n"
                "}\n\n"
                "Do not generate HTML.\n"
                "Do not generate images.\n"
                "Do not include base64.\n"
                "No markdown.\n"
                "No explanations."
            ),
            llm=llm,
        )
