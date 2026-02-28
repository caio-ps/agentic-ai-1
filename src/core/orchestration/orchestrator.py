from pathlib import Path

from src.agents.content_designer import ContentDesignerAgent
from src.agents.designer import DesignerAgent
from src.agents.developer import DeveloperAgent
from src.agents.devops import DevOpsAgent
from src.agents.product_manager import ProductManagerAgent
from src.agents.qa import QAAgent
from src.agents.researcher import ResearcherAgent
from src.core.llm import LLM


class Orchestrator:
    """Simple sequential orchestrator for V1."""

    def __init__(self, llm: LLM | None = None) -> None:
        shared_llm = llm or LLM()
        self.product_manager = ProductManagerAgent(llm=shared_llm)
        self.researcher = ResearcherAgent(llm=shared_llm)
        self.content_designer = ContentDesignerAgent(llm=shared_llm)
        self.designer = DesignerAgent(llm=shared_llm)
        self.developer = DeveloperAgent(llm=shared_llm)
        self.qa = QAAgent(llm=shared_llm)
        self.devops = DevOpsAgent(llm=shared_llm)

    def run(self, user_input: str) -> str:
        print("[ORCHESTRATOR] Stage 1: ProductManager refinement loop")
        requirements = self._refine_requirements(user_input)
        self._log_stage_output("FinalRequirements", requirements)

        print("[ORCHESTRATOR] Stage 2: Sending requirements to ResearcherAgent")
        research_dossier = self.researcher.run(requirements)
        self._log_stage_output("ResearcherAgent", research_dossier)

        print("[ORCHESTRATOR] Stage 3: Sending requirements + research to ContentDesignerAgent")
        content_designer_input = (
            "Structured requirements:\n"
            f"{requirements}\n\n"
            "Research dossier:\n"
            f"{research_dossier}"
        )
        content_plan = self.content_designer.run(content_designer_input)
        self._log_stage_output("ContentDesignerAgent", content_plan)

        print("[ORCHESTRATOR] Stage 4: Sending content plan to DesignerAgent")
        design_spec = self.designer.run(content_plan)
        self._log_stage_output("DesignerAgent", design_spec)

        print("[ORCHESTRATOR] Stage 5: Sending design spec + content plan to DeveloperAgent")
        developer_input = (
            "Structured design specification:\n"
            f"{design_spec}\n\n"
            "Structured content plan:\n"
            f"{content_plan}"
        )
        html = self.developer.run(developer_input)
        self._log_stage_output("DeveloperAgent", html)

        print("[ORCHESTRATOR] Stage 6: Running QA revision loop")
        html, qa_feedback = self._run_qa_revision_loop(
            base_developer_input=developer_input,
            initial_html=html,
        )

        print("[ORCHESTRATOR] Stage 7: Writing artifacts to disk")
        workspace_dir = Path("workspace")
        docker_dir = Path("docker")
        workspace_dir.mkdir(parents=True, exist_ok=True)
        docker_dir.mkdir(parents=True, exist_ok=True)

        html_path = workspace_dir / "index.html"
        html_path.write_text(html, encoding="utf-8")

        dockerfile_path = docker_dir / "Dockerfile"
        dockerfile_path.write_text(self._dockerfile_content(), encoding="utf-8")

        print("[ORCHESTRATOR] Stage 8: Sending QA output + HTML to DevOpsAgent")
        devops_input = (
            "QA feedback:\n"
            f"{qa_feedback}\n\n"
            "Final HTML:\n"
            f"{html}\n\n"
            f"Final HTML was also saved at {html_path}.\n"
            f"Dockerfile was also saved at {dockerfile_path}.\n\n"
            "Generate deployment instructions."
        )
        deployment_instructions = self.devops.run(devops_input)
        self._log_stage_output("DevOpsAgent", deployment_instructions)

        return (
            "Created files:\n"
            f"- {html_path}\n"
            f"- {dockerfile_path}\n\n"
            "Deployment instructions:\n"
            f"{deployment_instructions}"
        )

    def _refine_requirements(self, initial_input: str) -> str:
        latest_input = initial_input
        latest_output = initial_input

        for iteration in range(1, 6):
            print(f"[ORCHESTRATOR] ProductManager iteration {iteration}/5")
            latest_output = self.product_manager.run(latest_input)
            self._log_stage_output("ProductManagerAgent", latest_output)

            if "REQUIREMENTS_READY" in latest_output:
                print("[ORCHESTRATOR] ProductManager marked requirements as ready.")
                return self._extract_requirements_document(latest_output)

            print("[ORCHESTRATOR] ProductManager requested clarifications:")
            print(latest_output)
            additional_input = input("Additional details for ProductManager: ").strip()
            if additional_input:
                latest_input = (
                    f"{latest_input}\n\n"
                    f"Additional user input (iteration {iteration}):\n"
                    f"{additional_input}"
                )

        print(
            "[ORCHESTRATOR] Reached 5 ProductManager iterations without "
            "REQUIREMENTS_READY. Proceeding with latest output."
        )
        return latest_output

    def _run_qa_revision_loop(self, base_developer_input: str, initial_html: str) -> tuple[str, str]:
        html = initial_html
        qa_feedback = ""

        for iteration in range(1, 4):
            print(f"[ORCHESTRATOR] QA iteration {iteration}/3")
            qa_feedback = self.qa.run(html)
            self._log_stage_output("QAAgent", qa_feedback)
            qa_decision = self._extract_qa_decision(qa_feedback)
            print(f"[ORCHESTRATOR] QA decision on iteration {iteration}: {qa_decision}")

            if qa_decision != "NEEDS_CHANGES":
                return html, qa_feedback

            if iteration < 3:
                print("[ORCHESTRATOR] Sending QA feedback back to DeveloperAgent for revision")
                revision_input = (
                    "Previous HTML:\n"
                    f"{html}\n\n"
                    "QA feedback:\n"
                    f"{qa_feedback}\n\n"
                    "Revise the HTML to address all QA issues and return the "
                    "complete updated HTML."
                )
                html = self.developer.run(revision_input)
                self._log_stage_output("DeveloperAgentRevision", html)

        print(
            "[ORCHESTRATOR] WARNING: QA returned NEEDS_CHANGES after 3 iterations. "
            "Proceeding with deployment anyway."
        )
        return html, qa_feedback

    @staticmethod
    def _dockerfile_content() -> str:
        return (
            "FROM nginx:alpine\n"
            "COPY workspace/index.html /usr/share/nginx/html/index.html\n"
            "EXPOSE 80\n"
        )

    @staticmethod
    def _extract_requirements_document(product_manager_output: str) -> str:
        _, _, tail = product_manager_output.partition("REQUIREMENTS_READY")
        extracted = tail.strip()
        return extracted or product_manager_output.strip()

    @staticmethod
    def _extract_qa_decision(qa_feedback: str) -> str:
        if "NEEDS_CHANGES" in qa_feedback:
            return "NEEDS_CHANGES"
        if "APPROVED" in qa_feedback:
            return "APPROVED"
        return "NEEDS_CHANGES"

    @staticmethod
    def _log_stage_output(stage_name: str, output: str, preview_chars: int = 1200) -> None:
        print(f"[ORCHESTRATOR] {stage_name} output:")
        if len(output) <= preview_chars:
            print(output)
            return
        print(output[:preview_chars])
        print(f"[ORCHESTRATOR] ... output truncated ({len(output)} chars total)")
