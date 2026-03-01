import json
from pathlib import Path

from src.agents.content_designer import ContentDesignerAgent
from src.agents.designer import DesignerAgent
from src.agents.developer import DeveloperAgent
from src.agents.devops import DevOpsAgent
from src.agents.product_manager import ProductManagerAgent
from src.agents.qa import QAAgent
from src.agents.researcher import ResearcherAgent
from src.core.image_generator import ImageGenerator
from src.core.llm import LLM


class Orchestrator:
    """Simple sequential orchestrator for V1."""

    def __init__(self, llm: LLM | None = None) -> None:
        shared_llm = llm or LLM()
        self.product_manager = ProductManagerAgent(llm=shared_llm)
        self.researcher = ResearcherAgent(llm=shared_llm)
        self.content_designer = ContentDesignerAgent(llm=shared_llm)
        self.designer = DesignerAgent(llm=shared_llm)
        self.image_generator = ImageGenerator()
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

        print("[ORCHESTRATOR] Stage 4.5: Generating design images")
        generated_image_paths = self._generate_design_images(design_spec)

        print("[ORCHESTRATOR] Stage 5: Sending design spec + content plan + image paths to DeveloperAgent")
        image_paths_text = "\n".join(f"- {path}" for path in generated_image_paths)
        developer_input = (
            "Structured design specification:\n"
            f"{design_spec}\n\n"
            "Structured content plan:\n"
            f"{content_plan}\n\n"
            "Generated image paths:\n"
            f"{image_paths_text}"
        )
        project_json = self.developer.run(developer_input)
        self._log_stage_output("DeveloperAgent", project_json)

        print("[ORCHESTRATOR] Stage 6: Running QA revision loop")
        project_json, qa_feedback = self._run_qa_revision_loop(
            initial_project_json=project_json,
        )

        print("[ORCHESTRATOR] Stage 7: Writing artifacts to disk")
        workspace_dir = Path("workspace")
        docker_dir = Path("docker")
        workspace_dir.mkdir(parents=True, exist_ok=True)
        docker_dir.mkdir(parents=True, exist_ok=True)

        files = self._parse_project_files(project_json)
        if files is None:
            print("[ORCHESTRATOR] ERROR: Invalid DeveloperAgent JSON output. Aborting deployment.")
            return (
                "ERROR: Invalid DeveloperAgent JSON output.\n"
                "Expected JSON object with a 'files' dictionary.\n"
                "No files were written and deployment was skipped."
            )

        written_paths: list[Path] = []
        for relative_path, content in files.items():
            target_path = workspace_dir / relative_path
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content, encoding="utf-8")
            written_paths.append(target_path)
            print(f"[ORCHESTRATOR] Wrote file: {target_path}")

        dockerfile_path = docker_dir / "Dockerfile"
        dockerfile_path.write_text(self._dockerfile_content(), encoding="utf-8")
        print(f"[ORCHESTRATOR] Wrote file: {dockerfile_path}")

        print("[ORCHESTRATOR] Stage 8: Sending QA output + project JSON to DevOpsAgent")
        file_list = "\n".join(f"- {path}" for path in written_paths)
        devops_input = (
            "QA feedback:\n"
            f"{qa_feedback}\n\n"
            "Final project JSON:\n"
            f"{project_json}\n\n"
            "Written project files:\n"
            f"{file_list}\n\n"
            f"Dockerfile was also saved at {dockerfile_path}.\n\n"
            "Generate deployment instructions."
        )
        deployment_instructions = self.devops.run(devops_input)
        self._log_stage_output("DevOpsAgent", deployment_instructions)

        written_paths_summary = "\n".join(f"- {path}" for path in written_paths)
        generated_images_summary = "\n".join(f"- {path}" for path in generated_image_paths)
        return (
            "Created files:\n"
            f"{generated_images_summary}\n"
            f"{written_paths_summary}\n"
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

    def _run_qa_revision_loop(self, initial_project_json: str) -> tuple[str, str]:
        project_json = initial_project_json
        qa_feedback = ""

        for iteration in range(1, 4):
            print(f"[ORCHESTRATOR] QA iteration {iteration}/3")
            qa_feedback = self.qa.run(project_json)
            self._log_stage_output("QAAgent", qa_feedback)
            qa_decision = self._extract_qa_decision(qa_feedback)
            print(f"[ORCHESTRATOR] QA decision on iteration {iteration}: {qa_decision}")

            if qa_decision != "NEEDS_CHANGES":
                return project_json, qa_feedback

            if iteration < 3:
                print("[ORCHESTRATOR] Sending QA feedback back to DeveloperAgent for revision")
                revision_input = (
                    "Previous project JSON:\n"
                    f"{project_json}\n\n"
                    "QA feedback:\n"
                    f"{qa_feedback}\n\n"
                    "Revise the project to address all QA issues and return the "
                    "complete updated JSON with all files."
                )
                project_json = self.developer.run(revision_input)
                self._log_stage_output("DeveloperAgentRevision", project_json)

        print(
            "[ORCHESTRATOR] WARNING: QA returned NEEDS_CHANGES after 3 iterations. "
            "Proceeding with deployment anyway."
        )
        return project_json, qa_feedback

    def _generate_design_images(self, design_spec: str) -> list[Path]:
        assets_dir = Path("assets/images")
        assets_dir.mkdir(parents=True, exist_ok=True)
        image_paths: list[Path] = []

        try:
            payload = json.loads(design_spec)
            images = payload.get("design", {}).get("images", [])
            if not isinstance(images, list):
                print("[ORCHESTRATOR] WARNING: design.images is not a list. Skipping image generation.")
                return image_paths
        except json.JSONDecodeError:
            print("[ORCHESTRATOR] WARNING: Invalid design specification JSON. Skipping image generation.")
            return image_paths

        for index, image_def in enumerate(images, start=1):
            if not isinstance(image_def, dict):
                print(f"[ORCHESTRATOR] WARNING: Invalid image definition at index {index}. Skipping.")
                continue

            prompt = image_def.get("prompt")
            if not isinstance(prompt, str) or not prompt.strip():
                print(f"[ORCHESTRATOR] WARNING: Missing image prompt at index {index}. Skipping.")
                continue

            filename = self._safe_image_filename(image_def.get("filename"), index)
            target_path = assets_dir / filename

            try:
                print(f"[ORCHESTRATOR] Generating image {index}: {filename}")
                image_bytes = self.image_generator.generate_image(prompt.strip())
                target_path.write_bytes(image_bytes)
                image_paths.append(target_path)
                print(f"[ORCHESTRATOR] Image generated: {target_path}")
            except Exception as exc:  # noqa: BLE001
                print(f"[ORCHESTRATOR] WARNING: Failed to generate {filename}: {exc}")

        return image_paths

    @staticmethod
    def _safe_image_filename(raw_filename: object, index: int) -> str:
        if isinstance(raw_filename, str) and raw_filename.strip():
            name = Path(raw_filename.strip()).name
            if name:
                return name
        return f"generated_{index}.png"

    @staticmethod
    def _dockerfile_content() -> str:
        return (
            "FROM nginx:alpine\n"
            "COPY workspace/ /usr/share/nginx/html/\n"
            "EXPOSE 80\n"
        )

    @staticmethod
    def _parse_project_files(project_json: str) -> dict[str, str] | None:
        try:
            payload = json.loads(project_json)
        except json.JSONDecodeError:
            return None

        files = payload.get("files") if isinstance(payload, dict) else None
        if not isinstance(files, dict):
            return None

        normalized: dict[str, str] = {}
        for path, content in files.items():
            if not isinstance(path, str) or not isinstance(content, str):
                return None
            normalized[path] = content
        return normalized

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
