# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Literal

import pandas as pd
from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.entities.evaluation_result import AggregateMetricResult
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.providers.tool_call_metric_provider import \
    ToolCallMetricProvider
from ibm_watsonx_gov.utils.validation_util import validate_tool_calls
from pydantic import Field

TOOL_CALLING_SYNTACTIC_ACCURACY = "tool_call_syntactic_accuracy"


class ToolCallSyntacticAccuracyMetric(GenAIMetric):
    """
    ToolCallSyntacticAccuracyMetric compute the tool call syntactic correctness 
    by validating tool call against the schema of the list of available tools.

    The ToolCallSyntacticAccuracy metric will be computed by performing the syntactic checks.

    Examples:
        1. Create ToolCallSyntacticAccuracy metric by passing the basic configuration.
            .. code-block:: python

                config = GenAIConfiguration(tools = [get_weather,fetch_stock_price])
                evaluator = MetricsEvaluator(configuration=config)
                df = pd.read_csv("")
                metrics = [ToolCallSyntacticAccuracyMetric()]
                result = evaluator.evaluate(data=df, metrics=metrics)

        2. Create ToolCallSyntacticAccuracy metric by passing custom tool calls field in configuration.
            .. code-block:: python

                config = GenAIConfiguration(tools = [get_weather,fetch_stock_price],
                                            tool_calls_field="tools_used")
                evaluator = MetricsEvaluator(configuration=config)
                df = pd.read_csv("")
                metrics = [ToolCallSyntacticAccuracyMetric()]
                result = evaluator.evaluate(data=df, metrics=metrics)

        3. Create ToolCallSyntacticAccuracy metric with a custom threshold.
            .. code-block:: python

                threshold  = MetricThreshold(type="upper_limit", value=0.8)
                metric = ToolCallSyntacticAccuracyMetric(threshold=threshold)
    """

    name: Annotated[Literal["tool_call_syntactic_accuracy"], Field(title="Metric Name",
                                                                   description="The name of metric.",
                                                                   default=TOOL_CALLING_SYNTACTIC_ACCURACY)]

    tasks: Annotated[list[TaskType], Field(title="Task Type",
                                           description="The generative task type.",
                                           default=[TaskType.RAG])]
    group: Annotated[MetricGroup, Field(title="Group",
                                        description="The metric group.",
                                        default=MetricGroup.TOOL_CALL_QUALITY, frozen=True)]
    method: Annotated[Literal["syntactic_check"], Field(title="Computation Method",
                                                        description="The method used to compute the metric.",
                                                        default="syntactic_check")]
    thresholds: Annotated[list[MetricThreshold], Field(title="Metric threshold",
                                                       description="Value that defines the violation limit for the metric",
                                                       default=[MetricThreshold(
                                                           type="upper_limit", value=0.7)]
                                                       )]

    def evaluate(self, data: pd.DataFrame | dict,
                 configuration: GenAIConfiguration | AgenticAIConfiguration,
                 **kwargs) -> AggregateMetricResult:
        """
        Evaluate the data for ToolCallSyntacticAccuracyMetric
        Args:
            data (pd.DataFrame | dict): Data to be evaluated
            configuration (GenAIConfiguration | AgenticAIConfiguration): Metrics configuration

        Returns:
            AggregateMetricResult: The computed metrics
        """
        # Validate tool calls field in data and tools in configuration
        data_cols = data.columns.to_list()
        validate_tool_calls(data_cols, configuration)

        tool_call_provider = ToolCallMetricProvider(
            configuration=configuration, metric=self)

        # Compute the metrics
        metric_result = tool_call_provider.compute_metrics(data)

        return metric_result
