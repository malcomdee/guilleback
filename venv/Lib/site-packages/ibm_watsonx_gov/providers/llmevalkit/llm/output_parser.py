import re
import json
import asyncio
from abc import ABC, abstractmethod
from typing import (
    Any,
    Dict,
    List,
    Optional,
    Type,
    TypeVar,
    Union,
)

import jsonschema
from pydantic import (
    BaseModel,
    create_model,
    Field,
    ValidationError as PydanticValidationError,
)

from llmevalkit.llm.base import LLMClient

T = TypeVar("T")


def json_schema_to_pydantic_model(
    schema: Dict[str, Any], model_name: str = "AutoModel"
) -> Type[BaseModel]:
    fields = {}
    required_fields = set(schema.get("required", []))

    type_mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None),
    }

    def parse_type(type_def):
        if isinstance(type_def, list):
            python_types = [type_mapping.get(t, Any) for t in type_def]
            if type(None) in python_types:
                python_types.remove(type(None))
                if len(python_types) == 1:
                    return Optional[python_types[0]]
                else:
                    return Optional[Union[tuple(python_types)]]
            else:
                return Union[tuple(python_types)]
        else:
            return type_mapping.get(type_def, Any)

    for prop_name, prop_schema in schema.get("properties", {}).items():
        field_type = parse_type(prop_schema.get("type"))
        default = ... if prop_name in required_fields else None
        description = prop_schema.get("description", None)
        field_args = {"description": description} if description else {}
        fields[prop_name] = (field_type, Field(default, **field_args))

    return create_model(model_name, **fields)


class OutputValidationError(Exception):
    """Raised when LLM output cannot be validated against the provided schema."""


class ValidatingLLMClient(LLMClient, ABC):
    """
    An LLMClient wrapper enforcing output structure via:
      - JSON Schema (dict),
      - Pydantic model (BaseModel subclass),
      - or Python built-in types (int, float, str, bool, list, dict).

    Features:
      - Injects a system-level prompt describing the required format.
      - Cleans raw responses (strips Markdown, extracts JSON).
      - Validates and parses the response.
      - Retries only invalid items (single or batch) up to `retries` times.
      - Falls back to single-item loops if no batch method is configured.
    """

    @classmethod
    @abstractmethod
    def provider_class(cls) -> Type:
        """Return the underlying SDK client class, e.g. openai.OpenAI."""

    @abstractmethod
    def _register_methods(self) -> None:
        """
        Register MethodConfig entries:
          self.set_method_config("text", ...),
          self.set_method_config("chat", ...),
          self.set_method_config("text_async", ...),
          self.set_method_config("chat_async", ...),
          optionally "batch", "batch_async".
        """

    def _make_instruction(
        self, schema: Union[Dict[str, Any], Type[BaseModel], Type]
    ) -> str:
        """Produce a clear instruction describing exactly the required output format."""
        if isinstance(schema, dict):
            schema_json = json.dumps(schema, indent=2)
            return (
                "Please output ONLY a JSON object conforming exactly to the following JSON Schema:\n"
                f"{schema_json}"
            )
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            model_schema = schema.model_json_schema()
            return (
                "Please output ONLY a JSON object conforming exactly to this Pydantic model schema:\n"
                f"{model_schema}"
            )
        if isinstance(schema, type) and schema in (int, float, str, bool, list, dict):
            # For simple types, no JSON wrapper required
            return f"Please output ONLY a value of type `{schema.__name__}`."
        raise TypeError(f"Unsupported schema type: {schema!r}")

    @staticmethod
    def _extract_json(raw: str) -> str:
        """
        Extract JSON from markdown fences or inline braces.
        Falls back to returning the entire raw string.
        """
        # Code fence (```json ... ```)
        fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
        if fence:
            return fence.group(1)
        # Inline {...}
        inline = re.search(r"(\{[\s\S]*\})", raw)
        if inline:
            return inline.group(1)
        return raw

    def _clean_raw(self, raw: str) -> str:
        """Strip extraneous markdown and whitespace."""
        cleaned = self._extract_json(raw)
        return cleaned.strip()

    def _validate(
        self, raw: str, schema: Union[Dict[str, Any], Type[BaseModel], Type]
    ) -> Any:
        """
        Clean, parse, and validate raw text against the schema/type.
        Returns the parsed object or Pydantic instance.
        Raises OutputValidationError on any failure.
        """

        cleaned = self._clean_raw(raw)
        try:
            if isinstance(schema, str):
                data = cleaned
            else:
                data = json.loads(cleaned)
        except json.JSONDecodeError:
            try:
                data = json.loads(cleaned.encode("unicode_escape").decode("utf-8"))
            except Exception as e:
                data = cleaned

        # JSON Schema validation
        if isinstance(schema, dict):
            try:
                jsonschema.validate(instance=data, schema=schema)
            except jsonschema.ValidationError as e:
                raise OutputValidationError(
                    f"JSON Schema validation error: {e.message}"
                )
            return data

        # Pydantic model validation
        if isinstance(schema, type) and issubclass(schema, BaseModel):
            try:
                return schema.model_validate(data)
            except PydanticValidationError as e:
                raise OutputValidationError(f"Pydantic validation error: {e}")

        # Built-in type enforcement
        if isinstance(schema, type) and schema in (int, float, str, bool, list, dict):
            if not isinstance(data, schema):
                raise OutputValidationError(
                    f"Type mismatch: expected {schema.__name__}, got {type(data).__name__}"
                )
            return data

        raise TypeError(f"Unsupported schema type: {schema!r}")

    def _inject_system(
        self, prompt: Union[str, List[Dict[str, Any]]], instr: str
    ) -> Union[str, List[Dict[str, Any]]]:
        """
        Combine instruction and user prompt:
        - For text: prepend the instruction.
        - For chat messages: if first role=system, append instr to it;
          otherwise insert a new system message.
        """
        if isinstance(prompt, str):
            return f"{instr}\n\n{prompt}"

        msgs = prompt.copy()
        if msgs and msgs[0].get("role") == "system":
            msgs[0]["content"] = msgs[0]["content"].rstrip() + "\n\n" + instr
        else:
            msgs.insert(0, {"role": "system", "content": instr})
        return msgs

    def generate(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        *,
        schema: Union[Dict[str, Any], Type[BaseModel], Type],
        schema_field: Optional[str] = None,
        retries: Optional[int] = 3,
        mode: Optional[str] = "text",
        **kwargs: Any,
    ) -> Any:
        """
        Synchronous single-item generation with validation + retries.
        """
        instr = self._make_instruction(schema)
        current = self._inject_system(prompt, instr)
        if schema_field:
            kwargs[schema_field] = schema
            if isinstance(schema, dict):
                new_schema = json_schema_to_pydantic_model(schema)
                kwargs[schema_field] = new_schema

        last_error: Optional[str] = None
        for _ in range(1, retries + 1):
            raw = super().generate(**{"prompt": current, "mode": mode, **kwargs})
            try:
                if isinstance(raw, str):
                    return self._validate(raw, schema)
                return raw
            except OutputValidationError as e:
                last_error = str(e)
                correction = (
                    f"The previous response did not conform: {last_error}\nPlease correct it."
                    " And remember to output ONLY the requested schema, without any additional text."
                )
                if isinstance(current, str):
                    current = (
                        f"{instr}\n\nPrevious output:\n{raw}\n\n"
                        f"{correction}\n\n{prompt}"
                    )
                else:
                    current = current + [
                        {"role": "assistant", "content": raw},
                        {"role": "user", "content": correction},
                    ]
        raise OutputValidationError(f"Failed after {retries} attempts: {last_error}")

    async def generate_async(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        *,
        schema: Union[Dict[str, Any], Type[BaseModel], Type],
        schema_field: Optional[str] = None,
        retries: Optional[int] = 3,
        mode: Optional[str] = "text_async",
        **kwargs: Any,
    ) -> Any:
        """
        Asynchronous single-item generation with validation + retries.
        """
        instr = self._make_instruction(schema)
        current = self._inject_system(prompt, instr)
        if schema_field:
            kwargs[schema_field] = schema
            if isinstance(schema, dict):
                new_schema = json_schema_to_pydantic_model(schema)
                kwargs[schema_field] = new_schema

        last_error: Optional[str] = None
        for _ in range(1, retries + 1):
            raw = await super().generate_async(
                **{"prompt": current, "mode": mode, **kwargs}
            )
            try:
                if isinstance(raw, str):
                    return self._validate(raw, schema)
                return raw
            except OutputValidationError as e:
                last_error = str(e)
                correction = (
                    f"The previous response did not conform: {last_error}\nPlease correct it."
                    " And remember to output ONLY the requested schema, without any additional text."
                )
                if isinstance(current, str):
                    current = (
                        f"{instr}\n\nPrevious output:\n{raw}\n\n"
                        f"{correction}\n\n{prompt}"
                    )
                else:
                    current = current + [
                        {"role": "assistant", "content": raw},
                        {"role": "user", "content": correction},
                    ]
        raise OutputValidationError(f"Failed after {retries} attempts: {last_error}")

    # def generate_batch(
    #     self,
    #     prompts: Union[List[str], List[List[Dict[str, Any]]]],
    #     *,
    #     schema: Union[Dict[str, Any], Type[BaseModel], Type],
    #     schema_field: Optional[str] = None,
    #     retries: Optional[int] = 3,
    #     **kwargs: Any,
    # ) -> List[Any]:
    #     """
    #     Synchronous batch generation with per-item validation + selective retries.
    #     Falls back to single-item loop if no 'batch' config is registered.
    #     """
    #     if "batch" not in self._method_configs:
    #         return [
    #             self.generate(
    #                 **{"prompt": p, "schema_field": schema_field, "schema": schema, "retries": retries, **kwargs}
    #             )
    #             for p in prompts
    #         ]

    #     cfg = self.get_method_config("batch")
    #     fn = cfg.resolve(self._client)
    #     if not schema_field:
    #         instr = self._make_instruction(schema)

    #         originals = list(prompts)
    #         batch_prompts = [self._inject_system(p, instr) for p in originals]
    #     else:
    #         batch_prompts = prompts

    #     n = len(batch_prompts)
    #     results: List[Optional[Any]] = [None] * n
    #     valid: List[bool] = [False] * n
    #     last_errs: List[Optional[str]] = [None] * n

    #     for attempt in range(1, retries + 1):
    #         call_args = {cfg.prompt_arg: batch_prompts, **kwargs}
    #         self._emit("before_generate_batch", {"args": call_args})
    #         try:
    #             raws: List[str] = fn(**call_args)
    #             raws = [self._parse_llm_response(raw) for raw in raws]
    #         except Exception as e:
    #             self._emit("error", {"phase": "generate_batch", "error": str(e)})
    #             raise
    #         self._emit("after_generate_batch", {"responses": raws})

    #         for i, raw in enumerate(raws):
    #             if valid[i]:
    #                 continue
    #             try:
    #                 results[i] = self._validate(raw, schema)
    #                 valid[i] = True
    #             except OutputValidationError as e:
    #                 last_errs[i] = str(e)
    #                 correction = (
    #                     f"The previous response did not conform: {e}\nPlease correct it."
    #                     " And remember to output ONLY the requested schema, without any additional text."
    #                 )
    #                 batch_prompts[i] = batch_prompts[i] + [
    #                     {"role": "assistant", "content": raw},
    #                     {"role": "user", "content": correction},
    #                 ]

    #         if all(valid):
    #             return results

    #     failed = [i for i, ok in enumerate(valid) if not ok]
    #     errs = {i: last_errs[i] for i in failed}
    #     raise OutputValidationError(
    #         f"Batch failed after {retries} attempts at indices {failed}: {errs}"
    #     )

    # async def generate_batch_async(
    #     self,
    #     prompts: Union[List[str], List[List[Dict[str, Any]]]],
    #     *,
    #     schema: Union[Dict[str, Any], Type[BaseModel], Type],
    #     retries: int = 3,
    #     **kwargs: Any,
    # ) -> List[Any]:
    #     """
    #     Asynchronous batch generation with per-item validation + selective retries.
    #     Falls back to single-item loop if no 'batch_async' config is registered.
    #     """
    #     if "batch_async" not in self._method_configs:
    #         tasks = [
    #             self.generate_async(
    #                 **{"prompt": p, "schema": schema, "retries": retries, **kwargs}
    #             )
    #             for p in prompts
    #         ]
    #         return await asyncio.gather(*tasks)

    #     cfg = self.get_method_config("batch_async")
    #     fn = cfg.resolve(self._client)
    #     instr = self._make_instruction(schema)

    #     originals = list(prompts)
    #     batch_prompts = [self._inject_system(p, instr) for p in originals]

    #     n = len(batch_prompts)
    #     results: List[Optional[Any]] = [None] * n
    #     valid: List[bool] = [False] * n
    #     last_errs: List[Optional[str]] = [None] * n

    #     for attempt in range(1, retries + 1):
    #         call_args = {cfg.prompt_arg: batch_prompts, **kwargs}
    #         self._emit("before_generate_batch_async", {"args": call_args})
    #         try:
    #             raws: List[str] = await fn(**call_args)
    #             raws = [self._parse_llm_response(raw) for raw in raws]
    #         except Exception as e:
    #             self._emit("error", {"phase": "generate_batch_async", "error": str(e)})
    #             raise
    #         self._emit("after_generate_batch_async", {"responses": raws})

    #         for i, raw in enumerate(raws):
    #             if valid[i]:
    #                 continue
    #             try:
    #                 results[i] = self._validate(raw, schema)
    #                 valid[i] = True
    #             except OutputValidationError as e:
    #                 last_errs[i] = str(e)
    #                 correction = (
    #                     f"The previous response did not conform: {e}\nPlease correct it."
    #                     " And remember to output ONLY the requested schema, without any additional text."
    #                 )
    #                 batch_prompts[i] = batch_prompts[i] + [
    #                     {"role": "assistant", "content": raw},
    #                     {"role": "user", "content": correction},
    #                 ]

    #         if all(valid):
    #             return results

    #     failed = [i for i, ok in enumerate(valid) if not ok]
    #     errs = {i: last_errs[i] for i in failed}
    #     raise OutputValidationError(
    #         f"Async batch failed after {retries} attempts at indices {failed}: {errs}"
    #     )
