# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


import json
import re
from typing import Annotated, Any, Optional, Type

import requests
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class WebCrawlerInput(BaseModel):
    url: Annotated[str, Field(description="Url of the website")]


class WebCrawlerTool(BaseTool):
    """
    Tool for retrieving the content of the web url.

    Examples:
        Basic usage
            .. code-block:: python

                crawler_tool = WebCrawlerTool()
                crawler_tool.invoke({"url":"https://edition.cnn.com/2025/03/31/sport/torpedo-bats-mlb-yankees-explained-spt/index.html"})
    """
    name: str = "webcrawler_tool"
    description: str = "Retrieve the content of the Web url. Do not use for Web search."
    args_schema: Type[BaseModel] = WebCrawlerInput

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from ibm_watsonx_gov.tools.utils.package_utils import \
            install_and_import_packages

        install_and_import_packages(["bs4"])

    def _run(self, url: str, **kwargs: Any) -> Any:
        """Retrieve the content of the Web url."""

        from bs4 import BeautifulSoup
        url_pattern = "^(https?:\\/\\/)?([\\da-z\\.-]+)\\.([a-z\\.]{2,6})([\\/\\w \\.-]*)*\\/?$"
        pattern = re.compile(url_pattern)
        if not pattern.match(url):
            raise Exception("Invalid URL passed to WebCrawlerTool ")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        try:
            response = requests.get(url, headers=headers)
        except:
            raise Exception(
                f"Unable to connect to {url}. Check the url")
        if response.status_code >= 400:
            raise Exception(
                f"Unexpected response from WebCrawlerTool {response.text}")

        soup = BeautifulSoup(response.text, "html.parser")
        return soup.get_text()
