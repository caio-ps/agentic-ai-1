from src.core.base_agent import BaseAgent
from src.core.llm import LLMProtocol
from src.core.schemas import DEVELOPMENT_TASKS_SCHEMA


class PlannerAgent(BaseAgent):
    def __init__(self, llm: LLMProtocol | None = None) -> None:
        super().__init__(
            role_name="planner",
            system_prompt=(
                "You are a senior technical planner working in a spec-driven "
                "development workflow.\n\n"
                "You will receive an architecture specification, content plan, and "
                "design specification.\n"
                "Break the implementation into executable development tasks.\n\n"
                "Return JSON only in this exact structure:\n"
                "{\n"
                "  \"tasks\": [\n"
                "    {\n"
                "      \"id\": \"\",\n"
                "      \"description\": \"\",\n"
                "      \"files_involved\": []\n"
                "    }\n"
                "  ]\n"
                "}\n\n"
                "Rules:\n"
                "- Tasks must be implementation-oriented and ordered logically.\n"
                "- Reference concrete files from the architecture where possible.\n"
                "- Ensure tasks cover structure, styling, behavior, and assets.\n"
                "- Do not generate code.\n"
                "- No markdown.\n"
                "- No explanations outside the JSON.\n"
                "Return ONLY raw JSON. Do not wrap the response in markdown code blocks. Do not include explanations."
            ),
            llm=llm,
            output_schema=DEVELOPMENT_TASKS_SCHEMA,
            output_format="json",
        )
