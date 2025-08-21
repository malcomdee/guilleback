import asyncio
from typing import Any, Dict, List, Optional, Type, TypeVar, Union

try:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
except ImportError as e:
    raise ImportError(
        "Please install the ibm-watsonx-ai package: pip install ibm-watsonx-ai"
    ) from e

from llmevalkit.llm.base import LLMClient, register_llm, Hook
from llmevalkit.llm.output_parser import (
    ValidatingLLMClient,
)

T = TypeVar("T", bound="WatsonxLLMClient")
SchemaType = Union[Dict[str, Any], Type["BaseModel"], Type]

# -------------------------------------------------------------------
# 1. Non-validating Watsonx wrapper
# -------------------------------------------------------------------


@register_llm("watsonx")
class WatsonxLLMClient(LLMClient):
    """
    Adapter for IBM watsonx.ai Foundation Model (via ibm_watsonx_ai.foundation_models.ModelInference).

    Supports:
      - text:       sync generation (ModelInference.generate)
      - chat:       sync chat     (ModelInference.chat)
      - text_async: async generation (ModelInference.agenerate)
      - chat_async: async chat       (ModelInference.achat)
      - batch:      (fallback to looping generate())
      - batch_async (fallback to looping generate_async())
    """

    def __init__(
        self,
        model_id: str,
        api_key: str,
        project_id: Optional[str] = None,
        url: Optional[str] = "https://us-south.ml.cloud.ibm.com",
        hooks: Optional[List[Hook]] = None,
        **model_kwargs: Any,
    ) -> None:
        """
        Initialize the Watsonx client.

        Args:
            model_id:   Identifier of the watsonx model (e.g., "meta-llama/llama-3-70b-instruct").
            api_key:    Your IBM Cloud API Key for watsonx.ai.
            project_id: (Optional) watsonx project ID.
            url:        (Optional) Base URL for the watsonx endpoint (e.g., "https://us-south.ml.cloud.ibm.com").
            hooks:      Optional observability hooks.
            model_kwargs: Additional keyword args passed to ModelInference constructor.
        """
        self.model_id = model_id
        self._model_kwargs = model_kwargs

        creds = Credentials(api_key=api_key, url=url)

        # Assemble provider_kwargs for LLMClient base class
        provider_kwargs: Dict[str, Any] = {
            "model_id": model_id,
            "credentials": creds,
        }
        if project_id is not None:
            provider_kwargs["project_id"] = project_id

        # Pass through any additional ModelInference args (params, space_id, verify, validate, etc.)
        provider_kwargs.update(model_kwargs)

        # Initialize underlying ModelInference instance via LLMClient logic
        super().__init__(
            client=None, client_needs_init=True, hooks=hooks, **provider_kwargs
        )

    @classmethod
    def provider_class(cls) -> Type:
        """
        Underlying SDK client class for watsonx.ai: ModelInference.
        """
        return ModelInference

    def _register_methods(self) -> None:
        """
        Register how to call watsonx methods:

          - 'text'       -> ModelInference.generate
          - 'text_async' -> ModelInference.agenerate
          - 'chat'       -> ModelInference.chat
          - 'chat_async' -> ModelInference.achat
        """
        self.set_method_config("text", "generate", "prompt")
        self.set_method_config("text_async", "agenerate", "prompt")
        self.set_method_config("chat", "chat", "messages")
        self.set_method_config("chat_async", "achat", "messages")
        # No explicit 'batch' or 'batch_async' in watsonx SDK; fallback to loops.

    def _parse_llm_response(self, raw: Any) -> str:
        """
        Extract the generated text from a watsonx response.

        - For text generation: raw['results'][0]['generated_text']
        - For chat:           raw['choices'][0]['message']['content']
        """
        # Text‐generation style
        if isinstance(raw, dict) and "results" in raw:
            results = raw["results"]
            if isinstance(results, list) and results:
                first = results[0]
                return first.get("generated_text", "")
        # Chat style
        if isinstance(raw, dict) and "choices" in raw:
            choices = raw["choices"]
            if isinstance(choices, list) and choices:
                first = choices[0]
                msg = first.get("message")
                if isinstance(msg, dict) and "content" in msg:
                    return msg["content"]
                if "text" in first:
                    return first["text"]
        raise ValueError(f"Unexpected watsonx response format: {raw!r}")

    def generate(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        mode: str = "chat",
        **kwargs: Any,
    ) -> str:
        """
        Synchronous generation override.

        - If mode is 'chat' and prompt is str, wrap into messages list.
        - If mode is 'text', prompt must be str or list of strings.
        """
        mode = mode.lower()
        if mode not in ("text", "chat"):
            raise KeyError(f"Unsupported mode '{mode}' for WatsonxLLMClient.generate")

        # Normalize chat‐format prompts
        if mode == "chat":
            if isinstance(prompt, str):
                prompt = [{"role": "user", "content": prompt}]
            elif isinstance(prompt, list):
                prompt = prompt
            else:
                raise TypeError(
                    "For chat mode, prompt must be a string or List[Dict[str,str]]"
                )

        return super().generate(prompt=prompt, mode=mode, **kwargs)

    async def generate_async(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        mode: str = "chat_async",
        **kwargs: Any,
    ) -> str:
        """
        Asynchronous generation override.

        - If mode is 'chat_async', wrap prompt into messages.
        - If mode is 'text_async', prompt must be str or list of strings.
        """
        mode = mode.lower()
        if mode not in ("text_async", "chat_async"):
            raise KeyError(
                f"Unsupported mode '{mode}' for WatsonxLLMClient.generate_async"
            )

        if mode == "chat_async":
            if isinstance(prompt, str):
                prompt = [{"role": "user", "content": prompt}]
            elif isinstance(prompt, list):
                prompt = prompt
            else:
                raise TypeError(
                    "For chat_async mode, prompt must be a string or List[Dict[str,str]]"
                )

        return await super().generate_async(prompt=prompt, mode=mode, **kwargs)

    def generate_batch(
        self,
        prompts: Union[List[str], List[List[Dict[str, Any]]]],
        **kwargs: Any,
    ) -> List[str]:
        """
        Synchronous batch generation (fallback loop).

        If watsonx supported a true batch‐API, you'd register a 'batch' MethodConfig,
        but here we simply call generate() in a loop.
        """
        outputs: List[str] = []
        for p in prompts:
            if isinstance(p, str):
                result = self.generate(p, **kwargs)
            else:
                result = self.generate(p, **kwargs)
            outputs.append(result)
        return outputs

    async def generate_batch_async(
        self,
        prompts: Union[List[str], List[List[Dict[str, Any]]]],
        **kwargs: Any,
    ) -> List[str]:
        """
        Asynchronous batch generation (fallback loop).
        """
        tasks = []
        for p in prompts:
            if isinstance(p, str):
                tasks.append(self.generate_async(p, **kwargs))
            else:
                tasks.append(self.generate_async(p, **kwargs))
        return await asyncio.gather(*tasks)


# -------------------------------------------------------------------
# 2. Validating Watsonx wrapper
# -------------------------------------------------------------------


@register_llm("watsonx.output_val")
class WatsonxLLMClientOutputVal(ValidatingLLMClient):
    """
    Validating adapter for IBM watsonx.ai Foundation Model.

    Extends ValidatingLLMClient to enforce output structure (via JSON Schema,
    Pydantic models, or simple Python types) on all generate calls,
    with retries and batch support (sync & async).
    """

    def __init__(
        self,
        model_id: str,
        api_key: str,
        project_id: Optional[str] = None,
        url: Optional[str] = "https://us-south.ml.cloud.ibm.com",
        hooks: Optional[List[Hook]] = None,
        **model_kwargs: Any,
    ) -> None:
        """
        Initialize a Watsonx client with output validation.

        Args:
            model_id:   Identifier of the watsonx model.
            api_key:    Your IBM Cloud API Key.
            project_id: (Optional) watsonx project ID.
            url:        (Optional) Base URL for the watsonx endpoint.
            hooks:      Optional observability hooks.
            model_kwargs: Additional arguments passed to the ModelInference constructor.
        """
        self.model_id = model_id
        self._model_kwargs = model_kwargs

        creds = Credentials(api_key=api_key, url=url)

        provider_kwargs: Dict[str, Any] = {
            "model_id": model_id,
            "credentials": creds,
        }
        if project_id is not None:
            provider_kwargs["project_id"] = project_id
        provider_kwargs.update(model_kwargs)

        super().__init__(
            client=None, client_needs_init=True, hooks=hooks, **provider_kwargs
        )

    @classmethod
    def provider_class(cls) -> Type:
        """
        Underlying SDK client class: ModelInference.
        """
        return ModelInference

    def _register_methods(self) -> None:
        """
        Register how to call watsonx methods for validation:

          - 'text'       -> ModelInference.generate
          - 'text_async' -> ModelInference.agenerate
          - 'chat'       -> ModelInference.chat
          - 'chat_async' -> ModelInference.achat
          - batch / batch_async fall back to loops via base class.
        """
        self.set_method_config("text", "generate", "prompt")
        self.set_method_config("text_async", "agenerate", "prompt")
        self.set_method_config("chat", "chat", "messages")
        self.set_method_config("chat_async", "achat", "messages")

    def _parse_llm_response(self, raw: Any) -> str:
        """
        Extract the assistant-generated text from a watsonx response.

        Same logic as non-validating client.
        """
        if isinstance(raw, dict) and "results" in raw:
            results = raw["results"]
            if isinstance(results, list) and results:
                first = results[0]
                return first.get("generated_text", "")
        if isinstance(raw, dict) and "choices" in raw:
            choices = raw["choices"]
            if isinstance(choices, list) and choices:
                first = choices[0]
                msg = first.get("message")
                if isinstance(msg, dict) and "content" in msg:
                    return msg["content"]
                if "text" in first:
                    return first["text"]
        raise ValueError(f"Unexpected watsonx response format: {raw!r}")

    def generate(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        *,
        schema: SchemaType,
        retries: int = 3,
        **kwargs: Any,
    ) -> Any:
        """
        Synchronous chat generation with validation + retries.

        Args:
            prompt: Either a string or a list of chat messages.
            schema: JSON Schema dict, Pydantic model class, or built-in Python type.
            retries: Maximum attempts (including the first).
            **kwargs: Passed to the underlying ModelInference call (e.g., temperature).
        """
        model = self.model_id
        mode = "chat"

        # Normalize prompt to chat-messages
        if isinstance(prompt, str):
            prompt = [{"role": "user", "content": prompt}]

        return super().generate(
            **{
                "prompt": prompt,
                "schema": schema,
                "retries": retries,
                "mode": mode,
                **self._model_kwargs,
                **kwargs,
            }
        )

    async def generate_async(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        *,
        schema: SchemaType,
        retries: int = 3,
        **kwargs: Any,
    ) -> Any:
        """
        Asynchronous chat generation with validation + retries.

        Args:
            prompt: Either a string or a list of chat messages.
            schema: JSON Schema dict, Pydantic model class, or built-in Python type.
            retries: Maximum attempts.
            **kwargs: Passed to the underlying ModelInference call.
        """
        model = self.model_id
        mode = "chat_async"

        if isinstance(prompt, str):
            prompt = [{"role": "user", "content": prompt}]

        return await super().generate_async(
            **{
                "prompt": prompt,
                "schema": schema,
                "retries": retries,
                "mode": mode,
                **self._model_kwargs,
                **kwargs,
            }
        )

    def generate_batch(
        self,
        prompts: Union[List[str], List[List[Dict[str, Any]]]],
        *,
        schema: SchemaType,
        retries: int = 3,
        **kwargs: Any,
    ) -> List[Any]:
        """
        Synchronous batch generation with per-item validation + retries.

        Falls back to looping generate() if no 'batch' config is registered.
        """
        results: List[Any] = []
        for p in prompts:
            if isinstance(p, str):
                out = self.generate(p, schema=schema, retries=retries, **kwargs)
            else:
                out = self.generate(p, schema=schema, retries=retries, **kwargs)
            results.append(out)
        return results

    async def generate_batch_async(
        self,
        prompts: Union[List[str], List[List[Dict[str, Any]]]],
        *,
        schema: SchemaType,
        retries: int = 3,
        **kwargs: Any,
    ) -> List[Any]:
        """
        Asynchronous batch generation with per-item validation + retries.

        Falls back to looping generate_async() if no 'batch_async' config is registered.
        """
        tasks = []
        for p in prompts:
            if isinstance(p, str):
                tasks.append(
                    self.generate_async(p, schema=schema, retries=retries, **kwargs)
                )
            else:
                tasks.append(
                    self.generate_async(p, schema=schema, retries=retries, **kwargs)
                )
        return await asyncio.gather(*tasks)
