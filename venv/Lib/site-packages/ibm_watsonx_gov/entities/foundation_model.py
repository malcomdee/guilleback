# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Callable

from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing_extensions import Self

from ibm_watsonx_gov.entities.model_provider import (AzureOpenAIModelProvider,
                                                     CustomModelProvider,
                                                     ModelProvider,
                                                     OpenAIModelProvider,
                                                     RITSModelProvider,
                                                     WxAIModelProvider)
from ibm_watsonx_gov.utils.python_utils import get_environment_variable_value


class FoundationModel(BaseModel):
    """
    Defines the base FoundationModel class.
    """
    model_name: Annotated[
        str | None,
        Field(
            description="The name of the foundation model.",
            default=None,
        ),
    ]
    provider: Annotated[
        ModelProvider, Field(
            description="The provider of the foundation model.")
    ]
    model_config = ConfigDict(protected_namespaces=())


class WxAIFoundationModel(FoundationModel):
    """
    The IBM watsonx.ai foundation model details

    To initialize the foundation model, you can either pass in the credentials directly or set the environment.
    You can follow these examples to create the provider.

    Examples:
        1. Create foundation model by specifying the credentials during object creation:
            .. code-block:: python

                # Specify the credentials during object creation
                wx_ai_foundation_model = WxAIFoundationModel(
                    model_id="google/flan-ul2",
                    project_id=<PROJECT_ID>,
                    provider=WxAIModelProvider(
                        credentials=WxAICredentials(
                            url=wx_url, # This is optional field, by default US-Dallas region is selected
                            api_key=wx_apikey,
                        )
                    )
                )

        2. Create foundation model by setting the credentials environment variables:
            * The api key can be set using one of the environment variables ``WXAI_API_KEY``, ``WATSONX_APIKEY``, or ``WXG_API_KEY``. These will be read in the order of precedence.
            * The url is optional and will be set to US-Dallas region by default. It can be set using one of the environment variables ``WXAI_URL``, ``WATSONX_URL``, or ``WXG_URL``. These will be read in the order of precedence.

            .. code-block:: python

                wx_ai_foundation_model = WxAIFoundationModel(
                    model_id="google/flan-ul2",
                    project_id=<PROJECT_ID>,
                )

        3. Create foundation model by specifying watsonx.governance software credentials during object creation:
            .. code-block:: python

                wx_ai_foundation_model = WxAIFoundationModel(
                    model_id="google/flan-ul2",
                    project_id=project_id,
                    provider=WxAIModelProvider(
                        credentials=WxAICredentials(
                            url=wx_url,
                            api_key=wx_apikey,
                            username=wx_username,
                            version=wx_version,
                        )
                    )
                )

        4. Create foundation model by setting watsonx.governance software credentials environment variables:
            * The api key can be set using one of the environment variables ``WXAI_API_KEY``, ``WATSONX_APIKEY``, or ``WXG_API_KEY``. These will be read in the order of precedence.
            * The url can be set using one of these environment variable ``WXAI_URL``, ``WATSONX_URL``, or ``WXG_URL``. These will be read in the order of precedence.
            * The username can be set using one of these environment variable ``WXAI_USERNAME``, ``WATSONX_USERNAME``, or ``WXG_USERNAME``. These will be read in the order of precedence.
            * The version of watsonx.governance software can be set using one of these environment variable ``WXAI_VERSION``, ``WATSONX_VERSION``, or ``WXG_VERSION``. These will be read in the order of precedence.

            .. code-block:: python

                wx_ai_foundation_model = WxAIFoundationModel(
                    model_id="google/flan-ul2",
                    project_id=project_id,
                )

    """
    model_id: Annotated[
        str, Field(description="The unique identifier for the watsonx.ai model.")
    ]
    project_id: Annotated[
        str | None,
        Field(description="The project ID associated with the model.", default=None),
    ]
    space_id: Annotated[
        str | None,
        Field(description="The space ID associated with the model.", default=None),
    ]
    provider: Annotated[
        WxAIModelProvider,
        Field(
            description="The provider of the model.", default_factory=WxAIModelProvider
        ),
    ]

    @model_validator(mode="after")
    def get_params_from_env(self) -> Self:
        if self.space_id is None and self.project_id is None:
            try:
                self.project_id = get_environment_variable_value(
                    ["WX_PROJECT_ID", "WATSONX_PROJECT_ID"])
            except ValueError:
                self.project_id = None
            if self.project_id is None:
                try:
                    self.space_id = get_environment_variable_value(
                        ["WX_SPACE_ID", "WATSONX_SPACE_ID"])
                except ValueError:
                    self.space_id = None

        return self


class OpenAIFoundationModel(FoundationModel):
    """
    The OpenAI foundation model details

    Examples:
        1. Create OpenAI foundation model by passing the credentials during object creation. Note that the url is optional and will be set to the default value for OpenAI. To change the default value, the url should be passed to ``OpenAICredentials`` object.
            .. code-block:: python

                openai_foundation_model = OpenAIFoundationModel(
                    model_id="gpt-4o-mini",
                    provider=OpenAIModelProvider(
                        credentials=OpenAICredentials(
                            api_key=api_key,
                            url=openai_url,
                        )
                    )
                )

        2. Create OpenAI foundation model by setting the credentials in environment variables:
            * ``OPENAI_API_KEY`` is used to set the api key for OpenAI.
            * ``OPENAI_URL`` is used to set the url for OpenAI

            .. code-block:: python

                openai_foundation_model = OpenAIFoundationModel(
                    model_id="gpt-4o-mini",
                )
    """
    model_id: Annotated[str, Field(description="Model name from OpenAI")]
    provider: Annotated[OpenAIModelProvider, Field(
        description="OpenAI provider", default_factory=OpenAIModelProvider)]


class AzureOpenAIFoundationModel(FoundationModel):
    """
    The Azure OpenAI foundation model details

    Examples:
        1. Create Azure OpenAI foundation model by passing the credentials during object creation.
            .. code-block:: python

                azure_openai_foundation_model = AzureOpenAIFoundationModel(
                    model_id="gpt-4o-mini",
                    provider=AzureOpenAIModelProvider(
                        credentials=AzureOpenAICredentials(
                            api_key=azure_api_key,
                            url=azure_host_url,
                            api_version=azure_api_model_version,
                        )
                    )
                )

    2. Create Azure OpenAI foundation model by setting the credentials in environment variables:
        * ``AZURE_OPENAI_API_KEY`` is used to set the api key for OpenAI.
        * ``AZURE_OPENAI_HOST`` is used to set the url for Azure OpenAI.
        * ``AZURE_OPENAI_API_VERSION`` is uses to set the the api version for Azure OpenAI.

            .. code-block:: python

                openai_foundation_model = AzureOpenAIFoundationModel(
                    model_id="gpt-4o-mini",
                )

    """
    model_id: Annotated[str, Field(
        description="Model deployment name from Azure OpenAI")]
    provider: Annotated[AzureOpenAIModelProvider, Field(
        description="Azure OpenAI provider", default_factory=AzureOpenAIModelProvider)]


class RITSFoundationModel(FoundationModel):
    provider: Annotated[
        RITSModelProvider,
        Field(description="The provider of the model.",
              default_factory=RITSModelProvider),
    ]


class CustomFoundationModel(FoundationModel):
    """
    Defines the CustomFoundationModel class.

    This class extends the base `FoundationModel` to support custom inference logic through a user-defined scoring function.
    It is intended for use cases where the model is externally hosted and not in the list of supported frameworks.
    Examples:
        1. Define a custom scoring function and create a model:
            .. code-block:: python

                import pandas as pd

                def scoring_fn(data: pd.DataFrame):
                    predictions_list = []
                    # Custom logic to call an external LLM
                    return pd.DataFrame({"generated_text": predictions_list})                    

                model = CustomFoundationModel(
                    scoring_fn=scoring_fn
                )
    """

    scoring_fn: Annotated[
        Callable,
        Field(
            description="A callable function that wraps the inference calls to an external LLM."
        ),
    ]
    provider: Annotated[
        ModelProvider,
        Field(
            description="The provider of the model.",
            default_factory=CustomModelProvider,
        ),
    ]
