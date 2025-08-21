# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Callable, Dict, Optional, Union

from pydantic import Field, model_validator
from typing_extensions import Self

from ibm_watsonx_gov.entities.base_classes import BaseConfiguration
from ibm_watsonx_gov.entities.enums import TaskType
from ibm_watsonx_gov.entities.llm_judge import LLMJudge
from ibm_watsonx_gov.entities.metric import Locale


class GenAIConfiguration(BaseConfiguration):
    """
    Defines the GenAIConfiguration class.

    This is used to specify the fields mapping details in the data and other configuration parameters needed for evaluation.

    Examples:
        1. Create configuration with default parameters
            .. code-block:: python

                configuration = GenAIConfiguration()

        2. Create configuration with parameters
            .. code-block:: python

                configuration = GenAIConfiguration(input_fields=["input"], 
                                                   output_fields=["output"])

        2. Create configuration with dict parameters
            .. code-block:: python

                config = {"input_fields": ["input"],
                          "output_fields": ["output"],
                          "context_fields": ["contexts"],
                          "reference_fields": ["reference"]}
                configuration = GenAIConfiguration(**config)    
    """
    task_type: Annotated[TaskType | None, Field(title="Task Type",
                                                description="The generative task type. Default value is None.",
                                                default=None,
                                                examples=[TaskType.RAG])]
    input_fields: Annotated[list[str], Field(title="Input Fields",
                                             description="The list of model input fields in the data. Default value is ['input_text'].",
                                             examples=[
                                                 ["question"]],
                                             default=["input_text"])]
    context_fields: Annotated[list[str], Field(title="Context Fields",
                                               description="The list of context fields in the input fields. Default value is ['context'].",
                                               default=["context"],
                                               examples=[["context1", "context2"]])]
    output_fields: Annotated[list[str], Field(title="Output Fields",
                                              description="The list of model output fields in the data. Default value is ['generated_text'].",
                                              default=["generated_text"],
                                              examples=[["output"]])]
    reference_fields: Annotated[list[str], Field(title="Reference Fields",
                                                 description="The list of reference fields in the data. Default value is ['ground_truth'].",
                                                 default=["ground_truth"],
                                                 examples=[["reference"]])]
    locale: Annotated[Locale | None, Field(title="Locale",
                                           description="The language locale of the input, output and reference fields in the data.",
                                           default=None)]
    tools: Annotated[Union[list[Callable], list[Dict]], Field(title="Tools",
                                                              description="The list of tools used by the LLM.",
                                                              default=[],
                                                              examples=[["function1", "function2"]])]
    tool_calls_field: Annotated[Optional[str], Field(title="Tool Calls Field",
                                                     description="The tool calls field in the input fields. Default value is 'tool_calls'.",
                                                     default="tool_calls",
                                                     examples=["tool_calls"])]

    llm_judge: Annotated[LLMJudge | None, Field(title="LLM Judge",
                                                description="LLM as Judge Model details.",
                                                default=None)]
    prompt_field: Annotated[Optional[str], Field(title="Model Prompt Field",
                                                 description="The prompt field in the input fields. Default value is 'model_prompt'.",
                                                 default="model_prompt",
                                                 examples=["model_prompt"])]

    @model_validator(mode="after")
    def validate_fields(self) -> Self:

        if self.task_type == TaskType.RAG:
            if not self.input_fields or not self.context_fields:
                raise ValueError(
                    "input_fields and context_fields are required for RAG task type.")

        return self
