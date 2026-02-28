from src.agents.developer import DeveloperAgent
from src.agents.devops import DevOpsAgent
from src.agents.manager import ManagerAgent
from src.agents.qa import QAAgent
from src.core.llm import LLM
from pathlib import Path


class Orchestrator:
    """Simple sequential orchestrator for V1."""

    def __init__(self, llm: LLM | None = None) -> None:
        shared_llm = llm or LLM()
        self.manager = ManagerAgent(llm=shared_llm)
        self.developer = DeveloperAgent(llm=shared_llm)
        self.qa = QAAgent(llm=shared_llm)
        self.devops = DevOpsAgent(llm=shared_llm)

    def run(self, user_input: str) -> str:
        print("[ORCHESTRATOR] Step 1/7: Sending user input to ManagerAgent")
        manager_output = self.manager.run(user_input)
        requirements = manager_output  # V1: assume requirements are clear.

        print("[ORCHESTRATOR] Step 2/7: Sending requirements to DeveloperAgent")
        html = self.developer.run(requirements)
        print("[ORCHESTRATOR] Step 3/7: Sending generated HTML to QAAgent")
        qa_feedback = self.qa.run(html)
        qa_decision = self._extract_qa_decision(qa_feedback)
        print(f"[ORCHESTRATOR] Step 4/7: QA decision = {qa_decision}")

        if qa_decision == "NEEDS_CHANGES":
            print("[ORCHESTRATOR] Step 5/7: Requesting one revision from DeveloperAgent")
            revision_input = (
                "Original requirements:\n"
                f"{requirements}\n\n"
                "QA feedback:\n"
                f"{qa_feedback}\n\n"
                "Please update the HTML accordingly."
            )
            html = self.developer.run(revision_input)
            print("[ORCHESTRATOR] Step 6/7: Re-running QAAgent after revision")
            qa_feedback = self.qa.run(html)

        print("[ORCHESTRATOR] Step 7/7: Writing artifacts and requesting DevOps instructions")
        workspace_dir = Path("workspace")
        docker_dir = Path("docker")
        workspace_dir.mkdir(parents=True, exist_ok=True)
        docker_dir.mkdir(parents=True, exist_ok=True)

        html_path = workspace_dir / "index.html"
        html_path.write_text(html, encoding="utf-8")

        dockerfile_path = docker_dir / "Dockerfile"
        dockerfile_path.write_text(self._dockerfile_content(), encoding="utf-8")

        devops_input = (
            f"Validated HTML was saved at {html_path}.\n"
            f"Dockerfile was saved at {dockerfile_path}.\n\n"
            "Generate deployment instructions."
        )
        deployment_instructions = self.devops.run(devops_input)

        return (
            "Created files:\n"
            f"- {html_path}\n"
            f"- {dockerfile_path}\n\n"
            "Deployment instructions:\n"
            f"{deployment_instructions}"
        )

    @staticmethod
    def _extract_qa_decision(qa_feedback: str) -> str:
        last_line = qa_feedback.strip().splitlines()[-1].strip() if qa_feedback.strip() else ""
        if "APPROVED" in last_line:
            return "APPROVED"
        return "NEEDS_CHANGES"

    @staticmethod
    def _dockerfile_content() -> str:
        return (
            "FROM nginx:alpine\n"
            "COPY workspace/index.html /usr/share/nginx/html/index.html\n"
            "EXPOSE 80\n"
        )
