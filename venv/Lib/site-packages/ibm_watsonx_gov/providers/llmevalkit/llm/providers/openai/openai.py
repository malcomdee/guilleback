try:
    import openai
except ImportError as e:
    raise ImportError(
        "OpenAI library is required for this module. Please install it with 'pip install openai'"
    ) from e
from typing import Any, Optional
from llmevalkit.llm.base import LLMClient, register_llm


@register_llm("openai.sync")
class SyncOpenAIClient(LLMClient):
    """
    Adapter for openai.OpenAI.

    Supports:
      - text: responses.create
      - chat: chat.completions.create
      - text_async: responses.acreate
      - chat_async: chat.completions.acreate
    """

    def __init__(self, *, client: Optional[Any] = None, **provider_kwargs: Any) -> None:
        client_needs_init = client is None
        if client_needs_init:
            super().__init__(client_needs_init=True, **provider_kwargs)
        else:
            super().__init__(client=client, **provider_kwargs)

    @classmethod
    def provider_class(cls) -> type:
        return openai.OpenAI

    def _register_methods(self) -> None:
        self.set_method_config("text", "responses.create", "prompt")
        self.set_method_config("chat", "chat.completions.create", "messages")
        self.set_method_config("text_async", "responses.create", "prompt")
        self.set_method_config("chat_async", "chat.completions.create", "messages")
        # OpenAI has no dedicated batch endpoint

    def _parse_llm_response(self, raw: Any) -> str:
        return parse_llm_response(raw)


@register_llm("openai.async")
class AsyncOpenAIClient(LLMClient):
    """
    Adapter for openai.OpenAI.

    Supports:
      - text: responses.create
      - chat: chat.completions.create
      - text_async: responses.acreate
      - chat_async: chat.completions.acreate
    """

    def __init__(self, *, client: Optional[Any] = None, **provider_kwargs: Any) -> None:
        client_needs_init = client is None
        if client_needs_init:
            super().__init__(client_needs_init=True, **provider_kwargs)
        else:
            super().__init__(client=client, **provider_kwargs)

    @classmethod
    def provider_class(cls) -> type:
        return openai.AsyncOpenAI

    def _register_methods(self) -> None:
        self.set_method_config("text", "responses.create", "prompt")
        self.set_method_config("chat", "chat.completions.create", "messages")
        self.set_method_config("text_async", "responses.acreate", "prompt")
        self.set_method_config("chat_async", "chat.completions.acreate", "messages")
        # OpenAI has no dedicated batch endpoint

    def _parse_llm_response(self, raw: Any) -> str:
        return parse_llm_response(raw)


def parse_llm_response(raw: Any) -> str:
    if getattr(raw, "output_text", None):
        return raw.output_text
    choices = getattr(raw, "choices", None) or raw.get("choices", [])
    if not choices:
        raise ValueError("OpenAI response missing 'choices'")
    first = choices[0]
    if hasattr(first, "message") and hasattr(first.message, "content"):
        return first.message.content
    if hasattr(first, "text"):
        return first.text
    return first.get("message", {}).get("content", first.get("text", ""))
