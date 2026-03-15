import json
import logging
import re
from typing import Any

from .llm import LLM
from .llm import LLMProtocol
from .schema_validator import SchemaValidationError
from .schema_validator import validate_schema

logger = logging.getLogger(__name__)


def sanitize_llm_output(text: str) -> str:
    cleaned = re.sub(r"```json\s*", "", text, flags=re.IGNORECASE)
    cleaned = cleaned.replace("```", "").strip()
    cleaned = _remove_trailing_commas(cleaned)
    extracted = _extract_first_json_value(cleaned)
    return extracted.strip() if extracted is not None else cleaned.strip()


def _sanitize_json_response(response: str) -> str:
    return sanitize_llm_output(response)


def attempt_schema_repair(data: Any, schema: dict[str, Any]) -> Any:
    if not isinstance(schema, dict):
        return data

    schema_type = _resolve_schema_type(schema)

    if schema_type == "array":
        item_schema = schema.get("items", {})
        if isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list):
            data = [data]

        if isinstance(data, list):
            return [attempt_schema_repair(item, item_schema) for item in data]
        return data

    if schema_type == "object":
        properties = schema.get("properties", {})
        if isinstance(data, str):
            data = _repair_object_from_string(data, properties)
        elif isinstance(data, list) and len(data) == 1 and isinstance(data[0], dict):
            data = data[0]

        if isinstance(data, dict):
            repaired: dict[str, Any] = {}
            for key, value in data.items():
                property_schema = properties.get(key)
                repaired[key] = attempt_schema_repair(value, property_schema) if property_schema else value
            return repaired
        return data

    if schema_type == "string":
        if isinstance(data, dict):
            extracted = _extract_meaningful_string(data)
            return extracted if extracted is not None else json.dumps(data, sort_keys=True)
        if isinstance(data, list) and data:
            if len(data) == 1:
                return attempt_schema_repair(data[0], {"type": "string"})
            joined = ", ".join(
                str(item).strip()
                for item in data
                if str(item).strip()
            )
            return joined
        if data is None:
            return ""
        return data if isinstance(data, str) else str(data)

    if isinstance(data, dict):
        properties = schema.get("properties", {})
        repaired: dict[str, Any] = {}
        for key, value in data.items():
            property_schema = properties.get(key)
            repaired[key] = attempt_schema_repair(value, property_schema) if property_schema else value
        return repaired

    if isinstance(data, list) and "items" in schema:
        return [attempt_schema_repair(item, schema["items"]) for item in data]

    return data


def _remove_trailing_commas(text: str) -> str:
    previous = None
    cleaned = text
    while cleaned != previous:
        previous = cleaned
        cleaned = re.sub(r",\s*([}\]])", r"\1", cleaned)
    return cleaned


def _extract_first_json_value(text: str) -> str | None:
    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char not in "{[":
            continue
        candidate = text[index:]
        try:
            _, end = decoder.raw_decode(candidate)
        except json.JSONDecodeError:
            continue
        return candidate[:end]
    return None


def _resolve_schema_type(schema: dict[str, Any]) -> str | None:
    schema_type = schema.get("type")
    if isinstance(schema_type, str):
        return schema_type
    if isinstance(schema_type, list):
        for candidate in ("object", "array", "string", "number", "integer", "boolean"):
            if candidate in schema_type:
                return candidate
    if "properties" in schema:
        return "object"
    if "items" in schema:
        return "array"
    return None


def _extract_meaningful_string(value: dict[str, Any]) -> str | None:
    preferred_keys = (
        "name",
        "platform",
        "type",
        "title",
        "label",
        "value",
        "directory",
        "key_features",
    )
    for key in preferred_keys:
        candidate = value.get(key)
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()

    for candidate in value.values():
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
        if isinstance(candidate, dict):
            nested = _extract_meaningful_string(candidate)
            if nested:
                return nested
        if isinstance(candidate, list):
            for item in candidate:
                if isinstance(item, str) and item.strip():
                    return item.strip()
                if isinstance(item, dict):
                    nested = _extract_meaningful_string(item)
                    if nested:
                        return nested

    return None


def _repair_object_from_string(value: str, properties: dict[str, Any]) -> dict[str, Any]:
    if "value" in properties or not properties:
        return {"value": value}

    for key in ("name", "platform", "type", "title", "label"):
        if key in properties:
            return {key: value}

    if len(properties) == 1:
        only_key = next(iter(properties))
        return {only_key: value}

    return {"value": value}


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
        response = self._validate_output(response, user_input=user_input)
        print(f"[{self.role_name.upper()}] Execution completed.")
        return response

    def _validate_output(self, response: str, user_input: str, retry_allowed: bool = True) -> str:
        if self.output_schema is None or self.output_format is None:
            return response

        if self.output_format == "json":
            cleaned_response = sanitize_llm_output(response)
            if cleaned_response != response.strip():
                logger.info("[%s] Sanitized LLM JSON output before parsing.", self.role_name.upper())
            try:
                data = json.loads(cleaned_response)
            except json.JSONDecodeError as exc:
                logger.error("[%s] Returned invalid JSON output:\n%s", self.role_name.upper(), response)
                logger.error("[%s] Sanitized JSON output:\n%s", self.role_name.upper(), cleaned_response)
                if retry_allowed:
                    return self._retry_with_corrected_json(user_input=user_input, invalid_response=response)
                raise ValueError(f"{self.role_name} returned invalid JSON output: {exc.msg}") from exc

            repaired_data = attempt_schema_repair(data, self.output_schema)
            if repaired_data != data:
                logger.info("[%s] Repaired JSON output to better match schema.", self.role_name.upper())
            data = repaired_data
        elif self.output_format == "text":
            data = response
        else:
            raise ValueError(f"Unsupported output format '{self.output_format}' for {self.role_name}.")

        try:
            validate_schema(data, self.output_schema)
        except SchemaValidationError as exc:
            logger.error("[%s] Output failed schema validation.", self.role_name.upper())
            logger.error("[%s] Original response:\n%s", self.role_name.upper(), response)
            if self.output_format == "json":
                logger.error("[%s] Sanitized response:\n%s", self.role_name.upper(), cleaned_response)
                logger.error(
                    "[%s] Repaired parsed data:\n%s",
                    self.role_name.upper(),
                    json.dumps(data, indent=2, ensure_ascii=True),
                )
                if retry_allowed:
                    return self._retry_with_corrected_json(user_input=user_input, invalid_response=response)
            raise ValueError(f"{self.role_name} returned output that failed schema validation: {exc}") from exc

        if self.output_format == "json":
            return json.dumps(data, indent=2)
        return response

    def _retry_with_corrected_json(self, user_input: str, invalid_response: str) -> str:
        logger.warning("[%s] Retrying once after JSON/schema failure.", self.role_name.upper())
        correction_instruction = (
            f"{user_input}\n\n"
            "The previous output failed schema validation. Return corrected JSON matching the schema exactly. "
            "Return ONLY JSON.\n\n"
            "Previous invalid output:\n"
            f"{invalid_response}\n\n"
            "Target JSON schema:\n"
            f"{json.dumps(self.output_schema, indent=2, ensure_ascii=True)}"
        )
        corrected_response = self.llm.generate(
            system_prompt=self.system_prompt,
            user_input=correction_instruction,
            agent_name=self.role_name,
        )
        return self._validate_output(corrected_response, user_input=user_input, retry_allowed=False)
