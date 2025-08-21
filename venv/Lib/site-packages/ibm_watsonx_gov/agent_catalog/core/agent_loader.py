# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import ast
from typing import Callable, Dict, Set, Union

import pandas as pd
from ibm_watsonx_gov.agent_catalog.core.agents import (AgentInterface,
                                                       LangChainAgent,
                                                       LangGraphAgent,
                                                       RestAgent)
from ibm_watsonx_gov.tools.utils.python_utils import get_base64_decoding
from ibm_watsonx_gov.utils.python_utils import get

from ..clients.ai_agent_client import get_agent_by_name
from ..utils.constants import AgentType, Framework, ServiceProviderType


def load_agent(agent_name: str, **kwargs) -> AgentInterface:
    """
    Loads the agent based on agent name and framework information
    
    Args:
        agent_name: Agent name
    Returns:
        AgentInterface: The agent instance
    """

    agent_details = get_agent_by_name(agent_name=agent_name)

    # Get service provider type
    service_provider_type = get(agent_details, "entity.service_provider_type")
    agent_name = get(agent_details, "entity.agent_name")
    agent_type = get(agent_details, "entity.agent_type")

    # Load the agent based on the service provider type
    try:
        if service_provider_type == ServiceProviderType.CUSTOM.value:
    
            framework = get(agent_details, "entity.framework")
            if agent_type == AgentType.CODE.value and Framework.LANGGRAPH.value in framework:
                # This is a code based agent
                agent_encode_code = get(
                    agent_details, "entity.code.source_code_base64")
                
                agent_graph = _get_agent_instance(agent_encode_code)
                return LangGraphAgent(agent_graph, **kwargs)
            
            elif agent_type == AgentType.CODE.value and Framework.LANGCHAIN.value in framework:
                # This is a code based agent
                agent_encode_code = get(
                    agent_details, "entity.code.source_code_base64")
                
                agent_instance = _get_agent_instance(agent_encode_code)
                
                return LangChainAgent(agent_instance, **kwargs)
            
            elif agent_type == AgentType.ENDPOINT.value:

                endpoint = get(agent_details, "entity.endpoint.url")
                method = get(agent_details, "entity.endpoint.method")
                agent_headers = get(agent_details, "entity.endpoint.headers", {})
                input_headers = kwargs.get("headers", {})
                headers = agent_headers | input_headers
                
                return RestAgent(endpoint, headers, method, **kwargs)

        if service_provider_type == ServiceProviderType.WML.value:
            from ...tools.utils.tool_utils import get_token

            endpoint = get(agent_details, "entity.endpoint.url")
            method = get(agent_details, "entity.endpoint.method")
            agent_headers = get(agent_details, "entity.endpoint.headers", {})
            auth_token = get_token()
            agent_headers.update({"Authorization": "Bearer "+  auth_token})

            arg_headers = kwargs.get("headers", {})
            input_headers = agent_headers | arg_headers
            
            return RestAgent(endpoint, input_headers, method)

    except Exception as ex:
        raise Exception(f"Error loading agent {agent_name}. Details:{str(ex)}")


def invoke(agent: AgentInterface, input_data: dict) -> dict:
    """
    Executes the agent that implements AgentInterface.

    Args:
        agent (AgentInterface): The agent instance to invoke.
        input_data (dict): Input to pass to the agent.

    Returns:
        dict: Output from the agent.
    """
    
    return agent.invoke(input_data)


def get_agent_input_data_from_schema(schema: dict):

    """
    Generates  the input data based on the schema

    Args:
        schema (dict): agent schema.

    Returns:
        str: Input data to pass to the agent.
    """
    
    schema_type = schema.get("type")

    if schema_type == "object":
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        result = {}
        for key, prop_schema in properties.items():
            result[key] = get_agent_input_data_from_schema(prop_schema)
        
        return result

    elif schema_type == "array":
        item_schema = schema.get("items", {})
        return [get_agent_input_data_from_schema(item_schema)]

    elif schema_type == "string":
        return "<string value>"

    elif schema_type in ["float","double"]:
        return "<float/double value>"

    elif schema_type in ["integer","number"]:
        return "<integer value>"
    

    elif schema_type == "boolean":
        return "<boolean value>"

    else:
        return None 

def _get_agent_instance(agent_encoded_code: str) -> object:
    """
    Dynamically parses, compiles, and executes python agent code from a string,
    and returns the result of calling the main agent function.

    Assumes the agent code string defines at least one function, with the 
    last function in the code being the one to execute.

    Args:
        agent_encoded_code (str): encoded code

    Returns:
        object: The result of executing the main agent function.
    """

    agent_decode_code = get_base64_decoding(agent_encoded_code)

    tree = ast.parse(agent_decode_code, mode="exec")
    tree_len = len(tree.body)
    ## get main agent function name 
    function_name = tree.body[tree_len-1].name
    
    namespace = {}
    exec(agent_decode_code, namespace)
    compiled_agent = namespace[function_name]()

    return compiled_agent
