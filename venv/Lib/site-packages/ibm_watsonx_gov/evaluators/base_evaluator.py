# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated

from ibm_watsonx_gov.clients.api_client import APIClient


class BaseEvaluator(BaseModel):
    """
    The base class for all evaluators.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True)
    api_client: Annotated[APIClient | None,
                          Field(name="The IBM watsonx.governance client.", default=None)]
