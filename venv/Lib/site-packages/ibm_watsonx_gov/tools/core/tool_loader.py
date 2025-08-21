# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import ast
from typing import Callable, Union

import pandas as pd
from langchain_core.tools import StructuredTool
from pydantic import BaseModel

from ibm_watsonx_gov.utils.python_utils import get

from ..clients import get_tool_info
from ..utils import (TOOL_REGISTRY, get_base64_decoding, get_pydantic_model,
                     validate_envs)
from ..utils.constants import CustomToolType, ServiceProviderType
from ..utils.package_utils import install_and_import_packages


def load_tool(tool_name: str, **kwargs):
    """
        Method to load a tool based on tool name and other parameters

        Args:
            tool_name(str) : 
                    Name of the registered tool
            headers(Optional[headers]): 
                    - Dynamic headers to be supplied to the tool
                    - If the user supplies static headers (whose value do not change) no need of supplying this header while loading.
                    - User is expected to provide the information related to dynamic headers while tool loading . Types of dynamic headers
                        - If the tool is registered with header value $DYNAMIC HEADERS it is mandatory to supply the information while tool loading 
                        - If the tool is registered with convention `headers_key: $header_key` this information should be supplied as part of environment
            **kwargs: 
                    Optional configuration based on the tool .(Eg: Configuration  properties for OOTB tool)

        Returns:
            Tool : A Langchain/Langgraph compatible tool object

        Examples:
        -------
        1. Basic example to load a tool
            .. code-block:: python

                from ibm_watsonx_gov.tools import load_tool
                tool = load_tool(tool_name=<TOOL_NAME>)

        2. Example of tool loading that expects configuration
            .. code-block:: python

                from ibm_watsonx_gov.tools import load_tool
                from ibm_watsonx_gov.tools.clients import get_tool_info

                tool_details = get_tool_info(tool_name=<TOOL_NAME>)
                tool_config = tool_details.get("entity").get("config)
                config = {
                    <Provide the properties as per the details in tool config>
                }
                tool = load_tool(tool_name=<TOOL_NAME>,**config)

        3. Example of tool loading that expects headers 
            .. code-block:: python

                from ibm_watsonx_gov.tools import load_tool
                from ibm_watsonx_gov.tools.clients import get_tool_info

                tool_details = get_tool_info(tool_name=<TOOL_NAME>)
                headers = tool_details.get("entity").get("endpoint").get("headers")

                headers = {
                    "Authorization":"Bearer __TOKEN__"  #Need to supply dynamic headers
                }
                tool = load_tool(tool_name=<TOOL_NAME>,headers=headers)
    """
    # Get the tool information
    tool_details = get_tool_info(tool_name=tool_name)

    # Get service provider type
    service_provider_type = get(tool_details, "entity.service_provider_type")
    tool_name = get(tool_details, "entity.tool_name")
    env_list = get(tool_details, "entity.environment_variables", [])

    # Validate the env for loading the tool
    validate_envs(env_list)

    # Load the tool based on the service provider type
    try:
        if service_provider_type == ServiceProviderType.CUSTOM.value:
            tool_description = get(tool_details, "entity.description")
            tool_schema = get(tool_details, "entity.schema")
            tool_type = get(tool_details, "entity.tool_type")
            dependencies = get(
                tool_details, "entity.dependencies.run_time_packages")
            if len(dependencies) > 0:
                dependencies = [package for package in dependencies if not package.startswith(
                    "ibm-watsonx-gov")]
                install_and_import_packages(dependencies)

            if tool_type == CustomToolType.CODE.value:
                # This is a code based tool
                encode_tool_code = get(
                    tool_details, "entity.code.source_code_base64")
                tool_code = get_base64_decoding(encode_tool_code)
                return _load_custom_tool(tool_name,
                                         tool_description,
                                         tool_code,
                                         tool_schema,
                                         **kwargs)
            elif tool_type == CustomToolType.ENDPOINT.value:
                tool_endpoint = get(tool_details, "entity.endpoint.url")
                headers = get(tool_details, "entity.endpoint.headers", {})
                arg_headers = kwargs.get("headers", {})
                tool_headers = headers | arg_headers
                method = get(tool_details, "entity.endpoint.method", "POST")
                return _load_restapi_tool(tool_name,
                                          tool_description,
                                          tool_endpoint,
                                          tool_schema,
                                          tool_headers,
                                          method=method)
        elif service_provider_type == ServiceProviderType.IBM.value:
            return _load_ootb_tool(tool_name, **kwargs)
        else:
            raise Exception(
                f"service_provide_type:{service_provider_type} is not supporteds. Acceptable values:{ServiceProviderType.values()}")
    except Exception as ex:
        raise Exception(f"Error loading tool {tool_name}. Details:{str(ex)}")


def _load_ootb_tool(tool_name: str = None, **kwargs) -> Callable:
    """
    Load the OOTB tool using the tool name

    Args:
        tool_name (str): Name of the OOTB tool

    Returns:
        Callable: OOTB Tool loaded from the tool registry
    """
    if tool_name is None:
        raise Exception("'tool_name' parameter is missing.")

    tool_class_path = TOOL_REGISTRY.get(tool_name, None)
    if tool_class_path is None:
        raise Exception(f"OOTB tool  {tool_name} is not available")

    module_path, _, class_name = tool_class_path.rpartition('.')
    tool_module = __import__(module_path, fromlist=[f"{class_name}"])

    return getattr(tool_module, class_name)(**kwargs)


def _load_custom_tool(tool_name: str,
                      tool_description: str,
                      tool_code: str,
                      tool_schema: dict,
                      **kwargs) -> Callable:
    """Method to create custom tool 

    Args:
        tool_name (str): Name of the agent tool
        tool_description (str): Description of agent tool
        tool_code (str): Tool code in the form of doc string 
        tool_schema (dict): JSON args schema to be supplied for converting tool

    Returns:
        Callable: Custom tool created using the tool code
    """

    def call_tool(**kwargs):
        tree = ast.parse(tool_code, mode="exec")
        function_name = tree.body[0].name
        compiled_code = compile(tree, 'custom_tool', 'exec')
        namespace = {}
        exec(compiled_code, namespace)
        return namespace[function_name](**kwargs)

    title = tool_name + \
        "_schema" if tool_schema.get(
            'title') is None else tool_schema.get('title')

    tool = StructuredTool(
        name=tool_name,
        description=tool_description,
        func=call_tool,
        args_schema=get_pydantic_model(title, tool_schema)
    )
    return tool


def _load_restapi_tool(tool_name: str,
                       tool_description: str,
                       tool_endpoint: str,
                       tool_schema: Union[dict, BaseModel],
                       headers: dict = {},
                       method='POST') -> Callable:
    """Method to create custom tool

    Args:
        tool_name (str): Name of the agent tool 
        tool_description (str): Description of the agent tool 
        tool_endpoint (str): RestEndpoint to be used as a tool 
        tool_schema (Union[dict, BaseModel]): Tool schema 
        headers (dict,optional): Headers to be used while calling the tool .Defaults to {}
        method (str, optional): _description_. Defaults to 'POST'.

    Returns:
        Callable: RESTAPI tool created using the template tool
    """
    from ..rest_api import RestApiTool, load_headers
    if isinstance(tool_schema, dict):

        title = tool_name + \
            "_schema" if tool_schema.get(
                'title') is None else tool_schema.get('title')

        args_schema = get_pydantic_model(title, tool_schema)
    else:
        args_schema = tool_schema

    # Load headers with envs as needed
    headers = load_headers(tool_name, headers)

    tool = RestApiTool(
        name=tool_name,
        description=tool_description,
        endpoint=tool_endpoint,
        method=method,
        headers=headers,
        args_schema=args_schema
    )
    return tool
