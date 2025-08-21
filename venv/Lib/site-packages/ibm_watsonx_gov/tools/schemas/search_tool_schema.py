# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Optional

from pydantic import BaseModel, Field


# Define the args schema using Pydantic
class SearchToolInput(BaseModel):
    """
        Model that can be used for setting input args for search tools
    """
    query: Annotated[str,
                     Field(..., description="Search the input from the given search tool")]
    top_k_results: Annotated[Optional[int],  Field(
        3, description="Number of search results to retrieve")]


class SearchToolConfig(BaseModel):
    """
        Model to be used for getting the initialization parameters for search tools
    """
    top_k_results: Annotated[Optional[int],  Field(
        3, description="Number of search results to retrieve")]
