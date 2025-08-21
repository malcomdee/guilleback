# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


import json
import os
from typing import Any, Dict, Type

import requests
from langchain.tools import BaseTool
from pydantic import BaseModel


class RestApiTool(BaseTool):
    """
      Class to construct a tool using  the rest api , schema dynamically
    """
    name: str
    description: str
    method: str = "POST"
    endpoint: str = ""
    headers: Dict[str, str] = {}
    args_schema: Type[BaseModel]

    def _run(self, **kwargs) -> Any:
        if self.method.upper() == "GET":
            response = requests.get(
                self.endpoint, params=kwargs, headers=self.headers)
        elif self.method.upper() == "POST":
            parsed = self.args_schema(**kwargs)
            payload = json.loads(parsed.model_dump_json())
            response = requests.post(
                self.endpoint, json=payload, headers=self.headers)
        else:
            raise ValueError(f"Unsupported method {self.method}")
        return response.json()


def load_headers(tool_name, headers: dict = {}) -> dict:
    """Method to load the header using evv information

    Args:
        tool_name (_type_): Name of the tool 
        headers (dict, optional): Headers associated. Defaults to {}.

    Raises:
        Exception: _description_

    Returns:
        dict: _description_
    """
    missing_keys = []
    for key, value in headers.items():
        if value == f"${key}":
            value = os.getenv(key)
            if value is None:
                missing_keys.append(key)
            else:
                headers[key] = value
        elif value == "$DYNAMIC_HEADER":
            missing_keys.append(key)

    if len(missing_keys) > 0:
        raise Exception(
            f"Missing header information while loading tool :{tool_name}. Details :{missing_keys}")
    return headers
