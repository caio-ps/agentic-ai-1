import json

from src.core.base_agent import BaseAgent
from src.core.base_agent import sanitize_llm_output
from src.core.llm import LLMProtocol
from src.core.schemas import RESEARCH_OUTPUT_SCHEMA
from src.core.web_search import WebSearchService


class ResearcherAgent(BaseAgent):
    def __init__(
        self,
        llm: LLMProtocol | None = None,
        web_search_service: WebSearchService | None = None,
    ) -> None:
        super().__init__(
            role_name="researcher",
            system_prompt=(
                "You are a web research specialist responsible for both strategic "
                "website research and factual domain knowledge research.\n\n"
                "Use provided real web search findings to produce two outputs:\n"
                "1. strategic_insights\n"
                "2. knowledge_base\n\n"
                "For strategic_insights, analyze:\n"
                "- competitor patterns\n"
                "- SEO keywords\n"
                "- messaging patterns\n\n"
                "For knowledge_base, gather factual information that can later be "
                "used to write website content.\n"
                "Knowledge must be topic-based, factual, and source-backed.\n"
                "Do not generate final website copy.\n"
                "Do not invent facts.\n"
                "Use only the provided findings.\n\n"
                "Return JSON only in this exact structure:\n"
                "{\n"
                "  \"strategic_insights\": {\n"
                "    \"competitor_patterns\": [\n"
                "      {\n"
                "        \"platform\": \"\",\n"
                "        \"key_features\": \"\",\n"
                "        \"website\": \"\"\n"
                "      }\n"
                "    ],\n"
                "    \"seo_keywords\": [],\n"
                "    \"messaging_patterns\": []\n"
                "  },\n"
                "  \"knowledge_base\": {\n"
                "    \"topics\": [\n"
                "      {\n"
                "        \"topic\": \"\",\n"
                "        \"summary\": \"\",\n"
                "        \"key_points\": [],\n"
                "        \"facts\": [],\n"
                "        \"sources\": []\n"
                "      }\n"
                "    ]\n"
                "  }\n"
                "}\n\n"
                "Do not generate HTML.\n"
                "Do not include markdown.\n"
                "Return ONLY raw JSON. Do not wrap the response in markdown code blocks. Do not include explanations.\n"
                "Use concrete, specific findings.\n"
                "Represent competitor_patterns as structured objects with platform, key_features, and website when available.\n"
                "Each knowledge topic must contain factual, reusable research.\n"
                "Each knowledge topic must include source URLs in the sources array."
            ),
            llm=llm,
            output_schema=RESEARCH_OUTPUT_SCHEMA,
            output_format="json",
        )
        self.web_search_service = web_search_service or WebSearchService()

    def run(self, user_input: str) -> str:
        print(f"[{self.role_name.upper()}] Starting execution...")
        print(f"[{self.role_name.upper()}] Input length: {len(user_input)} characters")

        research_scope = self._extract_research_scope(user_input)
        strategic_queries = self._build_strategic_queries(research_scope)
        knowledge_queries = self._build_knowledge_queries(research_scope)

        strategic_results_parts: list[str] = []
        for index, query in enumerate(strategic_queries, start=1):
            print(f"[{self.role_name.upper()}] Strategic web search {index}/{len(strategic_queries)}: {query}")
            result_text = self.web_search_service.search(query)
            strategic_results_parts.append(f"Query: {query}\n{result_text}")

        knowledge_results_parts: list[str] = []
        for index, query in enumerate(knowledge_queries, start=1):
            print(f"[{self.role_name.upper()}] Knowledge web search {index}/{len(knowledge_queries)}: {query}")
            result_text = self.web_search_service.search(query)
            knowledge_results_parts.append(f"Query: {query}\n{result_text}")

        strategic_results = "\n\n".join(strategic_results_parts)
        knowledge_results = "\n\n".join(knowledge_results_parts)
        dossier_input = (
            "Structured website requirements:\n"
            f"{user_input}\n\n"
            "Extracted research scope:\n"
            f"{research_scope}\n\n"
            "Strategic search findings:\n"
            f"{strategic_results}\n\n"
            "Knowledge search findings:\n"
            f"{knowledge_results}\n\n"
            "Produce the structured research JSON using only these real findings."
        )
        response = self.llm.generate(
            system_prompt=self.system_prompt,
            user_input=dossier_input,
            agent_name=self.role_name,
        )
        response = self._validate_output(response, user_input=dossier_input)
        print(f"[{self.role_name.upper()}] Execution completed.")
        return response

    def _extract_research_scope(self, requirements: str) -> str:
        extraction_prompt = (
            "Extract the research scope from the website requirements.\n"
            "Return JSON only with this shape:\n"
            "{\n"
            "  \"primary_topic\": \"...\",\n"
            "  \"personas\": [\"...\"],\n"
            "  \"pain_points\": [\"...\"],\n"
            "  \"knowledge_topics\": [\"...\"]\n"
            "}\n"
            "Use up to 3 personas, up to 5 pain points, and 4 to 6 knowledge topics.\n"
            "Knowledge topics should represent factual subjects that website content "
            "may need to explain.\n"
            "Return ONLY raw JSON. Do not wrap the response in markdown code blocks. Do not include explanations."
        )
        return self.llm.generate(
            system_prompt=extraction_prompt,
            user_input=requirements,
            agent_name=f"{self.role_name}.extract_scope",
        )

    def _build_strategic_queries(self, research_scope: str) -> list[str]:
        topic = self._primary_topic_label(research_scope)
        query_prompt = (
            "Based on the research scope, generate 5 high-impact web "
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
            user_input=research_scope,
            agent_name=f"{self.role_name}.strategic_queries",
        )
        fallback_queries = [
            f"top {topic} competitor website homepage examples",
            f"best {topic} website hero section messaging patterns",
            f"high-converting {topic} website call to action patterns",
            f"{topic} SEO keyword clusters",
            f"{topic} website differentiation strategy examples",
        ]
        return self._normalize_queries(raw_queries, fallback_queries, limit=5)

    def _build_knowledge_queries(self, research_scope: str) -> list[str]:
        topic = self._primary_topic_label(research_scope)
        query_prompt = (
            "Based on the research scope, generate 5 high-impact web search queries "
            "for factual domain knowledge research.\n"
            "Queries must cover:\n"
            "- foundational concepts\n"
            "- notable entities, examples, or categories\n"
            "- adoption, use cases, or practical relevance\n"
            "- key milestones, events, or history when relevant\n"
            "Return one query per line and no extra text."
        )
        raw_queries = self.llm.generate(
            system_prompt=query_prompt,
            user_input=research_scope,
            agent_name=f"{self.role_name}.knowledge_queries",
        )
        fallback_queries = [
            f"{topic} overview and history",
            f"how {topic} works",
            f"major {topic} examples and categories",
            f"{topic} adoption and use cases",
            f"key events and milestones in {topic}",
        ]
        return self._normalize_queries(raw_queries, fallback_queries, limit=5)

    @staticmethod
    def _normalize_queries(raw_queries: str, fallback_queries: list[str], limit: int) -> list[str]:
        queries = [line.strip("- ").strip() for line in raw_queries.splitlines() if line.strip()]

        unique_queries: list[str] = []
        seen: set[str] = set()
        for query in queries:
            normalized = query.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            unique_queries.append(query)

        for query in fallback_queries:
            if len(unique_queries) >= limit:
                break
            if query.lower() not in seen:
                unique_queries.append(query)
                seen.add(query.lower())

        return unique_queries[:limit]

    @staticmethod
    def _primary_topic_label(research_scope: str) -> str:
        try:
            payload = json.loads(sanitize_llm_output(research_scope))
        except Exception:  # noqa: BLE001
            return "industry"

        topic = payload.get("primary_topic") if isinstance(payload, dict) else None
        if not isinstance(topic, str) or not topic.strip():
            return "industry"
        return topic.strip()
