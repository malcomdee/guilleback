# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Any, List

from pydantic import BaseModel, create_model

from ibm_watsonx_gov.tools.utils import environment
from ibm_watsonx_gov.tools.utils.python_utils import (get_bss_account_id,
                                                      process_result)
from ibm_watsonx_gov.utils.authenticator import Authenticator
from ibm_watsonx_gov.utils.rest_util import RestUtil

TOOL_REGISTRY = {
    "chromadb_retrieval_tool": "ibm_watsonx_gov.tools.ootb.vectordb.chromadb_retriever_tool.ChromaDBRetrievalTool",
    "duckduckgo_search_tool": "ibm_watsonx_gov.tools.ootb.search.duckduckgo_search_tool.DuckDuckGoSearchTool",
    "google_search_tool": "ibm_watsonx_gov.tools.ootb.search.google_search_tool.GoogleSearchTool",
    "weather_tool": "ibm_watsonx_gov.tools.ootb.search.weather_tool.WeatherTool",
    "webcrawler_tool": "ibm_watsonx_gov.tools.ootb.search.web_crawler_tool.WebCrawlerTool",
    "wikipedia_search_tool": "ibm_watsonx_gov.tools.ootb.search.wikipedia_search_tool.WikiPediaSearchTool"
}


def get_pydantic_model(name: str, schema: dict) -> type[BaseModel]:
    """Method to provide a pydantic model with the given schema

    Args:
        name (str): Name of the schema
        schema (dict): schema json

    Returns:
        type[BaseModel]: Pydantic model 
    """
    type_mapping = {
        "string": str,
        "number": float,
        "integer": int,
        "boolean": bool,
        "object": dict,
        "array": list,
        "float": float,
        "dict": dict
    }

    def build_fields(properties, required_fields):
        fields = {}
        for key, val in properties.items():
            typ = val.get("type")
            if typ == "object":
                nested_model = get_pydantic_model(
                    f"{name}_{key.capitalize()}", val)
                fields[key] = (nested_model, ...)
            elif typ == "array":
                item_schema = val.get("items")
                if item_schema["type"] == "object":
                    nested_model = get_pydantic_model(
                        f"{name}_{key.capitalize()}Item", item_schema)
                    fields[key] = (List[nested_model], ...)
                else:
                    item_type = type_mapping[item_schema["type"]]
                    fields[key] = (List[item_type], ...)
            else:
                py_type = type_mapping.get(typ, Any)
                default = ... if key in required_fields else val.get("default")
                fields[key] = (py_type, default)
        return fields

    props = schema.get("properties", {})
    required = schema.get("required", [])
    fields = build_fields(props, required)
    return create_model(name, **fields)


def list_ootb_tools():
    """Helper method to get the list of tools 
       TODO: Replace this method with REST API endpoint
    """
    import pandas as pd
    tools = list(TOOL_REGISTRY.keys())
    df = pd.DataFrame(tools, columns=["tool_name"])
    return df


def get_default_inventory():
    """Method to get the default inventory
      TODO: Need to revisit to cover CPD case
    """
    token = get_token()
    bss_account_id = get_bss_account_id(token)
    base_url = environment.get_base_url()
    get_default_inventory_url = f"{base_url}/v1/aigov/inventories/default_inventory?bss_account_id={bss_account_id}"
    headers = get_headers(token=token)
    verify = environment.get_ssl_verification()
    response = RestUtil.request_with_retry(retry_count=3).get(
        url=get_default_inventory_url, headers=headers, verify=verify)
    try:
        response = process_result(response)
        return response["metadata"]["guid"]
    except Exception as e:
        raise Exception("Error while getting default inventory_id: " + str(e))


# Generating user token
def get_token(api_key=None, authenticator_url=None, cpd_username=None, cpd_password=None, is_cpd=None):
    """
     Generate an authentication token for either CPD (Cloud Pak for Data) or IBM Cloud environment.

     Args:
         api_key (str, optional): API key for authentication.
         authenticator_url (str, optional): Authenticator URL endpoint for token generation.
         cpd_username (str, optional): Username for CPD authentication.
         cpd_password (str, optional): Password for CPD authentication.
         is_cpd (bool, optional): Flag indicating if the environment is CPD.

     Returns:
         str: Authentication token.

     Raises:
         Exception: If required credentials are missing.
     """

    is_cpd = is_cpd if is_cpd is not None else environment.get_is_cpd()
    authenticator_url = authenticator_url or environment.get_authenticator_url()
    api_key = api_key or environment.get_api_key()

    missing_vars = []
    credentials = {}

    if is_cpd:
        # Credentials structure for CPD environment:
        # credentials = {
        #     "url": "<authenticator_url>",
        #     "username": "<cpd_username>",
        #     "api_key": "<api_key>", # pragma: allowlist secret
        #     "password": "<cpd_password>" # pragma: allowlist secret
        # }

        cpd_username = cpd_username or environment.get_cpd_username()
        cpd_password = cpd_password or environment.get_cpd_password()

        if not authenticator_url:
            missing_vars.append("CPD_URL")
        if not cpd_username:
            missing_vars.append("CPD_USERNAME")
        if not api_key and not cpd_password:
            missing_vars += ["CPD_API_KEY", "CPD_PASSWORD"]

        credentials.update({
            "url": authenticator_url,
            "username": cpd_username
        })

        if api_key:
            credentials.update({"api_key": api_key})
        if cpd_password:
            credentials.update({"password": cpd_password})
    else:
        # Credentials structure for CLOUD environment:
        # credentials = {
        #     "iam_url": "<iam_url>",
        #     "apikey": "<api_key>" # pragma: allowlist secret
        # }

        if not authenticator_url:
            missing_vars.append("IAM_URL")
        if not api_key:
            missing_vars.append("WATSONX_APIKEY")

        credentials.update({
            "iam_url": authenticator_url,
            "apikey": api_key
        })

    if missing_vars:
        raise Exception(f"Unable to generate token because of the missing details . Details of missing envs: {missing_vars}")

    use_ssl = environment.get_ssl_verification()

    token = Authenticator(credentials=credentials, use_cpd=is_cpd, use_ssl=use_ssl).authenticate()
    return token


# Generating header
def get_headers(token: str = None):
    if token is None:
        token = get_token()
    return {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }
