from src.core.base_agent import BaseAgent
from src.core.llm import LLM


class ManagerAgent(BaseAgent):
    def __init__(self, llm: LLM | None = None) -> None:
        super().__init__(
            role_name="manager",
            system_prompt=(
                "You are a software project manager. Your job is to clarify "
                "requirements and decide when they are well defined."
            ),
            llm=llm,
        )
