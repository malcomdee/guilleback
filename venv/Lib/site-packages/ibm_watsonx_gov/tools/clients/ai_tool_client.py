# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Union

from ibm_watsonx_gov.utils.python_utils import get
from ibm_watsonx_gov.utils.rest_util import RestUtil

from ..entities.ai_tools import ToolRegistrationPayload, ToolUpdatePayload
from ..utils import environment
from ..utils.constants import (Categories, ComponentTypes, CustomToolType,
                               Framework, ServiceProviderType)
from ..utils.python_utils import process_result
from ..utils.tool_utils import get_default_inventory, get_headers, get_token

environment.get_base_url() # This is used to validate the base_url at the initial stage.

# Creating AI Tool asset
def register_tool(payload: Union[dict, ToolRegistrationPayload]):
    """
    Registers a new tool by converting the provided payload to an ToolRegistrationPayload instance.
    And then call the tool registration endpoint.

    Args:
        payload (Union[dict, ToolRegistrationPayload]): The payload to register the tool.
            It can either be a dictionary or an instance of ToolRegistrationPayload.

    Returns:
        dict: The processed result from the tool registration API.

    Examples:
    ---------
    1. Using ToolRegistrationPayload model:
        .. code-block:: python

            from ibm_watsonx_gov.tools.clients import register_tool, ToolRegistrationPayload
            post_payload = {
                "tool_name": "add",
                "description":"Use GooglSearch and return results for given query"
                "code": {
                    "source_code_base64": '''
                            def add(num1: int, num2: int):
                                return num1 + num2
                    ''',
                    "run_time_details": {
                        "engine": "python 3.11.0"
                    }
                },
                "schema":{
                        "properties": {
                            "num1": {
                                "description": "First number",
                                "title": "num1",
                                "type": "integer",
                            },
                            "query": {
                                "description": "Second number",
                                "title": "num2",
                                "type": "integer",
                            }
                        }
                    }
             }
            response = register_tool(ToolRegistrationPayload(**post_payload))
    2. Using Dict:
        .. code-block:: python

            from ibm_watsonx_gov.tools.clients.ai_tool_client import register_tool, Framework
            post_payload = {
             "tool_name": "add",
             "code": {
                "source_code_base64": '''
                        def add(num1: int, num2: int):
                            return num1 + num2
                ''',
                "run_time_details": {
                    "engine": "python 3.11.0"
                }
             },
             "schema":{
                    "properties": {
                        "num1": {
                            "description": "First number",
                            "title": "num1",
                            "type": "integer",
                        },
                        "query": {
                            "description": "Second number",
                            "title": "num2",
                            "type": "integer",
                        }
                    }
                }
             }
            response = register_tool(payload=post_payload)
"""
    if isinstance(payload, dict):
        post_payload = ToolRegistrationPayload(**payload)
    elif isinstance(payload, ToolRegistrationPayload):
        post_payload = payload
    else:
        raise Exception(
            "Invalid payload format. Only dict and ToolRegistrationPayload are allowed.")

    # Consider default inventory if no inventory_id is supplied
    if not post_payload.inventory_id:
        post_payload.inventory_id = get_default_inventory()

    verify = environment.get_ssl_verification()
    payload = post_payload.model_dump(
        mode="json", exclude_none=True, by_alias=True)
    url = f"{environment.get_base_url()}/v1/aigov/factsheet/ai_components/tools"
    response = RestUtil.request_with_retry(retry_count=2).post(
        url, json=payload, headers=get_headers(), verify=verify)

    if not response.ok:
        message = f"Error occurred while registering tool:{post_payload.tool_name}. Status code: {response.status_code}, Error: {response.text}"
        raise Exception(message)

    return process_result(response)


# Getting AI Tool asset
def get_tool(tool_id: str, inventory_id: str, **kwargs):
    """
        Retrieves the details of a specific tool based on the given tool ID and inventory ID.

        Args:
            tool_id (str): The ID of the tool to be retrieved.
            inventory_id (str): The ID of the inventory to fetch the tool from.

        Returns:
            dict: The processed result containing tool details.

        Example:
        --------
            .. code-block:: python

                from ibm_watsonx_gov.tools.clients.ai_tool_client import get_tool
                tool_id = '23dd7ec8-3d13-4f8f-a485-10278287bxxx'
                inventory_id = '81b1b891-0ded-46ca-bc3f-155e98a15xxx'
                response = get_tool(tool_id=tool_id, inventory_id=inventory_id)
        """
    verify = environment.get_ssl_verification()
    url = f"{environment.get_base_url()}/v1/aigov/factsheet/ai_components/tools/{tool_id}?inventory_id={inventory_id}"
    response = RestUtil.request_with_retry(
        etry_count=2).get(url=url, headers=get_headers(), verify=verify)
    # Added for purpose of printing tool_name when called from get_tool_info
    tool_name = kwargs.get("tool_name", tool_id)

    if not response.ok:
        message = f"Error occurred while getting tool {tool_name} details. Status code: {response.status_code}, Error: {response.text}"
        raise Exception(message)

    return process_result(response)


# Updating AI Tool asset
def update_tool(tool_id: str, inventory_id: str, payloads: Union[list[dict], ToolUpdatePayload]):
    """
    Patches the tool information based on the provided tool ID, inventory ID, and payloads.

    Args:
        tool_id (str): The ID of the tool to be patched.
        inventory_id (str): The ID of the inventory to which the tool contains.
        payloads (list[Union[dict, ToolUpdatePayload]]): A list of dictionaries or `ToolUpdatePayload` instances containing the update information for the tool.

    Returns:
        dict: The processed result from the tool update API.

    Notes:
        - Each item in the `payloads` list should be either a dictionary or an instance of `ToolUpdatePayload`.
        - If a dictionary is provided, it is converted into an `ToolUpdatePayload` instance.

    Examples:
    ---------
    Using ToolUpdatePayload model:
        .. code-block:: python

            from ibm_watsonx_gov.tools.clients.ai_tool_client import update_tool, ToolUpdatePayload, OPERATION_TYPE
            patch_payload = [
             {
                "op": OPERATION_TYPE.REPLACE.value,
                "path": "/reusable",
                "value": False
            },
            {
                "op": OPERATION_TYPE.REPLACE.value,
                "path": "/metrics",
                "value": {
                    "roc": "64"
                }
            }
            ]
            update_payload = ToolUpdatePayload(**patch_payload)
            response = update_tool(payload = update_payload)
    Using Dict:
        .. code-block:: python

            from ibm_watsonx_gov.tools.clients.ai_tool_client import update_tool, OPERATION_TYPE
            patch_payload = [
             {
                "op": OPERATION_TYPE.REPLACE.value,
                "path": "/reusable",
                "value": False
            },
            {
                "op": OPERATION_TYPE.REPLACE.value,
                "path": "/metrics",
                "value": {
                    "roc": "64"
                }
            }
            ]
            response = update_tool(payload = patch_payload)
"""

    if isinstance(payloads, list):
        patch_payload = ToolUpdatePayload(**{"payload": payloads})
    elif isinstance(payloads, ToolUpdatePayload):
        patch_payload = payloads
    else:
        raise TypeError(
            f"Invalid payload type: {type(payloads)}. Expected list[dict] or ToolUpdatePayload.")

    verify = environment.get_ssl_verification()
    payload = patch_payload.model_dump(mode="json")['payload']
    tool_patch_url = f"{environment.get_base_url()}/v1/aigov/factsheet/ai_components/tools/{tool_id}?inventory_id={inventory_id}"
    response = RestUtil.request_with_retry(retry_count=2).patch(
        url=tool_patch_url, headers=get_headers(), json=payload, verify=verify)

    if not response.ok:
        message = f"Error occurred while updating tool with id {tool_id}. Status code: {response.status_code}, Error: {response.text}"
        raise Exception(message)
    return process_result(response)


# Deleting AI Tool asset
def delete_tool(tool_id: str, inventory_id: str, **kwargs):
    """
    Delete the AI tool based on the tool_id and inventory_id

    Args:
        tool_id (str): The ID of the tool to be deleted.
        inventory_id (str): The ID of the inventory to which the tool contains.

    Returns:
       AI Tool Deleted Successfully

    Example:
    --------
        .. code-block:: python

            from ibm_watsonx_gov.tools.clients.ai_tool_client import delete_tool
            tool_id = '23dd7ec8-3d13-4f8f-a485-10278287bxxx'
            inventory_id = '81b1b891-0ded-46ca-bc3f-155e98a15xxx'
            response = delete_tool(tool_id=tool_id, inventory_id=inventory_id)
    """

    verify = environment.get_ssl_verification()
    url = f"{environment.get_base_url()}/v1/aigov/factsheet/ai_components/tools/{tool_id}?inventory_id={inventory_id}"
    response = RestUtil.request_with_retry(
        retry_count=2).delete(url=url, headers=get_headers(), verify=verify)
    # Added for purpose of printing tool_name when called from get_tool_info
    tool_name = kwargs.get("tool_name", tool_id)
    if not response.ok:
        message = f"Error occurred while updating tool with id {tool_name}. Status code: {response.status_code}, Error: {response.text}"
        raise Exception(message)

    if response.text:
        return process_result(response.text)
    return "Tool Deleted Successfully"


# Listing all AI Tools
def list_tools(service_provider_type: Union[list[str], str] = None, category: Union[list[str], str] = None,
               inventory_id: Union[list[str], str] = None, framework: Union[list[str], str] = None,
               tool_name: Union[list[str], str] = None, run_time_details: Union[list[str], str] = None,
               search_text: Union[list[str], str] = None):
    """
        Retrieves a list of registered AI tools based on the provided filter criteria.

        All parameters are optional. If no filters are provided, all tools will be listed.

       Args:
           service_provider_type (Union[list[str], str], optional): Filter tools by one or more service provider types.
           category (Union[list[str], str], optional): Filter tools by one or more categories.
           inventory_id (Union[list[str], str], optional): Filter tools by one or more inventory IDs.
           framework (Union[list[str], str], optional): Filter tools by one or more frameworks (e.g., "langchain").
           tool_name (Union[list[str], str], optional): Filter tools by one or more tool names.
           run_time_details (Union[list[str], str], optional): Filter tools by specific runtime details.
           search_text (Union[List[str], str], optional): Filters tools based on matching keywords.

        Returns:
           dict: A list of tools matching the filter criteria.

        Examples:
        -----------
            .. code-block:: python

                from ibm_watsonx_gov.tools.clients.ai_tool_client import list_tools
                inventory_ids = ['81b1b891-0ded-46ca-bc3f-155e98a15xxx']
                response = list_tools(inventory_id=inventory_ids)
       """
    component_type = ComponentTypes.AI_TOOL.value

    params = {}
    if component_type:
        params["component_type"] = ",".join(component_type) if isinstance(component_type, list) else component_type
    if service_provider_type:
        params["service_provider_type"] = ",".join(service_provider_type) if isinstance(service_provider_type,
                                                                                        list) else service_provider_type
    if category:
        params["category"] = ",".join(category) if isinstance(category, list) else category
    if inventory_id:
        params["inventory_id"] = ",".join(inventory_id) if isinstance(inventory_id, list) else inventory_id
    if framework:
        params["framework"] = ",".join(framework) if isinstance(framework, list) else framework
    if run_time_details:
        params["run_time_details"] = ",".join(run_time_details) if isinstance(run_time_details,
                                                                              list) else run_time_details
    if tool_name:
        params["asset_name"] = ",".join(tool_name) if isinstance(tool_name, list) else tool_name
    if search_text:
        params["match_text"] = ",".join(search_text) if isinstance(search_text, list) else search_text

    verify = environment.get_ssl_verification()
    tool_get_url = f"{environment.get_base_url()}/v1/aigov/factsheet/ai_components"
    response = RestUtil.request_with_retry().get(
        url=tool_get_url, headers=get_headers(), params=params, verify=verify)
    if not response.ok:
        message = f"Error while listing the tool details. Status code: {response.status_code}, Error: {response.text}"
        raise Exception(message)

    return process_result(response)


# Get tool info based on tool_name
def get_tool_info(tool_name: str, inventory_id: str = None) -> dict:
    """
    Method to retrieve tool information based on the tool name within the current inventory ID.

    Args:
        tool_name (str): Name of the tool
        inventory_id (str, optional): Inventory id

    Returns:
        dict: Returns the tool details based on the tool name.

    Example:
    --------
        .. code-block:: python

            from ibm_watsonx_gov.tools.clients.ai_tool_client import get_tool_info
            tool_name = 'Google_search'
            inventory_id = '81b1b891-0ded-46ca-bc3f-155e98a15xxx'
            response = get_tool_info(tool_name=tool_name,inventory_id=inventory_id)
    """
    # Get the tool details using tool name
    tool_details = (
        list_tools
            (
            tool_name=[tool_name],
            inventory_id=[inventory_id] if inventory_id else None,
        )
    )
    if len(tool_details['tools']) > 0:
        tool_id = get(tool_details['tools'][0], "metadata.id")
        if inventory_id is None:
            inventory_id = get(
                tool_details['tools'][0], "entity.inventory_id")

        # Now retain tool information using
        get_response = get_tool(tool_id, inventory_id, tool_name=tool_name)
        return get_response
    raise Exception(f"Tool: {tool_name} does not exist.")


def delete_tool_with_name(tool_name):
    """Method to delete the tool with tool_name

    Args:
        tool_name (str): Name of the tool
    """
    tool_details = list_tools(tool_name=[tool_name])
    if len(tool_details['tools']) > 0:
        tool_id = get(tool_details['tools'][0], "metadata.id")
        inventory_id = get(tool_details['tools'][0], "entity.inventory_id")
        delete_tool(tool_id=tool_id, inventory_id=inventory_id,
                    tool_name=tool_name)
        return f"Tool {tool_name} deleted successfully."
    raise Exception(f"Tool: {tool_name} does not exist.")
