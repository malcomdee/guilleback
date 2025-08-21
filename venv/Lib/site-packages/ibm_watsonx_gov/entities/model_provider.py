# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from ibm_watsonx_gov.entities.credentials import (AzureOpenAICredentials,
                                                  OpenAICredentials,
                                                  RITSCredentials,
                                                  WxAICredentials)
from ibm_watsonx_gov.entities.enums import ModelProviderType


class ModelProvider(BaseModel):
    type: Annotated[
        ModelProviderType, Field(
            description="The type of model provider.")
    ]


class WxAIModelProvider(ModelProvider):
    """
    This class represents a model provider configuration for IBM watsonx.ai. It includes the provider type and
    credentials required to authenticate and interact with the watsonx.ai platform. If credentials are not explicitly
    provided, it attempts to load them from environment variables.

    Examples:
        1. Create provider using credentials object:
            .. code-block:: python

                credentials = WxAICredentials(
                    url="https://us-south.ml.cloud.ibm.com",
                    api_key="your-api-key"
                )
                provider = WxAIModelProvider(credentials=credentials)

        2. Create provider using environment variables:
            .. code-block:: python

                import os

                os.environ['WATSONX_URL'] = "https://us-south.ml.cloud.ibm.com"
                os.environ['WATSONX_APIKEY'] = "your-api-key"

                provider = WxAIModelProvider()
    """

    type: Annotated[
        ModelProviderType,
        Field(
            description="The type of model provider.",
            default=ModelProviderType.IBM_WATSONX_AI,
            frozen=True
        )
    ]
    credentials: Annotated[
        WxAICredentials | None,
        Field(
            default=None,
            description="The credentials used to authenticate with watsonx.ai. If not provided, they will be loaded from environment variables."
        )
    ]

    @model_validator(mode="after")
    def create_credentials_from_env(self) -> Self:
        if self.credentials is None:
            try:
                self.credentials = WxAICredentials.create_from_env()
            except ValueError:
                self.credentials = None
        return self

class OpenAIModelProvider(ModelProvider):
    type: Annotated[ModelProviderType,
                    Field(description="The type of model provider.",
                          default=ModelProviderType.OPENAI, frozen=True)]
    credentials: Annotated[OpenAICredentials | None, Field(
        description="OpenAI credentials. This can also be set by using `OPENAI_API_KEY` environment variable.", default=None)]

    @model_validator(mode="after")
    def create_credentials_from_env(self) -> Self:
        if self.credentials is None:
            self.credentials = OpenAICredentials.create_from_env()
        return self


class AzureOpenAIModelProvider(ModelProvider):
    type: Annotated[ModelProviderType,
                    Field(description="The type of model provider.",
                          default=ModelProviderType.AZURE_OPENAI, frozen=True)]
    credentials: Annotated[AzureOpenAICredentials | None, Field(
        description="Azure OpenAI credentials.", default=None
    )]

    @model_validator(mode="after")
    def create_credentials_from_env(self) -> Self:
        if self.credentials is None:
            self.credentials = AzureOpenAICredentials.create_from_env()
        return self


class RITSModelProvider(ModelProvider):
    type: Annotated[ModelProviderType,
                    Field(description="The type of model provider.",
                          default=ModelProviderType.RITS, frozen=True)]
    credentials: Annotated[RITSCredentials | None, Field(
        description="RITS credentials.", default=None
    )]

    @model_validator(mode="after")
    def create_credentials_from_env(self) -> Self:
        if self.credentials is None:
            self.credentials = RITSCredentials.create_from_env()
        return self


class CustomModelProvider(ModelProvider):
    """
    Defines the CustomModelProvider class.

    This class represents a custom model provider, typically used when integrating with non-standard or user-defined
    model backends. It sets the provider type to `CUSTOM` by default.

    Examples:
        1. Create a custom model provider:
            .. code-block:: python

                provider = CustomModelProvider()

        2. Use with a custom foundation model:
            .. code-block:: python

                custom_model = CustomFoundationModel(
                    scoring_fn=my_scoring_function,
                    provider=CustomModelProvider()
                )

    Attributes:
        type (ModelProviderType): The type of model provider. Always set to `ModelProviderType.CUSTOM`.
    """    
    type: Annotated[ModelProviderType, Field(
        description="The type of model provider.", default=ModelProviderType.CUSTOM)]


