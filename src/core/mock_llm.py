from collections import deque
from typing import Any


class MockLLM:
    """In-memory LLM test double that never calls the OpenAI API."""

    def __init__(
        self,
        responses: list[str] | dict[str, list[str]] | None = None,
        *,
        default_responses: list[str] | None = None,
    ) -> None:
        self.calls: list[dict[str, object]] = []
        self._default_responses = deque(default_responses or [])
        self._responses_by_agent: dict[str, deque[str]] = {}

        if isinstance(responses, dict):
            self._responses_by_agent = {
                agent_name: deque(agent_responses)
                for agent_name, agent_responses in responses.items()
            }
        elif responses is not None:
            self._default_responses.extend(responses)

    def generate(
        self,
        system_prompt: str,
        user_input: str,
        tools: list[dict[str, Any]] | None = None,
        agent_name: str | None = None,
    ) -> str:
        self.calls.append(
            {
                "agent_name": agent_name,
                "system_prompt": system_prompt,
                "user_input": user_input,
                "tools": tools,
            }
        )

        if agent_name and agent_name in self._responses_by_agent:
            responses = self._responses_by_agent[agent_name]
            if responses:
                return responses.popleft()

        if self._default_responses:
            return self._default_responses.popleft()

        available_agents = sorted(self._responses_by_agent.keys())
        raise AssertionError(
            "MockLLM received more calls than configured responses. "
            f"agent_name={agent_name!r}, available_agent_queues={available_agents}"
        )
