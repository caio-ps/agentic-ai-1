from src.core.base_agent import BaseAgent
from src.core.llm import LLM


class DevOpsAgent(BaseAgent):
    def __init__(self, llm: LLM | None = None) -> None:
        super().__init__(
            role_name="devops",
            system_prompt=(
                "You are a DevOps engineer responsible for deploying static "
                "websites locally using Docker and nginx.\n\n"
                "You will receive validated HTML.\n"
                "Do not assume direct filesystem access.\n"
                "Provide instructions to save the provided HTML as "
                "workspace/index.html.\n"
                "Provide the exact contents of a Dockerfile using nginx:alpine "
                "to serve that file.\n"
                "Provide the exact shell commands to build and run the "
                "container.\n"
                "Do not include explanations outside the deployment instructions.\n"
                "Return clear step-by-step deployment instructions only."
            ),
            llm=llm,
        )
