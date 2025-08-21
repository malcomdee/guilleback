# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import os
from typing import Union

from ibm_watsonx_gov.tools.utils import environment
from ...tools.utils.constants import ComponentTypes
from ...tools.utils.tool_utils import (get_default_inventory, get_headers,
                                       get_token, process_result)
from ...utils.python_utils import get
from ...utils.rest_util import RestUtil
from ..entities.ai_agent import AgentRegistrationPayload, AgentUpdatePayload


def register_agent(payload: Union[dict, AgentRegistrationPayload]):
    """
    Registers a new agent by converting the provided payload to an AgentRegistrationPayload instance.
    And then call the agent registration endpoint.

    Args:
        payload (Union[dict, AgentRegistrationPayload]): The payload to register the agent.
        It can either be a dictionary or an instance of AgentRegistrationPayload.

    Returns:
        dict: The processed result from the agent registration API.

    Examples:
    ---------
    Using AgentRegistrationPayload model:
        .. code-block:: python

            from ibm_watsonx_gov.agent_catalog.clients import (
                AgentRegistrationPayload,
                register_agent,
            )

            post_payload = {
                "display_name": "banking agent",
                "agent_name": "banking_agent1",
                "description": "backing agent application",
                "endpoint": {
                    "url": "http://localhost:8000/tools/add",
                    "headers": {
                        "Authorization": "Bearer dummy-token-12345",
                        "Content-Type": "application/json",
                    },
                    "method": "POST"
                },
                "service_provider_type": "wml",
                "schema": {"properties": {"Query": {}}},
            }
            register_payload = AgentRegistrationPayload(**post_payload)
            register_response = register_agent(payload=register_payload)
            register_response
"""
    if isinstance(payload, dict):
        post_payload = AgentRegistrationPayload(**payload)
    elif isinstance(payload, AgentRegistrationPayload):
        post_payload = payload
    else:
        raise Exception(
            "Invalid payload format. Only dict and AgentRegistrationPayload formats are allowed.")
    if not post_payload.inventory_id:
        post_payload.inventory_id = get_default_inventory()

    payload = post_payload.model_dump(
        mode="json", exclude_none=True, by_alias=True)
    verify = environment.get_ssl_verification()
    agent_post_url = f"{environment.get_base_url()}/v1/aigov/factsheet/ai_components/agents"
    headers = get_headers()
    response = RestUtil.request_with_retry().post(
        url=agent_post_url, json=payload, headers=headers, verify=verify)
    return process_result(response)


def get_agent(agent_id: str, inventory_id: str):
    """
        Retrieves the details of a specific agent based on the given agent ID and inventory ID.

        Args:
            agent_id (str): The ID of the agent to be retrieved.
            inventory_id (str): The ID of the inventory to fetch the agent from.

        Returns:
            dict: The processed result from the agent get API.

        Example:
        --------
             .. code-block:: python

                from ibm_watsonx_gov.agent_catalog.clients import get_agent
                agent_id = '273d2b0c-dc04-407d-b3e8-2fdde790b1ed'
                inventory_id = "81b1b891-0ded-46ca-bc3f-155e98a1xxx"
                get_response = get_agent(agent_id=agent_id, inventory_id=inventory_id)
                get_response
        """

    agent_get_url = f"{environment.get_base_url()}/v1/aigov/factsheet/ai_components/agents/{agent_id}?inventory_id={inventory_id}"
    headers = get_headers()
    verify = environment.get_ssl_verification()
    response = RestUtil.request_with_retry().get(url=agent_get_url, headers=headers, verify=verify)
    return process_result(response)


def update_agent(agent_id: str, inventory_id: str, payloads: Union[list[dict], AgentUpdatePayload]):
    """
    Patches the agent information based on the provided agent ID, inventory ID, and payloads.

    Args:
        agent_id (str): The ID of the agent to be patched.
        inventory_id (str): The ID of the inventory to which the agent contains.
        payloads (list[Union[dict, AgentUpdatePayload]]): A list of dictionaries or `AgentUpdatePayload` instances containing the update information for the agent.

    Returns:
        dict: The processed result from the agent patch API.

    Notes:
        - Each item in the `payloads` list should be either a dictionary or an instance of `AgentUpdatePayload`.
        - If a dictionary is provided, it is converted into an `AgentUpdatePayload` instance.

    Examples:
    ---------
    Using AgentUpdatePayload model:
        .. code-block:: python

            from ibm_watsonx_gov.agent_catalog.clients import AgentUpdatePayload, update_agent
            agent_id = '273d2b0c-dc04-407d-b3e8-2fdde790b1ed'
            inventory_id = "81b1b891-0ded-46ca-bc3f-155e98a15xxx"
            patch_payload = [
                {"op": "replace", "path": "/reusable", "value": True},
                {"op": "replace", "path": "/metrics", "value": {"metric_id": "64"}},
            ]
            update_agent_payload = AgentUpdatePayload(**{"payload": patch_payload})
            update_response = update_agent(
                agent_id=agent_id,
                inventory_id=inventory_id,
                payloads=update_agent_payload,
            )
            update_response

"""

    if isinstance(payloads, list):
        patch_payload = AgentUpdatePayload(**{"payload": payloads})
    elif isinstance(payloads, AgentUpdatePayload):
        patch_payload = payloads
    else:
        raise TypeError(
            f"Invalid payload type: {type(payloads)}. Expected list[dict] or AgentUpdatePayload.")

    payload = patch_payload.model_dump(mode="json")['payload']
    verify = environment.get_ssl_verification()
    agent_patch_url = f"{environment.get_base_url()}/v1/aigov/factsheet/ai_components/agents/{agent_id}?inventory_id={inventory_id}"
    headers = get_headers()
    response = RestUtil.request_with_retry().patch(
        url=agent_patch_url, headers=headers, json=payload, verify=verify)
    return process_result(response)


def delete_agent(agent_id: str, inventory_id: str):
    """
    Delete the AI agent based on the agent_id and inventory_id

    Args:
        agent_id (str): The ID of the agent to be deleted.
        inventory_id (str): The ID of the inventory to which the agent contains.
    Returns:
        "AI agent Deleted Successfully"
    Example:
    --------
        .. code-block:: python

            from ibm_watsonx_gov.agent_catalog.clients import delete_agent
            agent_id = '273d2b0c-dc04-407d-b3e8-2fdde790b1ed'
            inventory_id = "81b1b891-0ded-46ca-bc3f-155e98a1xxx"
            response = delete_agent(agent_id=agent_id, inventory_id=inventory_id)
            response
    """

    agent_delete_url = f"{environment.get_base_url()}/v1/aigov/factsheet/ai_components/agents/{agent_id}?inventory_id={inventory_id}"
    headers = get_headers()
    verify = environment.get_ssl_verification()
    response = RestUtil.request_with_retry().delete(
        url=agent_delete_url, headers=headers, verify=verify)
    if response.text:
        return process_result(response)
    return "AI agent Deleted Successfully"


def list_agents(service_provider_type: Union[list[str], str] = None, category: Union[list[str], str] = None,
                inventory_id: Union[list[str], str] = None, framework: Union[list[str], str] = None,
                agent_name: Union[list[str], str] = None, search_text: Union[list[str], str] = None):
    """
       Retrieves a list of registered AI agents based on the provided filter criteria.

       All parameters are optional. If no filters are provided, all agents will be listed.

       Args:
           service_provider_type (Union[list[str], str], optional): Filter agents by one or more service provider types.
           category (Union[list[str], str], optional): Filter agents by one or more categories.
           inventory_id (Union[list[str], str], optional): Filter agents by one or more inventory IDs.
           framework (Union[list[str], str], optional): Filter agents by one or more frameworks (e.g., "langchain").
           agent_name (Union[list[str], str], optional): Filter agents by one or more agent names.

       Returns:
           list: A list of agents matching the filter criteria.

       Examples:
       ---------
            .. code-block:: python

                from ibm_watsonx_gov.agent_catalog.clients import list_agents
                response = list_agents(agent_name=["banking_agent1"])
                response
       """
    component_type = ComponentTypes.AI_AGENT.value

    parms = {}
    if component_type:
        parms["component_type"] = ",".join(component_type) if isinstance(
            component_type, list) else component_type
    if service_provider_type:
        parms["service_provider_type"] = ",".join(service_provider_type) if isinstance(service_provider_type,
                                                                                       list) else service_provider_type
    if category:
        parms["category"] = ",".join(category) if isinstance(
            category, list) else category
    if inventory_id:
        parms["inventory_id"] = ",".join(inventory_id) if isinstance(
            inventory_id, list) else inventory_id
    if framework:
        parms["framework"] = ",".join(framework) if isinstance(
            framework, list) else framework
    if agent_name:
        parms["asset_name"] = ",".join(agent_name) if isinstance(
            agent_name, list) else agent_name
    if search_text:
        parms["match_text"] = ",".join(search_text) if isinstance(
            search_text, list) else search_text

    agent_list_url = f"{environment.get_base_url()}/v1/aigov/factsheet/ai_components"
    headers = get_headers()
    verify = environment.get_ssl_verification()
    response = RestUtil.request_with_retry().get(
        url=agent_list_url, headers=headers, params=parms, verify=verify)
    return process_result(response)


def get_agent_by_name(agent_name: str, inventory_id: str = None):
    """
        Method to retrieve agent information based on the agent name within the current inventory ID.

        Args:
            agent_name (str): Name of the agent
            inventory_id (str, optional): Inventory id

        Returns:
            dict: Returns the agent details based on the agent name.

        Example:
        --------
            .. code-block:: python

                from ibm_watsonx_gov.agent_catalog.clients import get_agent_by_name
                response = get_agent_by_name("banking_agent1")
                response

        """
    # Get the agent details using agent name
    agent_details = (
        list_agents
        (
            agent_name=agent_name,
            inventory_id=inventory_id
        )
    )
    if len(agent_details['agents']) > 0:
        agent_id = get(agent_details['agents'][0], "metadata.id")
        if inventory_id is None:
            inventory_id = get(
                agent_details['agents'][0], "entity.inventory_id")

        # Now retain agent information using agent_id and inventory_id
        get_response = get_agent(agent_id, inventory_id)
        return get_response
    raise Exception(f"You don't have any agent with agent_name: {agent_name}")


def delete_agent_with_name(agent_name: str, inventory_id: str = None):
    """
    Method to delete the agent with agent_name

    Args:
        agent_name (str): Name of the agent
        inventory_id (str, Optional) Inventory_id

    Example:
    --------
        .. code-block:: python

            from ibm_watsonx_gov.agent_catalog.clients import delete_agent_with_name
            response = delete_agent_with_name("banking_agent1")
            response
    """
    # Get the agent details using agent name
    agent_details = list_agents(
        agent_name=agent_name, inventory_id=inventory_id)
    if len(agent_details["agents"]) > 0:
        agent_id = get(agent_details['agents'][0], "metadata.id")
        if inventory_id is None:
            inventory_id = get(
                agent_details['agents'][0], "entity.inventory_id")

        # Now deleting agent information using agent_id and inventory_id
        delete_agent(agent_id=agent_id, inventory_id=inventory_id)
        return f"The agent with agent_name: {agent_name} was deleted successfully."
    raise Exception(f"You don't have any agent with agent_name: {agent_name}")
