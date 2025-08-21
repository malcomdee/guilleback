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
from pydantic import Field

from ibm_watsonx_gov.config.gen_ai_configuration import GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.providers.detectors_provider import DetectorsProvider
from ibm_watsonx_gov.utils.validation_util import validate_input

PROMPT_SAFETY_RISK = "prompt_safety_risk"


class PromptSafetyRiskResult(RecordMetricResult):
    name: str = PROMPT_SAFETY_RISK
    group: MetricGroup = MetricGroup.CONTENT_SAFETY


prompt_safety_methods = ["prompt_injection_125m_0.7_en"]


class PromptSafetyRiskMetric(GenAIMetric):
    """
    Defines the PromptSafetyRisk metric class.

    The PromptSafetyRisk metric evaluates how likely an AI is to respond with harmful, unsafe, or inappropriate content.

    Note : system_prompt is mandatory 

    Examples:
        1. Create PromptSafetyRisk metric with default parameters and compute using metrics evaluator.
            .. code-block:: python

                metric = PromptSafetyRiskMetric(system_prompt="...")
                result = MetricsEvaluator().evaluate(data={"input_text": "...", metrics=[metric])

        2. Create PromptSafetyRisk metric with a custom threshold.
            .. code-block:: python

                threshold  = MetricThreshold(type="lower_limit", value=0.5)
                metric = PromptSafetyRiskMetric(threshold=threshold, system_prompt="...")
    """
    name: Annotated[Literal["prompt_safety_risk"],
                    Field(title="Name",
                          description="The prompt safety risk metric name.",
                          default=PROMPT_SAFETY_RISK, frozen=True)]
    method: Annotated[
        Literal["prompt_injection_125m_0.7_en"],
        Field(title="Method",
              description=f"The method used to compute the prompt safety risk metric.",
              default="prompt_injection_125m_0.7_en")]
    thresholds: Annotated[list[MetricThreshold],
                          Field(title="Thresholds",
                                description="The metric thresholds.",
                                default=[MetricThreshold(type="lower_limit", value=0.7)])]
    tasks: Annotated[list[TaskType],
                     Field(title="Tasks",
                           description="The list of supported tasks.",
                           default=TaskType.values(), frozen=True)]
    # TODO uncomment when the metric is pushed to prod
    # group: Annotated[MetricGroup, Field(title="Group",
    #                                     description="The metric group.",
    #                                     default=MetricGroup.CONTENT_SAFETY, frozen=True)]
    system_prompt: Annotated[str, Field(title="System Prompt",
                                        description=f"The AI model system prompt which contains instructions to define its overall behavior.")]

    def evaluate(
            self,
            data: pd.DataFrame | dict,
            configuration: GenAIConfiguration,
            **kwargs
    ) -> list[AggregateMetricResult]:
        if not self.system_prompt:
            raise AssertionError(
                f"The system_prompt field is required but was missing from the input.")
        if self.method not in prompt_safety_methods:
            raise ValueError(
                f"The provided method '{self.method}' for computing '{self.name}' metric is not supported.")

        validate_input(data.columns.to_list(), configuration)
        # Set system_prompt as part of the detector parameters
        kwargs["detector_params"] = {"system_prompt": self.system_prompt}
        provider = DetectorsProvider(configuration=configuration,
                                     metric_name=self.name,
                                     metric_method=self.method,
                                     metric_group=MetricGroup.CONTENT_SAFETY,
                                     thresholds=self.thresholds,
                                     **kwargs)
        aggregated_metric_result = provider.evaluate(data=data)
        return aggregated_metric_result
