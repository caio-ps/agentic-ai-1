import json
import logging

from .llm import LLM
from .llm import LLMProtocol
from .schema_validator import SchemaValidationError
from .schema_validator import validate_schema

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents."""

    def __init__(
        self,
        role_name: str,
        system_prompt: str,
        llm: LLMProtocol | None = None,
        output_schema: dict[str, object] | None = None,
        output_format: str | None = None,
    ) -> None:
        self.role_name = role_name
        self.system_prompt = system_prompt
        self.llm = llm or LLM()
        self.output_schema = output_schema
        self.output_format = output_format

    def run(self, user_input: str) -> str:
        print(f"[{self.role_name.upper()}] Starting execution...")
        print(f"[{self.role_name.upper()}] Input length: {len(user_input)} characters")
        response = self.llm.generate(
            system_prompt=self.system_prompt,
            user_input=user_input,
            agent_name=self.role_name,
        )
        response = self._validate_output(response)
        print(f"[{self.role_name.upper()}] Execution completed.")
        return response

    def _validate_output(self, response: str) -> str:
        if self.output_schema is None or self.output_format is None:
            return response

        if self.output_format == "json":
            try:
                data = json.loads(response)
            except json.JSONDecodeError as exc:
                logger.error("[%s] Returned invalid JSON output:\n%s", self.role_name.upper(), response)
                raise ValueError(f"{self.role_name} returned invalid JSON output: {exc.msg}") from exc
        elif self.output_format == "text":
            data = response
        else:
            raise ValueError(f"Unsupported output format '{self.output_format}' for {self.role_name}.")

        try:
            validate_schema(data, self.output_schema)
        except SchemaValidationError as exc:
            logger.error("[%s] Output failed schema validation.", self.role_name.upper())
            raise ValueError(f"{self.role_name} returned output that failed schema validation: {exc}") from exc

        if self.output_format == "json":
            return json.dumps(data, indent=2)
        return response
