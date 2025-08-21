import inspect
import asyncio
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union

T = TypeVar("T", bound="LLMClient")
Hook = Callable[[str, Dict[str, Any]], None]


# Registry
_REGISTRY: Dict[str, Type["LLMClient"]] = {}


def register_llm(name: str):
    def deco(cls: Type["LLMClient"]):
        _REGISTRY[name] = cls
        return cls

    return deco


def get_llm(name: str) -> Type["LLMClient"]:
    try:
        return _REGISTRY[name]
    except KeyError:
        raise ValueError(f"No LLMClient registered under '{name}'")


class MethodConfig:
    """
    Configuration for a provider method.

    Attributes:
        path: Dot-delimited attribute path on the client (e.g. "chat.completions.create").
        prompt_arg: Name of the parameter used for the prompt/messages.
    """

    def __init__(self, path: str, prompt_arg: str) -> None:
        self.path = path
        self.prompt_arg = prompt_arg

    def resolve(self, client: Any) -> Callable[..., Any]:
        """
        Traverse `path` on `client` to retrieve the bound callable.

        Raises:
            AttributeError: if any attribute in the path is missing.
            TypeError: if the resolved attribute is not callable.
        """
        obj: Any = client
        for attr in self.path.split("."):
            obj = getattr(obj, attr, None)
            if obj is None:
                raise AttributeError(
                    f"Could not resolve method path '{self.path}' on {client}"
                )
        if not callable(obj):
            raise TypeError(f"Resolved '{self.path}' is not callable on {client}")
        return obj


class LLMClient(ABC):
    """
    Abstract base wrapper for any LLM provider.

    Responsibilities:
      - Accept an existing SDK client or construct one from kwargs.
      - Register provider methods via MethodConfig.
      - Provide sync/async/batch generate calls.
      - Emit observability hooks.
      - Parse raw responses into plain text.
    """

    def __init__(
        self,
        *,
        client: Optional[Any] = None,
        client_needs_init: bool = False,
        hooks: Optional[List[Hook]] = None,
        **provider_kwargs: Any,
    ) -> None:
        """
        Initialize the wrapper.

        Args:
            client: Pre-initialized provider SDK instance.
            client_needs_init: If True, client is not initialized and will be
                initialized with provider_kwargs.
            hooks: Callables(event_name, payload) for observability.
            provider_kwargs: Passed to provider_class constructor if client is None.

        Raises:
            TypeError: if `client` is provided but is not instance of provider_class.
            RuntimeError: if provider_class instantiation fails.
        """
        self._hooks: List[Hook] = hooks or []
        self._method_configs: Dict[str, MethodConfig] = {}

        if client is not None:
            if not isinstance(client, self.provider_class()):
                raise TypeError(
                    f"Expected client of type {self.provider_class().__name__}, "
                    f"got {type(client).__name__}"
                )
            self._client = client
        else:
            if client_needs_init:
                sig = inspect.signature(self.provider_class().__init__)
                init_kwargs = {
                    k: v
                    for k, v in provider_kwargs.items()
                    if k in sig.parameters and k != "self"
                }
                try:
                    self._client = self.provider_class()(**init_kwargs)
                except Exception as e:
                    raise RuntimeError(
                        f"Failed to initialize {self.provider_class().__name__}: {e}"
                    ) from e
            else:
                self._client = self.provider_class()

        self._register_methods()

    @classmethod
    @abstractmethod
    def provider_class(cls) -> Type:
        """
        Underlying SDK client class, e.g. openai.OpenAI or litellm.LiteLLM.
        """

    @abstractmethod
    def _register_methods(self) -> None:
        """
        Subclasses register MethodConfig entries by calling:
            self.set_method_config(key, path, prompt_arg)
        for keys: 'text', 'chat', 'text_async', 'chat_async', optionally 'batch' and 'batch_async'.
        """

    def set_method_config(self, key: str, path: str, prompt_arg: str) -> None:
        """
        Register how to invoke a provider method.

        Args:
            key: Identifier ('text', 'chat', 'text_async', 'chat_async', 'batch').
            path: Dot-separated path on the SDK client.
            prompt_arg: Name of the argument carrying the prompt/messages.
        """
        self._method_configs[key] = MethodConfig(path, prompt_arg)

    def get_method_config(self, key: str) -> MethodConfig:
        """
        Retrieve a previously registered MethodConfig.

        Raises:
            KeyError: if no config exists for `key`.
        """
        try:
            return self._method_configs[key]
        except KeyError:
            raise KeyError(f"No method config registered under '{key}'")

    def get_client(self) -> Any:
        """Return the raw underlying SDK client."""
        return self._client

    def _emit(self, event: str, payload: Dict[str, Any]) -> None:
        """Invoke all observability hooks, swallowing errors."""
        for hook in self._hooks:
            try:
                hook(event, payload)
            except Exception:
                pass

    @abstractmethod
    def _parse_llm_response(self, raw: Any) -> str:
        """
        Extract the generated text from a single raw response.

        Raises:
            ValueError: if extraction fails.
        """

    def generate(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        mode: str = "chat",
        **kwargs: Any,
    ) -> str:
        """
        Synchronous generation.

        Args:
            prompt: Either a plain string or a list of chat messages dicts.
            mode: One of 'text' or 'chat'.

        Returns:
            The generated text.

        Raises:
            KeyError: if no MethodConfig for `mode`.
            Exception: if the underlying call or parsing fails.
        """
        cfg = self.get_method_config(mode)
        fn = cfg.resolve(self._client)

        call_args = {cfg.prompt_arg: prompt, **kwargs}

        self._emit("before_generate", {"mode": mode, "args": call_args})
        try:
            raw = fn(**call_args)
        except Exception as e:
            self._emit("error", {"phase": "generate", "error": str(e)})
            raise
        text = self._parse_llm_response(raw)
        self._emit("after_generate", {"mode": mode, "response": text})
        return text

    async def generate_async(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        mode: str = "chat_async",
        **kwargs: Any,
    ) -> str:
        """
        Asynchronous generation.

        Uses provider async method if registered, otherwise falls back to thread.

        Args:
            prompt: string or messages list.
            mode: 'text_async' or 'chat_async'.

        Returns:
            The generated text.

        Raises:
            Exception: if generation or parsing fails.
        """
        mode = mode.replace("batch", "chat")
        if mode in self._method_configs:
            cfg = self.get_method_config(mode)
            fn = cfg.resolve(self._client)

            call_args = {cfg.prompt_arg: prompt, **kwargs}

            self._emit("before_generate_async", {"mode": mode, "args": call_args})
            try:
                raw = await fn(**call_args)
            except Exception as e:
                self._emit("error", {"phase": "generate_async", "error": str(e)})
                raise
            text = self._parse_llm_response(raw)
            self._emit("after_generate_async", {"mode": mode, "response": text})
            return text

        kwargs["mode"] = mode.replace("_async", "")

        # fallback to sync generate in thread
        return await asyncio.to_thread(self.generate, prompt, **kwargs)

    def generate_batch(
        self, prompts: Union[List[str], List[List[Dict[str, Any]]]], **kwargs: Any
    ) -> List[str]:
        """
        Synchronous batch generation.

        Uses provider 'batch' method if configured, else loops generate().

        Args:
            prompts: list of prompts (str or messages).
        """
        if "batch" in self._method_configs:
            cfg = self.get_method_config("batch")
            fn = cfg.resolve(self._client)

            call_args = {cfg.prompt_arg: prompts, **kwargs}

            self._emit("before_generate_batch", {"args": call_args})
            try:
                raw_list = fn(**call_args)
            except Exception as e:
                self._emit("error", {"phase": "generate_batch", "error": str(e)})
                raise
            texts = [self._parse_llm_response(raw) for raw in raw_list]
            self._emit("after_generate_batch", {"responses": texts})
            return texts

        # fallback: loop
        return [self.generate(**{"prompt": p, **kwargs}) for p in prompts]

    async def generate_batch_async(
        self, prompts: Union[List[str], List[List[Dict[str, Any]]]], **kwargs: Any
    ) -> List[str]:
        """
        Asynchronous batch generation.

        Uses provider 'batch_async' method if configured, else loops generate_async().
        """
        if "batch_async" in self._method_configs:
            cfg = self.get_method_config("batch_async")
            fn = cfg.resolve(self._client)

            call_args = {cfg.prompt_arg: prompts, **kwargs}

            self._emit("before_generate_batch_async", {"args": call_args})
            try:
                raw_list = await fn(**call_args)
            except Exception as e:
                self._emit("error", {"phase": "generate_batch_async", "error": str(e)})
                raise
            texts = [self._parse_llm_response(raw) for raw in raw_list]
            self._emit("after_generate_batch_async", {"responses": texts})
            return texts

        # fallback: loop
        tasks = [
            asyncio.create_task(self.generate_async(**{"prompt": p, **kwargs}))
            for p in prompts
        ]
        results = await asyncio.gather(*tasks)
        return results
