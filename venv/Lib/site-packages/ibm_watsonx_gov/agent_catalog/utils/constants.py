# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from enum import Enum


class ServiceProviderType(Enum):
    WML = "wml"
    CUSTOM = "custom"

    @classmethod
    def values(cls):
        return [member.value for member in cls]

class AgentType(Enum):
    CODE = "code"
    ENDPOINT = "endpoint"

    @classmethod
    def values(cls):
        return [member.value for member in cls]

class Framework(Enum):
    LANGCHAIN = "langchain"
    LANGGRAPH = "langgraph"

    @classmethod
    def values(cls):
        return [member.value for member in cls]
