# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from typing import List, Optional, Type

import requests
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, PrivateAttr

from ...schemas.search_tool_schema import SearchToolConfig, SearchToolInput


class GoogleSearchTool(BaseTool):
    """
    Tool to search and get results using duckduckgo search engine

    Examples:
        Basic usage
            .. code-block:: python

                google_search_tool = GoogleSearchTool()
                google_search_tool.invoke({"query":"What is RAG?"})
    """
    name: str = "google_search_tool"
    description: str = "Search google and return the top-k results.Default :3"
    args_schema: Type[BaseModel] = SearchToolInput

    _top_k_results: any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from ibm_watsonx_gov.tools.utils.package_utils import \
            install_and_import_packages

        install_and_import_packages(["bs4", "googlesearch-python"])

        # Load args into config
        config = SearchToolConfig(**kwargs)
        self._top_k_results = config.top_k_results

    # Define Google Search Tool Without API Key
    def _run(self,
             query: str,
             top_k_results: int = None,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             **kwargs) -> List[str]:
        """Performs a Google search and extracts content from the top results."""
        from bs4 import BeautifulSoup
        from googlesearch import search

        if top_k_results is None:
            top_k_results = self._top_k_results

        search_results = list(search(query, num_results=top_k_results))

        results = []
        for url in search_results:
            try:
                url = url[:-1] if url.endswith("/") else url
                response = requests.get(url, timeout=5)
                soup = BeautifulSoup(response.text, "html.parser")

                # Extract text from the webpage
                text = ' '.join([p.text for p in soup.find_all("p")])
                # Adjust the content text
                results.append(text)

            except Exception as e:
                print(f"Skipping {url}: {e}")

        return results
