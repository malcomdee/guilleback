# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from abc import abstractmethod
from typing import TYPE_CHECKING, Annotated, List

import pandas as pd
from pydantic import BaseModel, Field, computed_field, field_serializer

from ibm_watsonx_gov.entities.base_classes import BaseMetric
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold

if TYPE_CHECKING:
    from ibm_watsonx_gov.config import (AgenticAIConfiguration,
                                        GenAIConfiguration)


class Locale(BaseModel):
    input: list[str] | dict[str, str] | str | None = None
    output: list[str] | None = None
    reference: list[str] | dict[str, str] | str | None = None


class GenAIMetric(BaseMetric):
    """Defines the Generative AI metric interface"""
    thresholds: Annotated[list[MetricThreshold],
                          Field(description="The list of thresholds", default=[])]
    tasks: Annotated[list[TaskType], Field(
        description="The task types this metric is associated with.", frozen=True)]
    group: Annotated[MetricGroup | None, Field(
        description="The metric group this metric belongs to.", frozen=True, default=None)]
    is_reference_free: Annotated[bool, Field(
        description="Decides whether this metric needs a reference for computation", frozen=True, default=True)]
    method: Annotated[
        str | None,
        Field(description="The method used to compute the metric.",
              default=None)]
    metric_dependencies: Annotated[list["GenAIMetric"], Field(
        description="Metrics that needs to be evaluated first", default=[])]

    @field_serializer("metric_dependencies", when_used="json")
    def metric_dependencies_serializer(self, metric_dependencies: list["GenAIMetric"]):
        return [metric.model_dump(mode="json") for metric in metric_dependencies]

    @computed_field(return_type=str)
    @property
    def id(self):
        if self._id is None:
            self._id = self.name + (f"_{self.method}" if self.method else "")
        return self._id

    @abstractmethod
    def evaluate(self, data: pd.DataFrame | dict,
                 configuration: "GenAIConfiguration | AgenticAIConfiguration",
                 **kwargs) -> AggregateMetricResult:
        raise NotImplementedError

    def info(self):
        pass

    def get_aggregated_results_from_individual_results(self, record_results: List[RecordMetricResult]):
        values = [record.value for record in record_results]
        record_result = record_results[0]
        mean = sum(values) / len(values)
        return AggregateMetricResult(
            name=record_result.name,
            method=record_result.method,
            provider=record_result.provider,
            group=record_result.group,
            value=mean,
            total_records=len(record_results),
            record_level_metrics=record_results,
            min=min(values),
            max=max(values),
            mean=mean,
        )


class PredictiveAIMetric(BaseMetric):
    pass
