# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import os
from typing import Annotated

from pydantic import BaseModel, Field, model_validator

from ibm_watsonx_gov.entities.enums import Region
from ibm_watsonx_gov.utils.python_utils import get_environment_variable_value
from ibm_watsonx_gov.utils.url_mapping import (WATSONX_REGION_URLS,
                                               WOS_URL_MAPPING)


class Credentials(BaseModel):
    api_key: Annotated[str | None, Field(title="Api Key",
                                         description="The user api key. Required for using watsonx as a service and one of api_key or password is required for using watsonx on-prem software.",
                                         strip_whitespace=True,
                                         default=None)]
    region: Annotated[str | None,
                      Field(title="Region",
                            description="The watsonx cloud region. By default us-south region is used.",
                            default=Region.US_SOUTH.value)]
    url: Annotated[str, Field(title="watsonx url",
                              description="The watsonx url. Required for using watsonx on-prem software.",
                              default=None)]
    service_instance_id:  Annotated[str | None, Field(title="Service instance id",
                                                      description="The watsonx.governance service instance id.",
                                                      default=None)]
    username: Annotated[str | None, Field(title="User name",
                                          description="The user name. Required for using watsonx on-prem software.",
                                          default=None)]
    password: Annotated[str | None, Field(title="Password",
                                          description="The user password. One of api_key or password is required for using watsonx on-prem software.",
                                          default=None)]
    # TODO Add support
    # token: Annotated[str | None, Field(title="Token",
    #                                    description="The bearer token.",
    #                                    default=None)]
    version: Annotated[str | None, Field(title="Version",
                                         description="The watsonx on-prem software version. Required for using watsonx on-prem software.",
                                         default=None,
                                         examples=["5.2"])]
    disable_ssl: Annotated[bool, Field(title="Disable ssl",
                                       description="The flag to disable ssl.",
                                       default=False)]

    @model_validator(mode="after")
    def validate_credentials(self):
        if self.version:  # on-prem
            if not self.url:
                raise ValueError("The url value is required.")
            if not self.username:
                raise ValueError("The username value is required.")
            if not (self.api_key or self.password):
                raise ValueError(
                    "One of api_key or password value is required.")
        else:
            if not self.api_key:
                raise ValueError("The api_key value is required.")
            if self.url:
                url_map = WOS_URL_MAPPING.get(self.url)
                if not url_map:
                    raise ValueError(
                        f"Invalid url {self.url}. Please provide valid watsonx.governance service url.")
                self.region = url_map.region
            else:
                url_map = WATSONX_REGION_URLS.get(self.region)
                if not url_map:
                    raise ValueError(
                        f"Invalid region {self.region}. Please provide valid watsonx.governance region. Supported regions are {Region.values()}")
                self.url = url_map.wxg_url

        return self

    @classmethod
    def create_from_env(cls):
        region = get_environment_variable_value(
            ["WATSONX_REGION"])
        # possible API key environment variable names
        api_key = get_environment_variable_value(
            ["WXG_API_KEY", "WATSONX_APIKEY"])
        username = get_environment_variable_value(
            ["WXG_USERNAME", "WATSONX_USERNAME"])
        password = get_environment_variable_value(["WATSONX_PASSWORD"])
        version = get_environment_variable_value(
            ["WXG_VERSION", "WATSONX_VERSION"])
        # TODO Add support
        # token = get_environment_variable_value(["WATSONX_TOKEN"])

        if version:  # on-prem
            url = get_environment_variable_value(["WATSONX_URL"])
            if not url:
                raise ValueError(
                    "The watsonx url is required and should be set using WATSONX_URL environment variable.")
            if not username:
                raise ValueError(
                    "The username is required and should be set using WATSONX_USERNAME environment variable.")
            if not (api_key or password):
                raise ValueError(
                    "One of api_key or password is required and should be set using WATSONX_APIKEY or WATSONX_PASSWORD environment variable.")
        else:
            url = os.getenv("WXG_URL")
            if region:
                if region not in Region.values():
                    raise ValueError(
                        f"Invalid region {url}. Supported regions are {Region.values()}.")

            if url:
                url_map = WOS_URL_MAPPING.get(url)
                if not url_map:
                    raise ValueError(
                        f"Invalid url {url}. Please provide valid watsonx.governance service url.")
                region = url_map.region
            else:
                if not region:
                    region = Region.US_SOUTH.value
                url = WATSONX_REGION_URLS.get(region).wxg_url

            if not api_key:
                raise ValueError(
                    "The api_key is required and should be set using WATSONX_APIKEY environment variable.")

        disable_ssl = os.getenv("WATSONX_DISABLE_SSL", False)

        return Credentials(
            region=region,
            api_key=api_key,
            url=url,
            service_instance_id=os.getenv("WXG_SERVICE_INSTANCE_ID"),
            username=username,
            password=password,
            # token=token,
            version=version,
            disable_ssl=disable_ssl
        )


class WxAICredentials(BaseModel):
    """
    Defines the WxAICredentials class to specify the watsonx.ai server details.

    Examples:
        1. Create WxAICredentials with default parameters. By default Dallas region is used.
            .. code-block:: python

                wxai_credentials = WxAICredentials(api_key="...")

        2. Create WxAICredentials by specifying region url.
            .. code-block:: python

                wxai_credentials = WxAICredentials(api_key="...",
                                                   url="https://au-syd.ml.cloud.ibm.com")

        3. Create WxAICredentials by reading from environment variables.
            .. code-block:: python

                os.environ["WATSONX_APIKEY"] = "..."
                # [Optional] Specify watsonx region specific url. Default is https://us-south.ml.cloud.ibm.com .
                os.environ["WATSONX_URL"] = "https://eu-gb.ml.cloud.ibm.com"
                wxai_credentials = WxAICredentials.create_from_env()

        4. Create WxAICredentials for on-prem.
            .. code-block:: python

                wxai_credentials = WxAICredentials(url="https://<hostname>",
                                                   username="..."
                                                   api_key="...",
                                                   version="5.2")

        5. Create WxAICredentials by reading from environment variables for on-prem.
            .. code-block:: python

                os.environ["WATSONX_URL"] = "https://<hostname>"
                os.environ["WATSONX_VERSION"] = "5.2"
                os.environ["WATSONX_USERNAME"] = "..."
                os.environ["WATSONX_APIKEY"] = "..."
                # Only one of api_key or password is needed
                #os.environ["WATSONX_PASSWORD"] = "..."
                wxai_credentials = WxAICredentials.create_from_env()
    """
    url: Annotated[str, Field(
        title="watsonx.ai url",
        description="The url for watsonx ai service",
        default="https://us-south.ml.cloud.ibm.com",
        examples=[
            "https://us-south.ml.cloud.ibm.com",
            "https://eu-de.ml.cloud.ibm.com",
            "https://eu-gb.ml.cloud.ibm.com",
            "https://jp-tok.ml.cloud.ibm.com",
            "https://au-syd.ml.cloud.ibm.com",
        ]
    )]
    api_key: Annotated[str | None, Field(title="Api Key",
                                         description="The user api key. Required for using watsonx as a service and one of api_key or password is required for using watsonx on-prem software.",
                                         strip_whitespace=True,
                                         default=None)]
    version: Annotated[str | None, Field(title="Version",
                                         description="The watsonx on-prem software version. Required for using watsonx on-prem software.",
                                         default=None)]
    username: Annotated[str | None, Field(title="User name",
                                          description="The user name. Required for using watsonx on-prem software.",
                                          default=None)]
    password: Annotated[str | None, Field(title="Password",
                                          description="The user password. One of api_key or password is required for using watsonx on-prem software.",
                                          default=None)]
    instance_id: Annotated[str | None, Field(title="Instance id",
                                             description="The watsonx.ai instance id. Default value is openshift.",
                                             default="openshift")]

    @classmethod
    def create_from_env(cls):
        # possible API key environment variable names
        api_key = get_environment_variable_value(
            ["WXAI_API_KEY", "WATSONX_APIKEY", "WXG_API_KEY"])

        username = get_environment_variable_value(
            ["WXAI_USERNAME", "WATSONX_USERNAME", "WXG_USERNAME"])

        version = get_environment_variable_value(
            ["WXAI_VERSION", "WATSONX_VERSION", "WXG_VERSION"])

        url = get_environment_variable_value(
            ["WXAI_URL", "WATSONX_URL"])

        password = get_environment_variable_value(["WATSONX_PASSWORD"])

        instance_id = get_environment_variable_value(
            ["WATSONX_INSTANCE_ID"], "openshift")

        if version:  # on-prem
            url = get_environment_variable_value(["WATSONX_URL"])
            if not url:
                raise ValueError(
                    "The watsonx url is required and should be set using WATSONX_URL environment variable.")
            if not username:
                raise ValueError(
                    "The username is required and should be set using WATSONX_USERNAME environment variable.")
            if not (api_key or password):
                raise ValueError(
                    "One of api_key or password is required and should be set using WATSONX_APIKEY or WATSONX_PASSWORD environment variable.")
        else:
            # Check the url & update it
            if url in WOS_URL_MAPPING.keys():
                url = WOS_URL_MAPPING.get(url).wml_url

            # If the url environment variable is not found, use the default
            if not url:
                url = "https://us-south.ml.cloud.ibm.com"

            if not api_key:
                raise ValueError(
                    "The api_key is required and should be set using WATSONX_APIKEY environment variable.")

        credentials = {
            "url": url,
            "api_key": api_key,
            "version": version,
            "username": username,
            "password": password,
            "instance_id": instance_id
        }

        return WxAICredentials(
            **credentials
        )


class WxGovConsoleCredentials(BaseModel):
    """
    This class holds the authentication credentials required to connect to the watsonx Governance Console.

    Examples:
        1. Create credentials manually:
            .. code-block:: python

                credentials = WxGovConsoleCredentials(
                    url="https://governance-console.example.com",
                    username="admin",
                    password="securepassword",
                    api_key="optional-api-key"
                )

        2. Create credentials using environment variables:
            .. code-block:: python

                import os

                os.environ['WXGC_URL'] = "https://governance-console.example.com"
                os.environ['WXGC_USERNAME'] = "admin"
                os.environ['WXGC_PASSWORD'] = "securepassword"
                os.environ['WXGC_API_KEY'] = "optional-api-key"  # Optional

                credentials = WxGovConsoleCredentials.create_from_env()
    """
    url: str = Field(
        description="The base URL of the watsonx Governance Console.")
    username: str = Field(description="The username used for authentication.")
    password: str = Field(description="The password used for authentication.")
    api_key: str | None = Field(
        default=None, description="Optional API key for token-based authentication.")

    @classmethod
    def create_from_env(cls):
        return WxGovConsoleCredentials(
            url=os.getenv("WXGC_URL"),
            username=os.getenv("WXGC_USERNAME"),
            password=os.getenv("WXGC_PASSWORD"),
            api_key=os.getenv("WXGC_API_KEY"),
        )


class RITSCredentials(BaseModel):
    hostname: Annotated[
        str | None,
        Field(description="The rits hostname",
              default="https://inference-3scale-apicast-production.apps.rits.fmaas.res.ibm.com"),
    ]
    api_key: str

    @classmethod
    def create_from_env(cls):
        api_key = os.getenv("RITS_API_KEY")
        rits_host = os.getenv(
            "RITS_HOST", "https://inference-3scale-apicast-production.apps.rits.fmaas.res.ibm.com")

        return RITSCredentials(
            hostname=rits_host,
            api_key=api_key,
        )


class OpenAICredentials(BaseModel):
    """
    Defines the OpenAICredentials class to specify the OpenAI server details.

    Examples:
        1. Create OpenAICredentials with default parameters. By default Dallas region is used.
            .. code-block:: python

                openai_credentials = OpenAICredentials(api_key=api_key,
                                                       url=openai_url)

        2. Create OpenAICredentials by reading from environment variables.
            .. code-block:: python

                os.environ["OPENAI_API_KEY"] = "..."
                os.environ["OPENAI_URL"] = "..."
                openai_credentials = OpenAICredentials.create_from_env()
    """
    url: str | None
    api_key: str | None

    @classmethod
    def create_from_env(cls):
        return OpenAICredentials(
            url=os.getenv("OPENAI_URL"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )


class AzureOpenAICredentials(BaseModel):
    url: Annotated[str | None, Field(
        description="Azure OpenAI url. This attribute can be read from `AZURE_OPENAI_HOST` environment variable.",
        serialization_alias="azure_openai_host")]
    api_key: Annotated[str | None, Field(
        description="API key for Azure OpenAI. This attribute can be read from `AZURE_OPENAI_API_KEY` environment variable.")]
    api_version: Annotated[str | None, Field(
        description="The model API version from Azure OpenAI. This attribute can be read from `AZURE_OPENAI_API_VERSION` environment variable.")]

    @classmethod
    def create_from_env(cls):
        return AzureOpenAICredentials(
            url=os.getenv("AZURE_OPENAI_HOST"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        )
