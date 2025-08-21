# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from enum import Enum


class CustomToolType(Enum):
    CODE = "code"
    ENDPOINT = "endpoint"

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class ServiceProviderType(Enum):
    IBM = "IBM"
    CUSTOM = "custom"

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class Categories(Enum):
    SEARCH = "Search"
    GUARDRAILS = "Guardrails"
    QUERY = "Query"
    RAG = "RAG"
    EVALUATION = "Evaluation"
    OTHER = "Other"

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class PatchOperationTypes(Enum):
    ADD = "add"
    REMOVE = "remove"
    REPLACE = "replace"

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class ComponentTypes(Enum):
    AI_TOOL = "ai_tool"
    AI_AGENT = "ai_agent"

    @classmethod
    def values(cls):
        return [member.value for member in cls]


class Framework(Enum):
    LANGCHAIN = "langchain"
    LANGGRAPH = "langgraph"

    @classmethod
    def values(cls):
        return [member.value for member in cls]
