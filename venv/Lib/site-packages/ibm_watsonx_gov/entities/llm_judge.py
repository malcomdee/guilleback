# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Union

from pydantic import BaseModel, Field

from ibm_watsonx_gov.entities.foundation_model import (
    AzureOpenAIFoundationModel, OpenAIFoundationModel, RITSFoundationModel,
    WxAIFoundationModel)


class LLMJudge(BaseModel):
    """
    Defines the LLMJudge.

    The LLMJudge class contains the details of the llm judge model to be used for computing the metric.

    Examples:
        1. Create LLMJudge using watsonx.ai foundation model:
            .. code-block:: python

                wx_ai_foundation_model = WxAIFoundationModel(
                    model_id="google/flan-ul2",
                    project_id=PROJECT_ID,
                    provider=WxAIModelProvider(
                        credentials=WxAICredentials(api_key=wx_apikey)
                    )
                )
                llm_judge = LLMJudge(model=wx_ai_foundation_model)
    """
    model: Annotated[Union[WxAIFoundationModel, OpenAIFoundationModel, AzureOpenAIFoundationModel, RITSFoundationModel], Field(
        description="The foundation model to be used as judge")]

    def get_model_provider(self):
        return self.model.provider.type.value
