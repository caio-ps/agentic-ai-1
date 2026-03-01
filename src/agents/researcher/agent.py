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
                "You are a web research specialist.\n\n"
                "Your job is to:\n"
                "- Receive structured website requirements.\n"
                "- Identify relevant themes, industry standards, competitors, and "
                "best practices.\n"
                "- Perform real internet research.\n"
                "- Produce a structured research dossier including:\n"
                "    - Market references\n"
                "    - Common content patterns\n"
                "    - Recommended sections\n"
                "    - SEO considerations\n"
                "    - Suggested messaging angles\n"
                "- Summarize findings clearly and objectively.\n"
                "- Provide references with source names and URLs.\n"
                "- Do not design or generate HTML.\n"
                "- Focus only on research and insights.\n"
                "- Keep output concise and structured."
            ),
            llm=llm,
        )
        self.web_search_service = web_search_service or WebSearchService()

    def run(self, user_input: str) -> str:
        print(f"[{self.role_name.upper()}] Starting execution...")
        print(f"[{self.role_name.upper()}] Input length: {len(user_input)} characters")

        topics = self._extract_key_topics(user_input)
        search_queries = self._build_search_queries(topics)

        aggregated_results_parts: list[str] = []
        for index, query in enumerate(search_queries, start=1):
            print(f"[{self.role_name.upper()}] Web search {index}/{len(search_queries)}: {query}")
            result_text = self.web_search_service.search(query)
            aggregated_results_parts.append(f"Query: {query}\n{result_text}")

        aggregated_results = "\n\n".join(aggregated_results_parts)
        dossier_input = (
            "Structured website requirements:\n"
            f"{user_input}\n\n"
            "Web search findings:\n"
            f"{aggregated_results}\n\n"
            "Create a structured research dossier based only on the findings above. "
            "Include references with URLs."
        )
        response = self.llm.generate(system_prompt=self.system_prompt, user_input=dossier_input)
        print(f"[{self.role_name.upper()}] Execution completed.")
        return response

    def _extract_key_topics(self, requirements: str) -> list[str]:
        topic_prompt = (
            "Extract up to 5 high-impact web research topics from the requirements. "
            "Return one topic per line and no extra text."
        )
        raw_topics = self.llm.generate(system_prompt=topic_prompt, user_input=requirements)
        topics = [line.strip("- ").strip() for line in raw_topics.splitlines() if line.strip()]
        unique_topics: list[str] = []
        seen: set[str] = set()
        for topic in topics:
            normalized = topic.lower()
            if normalized in seen:
                continue
            seen.add(normalized)
            unique_topics.append(topic)
        return unique_topics

    def _build_search_queries(self, topics: list[str]) -> list[str]:
        selected_topics = topics[:5]
        queries = [f"{topic} website best practices" for topic in selected_topics]
        if len(queries) < 3:
            fallback_queries = [
                "website information architecture best practices",
                "responsive web design accessibility checklist",
                "landing page content structure best practices",
            ]
            for query in fallback_queries:
                if query not in queries:
                    queries.append(query)
                if len(queries) >= 3:
                    break
        return queries[:5]
