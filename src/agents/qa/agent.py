from src.core.base_agent import BaseAgent
from src.core.llm import LLM


class QAAgent(BaseAgent):
    def __init__(self, llm: LLM | None = None) -> None:
        super().__init__(
            role_name="qa",
            system_prompt=(
                "You are a QA engineer specialized in reviewing front-end code "
                "for performance, accessibility, responsiveness and best practices.\n\n"
                "You will receive full HTML code.\n"
                "Analyze the structure.\n"
                "Evaluate accessibility.\n"
                "Evaluate responsiveness.\n"
                "Return structured bullet point feedback.\n"
                "Conclude explicitly on the last line with exactly one of:\n"
                "APPROVED\n"
                "NEEDS_CHANGES\n"
                "Use uppercase for the final decision.\n"
                "The final line must contain ONLY one word: APPROVED or "
                "NEEDS_CHANGES.\n"
                "No extra text on that final line.\n"
                "The final line must not contain punctuation."
            ),
            llm=llm,
        )
