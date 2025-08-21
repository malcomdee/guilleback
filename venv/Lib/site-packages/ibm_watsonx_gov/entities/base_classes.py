# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field, PrivateAttr, computed_field

from ibm_watsonx_gov.entities.enums import MetricGroup
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold


class BaseConfiguration(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True)

    record_id_field: Annotated[str, Field(title="Record id field",
                                          description="The record identifier field name.",
                                          examples=["record_id"],
                                          default="record_id")]
    record_timestamp_field: Annotated[str, Field(title="Record timestamp field",
                                                 description="The record timestamp field name.",
                                                 examples=["record_timestamp"],
                                                 default="record_timestamp")]


class BaseMetric(BaseModel):
    name: Annotated[str, Field(
        title="Metric Name", description="The name of the metric", frozen=True)]
    _id: Annotated[str, PrivateAttr(default=None)]

    @computed_field(return_type=str)
    @property
    def id(self):
        if self._id is None:
            self._id = self.name
        return self._id


class BaseMetricGroup(BaseModel):
    name: Annotated[str, Field(description="The name of the metric group")]
    _metrics: Annotated[list[BaseMetric], Field(
        description="Metrics to be computed when selecting this metric group", default=[])]

    @property
    def metrics(self) -> list[BaseMetric]:
        return self._metrics


class Error(BaseModel):
    code: Annotated[str, Field(description="The error code")]
    message_en: Annotated[str, Field(
        description="The error message in English.")]
    parameters: Annotated[list[Any], Field(
        description="The list of parameters to construct the message in a different locale.", default=[])]


class BaseMetricResult(BaseModel):
    name: Annotated[str, Field(
        description="The name of the metric.", examples=["answer_correctness", "context_relevance"])]
    method: Annotated[str | None, Field(
        description="The method used to compute this metric result.",
        examples=["token_recall"], default=None)]
    provider: Annotated[str | None, Field(
        description="The provider used to compute this metric result.", default=None)]
    value: Annotated[float | str | bool | None, Field(
        description="The metric value.")]
    errors: Annotated[list[Error] | None, Field(
        description="The list of error messages", default=None)]
    additional_info: Annotated[dict | None, Field(
        description="The additional information about the metric result.", default=None)]
    group: Annotated[MetricGroup | None, Field(
        description="The metric group", default=None)]
    thresholds: Annotated[list[MetricThreshold], Field(
        description="The metric thresholds", default=[])]

    model_config = ConfigDict(
        arbitrary_types_allowed=True, use_enum_values=True)
