# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import asyncio
import json
import os
from typing import Annotated, Literal

import pandas as pd
from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.entities.evaluation_result import AggregateMetricResult
from ibm_watsonx_gov.entities.llm_judge import LLMJudge
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.providers.tool_call_metric_provider import \
    ToolCallMetricProvider
from ibm_watsonx_gov.utils.python_utils import get
from ibm_watsonx_gov.utils.validation_util import validate_tool_calls
from pydantic import Field

TOOL_CALL_PARAMETER_ACCURACY = "tool_call_parameter_accuracy"


class ToolCallParameterAccuracyMetric(GenAIMetric):
    """
    ToolCallParameterAccuracyMetric assesses whether ALL parameter values 
    in a function call are directly supported by conversation history 
    or API specifications. Identifies hallucinated values, missing information, 
    format errors, and contradictory values.

    The ToolCallParameterAccuracyMetric will be computed using llm_as_judge.

    Examples:
        1. Create ToolCallParameterAccuracyMetric by passing the basic configuration.
            .. code-block:: python

                config = GenAIConfiguration(tools = [get_weather,fetch_stock_price])
                evaluator = MetricsEvaluator(configuration=config)
                df = pd.read_csv("")
                llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                metrics = [ToolCallParameterAccuracyMetric(llm_judge=llm_judge)]
                result = evaluator.evaluate(data=df, metrics=metrics)

        2. Create ToolCallParameterAccuracyMetric by passing custom tool calls field in configuration.
            .. code-block:: python

                config = GenAIConfiguration(tools = [get_weather,fetch_stock_price],
                                            tool_calls_field="tools_used")
                evaluator = MetricsEvaluator(configuration=config)
                df = pd.read_csv("")
                llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                metrics = [ToolCallParameterAccuracyMetric(llm_judge=llm_judge)]
                result = evaluator.evaluate(data=df, metrics=metrics)

        3. Create ToolCallParameterAccuracyMetric with a custom threshold.
            .. code-block:: python

                llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                threshold  = MetricThreshold(type="upper_limit", value=0.8)
                metric = ToolCallParameterAccuracyMetric(llm_judge=llm_judge, threshold=threshold)
    """

    name: Annotated[Literal["tool_call_parameter_accuracy"], Field(title="Metric Name",
                                                                   description="The name of metric.",
                                                                   default=TOOL_CALL_PARAMETER_ACCURACY)]

    tasks: Annotated[list[TaskType], Field(title="Task Type",
                                           description="The generative task type.",
                                           default=[TaskType.RAG])]
    group: Annotated[MetricGroup, Field(
        default=MetricGroup.TOOL_CALL_QUALITY, frozen=True)]

    llm_judge: Annotated[LLMJudge | None, Field(
        description="The LLM judge used to compute the metric.", default=None)]

    method: Annotated[Literal["llm_as_judge"], Field(title="Computation Method",
                                                           description="The method used to compute the metric.",
                                                           default="llm_as_judge")]
    thresholds: Annotated[list[MetricThreshold], Field(title="Metric threshold",
                                                       description="Value that defines the violation limit for the metric",
                                                       default=[MetricThreshold(
                                                           type="upper_limit", value=0.7)]
                                                       )]
    metric_mapping_name: Annotated[Literal["general_hallucination_check"], Field(title="Metric Mapping Name",
                                                                                 description="The mapping name of metric with llmevalkit.",
                                                                                 default="general_hallucination_check")]

    def evaluate(self, data: pd.DataFrame | dict,
                 configuration: GenAIConfiguration | AgenticAIConfiguration,
                 **kwargs) -> AggregateMetricResult:
        """
        Evaluate the data for ToolCallParameterAccuracyMetric
        Args:
            data (pd.DataFrame | dict): Data to be evaluated
            configuration (GenAIConfiguration | AgenticAIConfiguration): Metrics configuration
            **kwargs: Additional keyword arguments

        Returns:
            AggregateMetricResult: The computed metrics
        """
        data_cols = data.columns.to_list()
        validate_tool_calls(data_cols, configuration)

        tool_call_provider = ToolCallMetricProvider(
            configuration=configuration, metric=self)
        metric_config = {
            "general_metrics": [self.metric_mapping_name],
            "function_metrics": None,
            "parameter_metrics": None,
            "transform_enabled": False
        }
        metric_result = tool_call_provider.compute_metrics(
            data, syntactic_only=False, metric_result_mapping_name="general",  **metric_config)

        return metric_result
