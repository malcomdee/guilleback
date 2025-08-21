import os
from typing import Any, List, Optional
from llmevalkit.llm.providers.litellm.litellm import (
    LiteLLMClient,
    LiteLLMClientOutputVal,
)
from llmevalkit.llm.base import Hook, register_llm
from ..consts import RITS_API_KEY, RITS_API_URL, XGRAMMAR


@register_llm("litellm.rits")
class RITSLiteLLMClient(LiteLLMClient):
    """
    Specialized LiteLLMClient for RITS-hosted models.

    Automatically injects:
      - model_path = "hosted_vllm/{model_name}"
      - api_base URL = "{api_url}/{model_url}/v1"
      - authentication headers with RITS_API_KEY
      - guided_decoding_backend
    """

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        model_url: Optional[str] = None,
        api_url: Optional[str] = RITS_API_URL,
        guided_decoding_backend: Optional[str] = XGRAMMAR,
        *,
        hooks: Optional[List[Hook]] = None,
        **lite_kwargs: Any,
    ) -> None:
        """
        Initialize the RITS LiteLLM client.

        Args:
            model_name: Name of the hosted RITS model (e.g. "my-model").
            api_key: RITS API key (falls back to env var RITS_API_KEY).
            model_url: URL fragment for the model; derived from model_name if omitted.
            api_url: Base RITS API URL (defaults to RITS_API_URL constant).
            guided_decoding_backend: Backend identifier for guided decoding (defaults to XGRAMMAR).
            hooks: Optional observability hooks to receive events.
            lite_kwargs: Additional parameters passed to the underlying LiteLLM constructor.

        Raises:
            ValueError: If model_url derivation fails.
            EnvironmentError: If API key is missing.
        """
        # Derive model_url from model_name if not provided
        if not model_url:
            try:
                model_url = model_name.split("/", 1)[-1].lower().replace(".", "-")
            except Exception as e:
                raise ValueError(f"Unable to derive model_url from '{model_name}': {e}")

        # Obtain API key from environment if still not provided
        if not api_key:
            api_key = os.getenv(RITS_API_KEY)
            if not api_key:
                raise EnvironmentError(
                    f"Missing API key; please set the '{RITS_API_KEY}' environment variable."
                )

        # Construct the full API base endpoint
        api_base = f"{api_url.rstrip('/')}/{model_url}/v1"

        # Call parent constructor with all required lite parameters
        super().__init__(
            model_path=f"hosted_vllm/{model_name}",
            hooks=hooks,
            api_base=api_base,
            api_key=api_key,
            headers={RITS_API_KEY: api_key},
            guided_decoding_backend=guided_decoding_backend,
            **lite_kwargs,
        )


@register_llm("litellm.rits.output_val")
class RITSLiteLLMClientOutputVal(LiteLLMClientOutputVal):
    """
    Specialized LiteLLMClientOutputVal for RITS-hosted models.

    Automatically injects:
      - model_path = "hosted_vllm/{model_name}"
      - api_base URL = "{api_url}/{model_url}/v1"
      - authentication headers with RITS_API_KEY
      - guided_decoding_backend

    Inherits full JSON / Pydantic / type-based output validation,
    retry logic, batch & async support from LiteLLMClientOutputVal.
    """

    def __init__(
        self,
        model_name: str,
        api_key: Optional[str] = None,
        model_url: Optional[str] = None,
        api_url: Optional[str] = RITS_API_URL,
        guided_decoding_backend: Optional[str] = XGRAMMAR,
        *,
        hooks: Optional[List[Hook]] = None,
        **lite_kwargs: Any,
    ) -> None:
        """
        Initialize the RITS LiteLLM client with output validation.

        Args:
            model_name: Name of the hosted RITS model (e.g. "my-model").
            api_key: RITS API key (falls back to env var RITS_API_KEY).
            model_url: URL fragment for the model; derived from model_name if omitted.
            api_url: Base RITS API URL (defaults to RITS_API_URL constant).
            guided_decoding_backend: Backend identifier for guided decoding (defaults to XGRAMMAR).
            hooks: Optional observability hooks to receive events.
            lite_kwargs: Additional parameters passed to the underlying LiteLLM constructor.

        Raises:
            ValueError: If model_url derivation fails.
            EnvironmentError: If API key is missing.
        """
        # Derive model_url from model_name if not provided
        if not model_url:
            try:
                model_url = model_name.split("/", 1)[-1].lower().replace(".", "-")
            except Exception as e:
                raise ValueError(f"Unable to derive model_url from '{model_name}': {e}")

        # Obtain API key from environment if still not provided
        if not api_key:
            api_key = os.getenv(RITS_API_KEY)
            if not api_key:
                raise EnvironmentError(
                    f"Missing API key; please set the '{RITS_API_KEY}' environment variable."
                )

        # Construct the full API base endpoint
        api_base = f"{api_url.rstrip('/')}/{model_url}/v1"

        # Call parent constructor with all required lite parameters
        super().__init__(
            model_path=f"hosted_vllm/{model_name}",
            hooks=hooks,
            api_base=api_base,
            api_key=api_key,
            headers={RITS_API_KEY: api_key},
            guided_decoding_backend=guided_decoding_backend,
            **lite_kwargs,
        )
