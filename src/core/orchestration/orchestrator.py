import json
import re
from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path

from src.agents.architect import ArchitectAgent
from src.agents.content_designer import ContentDesignerAgent
from src.agents.designer import DesignerAgent
from src.agents.developer import DeveloperAgent
from src.agents.devops import DevOpsAgent
from src.agents.planner import PlannerAgent
from src.agents.product_manager import ProductManagerAgent
from src.agents.qa import QAAgent
from src.agents.researcher import ResearcherAgent
from src.core.image_generator import ImageGenerator
from src.core.llm import LLM
from src.core.llm import LLMProtocol
from src.core.schema_validator import SchemaValidationError
from src.core.schema_validator import validate_schema
from src.core.schemas import ARCHITECTURE_SPEC_SCHEMA
from src.core.schemas import DESIGN_SPEC_SCHEMA
from src.core.schemas import DEVELOPMENT_TASKS_SCHEMA
from src.core.schemas import GENERATED_FILES_SCHEMA
from src.core.schemas import RESEARCH_OUTPUT_SCHEMA
from src.core.schemas import SITE_STRUCTURE_SCHEMA


@dataclass
class _RenderedHTMLDocument:
    path: str
    title_text: str
    visible_text: str


@dataclass
class _PipelineArtifacts:
    product_requirements: str = ""
    research_output: str = ""
    site_structure: str = ""
    architecture_spec: str = ""
    design_spec: str = ""
    development_tasks: str = ""
    generated_files: str = ""
    generated_image_paths: list[Path] = field(default_factory=list)


class _HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._ignored_depth = 0
        self._in_title = False
        self._text_parts: list[str] = []
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag in {"script", "style", "noscript"}:
            self._ignored_depth += 1
        if tag == "title" and self._ignored_depth == 0:
            self._in_title = True

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript"} and self._ignored_depth > 0:
            self._ignored_depth -= 1
        if tag == "title":
            self._in_title = False

    def handle_data(self, data: str) -> None:
        if self._ignored_depth > 0:
            return
        stripped = data.strip()
        if not stripped:
            return
        self._text_parts.append(stripped)
        if self._in_title:
            self._title_parts.append(stripped)

    @property
    def title_text(self) -> str:
        return " ".join(self._title_parts)

    @property
    def visible_text(self) -> str:
        return " ".join(self._text_parts)


class Orchestrator:
    """Simple sequential orchestrator for V1."""

    def __init__(self, llm: LLMProtocol | None = None) -> None:
        shared_llm = llm or LLM()
        self.product_manager = ProductManagerAgent(llm=shared_llm)
        self.researcher = ResearcherAgent(llm=shared_llm)
        self.content_designer = ContentDesignerAgent(llm=shared_llm)
        self.architect = ArchitectAgent(llm=shared_llm)
        self.designer = DesignerAgent(llm=shared_llm)
        self.image_generator = ImageGenerator()
        self.planner = PlannerAgent(llm=shared_llm)
        self.developer = DeveloperAgent(llm=shared_llm)
        self.qa = QAAgent(llm=shared_llm)
        self.devops = DevOpsAgent(llm=shared_llm)

    def run(self, user_input: str) -> str:
        artifacts = _PipelineArtifacts()

        print("[ORCHESTRATOR] Stage 1: ProductManagerAgent -> product_requirements")
        artifacts.product_requirements = self._refine_requirements(user_input)
        self._log_artifact("ProductManagerAgent", "product_requirements", artifacts.product_requirements)

        print("[ORCHESTRATOR] Stage 2: ResearcherAgent -> research_output")
        self._log_stage_inputs("ResearcherAgent", product_requirements=artifacts.product_requirements)
        research_input = self._artifact_payload(
            product_requirements=artifacts.product_requirements,
        )
        artifacts.research_output = self.researcher.run(research_input)
        self._log_artifact("ResearcherAgent", "research_output", artifacts.research_output)
        artifacts.research_output, research_error = self._validate_stage_output(
            stage_name="ResearcherAgent",
            stage_output=artifacts.research_output,
            schema=RESEARCH_OUTPUT_SCHEMA,
        )
        if research_error:
            return research_error
        self._log_artifact("ResearcherAgentValidated", "research_output", artifacts.research_output)

        print("[ORCHESTRATOR] Stage 3: ContentDesignerAgent -> site_structure")
        self._log_stage_inputs(
            "ContentDesignerAgent",
            product_requirements=artifacts.product_requirements,
            research_output=artifacts.research_output,
        )
        content_designer_input = self._artifact_payload(
            product_requirements=artifacts.product_requirements,
            research_output=artifacts.research_output,
        )
        artifacts.site_structure = self.content_designer.run(content_designer_input)
        self._log_artifact("ContentDesignerAgent", "site_structure", artifacts.site_structure)
        artifacts.site_structure, content_error = self._validate_stage_output(
            stage_name="ContentDesignerAgent",
            stage_output=artifacts.site_structure,
            schema=SITE_STRUCTURE_SCHEMA,
        )
        if content_error:
            return content_error
        self._log_artifact("ContentDesignerAgentValidated", "site_structure", artifacts.site_structure)

        print("[ORCHESTRATOR] Stage 4: ArchitectAgent -> architecture_spec")
        self._log_stage_inputs(
            "ArchitectAgent",
            product_requirements=artifacts.product_requirements,
            research_output=artifacts.research_output,
            site_structure=artifacts.site_structure,
        )
        architect_input = self._artifact_payload(
            product_requirements=artifacts.product_requirements,
            research_output=artifacts.research_output,
            site_structure=artifacts.site_structure,
        )
        artifacts.architecture_spec = self.architect.run(architect_input)
        self._log_artifact("ArchitectAgent", "architecture_spec", artifacts.architecture_spec)
        artifacts.architecture_spec, architecture_error = self._validate_stage_output(
            stage_name="ArchitectAgent",
            stage_output=artifacts.architecture_spec,
            schema=ARCHITECTURE_SPEC_SCHEMA,
        )
        if architecture_error:
            return architecture_error
        self._log_artifact("ArchitectAgentValidated", "architecture_spec", artifacts.architecture_spec)

        print("[ORCHESTRATOR] Stage 5: DesignerAgent -> design_spec")
        self._log_stage_inputs(
            "DesignerAgent",
            architecture_spec=artifacts.architecture_spec,
            site_structure=artifacts.site_structure,
        )
        designer_input = self._artifact_payload(
            architecture_spec=artifacts.architecture_spec,
            site_structure=artifacts.site_structure,
        )
        artifacts.design_spec = self.designer.run(designer_input)
        self._log_artifact("DesignerAgent", "design_spec", artifacts.design_spec)
        artifacts.design_spec, design_error = self._validate_stage_output(
            stage_name="DesignerAgent",
            stage_output=artifacts.design_spec,
            schema=DESIGN_SPEC_SCHEMA,
        )
        if design_error:
            return design_error
        self._log_artifact("DesignerAgentValidated", "design_spec", artifacts.design_spec)

        print("[ORCHESTRATOR] Stage 6: PlannerAgent -> development_tasks")
        self._log_stage_inputs(
            "PlannerAgent",
            architecture_spec=artifacts.architecture_spec,
            site_structure=artifacts.site_structure,
            design_spec=artifacts.design_spec,
        )
        planner_input = self._artifact_payload(
            architecture_spec=artifacts.architecture_spec,
            site_structure=artifacts.site_structure,
            design_spec=artifacts.design_spec,
        )
        artifacts.development_tasks = self.planner.run(planner_input)
        self._log_artifact("PlannerAgent", "development_tasks", artifacts.development_tasks)
        artifacts.development_tasks, planner_error = self._validate_stage_output(
            stage_name="PlannerAgent",
            stage_output=artifacts.development_tasks,
            schema=DEVELOPMENT_TASKS_SCHEMA,
        )
        if planner_error:
            return planner_error
        self._log_artifact("PlannerAgentValidated", "development_tasks", artifacts.development_tasks)

        print("[ORCHESTRATOR] Auxiliary: Image generation from design_spec")
        artifacts.generated_image_paths = self._generate_design_images(artifacts.design_spec)
        self._log_generated_images(artifacts.generated_image_paths)

        print("[ORCHESTRATOR] Stage 7: DeveloperAgent -> generated_files")
        self._log_stage_inputs(
            "DeveloperAgent",
            architecture_spec=artifacts.architecture_spec,
            design_spec=artifacts.design_spec,
            site_structure=artifacts.site_structure,
            development_tasks=artifacts.development_tasks,
        )
        developer_input = self._artifact_payload(
            architecture_spec=artifacts.architecture_spec,
            design_spec=artifacts.design_spec,
            site_structure=artifacts.site_structure,
            development_tasks=artifacts.development_tasks,
        )
        artifacts.generated_files = self.developer.run(developer_input)
        self._log_artifact("DeveloperAgent", "generated_files", artifacts.generated_files)
        artifacts.generated_files, generated_files_error = self._validate_generated_files_output(
            stage_name="DeveloperAgent",
            stage_output=artifacts.generated_files,
        )
        if generated_files_error:
            return generated_files_error
        self._log_artifact("DeveloperAgentValidated", "generated_files", artifacts.generated_files)

        print("[ORCHESTRATOR] Stage 8: QAAgent revision loop")
        artifacts.generated_files, qa_feedback = self._run_qa_revision_loop(artifacts)
        if not artifacts.generated_files:
            return qa_feedback

        print("[ORCHESTRATOR] Stage 9: Persisting generated_files artifact")
        workspace_dir = Path("workspace")
        docker_dir = Path("docker")
        workspace_dir.mkdir(parents=True, exist_ok=True)
        docker_dir.mkdir(parents=True, exist_ok=True)

        files = self._parse_project_files(artifacts.generated_files)
        if files is None:
            print("[ORCHESTRATOR] ERROR: Invalid generated_files artifact. Aborting deployment.")
            return (
                "ERROR: Invalid generated_files artifact.\n"
                "Expected JSON object with a 'files' dictionary.\n"
                "No files were written and deployment was skipped."
            )

        written_paths: list[Path] = []
        protected_image_paths = {path.resolve() for path in artifacts.generated_image_paths}
        for relative_path, content in files.items():
            target_path = workspace_dir / relative_path
            if target_path.resolve() in protected_image_paths:
                print(f"[ORCHESTRATOR] Preserved generated image file (skip overwrite): {target_path}")
                continue
            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(content, encoding="utf-8")
            written_paths.append(target_path)
            print(f"[ORCHESTRATOR] Wrote file: {target_path}")

        dockerfile_path = docker_dir / "Dockerfile"
        dockerfile_path.write_text(self._dockerfile_content(), encoding="utf-8")
        print(f"[ORCHESTRATOR] Wrote file: {dockerfile_path}")

        print("[ORCHESTRATOR] Stage 10: DevOpsAgent deployment handoff")
        written_files = [str(path) for path in written_paths]
        self._log_stage_inputs(
            "DevOpsAgent",
            qa_feedback=qa_feedback,
            generated_files=artifacts.generated_files,
        )
        devops_input = self._artifact_payload(
            qa_feedback=qa_feedback,
            generated_files=artifacts.generated_files,
            written_files=written_files,
            docker_artifact={
                "path": str(dockerfile_path),
                "contents": self._dockerfile_content(),
            },
        )
        deployment_instructions = self.devops.run(devops_input)
        self._log_artifact("DevOpsAgent", "deployment_instructions", deployment_instructions)

        written_paths_summary = "\n".join(f"- {path}" for path in written_paths)
        generated_images_summary = "\n".join(f"- {path}" for path in artifacts.generated_image_paths)
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

        for iteration in range(1, 4):
            print(f"[ORCHESTRATOR] ProductManager iteration {iteration}/3")
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
            "[ORCHESTRATOR] Reached 3 ProductManager iterations without "
            "REQUIREMENTS_READY. Proceeding with latest output."
        )
        return latest_output

    def _run_qa_revision_loop(self, artifacts: _PipelineArtifacts) -> tuple[str, str]:
        generated_files = artifacts.generated_files
        qa_feedback = ""

        for iteration in range(1, 4):
            print(f"[ORCHESTRATOR] QA iteration {iteration}/3")
            deterministic_feedback, deterministic_has_failures = self._build_deterministic_qa_feedback(
                site_structure=artifacts.site_structure,
                generated_files=generated_files,
            )
            self._log_stage_inputs(
                f"QAAgent iteration {iteration}",
                architecture_spec=artifacts.architecture_spec,
                site_structure=artifacts.site_structure,
                generated_files=generated_files,
            )
            qa_input = self._artifact_payload(
                architecture_spec=artifacts.architecture_spec,
                site_structure=artifacts.site_structure,
                generated_files=generated_files,
                deterministic_validation=deterministic_feedback,
            )
            qa_feedback = self.qa.run(qa_input)
            qa_feedback = self._merge_qa_feedback(
                llm_feedback=qa_feedback,
                deterministic_feedback=deterministic_feedback,
                force_needs_changes=deterministic_has_failures,
            )
            self._log_stage_output("QAAgent", qa_feedback)
            qa_decision = self._extract_qa_decision(qa_feedback)
            print(f"[ORCHESTRATOR] QA decision on iteration {iteration}: {qa_decision}")

            if qa_decision != "NEEDS_CHANGES":
                return generated_files, qa_feedback

            if iteration < 3:
                print("[ORCHESTRATOR] Sending QA feedback back to DeveloperAgent for revision")
                revision_input = self._artifact_payload(
                    architecture_spec=artifacts.architecture_spec,
                    design_spec=artifacts.design_spec,
                    site_structure=artifacts.site_structure,
                    development_tasks=artifacts.development_tasks,
                    generated_files=generated_files,
                    qa_feedback=self._strip_qa_decision(qa_feedback),
                    revision_instruction=(
                        "Revise the project to address all QA issues while preserving "
                        "the provided site_structure content and return the complete "
                        "updated JSON with all files."
                    ),
                )
                generated_files = self.developer.run(revision_input)
                self._log_artifact("DeveloperAgentRevision", "generated_files", generated_files)
                generated_files, generated_files_error = self._validate_generated_files_output(
                    stage_name="DeveloperAgentRevision",
                    stage_output=generated_files,
                )
                if generated_files_error:
                    return generated_files, generated_files_error
                self._log_artifact("DeveloperAgentRevisionValidated", "generated_files", generated_files)

        print(
            "[ORCHESTRATOR] WARNING: QA returned NEEDS_CHANGES after 3 iterations. "
            "Proceeding with deployment anyway."
        )
        return generated_files, qa_feedback

    def _generate_design_images(self, design_spec: str) -> list[Path]:
        workspace_dir = Path("workspace")
        assets_dir = workspace_dir / "assets" / "images"
        assets_dir.mkdir(parents=True, exist_ok=True)
        image_paths: list[Path] = []

        try:
            payload = json.loads(design_spec)
        except json.JSONDecodeError:
            print("[ORCHESTRATOR] WARNING: Invalid design specification JSON. Skipping image generation.")
            return image_paths

        images = self._extract_design_images(payload)
        if not images:
            print("[ORCHESTRATOR] WARNING: No supported image definitions found in design spec. Skipping image generation.")
            return image_paths

        for index, image_def in enumerate(images, start=1):
            if not isinstance(image_def, dict):
                print(f"[ORCHESTRATOR] WARNING: Invalid image definition at index {index}. Skipping.")
                continue

            prompt = image_def.get("prompt")
            if not isinstance(prompt, str) or not prompt.strip():
                print(f"[ORCHESTRATOR] WARNING: Missing image prompt at index {index}. Skipping.")
                continue

            target_path = self._workspace_image_path(assets_dir, image_def.get("filename"), index)
            if target_path is None:
                print(f"[ORCHESTRATOR] WARNING: Invalid image filename at index {index}. Skipping.")
                continue

            try:
                print(f"[ORCHESTRATOR] Generating image {index}: {target_path}")
                image_bytes = self.image_generator.generate_image(prompt.strip())
                target_path.write_bytes(image_bytes)
                image_paths.append(target_path)
                print(f"[ORCHESTRATOR] Image generated: {target_path}")
            except Exception as exc:  # noqa: BLE001
                print(f"[ORCHESTRATOR] WARNING: Failed to generate {target_path}: {exc}")

        return image_paths

    @staticmethod
    def _extract_design_images(payload: object) -> list[dict[str, object]]:
        if not isinstance(payload, dict):
            return []

        candidate_paths = [
            payload.get("images"),
            payload.get("design", {}).get("images") if isinstance(payload.get("design"), dict) else None,
            payload.get("design_system", {}).get("images")
            if isinstance(payload.get("design_system"), dict)
            else None,
        ]
        for candidate in candidate_paths:
            if isinstance(candidate, list):
                return [item for item in candidate if isinstance(item, dict)]
        return []

    @staticmethod
    def _workspace_image_path(assets_dir: Path, raw_filename: object, index: int) -> Path | None:
        if not isinstance(raw_filename, str) or not raw_filename.strip():
            return assets_dir / f"generated_{index}.png"

        relative_name = Path(raw_filename.strip())
        if relative_name.is_absolute() or ".." in relative_name.parts:
            return None

        target_path = assets_dir / relative_name
        target_path.parent.mkdir(parents=True, exist_ok=True)
        return target_path

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
    def _validate_generated_files_output(
        stage_name: str,
        stage_output: str,
    ) -> tuple[str, str | None]:
        return Orchestrator._validate_stage_output(
            stage_name=stage_name,
            stage_output=stage_output,
            schema=GENERATED_FILES_SCHEMA,
        )

    @staticmethod
    def _artifact_payload(**artifacts: object) -> str:
        payload = {
            name: Orchestrator._artifact_to_json_value(value)
            for name, value in artifacts.items()
        }
        return json.dumps(payload, indent=2)

    @staticmethod
    def _artifact_to_json_value(value: object) -> object:
        if isinstance(value, str):
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, list):
            return [Orchestrator._artifact_to_json_value(item) for item in value]
        if isinstance(value, dict):
            return {
                str(key): Orchestrator._artifact_to_json_value(item)
                for key, item in value.items()
            }
        return value

    @staticmethod
    def _log_stage_inputs(stage_name: str, **artifacts: object) -> None:
        print(f"[ORCHESTRATOR] {stage_name} input artifacts:")
        for artifact_name, artifact_value in artifacts.items():
            summary = Orchestrator._describe_artifact(artifact_value)
            print(f"[ORCHESTRATOR] - {artifact_name}: {summary}")

    @staticmethod
    def _log_artifact(stage_name: str, artifact_name: str, artifact_value: object) -> None:
        print(f"[ORCHESTRATOR] {stage_name} produced artifact '{artifact_name}'.")
        print(f"[ORCHESTRATOR] {artifact_name} summary: {Orchestrator._describe_artifact(artifact_value)}")
        if isinstance(artifact_value, str):
            Orchestrator._log_stage_output(f"{stage_name}.{artifact_name}", artifact_value)

    @staticmethod
    def _log_generated_images(image_paths: list[Path]) -> None:
        print(f"[ORCHESTRATOR] Generated image count: {len(image_paths)}")
        for image_path in image_paths:
            print(f"[ORCHESTRATOR] - generated_image: {image_path}")

    @staticmethod
    def _describe_artifact(artifact_value: object) -> str:
        if isinstance(artifact_value, str):
            try:
                parsed = json.loads(artifact_value)
            except json.JSONDecodeError:
                lines = artifact_value.count("\n") + 1 if artifact_value else 0
                return f"text, {len(artifact_value)} chars, {lines} lines"
            return Orchestrator._describe_json_value(parsed)
        if isinstance(artifact_value, Path):
            return f"path '{artifact_value}'"
        if isinstance(artifact_value, list):
            return f"list[{len(artifact_value)}]"
        if isinstance(artifact_value, dict):
            return Orchestrator._describe_json_value(artifact_value)
        return type(artifact_value).__name__

    @staticmethod
    def _describe_json_value(value: object) -> str:
        if isinstance(value, dict):
            keys = ", ".join(list(value.keys())[:5])
            if len(value) > 5:
                keys += ", ..."
            return f"json object with {len(value)} keys ({keys})"
        if isinstance(value, list):
            return f"json array with {len(value)} items"
        return type(value).__name__

    @classmethod
    def _build_deterministic_qa_feedback(
        cls,
        site_structure: str,
        generated_files: str,
    ) -> tuple[str, bool]:
        findings = cls._deterministic_site_structure_findings(
            site_structure=site_structure,
            generated_files=generated_files,
        )
        if findings:
            lines = ["Deterministic validation findings:"]
            lines.extend(f"- {finding}" for finding in findings)
            return "\n".join(lines), True

        return (
            "Deterministic validation findings:\n"
            "- All site_structure pages were matched to generated HTML output.\n"
            "- All required headings, body copy, and supporting points were found in rendered HTML.\n"
            "- No placeholder text was detected in generated HTML content.",
            False,
        )

    @classmethod
    def _deterministic_site_structure_findings(
        cls,
        site_structure: str,
        generated_files: str,
    ) -> list[str]:
        findings: list[str] = []
        files = cls._parse_project_files(generated_files)
        if files is None:
            return ["Developer output is not valid JSON with a string-only files map."]

        try:
            content_payload = json.loads(site_structure)
        except json.JSONDecodeError as exc:
            return [f"Site structure could not be parsed for deterministic validation: {exc.msg}."]

        try:
            validate_schema(content_payload, SITE_STRUCTURE_SCHEMA)
        except SchemaValidationError as exc:
            return [f"Site structure could not be validated for deterministic validation: {exc}."]

        html_documents = cls._extract_html_documents(files)
        if not html_documents:
            return ["No HTML files were generated, so site_structure content cannot be verified."]

        placeholder_terms = ("lorem ipsum", "placeholder", "tbd", "coming soon")
        for document in html_documents.values():
            normalized_text = cls._normalize_match_text(document.visible_text)
            for term in placeholder_terms:
                if cls._normalize_match_text(term) in normalized_text:
                    findings.append(
                        f"{document.path} contains placeholder text ('{term}') in rendered content."
                    )
                    break

        for page in content_payload["site_structure"]["pages"]:
            matched_document = cls._match_page_to_html_document(page, html_documents)
            if matched_document is None:
                findings.append(
                    f"Page '{page['slug']}' titled '{page['title']}' was not found in any generated HTML file."
                )
                continue

            searchable_text = " ".join([matched_document.title_text, matched_document.visible_text])
            if not cls._contains_normalized_text(searchable_text, page["title"]):
                findings.append(
                    f"Page '{page['slug']}' is missing the page title '{page['title']}' in {matched_document.path}."
                )

            for section in page["sections"]:
                if not cls._contains_normalized_text(matched_document.visible_text, section["heading"]):
                    findings.append(
                        f"Page '{page['slug']}' is missing section heading '{section['heading']}' in {matched_document.path}."
                    )
                if not cls._contains_normalized_text(matched_document.visible_text, section["text"]):
                    findings.append(
                        f"Page '{page['slug']}' is missing section body text for '{section['heading']}' in {matched_document.path}."
                    )
                for point in section["supporting_points"]:
                    if not cls._contains_normalized_text(matched_document.visible_text, point):
                        findings.append(
                            f"Page '{page['slug']}' is missing supporting point '{point}' in {matched_document.path}."
                        )

        return findings

    @staticmethod
    def _extract_html_documents(files: dict[str, str]) -> dict[str, _RenderedHTMLDocument]:
        html_documents: dict[str, _RenderedHTMLDocument] = {}
        for path, content in files.items():
            if not path.endswith(".html"):
                continue
            parser = _HTMLTextExtractor()
            parser.feed(content)
            html_documents[path] = _RenderedHTMLDocument(
                path=path,
                title_text=parser.title_text,
                visible_text=parser.visible_text,
            )
        return html_documents

    @classmethod
    def _match_page_to_html_document(
        cls,
        page: dict[str, object],
        html_documents: dict[str, _RenderedHTMLDocument],
    ) -> _RenderedHTMLDocument | None:
        slug = page.get("slug", "")
        for candidate_path in cls._candidate_paths_for_slug(slug):
            document = html_documents.get(candidate_path)
            if document is not None:
                return document

        page_title = cls._normalize_match_text(str(page.get("title", "")))
        sections = page.get("sections", [])
        first_heading = ""
        if isinstance(sections, list) and sections:
            first_section = sections[0]
            if isinstance(first_section, dict):
                first_heading = cls._normalize_match_text(str(first_section.get("heading", "")))

        best_document: _RenderedHTMLDocument | None = None
        best_score = 0
        slug_key = str(slug).strip("/").lower()

        for path, document in html_documents.items():
            score = 0
            normalized_path = path.lower()
            normalized_title = cls._normalize_match_text(document.title_text)
            normalized_text = cls._normalize_match_text(document.visible_text)
            if slug_key and slug_key in normalized_path:
                score += 1
            if page_title and page_title in normalized_title:
                score += 5
            if page_title and page_title in normalized_text:
                score += 4
            if first_heading and first_heading in normalized_text:
                score += 3
            if score > best_score:
                best_score = score
                best_document = document

        if best_score == 0:
            return None
        return best_document

    @staticmethod
    def _candidate_paths_for_slug(slug: str) -> list[str]:
        normalized_slug = slug.strip()
        if normalized_slug in {"", "/"}:
            return ["index.html"]

        slug_path = normalized_slug.strip("/")
        return [
            f"{slug_path}.html",
            f"{slug_path}/index.html",
        ]

    @staticmethod
    def _contains_normalized_text(haystack: str, needle: str) -> bool:
        normalized_haystack = Orchestrator._normalize_match_text(haystack)
        normalized_needle = Orchestrator._normalize_match_text(needle)
        if not normalized_needle:
            return True
        return normalized_needle in normalized_haystack

    @staticmethod
    def _normalize_match_text(value: str) -> str:
        lowered = value.lower()
        alphanumeric = re.sub(r"[^a-z0-9]+", " ", lowered)
        return re.sub(r"\s+", " ", alphanumeric).strip()

    @staticmethod
    def _validate_stage_output(
        stage_name: str,
        stage_output: str,
        schema: dict[str, object],
    ) -> tuple[str, str | None]:
        try:
            parsed = json.loads(stage_output)
        except json.JSONDecodeError as exc:
            print(f"[ORCHESTRATOR] ERROR: {stage_name} returned invalid JSON.")
            return (
                "",
                (
                    f"ERROR: {stage_name} returned invalid structured output.\n"
                    "Validation details:\n"
                    f"{exc.msg}\n"
                    "Pipeline aborted before downstream stages."
                ),
            )

        try:
            validate_schema(parsed, schema)
        except SchemaValidationError as exc:
            print(f"[ORCHESTRATOR] ERROR: {stage_name} failed JSON schema validation.")
            return (
                "",
                (
                    f"ERROR: {stage_name} returned invalid structured output.\n"
                    "Validation details:\n"
                    f"{exc}\n"
                    "Pipeline aborted before downstream stages."
                ),
            )
        return json.dumps(parsed, indent=2), None

    @staticmethod
    def _extract_requirements_document(product_manager_output: str) -> str:
        _, _, tail = product_manager_output.partition("REQUIREMENTS_READY")
        extracted = tail.strip()
        return extracted or product_manager_output.strip()

    @staticmethod
    def _merge_qa_feedback(
        llm_feedback: str,
        deterministic_feedback: str,
        force_needs_changes: bool,
    ) -> str:
        llm_body = Orchestrator._strip_qa_decision(llm_feedback).strip()
        decision = "NEEDS_CHANGES" if force_needs_changes else Orchestrator._extract_qa_decision(llm_feedback)

        parts = [deterministic_feedback.strip()]
        if llm_body:
            parts.append("LLM QA feedback:\n" + llm_body)
        return "\n\n".join(parts).strip() + f"\n{decision}"

    @staticmethod
    def _strip_qa_decision(qa_feedback: str) -> str:
        lines = qa_feedback.rstrip().splitlines()
        if lines and lines[-1].strip() in {"APPROVED", "NEEDS_CHANGES"}:
            return "\n".join(lines[:-1]).rstrip()
        return qa_feedback.rstrip()

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
