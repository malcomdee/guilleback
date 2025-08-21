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
from langchain_community.utilities import WikipediaAPIWrapper
from pydantic import BaseModel, PrivateAttr

from ...schemas.search_tool_schema import SearchToolConfig, SearchToolInput


# Create a wrapper to call the tool
class WikiPediaSearchTool(BaseTool):
    """
    Tool to search and get results using wikipedia search

    Examples:
        Basic usage
            .. code-block:: python

                wikipedia_search_tool = WikiPediaSearchTool()
                wikipedia_search_tool.invoke({"query":"What is RAG?"})
    """
    name: str = "wikipedia_search_tool"
    description: str = "Search Wikipedia and return the top-k results.Default :3"
    args_schema: Type[BaseModel] = SearchToolInput

    _top_k_results: any = PrivateAttr()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        from ibm_watsonx_gov.tools.utils.package_utils import \
            install_and_import_packages
        install_and_import_packages(["wikipedia"])

        config = SearchToolConfig(**kwargs)
        self._top_k_results = config.top_k_results

    def _run(self,
             query: str,
             top_k_results: int = None,
             run_manager: Optional[CallbackManagerForToolRun] = None,
             **kwargs) -> List[str]:

        if top_k_results is None:
            top_k_results = self._top_k_results

        search_results = WikipediaAPIWrapper(
            top_k_results=top_k_results).run(query)

        # return search_results
        results = [para.strip()
                   for para in search_results.split("\n\n") if para.strip()]
        return results
