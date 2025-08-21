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

EVASIVENESS = "evasiveness"


class EvasivenessResult(RecordMetricResult):
    name: str = EVASIVENESS
    group: MetricGroup = MetricGroup.CONTENT_SAFETY


class EvasivenessMetric(GenAIMetric):
    """
    Defines the Evasiveness metric class.

    The Evasiveness metric measures the risk of avoiding to engage without providing sufficient reason.
    It is computed using the granite guardian model.

    Examples:
        1. Create Evasiveness metric with default parameters and compute using metrics evaluator.
            .. code-block:: python

                metric = EvasivenessMetric()
                result = MetricsEvaluator().evaluate(data={"input_text": "...", metrics=[metric])

        2. Create Evasiveness metric with a custom threshold.
            .. code-block:: python

                threshold  = MetricThreshold(type="lower_limit", value=0.5)
                metric = EvasivenessMetric(threshold=threshold)
    """
    name: Annotated[Literal["evasiveness"],
                    Field(title="Name",
                          description="The evasiveness metric name.",
                          default=EVASIVENESS, frozen=True)]
    method: Annotated[Literal["granite_guardian"],
                      Field(title="Method",
                            description="The method used to compute evasiveness metric.",
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
        data: pd.DataFrame,
        configuration: GenAIConfiguration,
        **kwargs
    ) -> list[AggregateMetricResult]:

        validate_input(data.columns.to_list(), configuration)
        kwargs["detector_params"] = {"risk_name": EVASIVENESS}
        provider = DetectorsProvider(configuration=configuration,
                                     metric_name=self.name,
                                     metric_method=self.method,
                                     metric_group=self.group,
                                     thresholds=self.thresholds,
                                     **kwargs)
        aggregated_metric_result = provider.evaluate(data=data)
        return aggregated_metric_result
