try:
    import litellm
except ImportError as e:
    raise ImportError(
        "litellm is not installed. Please install it with `pip install litellm`."
    ) from e

from typing import Any, Dict, List, Optional, Union, Type
from llmevalkit.llm.base import LLMClient, register_llm, Hook
from pydantic import BaseModel
from llmevalkit.llm.output_parser import ValidatingLLMClient


@register_llm("litellm")
class LiteLLMClient(LLMClient):
    """
    Adapter for litellm.LiteLLM.

    Supports:
      - text: completion
      - chat: chat
      - text_async: acompletion
      - chat_async: achat
      - batch (if available): batch_completion
    """

    def __init__(
        self, model_path: str, hooks: Optional[List[Hook]] = None, **lite_kwargs: Any
    ) -> None:
        self.model_path = model_path
        self._lite_kwargs = lite_kwargs
        super().__init__(client=None, hooks=hooks, **lite_kwargs)

    @classmethod
    def provider_class(cls) -> type:
        return litellm

    def _register_methods(self) -> None:
        self.set_method_config("chat", "completion", "messages")
        self.set_method_config("chat_async", "acompletion", "messages")
        if hasattr(litellm, "batch_completion"):
            self.set_method_config("batch", "batch_completion", "messages")

    def _parse_llm_response(self, raw: Any) -> str:
        choices = getattr(raw, "choices", None) or raw.get("choices", [])
        if not choices:
            raise ValueError("LiteLLM response missing 'choices'")
        first = choices[0]
        delta = getattr(first, "delta", None)
        if delta and hasattr(delta, "content"):
            return delta.content
        msg = getattr(first, "message", None)
        if msg and hasattr(msg, "content"):
            return msg.content
        if hasattr(first, "text"):
            return first.text
        return first.get("delta", {}).get("content", first.get("text", ""))

    def generate(self, prompt: Union[str, List[Dict[str, Any]]], **kwargs: Any) -> str:
        model_str = self.model_path
        mode = "chat"
        if isinstance(prompt, str):
            prompt = [{"role": "user", "content": prompt}]
        prompt = prompt if isinstance(prompt, list) else [prompt]
        return super().generate(
            **{
                "prompt": prompt,
                "model": model_str,
                "mode": mode,
                **self._lite_kwargs,
                **kwargs,
            }
        )

    def generate_batch(
        self, prompts: Union[List[str], List[List[Dict[str, Any]]]], **kwargs: Any
    ) -> List[str]:
        model_str = self.model_path
        mode = "batch"
        new_prompts = []
        for prompt in prompts:
            if isinstance(prompt, str):
                prompt = [{"role": "user", "content": prompt}]
            new_prompts.append(prompt)
        prompts = new_prompts
        return super().generate_batch(
            **{
                "prompts": prompts,
                "model": model_str,
                "mode": mode,
                **self._lite_kwargs,
                **kwargs,
            }
        )

    async def generate_async(
        self, prompt: Union[str, List[Dict[str, Any]]], **kwargs: Any
    ) -> str:
        model_str = self.model_path
        mode = "chat_async"
        if isinstance(prompt, str):
            prompt = [{"role": "user", "content": prompt}]
        prompt = prompt if isinstance(prompt, list) else [prompt]
        return await super().generate_async(
            **{
                "prompt": prompt,
                "model": model_str,
                "mode": mode,
                **self._lite_kwargs,
                **kwargs,
            }
        )

    async def generate_batch_async(
        self, prompts: Union[List[str], List[List[Dict[str, Any]]]], **kwargs: Any
    ) -> List[str]:
        model_str = self.model_path
        return await super().generate_batch_async(
            **{"prompts": prompts, "model": model_str, **self._lite_kwargs, **kwargs}
        )


@register_llm("litellm.output_val")
class LiteLLMClientOutputVal(ValidatingLLMClient):
    """
    Validating adapter for litellm.LiteLLM.

    Extends ValidatingLLMClient to enforce output structure (via JSON Schema,
    Pydantic models, or simple Python types) on all generate calls,
    with retries and batch support (sync & async).
    """

    def __init__(
        self, model_path: str, hooks: Optional[List[Hook]] = None, **lite_kwargs: Any
    ) -> None:
        """
        Initialize a LiteLLMClient.

        Args:
            model_path: Identifier or path for the LiteLLM model.
            hooks: Optional observability hooks (callable(event, payload)).
            lite_kwargs: Extra arguments passed when initializing the litellm client.
        """
        self.model_path = model_path
        self._lite_kwargs = lite_kwargs
        super().__init__(client=None, hooks=hooks, **lite_kwargs)

    @classmethod
    def provider_class(cls) -> Type:
        """
        Underlying SDK client for litellm.

        Must be callable with no arguments (per LLMClient __init__ logic).
        """
        return litellm

    def _register_methods(self) -> None:
        """
        Register how to call litellm methods:

        - 'chat'       → litellm.completion
        - 'chat_async' → litellm.acompletion
        - 'batch'      → litellm.batch_completion (if available)
        - 'batch_async'→ litellm.abatch_completion (if available)
        """
        self.set_method_config("chat", "completion", "messages")
        self.set_method_config("chat_async", "acompletion", "messages")

        if hasattr(litellm, "batch_completion"):
            self.set_method_config("batch", "batch_completion", "messages")
        if hasattr(litellm, "abatch_completion"):
            self.set_method_config("batch_async", "abatch_completion", "messages")

    def _parse_llm_response(self, raw: Any) -> str:
        """
        Extract the assistant-generated text from a LiteLLM response.

        Handles:
          - chat streaming (.choices[0].delta.content)
          - chat non-streaming (.choices[0].message.content)
          - text completion (.choices[0].text)
        """
        choices = getattr(raw, "choices", None) or raw.get("choices", [])
        if not choices:
            raise ValueError("LiteLLM response missing 'choices'")
        first = choices[0]

        # Streaming delta
        delta = getattr(first, "delta", None)
        if delta and hasattr(delta, "content"):
            return delta.content

        # Non-streaming chat
        msg = getattr(first, "message", None)
        if msg and hasattr(msg, "content"):
            return msg.content

        # Text completion
        if hasattr(first, "text"):
            return first.text

        # Fallback to dict lookup
        return first.get("delta", {}).get("content", first.get("text", ""))

    def generate(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        *,
        schema: Union[Dict[str, Any], Type[BaseModel], Type],
        schema_field: Optional[str] = "response_format",
        retries: int = 3,
        **kwargs: Any,
    ) -> Any:
        """
        Synchronous chat generation with validation + retries.

        Args:
            prompt: Either a string or a list of chat messages.
            schema: JSON Schema dict, Pydantic model class, or built-in Python type.
            retries: Maximum attempts (including the first).
            **kwargs: Passed to the underlying litellm call (e.g. temperature).

        Returns:
            The parsed & validated Python object (or Pydantic instance).
        """
        model = self.model_path
        mode = "chat"

        # Normalize prompt to chat-messages
        if isinstance(prompt, str):
            prompt = [{"role": "user", "content": prompt}]

        # Delegate to ValidatingLLMClient.generate
        return super().generate(
            **{
                "prompt": prompt,
                "schema": schema,
                # "schema_field": schema_field,
                "retries": retries,
                "model": model,
                "mode": mode,
                **self._lite_kwargs,
                **kwargs,
            }
        )

    async def generate_async(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        *,
        schema: Union[Dict[str, Any], Type[BaseModel], Type],
        schema_field: Optional[str] = "response_format",
        retries: int = 3,
        **kwargs: Any,
    ) -> Any:
        """
        Asynchronous chat generation with validation + retries.
        """
        model = self.model_path
        mode = "chat_async"

        if isinstance(prompt, str):
            prompt = [{"role": "user", "content": prompt}]

        return await super().generate_async(
            **{
                "prompt": prompt,
                "schema": schema,
                # "schema_field": schema_field,
                "retries": retries,
                "model": model,
                "mode": mode,
                **self._lite_kwargs,
                **kwargs,
            }
        )

    # def generate_batch(
    #     self,
    #     prompts: Union[List[str], List[List[Dict[str, Any]]]],
    #     *,
    #     schema: Union[Dict[str, Any], Type[BaseModel], Type],
    #     retries: int = 3,
    #     **kwargs: Any,
    # ) -> List[Any]:
    #     """
    #     Synchronous batch generation with selective per-item retries.

    #     If no 'batch' method is registered, falls back to looping generate().
    #     """
    #     model = self.model_path
    #     mode = "batch"

    #     # Normalize each prompt to a list of chat messages
    #     normalized: List[List[Dict[str, Any]]] = []
    #     for p in prompts:
    #         if isinstance(p, str):
    #             normalized.append([{"role": "user", "content": p}])
    #         else:
    #             normalized.append(p)
    #     return super().generate_batch(
    #         **{
    #             "prompts": normalized,
    #             "schema": schema,
    #             "retries": retries,
    #             "model": model,
    #             "mode": mode,
    #             **self._lite_kwargs,
    #             **kwargs,
    #         }
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
    #     Asynchronous batch generation with selective per-item retries.

    #     Falls back to looping generate_async() if no 'batch_async' is registered.
    #     """
    #     model = self.model_path
    #     mode = "batch_async"

    #     normalized: List[List[Dict[str, Any]]] = []
    #     for p in prompts:
    #         if isinstance(p, str):
    #             normalized.append([{"role": "user", "content": p}])
    #         else:
    #             normalized.append(p)
    #     return await super().generate_batch_async(
    #         **{
    #             "prompts": normalized,
    #             "schema": schema,
    #             "retries": retries,
    #             "model": model,
    #             "mode": mode,
    #             **self._lite_kwargs,
    #             **kwargs,
    #         }
    #     )
