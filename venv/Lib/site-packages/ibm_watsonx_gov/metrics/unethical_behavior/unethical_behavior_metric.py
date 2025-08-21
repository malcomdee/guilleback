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

UNETHICAL_BEHAVIOR = "unethical_behavior"


class UnethicalBehaviorResult(RecordMetricResult):
    name: str = UNETHICAL_BEHAVIOR
    group: MetricGroup = MetricGroup.CONTENT_SAFETY


class UnethicalBehaviorMetric(GenAIMetric):
    """
    Defines the Unethical Behavior metric class.

    The Unethical Behavior metric measures the risk of content with actions that violate moral or professional standards, focusing on exploitation for personal gain or disregard for others' well-being. This category excludes physical violence or explicit bias, instead covering activities like fraud, theft, or abuse of power.
    It is computed using the granite guardian model.

    Examples:
        1. Create Unethical Behavior metric with default parameters and compute using metrics evaluator.
            .. code-block:: python

                metric = UnethicalBehaviorMetric()
                result = MetricsEvaluator().evaluate(data={"input_text": "...", metrics=[metric])

        2. Create Unethical Behavior metric with a custom threshold.
            .. code-block:: python

                threshold  = MetricThreshold(type="lower_limit", value=0.5)
                metric = UnethicalBehaviorMetric(threshold=threshold)
    """
    name: Annotated[Literal["unethical_behavior"],
                    Field(title="Name",
                          description="The unethical behavior metric name.",
                          default=UNETHICAL_BEHAVIOR, frozen=True)]
    method: Annotated[Literal["granite_guardian"],
                      Field(title="Method",
                            description="The method used to compute harm metric.",
                            default="granite_guardian")]
    tasks: Annotated[list[TaskType],
                     Field(title="Tasks",
                           description="The list of supported tasks.",
                           default=TaskType.values(), frozen=True)]
    thresholds: Annotated[list[MetricThreshold],
                          Field(title="Thresholds",
                                description="The metric thresholds.",
                                default=[MetricThreshold(type="lower_limit", value=0.7)])]
    group: Annotated[MetricGroup,
                     Field(title="Group",
                           description="The metric group.",
                           default=MetricGroup.CONTENT_SAFETY, frozen=True)]

    def evaluate(
        self,
        data: pd.DataFrame | dict,
        configuration: GenAIConfiguration,
        **kwargs
    ) -> list[AggregateMetricResult]:

        validate_input(data.columns.to_list(), configuration)
        kwargs["detector_params"] = {"risk_name": UNETHICAL_BEHAVIOR}
        provider = DetectorsProvider(configuration=configuration,
                                     metric_name=self.name,
                                     metric_method=self.method,
                                     metric_group=self.group,
                                     thresholds=self.thresholds,
                                     **kwargs)
        aggregated_metric_result = provider.evaluate(data=data)
        return aggregated_metric_result
