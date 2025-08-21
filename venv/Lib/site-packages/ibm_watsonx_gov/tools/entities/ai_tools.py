# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Any, Dict, List, Optional

from pydantic import BaseModel, Field, model_validator
from pydantic_core import PydanticCustomError

from ..utils.constants import (Categories, CustomToolType, Framework,
                               PatchOperationTypes, ServiceProviderType)
from ..utils.python_utils import get_base64_encoding


class AIToolRuntimeDetails(BaseModel):
    engine: Annotated[
        str,
        Field(
            ...,
            description="Python version required by the tool."
        )
    ]
    cpu_capacity: Annotated[
        Optional[str],
        Field(
            default=None,
            description="CPU capacity required by the tool."
        )
    ]
    memory: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Memory required by the tool."
        )
    ]


class AIToolCodePayload(BaseModel):
    source: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Source location of the tool's code."
        )
    ]
    commit: Annotated[
        Optional[str],
        Field(
            default=None
        )
    ]
    language: Annotated[
        Optional[str],
        Field(
            default="python",
            description="Language used in the code"
        )
    ]
    source_code_url: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Remote URL for accessing the source code. Currently, only GitHub URLs are supported."
        )
    ]
    source_code_base64: Annotated[
        Optional[str],
        Field(
            ...,
            description="Source code for invoking the tool.",
        )
    ]
    run_time_details: Annotated[
        Optional[AIToolRuntimeDetails],
        Field(
            ...,
            description="Runtime details required for executing the source code."
        )
    ]

    @model_validator(mode='before')
    @classmethod
    def accept_multiple_field_names(cls, data):
        if "source_code" in data and "source_code_base64" not in data:
            data["source_code_base64"] = data["source_code"]
        return data


class AIToolEndpointPayload(BaseModel):
    url: Annotated[
        str,
        Field(
            ...,
            description="URL to access the endpoint."
        )
    ]
    method: Annotated[
        str,
        Field(
            ...,
            description="Method to access the endpoint."
        )
    ]
    headers: Annotated[
        Dict[str, Any],
        Field(
            ...,
            description="Headers required to call the endpoint."
        )
    ]


class AIToolUsedInApplication(BaseModel):
    inventory_id: Annotated[
        str,
        Field(
            ...,
            description="Inventory ID of the application where the tool is used."
        )
    ]
    agent_asset_id: Annotated[
        str,
        Field(
            ...,
            description="Agent ID of the application where the tool is used."
        )
    ]


class AIToolDependencies(BaseModel):
    remote_services: Annotated[
        list[str],
        Field(
            default=None,
        )
    ]
    run_time_packages: Annotated[
        list[str],
        Field(
            default=None,
        )
    ]


class AIToolBenchmark(BaseModel):
    avg_latency: Annotated[
        str,
        Field(
            default=None,
        )]
    dataset: Annotated[
        str,
        Field(
            ...,
            description="GitHub URL for the dataset."
        )]
    records: Annotated[
        int,
        Field(
            ...,
            description="Number of records contained in the dataset."
        )]


class AIToolSchema(BaseModel):
    title: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Title for schema."
        )]
    type: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Type of schema."
        )]
    properties: Annotated[
        dict,
        Field(
            ...,
            description="Properties for schema."
        )]
    required: Annotated[
        Optional[list],
        Field(
            default=None,
            description="Required for schema."
        )]


class ToolRegistrationPayload(BaseModel):
    tool_name: Annotated[
        str,
        Field(
            ...,
            description="Unique name for the tool"
        )
    ]
    display_name: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Unique name for displaying the tool."
        )
    ]
    service_provider_type: Annotated[
        Optional[ServiceProviderType],
        Field(
            default=ServiceProviderType.CUSTOM,
            description=f"Service provider type. Allowed values are: {ServiceProviderType.values()}."
        )
    ]
    tool_type: Annotated[
        Optional[CustomToolType],
        Field(
            default=CustomToolType.CODE,
            description=f"Type of the tool. Allowed tool types are: {CustomToolType.values()}."
        )
    ]
    description: Annotated[
        str,
        Field(
            ...,
            description="Short description about the tool."
        )
    ]
    summary: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Summary of the tool."
        )
    ]
    development_uri_link: Annotated[
        Optional[str],
        Field(
            default=None
        )
    ]
    inventory_id: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Inventory ID in which the asset needs to be created."
        )
    ]
    reusable: Annotated[
        bool,
        Field(
            default=True,
            description="Specify the tool will be reusable."
        )
    ]
    framework: Annotated[
        list[Framework],
        Field(
            default_factory=lambda: [Framework.LANGCHAIN, Framework.LANGGRAPH],
            description="Specify the framework used by the tool."
        )
    ]
    category: Annotated[
        List[Categories],
        Field(
            default_factory=lambda: [Categories.OTHER],
            description=f"Specify the category under which the tool will be classified. Allowed values are {Categories.values()}."
        )
    ]
    used_in_applications: Annotated[
        Optional[List[AIToolUsedInApplication]],
        Field(
            default=None,
            description="List of applications where this tool is used."
        )
    ]
    code: Annotated[
        Optional[AIToolCodePayload],
        Field(
            default=None,
            description="Code-related information for the tool."
        )
    ]
    endpoint: Annotated[
        Optional[AIToolEndpointPayload],
        Field(
            default=None,
            description="Endpoint-related information for the tool."
        )
    ]
    dependencies: Annotated[
        Optional[AIToolDependencies],
        Field(
            default=None,
            description="Dependencies required by this tool."
        )
    ]
    config: Annotated[
        Optional[Dict],
        Field(
            default=None,
            description="Configuration information for this tool."
        )
    ]
    schema_: Annotated[
        AIToolSchema,
        Field(
            ...,
            description="Schema information for this tool.",
            alias="schema"
        )
    ]
    environment_variables: Annotated[
        Optional[list[str]],
        Field(
            default=None,
            description="Environment variables required by this tool."
        )
    ]
    metrics: Annotated[
        Optional[Dict],
        Field(
            default=None,
            description="Metrics and their respective values."
        )
    ]
    pricing: Annotated[
        Optional[Dict],
        Field(
            default=None,
            description="Type of currency and its corresponding price."
        )
    ]
    benchmark_test: Annotated[
        Optional[AIToolBenchmark],
        Field(
            default=None,
            description="Benchmark test details."
        )
    ]

    @model_validator(mode='before')
    @classmethod
    def check_tool_type(cls, data):
        if "tool_type" not in data:
            data["tool_type"] = CustomToolType.CODE.value
        if data["tool_type"] == CustomToolType.CODE.value and "code" in data and "endpoint" in data:
            data["endpoint"] = None
        if data["tool_type"] == CustomToolType.ENDPOINT.value and "code" in data and "endpoint" in data:
            data["code"] = None
        return data

    @model_validator(mode="after")
    def validate_post_payload(self):
        if self.tool_type == CustomToolType.CODE and not self.code:
            raise PydanticCustomError(
                "missing code_payload", 'tool_type is "code", but code field missing in payload.'
            )

        if self.tool_type == CustomToolType.CODE and not self.code.source_code_url and not self.code.source_code_base64:
            raise PydanticCustomError(
                "missing_source_code ", 'Missing both source_code_url and source_code_base64.'
            )

        if self.code and self.code.source_code_base64:
            self.code.source_code_base64 = get_base64_encoding(
                tool_code=self.code.source_code_base64)

        if self.tool_type == CustomToolType.ENDPOINT and not self.endpoint:
            raise PydanticCustomError(
                "missing_endpoint_payload", 'tool_type is "endpoint", but endpoint field missing in payload.'
            )

        if self.service_provider_type.value == ServiceProviderType.IBM.value:
            raise Exception(f"The service provider type 'IBM' is not supported. Supported service provider type are: 'custom'")

        if not self.display_name:
            self.display_name = self.tool_name

        return self


class PatchPayload(BaseModel):
    op: Annotated[
        PatchOperationTypes,
        Field(
            ...,
            description="Type of operation to be performed."
        )
    ]
    path: Annotated[
        str,
        Field(
            ...,
            description="Path of the field on which the operation needs to be performed."
        )
    ]
    value: Annotated[
        Any,
        Field(
            ...,
            description="The value to be applied during the specified operation on the given field path."
        )
    ]

    @model_validator(mode="after")
    def validate_patch_payload(self):
        if "source_code_base64" in self.path:
            self.value = get_base64_encoding(tool_code=self.value)
        return self


class ToolUpdatePayload(BaseModel):
    payload: Annotated[
        list[PatchPayload],
        Field(
            ...,
            description="List of patch payloads used to perform the patch operation."
        )
    ]

    @model_validator(mode='before')
    @classmethod
    def validate_ai_tool_patch_payload(cls, values):
        if "payload" not in values or not isinstance(values.get("payload"), list):
            raise PydanticCustomError(
                "Invalid_payload",
                "The payload is either missing or not in a valid list format."
            )
        return values
