# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any, Annotated
from pydantic_core import PydanticCustomError
from ..utils.constants import ServiceProviderType
from ibm_watsonx_gov.tools.utils.constants import CustomToolType, PatchOperationTypes, Framework, Categories
from ibm_watsonx_gov.tools.utils.python_utils import get_base64_encoding


class AIAgentParentApplication(BaseModel):
    inventory_id: Annotated[
        str,
        Field(
            ...,
            description="Inventory ID of the parent application."
        )
    ]
    agent_id: Annotated[
        str,
        Field(
            ...,
            description="Agent ID of the parent application"
        )
    ]


class AIAgentUsedInApplication(BaseModel):
    inventory_id: Annotated[
        str,
        Field(
            ...,
            description="Inventory ID of the application where the agent is used."
        )
    ]
    agent_asset_id: Annotated[
        str,
        Field(
            ...,
            description="Agent ID of the application where the agent is used."
        )
    ]


class AIAgentRuntimeDetails(BaseModel):
    engine: Annotated[
        str,
        Field(
            ...,
            description="Python version required by the agent."
        )
    ]
    cpu_capacity: Annotated[
        Optional[str],
        Field(
            default=None,
            description="CPU capacity required by the agent."
        )
    ]
    memory: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Memory required by the agent."
        )
    ]


class AIAgentCodePayload(BaseModel):
    source: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Source location of the agent's code."
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
    source_code: Annotated[
        Optional[str],
        Field(
            ...,
            description="Source code encoded in Base64 format.",
            alias="source_code_base64"
        )
    ]
    run_time_details: Annotated[
        AIAgentRuntimeDetails,
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


class AIAgentEndpointPayload(BaseModel):
    url: Annotated[
        str,
        Field(
            ...,
            description="URL to access the endpoint."
        )
    ]
    headers: Annotated[
        Dict[str, str],
        Field(
            ...,
            description="Headers required to call the endpoint."
        )
    ]
    method: Annotated[
        str,
        Field(
            ...,
            description="Method to call the endpoint."
        )
    ]


class AIAgentTool(BaseModel):
    inventory_id: Annotated[
        str,
        Field(
            ...,
            description="Inventory ID of the tool where the application is used."
        )
    ]
    tool_id: Annotated[
        str,
        Field(
            ...,
            description="Tool ID of the tool where the application is used."
        )
    ]


class AIAgentDependencies(BaseModel):
    remote_services: Annotated[
        list[str],
        Field(
            ...,
        )
    ]
    run_time_packages: Annotated[
        list[str],
        Field(
            ...,
        )
    ]


class AIAgentSchema(BaseModel):
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


class AgentRegistrationPayload(BaseModel):
    display_name: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Unique name for displaying the agent."
        )
    ]
    agent_name: Annotated[
        str,
        Field(
            ...,
            description="Unique name for the agent"
        )
    ]
    description: Annotated[
        str,
        Field(
            ...,
            description="Short description about the agent."
        )
    ]
    inventory_id: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Inventory ID in which the asset needs to be created."
        )
    ]
    summary: Annotated[
        Optional[str],
        Field(
            default=None,
            description="Summary of the agent."
        )
    ]
    service_provider_type: Annotated[
        Optional[ServiceProviderType],
        Field(
            default=ServiceProviderType.CUSTOM,
            description=f"Service provider type. Allowed values are: {ServiceProviderType.values()}."
        )
    ]
    framework: Annotated[
        Optional[list[Framework]],
        Field(
            default_factory=lambda: [Framework.LANGGRAPH],
            description="Specify the framework used by the agent."
        )
    ]
    category: Annotated[
        Optional[list[Categories]],
        Field(
            default_factory=lambda: [Categories.OTHER],
            description=f"Specify the category under which the agent will be classified. Allowed values are {Categories.values()}."
        )
    ]
    agent_type: Annotated[
        Optional[CustomToolType],
        Field(
            default=CustomToolType.ENDPOINT,
            description=f"Type of the agent. Allowed agent types are: {CustomToolType.values()}."
        )
    ]
    development_implementation_url: Annotated[
        Optional[str],
        Field(
            default=None,
        )
    ]
    validation_implementation_url: Annotated[
        Optional[str],
        Field(
            default=None,
        )
    ]
    implementation_url: Annotated[
        Optional[str],
        Field(
            default=None,
        )
    ]
    reusable: Annotated[
        bool,
        Field(
            default=False,
            description="Specify the agent will be reusable."
        )
    ]
    version: Annotated[
        Optional[str],
        Field(
            default=None,
        )
    ]
    parent_applications: Annotated[
        Optional[list[AIAgentParentApplication]],
        Field(
            default=None,
            description="List of parent applications"
        )
    ]
    tools: Annotated[
        Optional[list[AIAgentTool]],
        Field(
            default=None,
            description="List of tools used in this applications"
        )
    ]
    used_in_applications: Annotated[
        Optional[list[AIAgentUsedInApplication]],
        Field(
            default=None,
            description="List of applications where this application is used."
        )
    ]
    code: Annotated[
        Optional[AIAgentCodePayload],
        Field(
            default=None,
            description="Code-related information for the agent."
        )
    ]
    endpoint: Annotated[
        Optional[AIAgentEndpointPayload],
        Field(
            default=None,
            description="Endpoint-related information for the agent."
        )
    ]
    dependencies: Annotated[
        Optional[AIAgentDependencies],
        Field(
            default=None,
            description="Dependencies required by this agent."
        )
    ]
    metrics: Annotated[
        Optional[dict],
        Field(
            default=None,
            description="Metrics and their respective values."
        )
    ]
    benchmark_test: Annotated[
        Optional[dict],
        Field(
            default=None,
            description="Benchmark test details."
        )
    ]
    pricing: Annotated[
        Optional[dict],
        Field(
            default=None,
            description="Type of currency and its corresponding price."
        )
    ]
    schema_: Annotated[
        Optional[AIAgentSchema],
        Field(
            default=None,
            description="Schema information for this agent.",
            alias="schema"
        )
    ]

    environment_variables: Annotated[
        Optional[list[str]],
        Field(
            default=None,
            description="Environment variables required by this agent."
        )
    ]

    @model_validator(mode="before")
    @classmethod
    def check_required_fields(cls, values):
        if 'agent_name' not in values or not values['agent_name']:
            raise ValueError("Missing required field: 'agent_name'. Please provide a unique name for the agent.")
        if "agent_type" not in values:
            values["agent_type"] = CustomToolType.ENDPOINT.value
        if values["agent_type"] == CustomToolType.ENDPOINT.value and "code" in values:
            values["code"] = None
        if values["agent_type"] == CustomToolType.CODE.value and "endpoint" in values:
            values["endpoint"] = None
        return values

    @model_validator(mode="after")
    def validate_post_payload(self):
        if self.agent_type == CustomToolType.CODE and not self.code:
            raise PydanticCustomError(
                "missing code_payload", 'agent_type is "code", but code field missing in payload.'
            )

        if self.agent_type == CustomToolType.ENDPOINT and not self.endpoint:
            raise PydanticCustomError(
                "missing_endpoint_payload", 'agent_type is "endpoint", but endpoint field missing payload'
            )

        if self.code and self.code.source_code:
            self.code.source_code = get_base64_encoding(tool_code=self.code.source_code)

        if not self.display_name:
            self.display_name = self.agent_name

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


class AgentUpdatePayload(BaseModel):
    payload: Annotated[
        list[PatchPayload],
        Field(
            ...,
            description="List of patch payloads used to perform the patch operation."
        )
    ]

    @model_validator(mode='before')
    @classmethod
    def validate_ai_agent_patch_payload(cls, values):
        if "payload" not in values or not isinstance(values.get("payload"), list):
            raise PydanticCustomError(
                "Invalid_payload",
                "The payload is either missing or not in a valid list format."
            )
        return values
