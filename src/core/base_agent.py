from .llm import LLM


class BaseAgent:
    """Base class for all agents."""

    def __init__(self, role_name: str, system_prompt: str, llm: LLM | None = None) -> None:
        self.role_name = role_name
        self.system_prompt = system_prompt
        self.llm = llm or LLM()

    def run(self, user_input: str) -> str:
        print(f"[{self.role_name.upper()}] Starting execution...")
        print(f"[{self.role_name.upper()}] Input length: {len(user_input)} characters")
        response = self.llm.generate(system_prompt=self.system_prompt, user_input=user_input)
        print(f"[{self.role_name.upper()}] Execution completed.")
        return response
