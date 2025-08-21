# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import List, Optional, Type

from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.tools import BaseTool
from pydantic import BaseModel, PrivateAttr

from ...schemas.search_tool_schema import SearchToolConfig, SearchToolInput


class DuckDuckGoSearchTool(BaseTool):
    """
    Tool to search and get results using duckduckgo search engine

    Examples:
        Basic usage
            .. code-block:: python

                duckduckgosearch_tool = DuckDuckGoSearchTool()
                duckduckgosearch_tool.invoke({"query":"What is RAG?"})
    """
    name: str = "duckduckgo_search_tool"
    description: str = "Search using duckduckgo search engine and return the top-k results.Default :3"
    args_schema: Type[BaseModel] = SearchToolInput
    _top_k_results = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from ibm_watsonx_gov.tools.utils.package_utils import \
            install_and_import_packages

        install_and_import_packages(["duckduckgo-search"])
        config = SearchToolConfig(**kwargs)
        self._top_k_results = config.top_k_results

    def _run(self,
             query: str,
             top_k_results: int = None,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             **kwargs) -> List[str]:
        """Use DuckDuckGo Search and return the top-k results."""
        if top_k_results is None:
            top_k_results = self._top_k_results

        from langchain_community.utilities import DuckDuckGoSearchAPIWrapper
        results = DuckDuckGoSearchAPIWrapper().results(
            query=query, max_results=top_k_results)

        # Ensure results are in string format
        if isinstance(results, list):
            # Extract snippets
            return [res["snippet"] for res in results if "snippet" in res]

        return [str(results)]  # Send list if the response is not a list
