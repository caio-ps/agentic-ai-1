import json
import re

from src.core.base_agent import BaseAgent
from src.core.image_generator import ImageGenerator
from src.core.llm import LLM


class DesignerAgent(BaseAgent):
    def __init__(
        self,
        llm: LLM | None = None,
        image_generator: ImageGenerator | None = None,
    ) -> None:
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
                "    - Interaction behaviors (hover, scroll, animations)\n\n"
                "Output JSON only using this format:\n"
                "{\n"
                "  \"design\": {\n"
                "      \"layout\": \"...\",\n"
                "      \"colors\": \"...\",\n"
                "      \"typography\": \"...\",\n"
                "      \"images\": []\n"
                "  }\n"
                "}\n\n"
                "Do NOT generate HTML.\n"
                "Do not embed base64.\n"
                "Keep output structured."
            ),
            llm=llm,
        )
        self.image_generator = image_generator or ImageGenerator()
        self.generated_images: dict[str, bytes] = {}

    def run(self, user_input: str) -> str:
        print(f"[{self.role_name.upper()}] Starting execution...")
        print(f"[{self.role_name.upper()}] Input length: {len(user_input)} characters")

        base_design = self._generate_base_design(user_input)
        sections = self._extract_major_sections(user_input)

        images: list[dict[str, str]] = []
        for index, section in enumerate(sections, start=1):
            prompt = self._build_image_prompt(section, user_input)
            filename = self._build_filename(section, index)
            self.generated_images[filename] = self.image_generator.generate_image(prompt)
            images.append(
                {
                    "filename": filename,
                    "prompt": prompt,
                    "placement": section,
                }
            )

        design_payload = {
            "design": {
                "layout": base_design.get("layout", "Responsive section-based layout"),
                "colors": base_design.get("colors", "Modern high-contrast palette"),
                "typography": base_design.get("typography", "Google Fonts pairing"),
                "images": images,
            }
        }

        print(f"[{self.role_name.upper()}] Execution completed.")
        return json.dumps(design_payload, ensure_ascii=False, indent=2)

    def _generate_base_design(self, content_plan: str) -> dict[str, str]:
        base_prompt = (
            "Based on the content plan, return JSON only with this shape: "
            "{\"layout\":\"...\",\"colors\":\"...\",\"typography\":\"...\"}. "
            "Keep each field concise."
        )
        raw = self.llm.generate(system_prompt=base_prompt, user_input=content_plan)
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                return {
                    "layout": str(parsed.get("layout", "")),
                    "colors": str(parsed.get("colors", "")),
                    "typography": str(parsed.get("typography", "")),
                }
        except json.JSONDecodeError:
            pass
        return {}

    def _extract_major_sections(self, content_plan: str) -> list[str]:
        topic_prompt = (
            "Extract 3 to 5 major website sections from the content plan. "
            "Return one section name per line and no extra text."
        )
        raw = self.llm.generate(system_prompt=topic_prompt, user_input=content_plan)
        sections = [line.strip("- ").strip() for line in raw.splitlines() if line.strip()]

        unique_sections: list[str] = []
        seen: set[str] = set()
        for section in sections:
            normalized = section.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            unique_sections.append(section)

        if len(unique_sections) < 3:
            fallback = ["Hero", "Features", "Testimonials", "Pricing", "Contact"]
            for item in fallback:
                if item.lower() not in seen:
                    unique_sections.append(item)
                if len(unique_sections) >= 3:
                    break
        return unique_sections[:5]

    def _build_image_prompt(self, section: str, content_plan: str) -> str:
        prompt_builder = (
            "Write one high-quality image generation prompt for the given website "
            "section. Return only the prompt text.\n\n"
            f"Section: {section}\n\n"
            f"Content plan context:\n{content_plan}"
        )
        return self.llm.generate(
            system_prompt="You create concise, production-ready prompts for realistic website imagery.",
            user_input=prompt_builder,
        ).strip()

    @staticmethod
    def _build_filename(section: str, index: int) -> str:
        slug = re.sub(r"[^a-z0-9]+", "_", section.lower()).strip("_")
        if not slug:
            slug = f"section_{index}"
        return f"{slug}.png"
