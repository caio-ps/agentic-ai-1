from src.core.base_agent import BaseAgent
from src.core.llm import LLM
from src.core.web_search import WebSearchService


class ResearcherAgent(BaseAgent):
    def __init__(
        self,
        llm: LLM | None = None,
        web_search_service: WebSearchService | None = None,
    ) -> None:
        super().__init__(
            role_name="researcher",
            system_prompt=(
                "You are a strategic web research specialist.\n\n"
                "Use provided real web search findings to produce high-quality "
                "strategic research.\n"
                "Analyze competitor websites and extract:\n"
                "- Common page structure\n"
                "- Messaging patterns\n"
                "- Hero section patterns\n"
                "- Call-to-action patterns\n"
                "Identify industry-specific keywords.\n"
                "Identify differentiation opportunities.\n"
                "Provide SEO keyword clusters.\n"
                "Provide examples of strong headlines from market leaders.\n\n"
                "Return JSON only in this exact structure:\n"
                "{\n"
                "  \"market_patterns\": [...],\n"
                "  \"competitor_analysis\": [...],\n"
                "  \"seo_keywords\": [...],\n"
                "  \"headline_examples\": [...],\n"
                "  \"differentiation_opportunities\": [...]\n"
                "}\n\n"
                "Do not generate HTML.\n"
                "Do not include markdown.\n"
                "Use concrete, specific findings and include source URLs within "
                "relevant items."
            ),
            llm=llm,
        )
        self.web_search_service = web_search_service or WebSearchService()

    def run(self, user_input: str) -> str:
        print(f"[{self.role_name.upper()}] Starting execution...")
        print(f"[{self.role_name.upper()}] Input length: {len(user_input)} characters")

        personas_and_pain_points = self._extract_personas_and_pain_points(user_input)
        search_queries = self._build_search_queries(personas_and_pain_points)

        aggregated_results_parts: list[str] = []
        for index, query in enumerate(search_queries, start=1):
            print(f"[{self.role_name.upper()}] Web search {index}/{len(search_queries)}: {query}")
            result_text = self.web_search_service.search(query)
            aggregated_results_parts.append(f"Query: {query}\n{result_text}")

        aggregated_results = "\n\n".join(aggregated_results_parts)
        dossier_input = (
            "Structured website requirements:\n"
            f"{user_input}\n\n"
            "Extracted personas and pain points:\n"
            f"{personas_and_pain_points}\n\n"
            "Web search findings:\n"
            f"{aggregated_results}\n\n"
            "Produce strategic research JSON using only these real findings."
        )
        response = self.llm.generate(system_prompt=self.system_prompt, user_input=dossier_input)
        print(f"[{self.role_name.upper()}] Execution completed.")
        return response

    def _extract_personas_and_pain_points(self, requirements: str) -> str:
        extraction_prompt = (
            "Extract audience personas and pain points from the requirements.\n"
            "Return JSON only with this shape:\n"
            "{\n"
            "  \"personas\": [\"...\"],\n"
            "  \"pain_points\": [\"...\"]\n"
            "}\n"
            "Use up to 3 personas and up to 5 pain points."
        )
        return self.llm.generate(system_prompt=extraction_prompt, user_input=requirements)

    def _build_search_queries(self, personas_and_pain_points: str) -> list[str]:
        query_prompt = (
            "Based on the personas and pain points, generate 5 high-impact web "
            "search queries for strategic website research.\n"
            "Queries must cover:\n"
            "- competitor website examples\n"
            "- hero/messaging/CTA patterns\n"
            "- industry keywords and SEO terms\n"
            "- differentiation strategies\n"
            "Return one query per line and no extra text."
        )
        raw_queries = self.llm.generate(
            system_prompt=query_prompt,
            user_input=personas_and_pain_points,
        )
        queries = [line.strip("- ").strip() for line in raw_queries.splitlines() if line.strip()]

        unique_queries: list[str] = []
        seen: set[str] = set()
        for query in queries:
            normalized = query.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            unique_queries.append(query)

        fallback_queries = [
            "top industry competitor website homepage examples",
            "best website hero section messaging patterns",
            "high-converting website call to action patterns",
            "industry SEO keyword clusters",
            "website differentiation strategy examples",
        ]
        for query in fallback_queries:
            if len(unique_queries) >= 5:
                break
            if query.lower() not in seen:
                unique_queries.append(query)
                seen.add(query.lower())

        return unique_queries[:5]
