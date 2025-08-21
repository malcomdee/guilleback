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

from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.utils.validation_util import validate_output

UNSUCCESSFUL_REQUESTS = "unsuccessful_requests"


class UnsuccessfulRequestsResult(RecordMetricResult):
    name: str = UNSUCCESSFUL_REQUESTS
    group: MetricGroup = MetricGroup.ANSWER_QUALITY


class UnsuccessfulRequestsMetric(GenAIMetric):
    """
    Defines the Unsuccessful Requests metric class.

    The Unsuccessful Requests metric measures whether the model answered the request successfully or not by comparing the generated text against the list of unsuccessful phrases.

    Examples:
        1. Create Unsuccessful Requests metric with default parameters and compute using metrics evaluator.
            .. code-block:: python

                metric = UnsuccessfulRequestsMetric()
                result = MetricsEvaluator().evaluate(data={"generated_text": "...", metrics=[metric])

        2. Create Unsuccessful Requests metric with a custom threshold.
            .. code-block:: python

                threshold  = MetricThreshold(type="upper_limit", value=0.2)
                metric = UnsuccessfulRequestsMetric(threshold=threshold)
    """
    name: Annotated[Literal["unsuccessful_requests"],
                    Field(title="Name",
                          description="The unsuccessful requests metric name.",
                          default=UNSUCCESSFUL_REQUESTS, frozen=True)]
    tasks: Annotated[list[TaskType],
                     Field(title="Tasks",
                           description="The list of supported tasks.",
                           default=[TaskType.RAG, TaskType.QA])]
    thresholds: Annotated[list[MetricThreshold],
                          Field(title="Thresholds",
                                description="The metric thresholds.",
                                default=[MetricThreshold(type="upper_limit", value=0.1)])]
    group: Annotated[MetricGroup,
                     Field(title="Group",
                           description="The metric group.",
                           default=MetricGroup.ANSWER_QUALITY, frozen=True)]
    unsuccessful_phrases: Annotated[list[str],
                                    Field(title="Unsuccessful phrases",
                                          description="List of phrases to identify unsuccessful responses",
                                          examples=[
                                              ["i do not know", "i am not sure"]],
                                          default=["i don't know", "i do not know", "i'm not sure",
                                                   "i am not sure", "i'm unsure", "i am unsure",
                                                   "i'm uncertain", "i am uncertain", "i'm not certain",
                                                   "i am not certain", "i can't fulfill", "i cannot fulfill"],
                                          )]

    def evaluate(
            self,
            data: pd.DataFrame,
            configuration: GenAIConfiguration | AgenticAIConfiguration,
            **kwargs
    ) -> AggregateMetricResult:
        record_level_metrics = []
        scores = []

        validate_output(data.columns.to_list(), configuration)
        for prediction_field in configuration.output_fields:
            for prediction, record_id in zip(data[prediction_field], data[configuration.record_id_field]):
                value = 0
                for phrase in self.unsuccessful_phrases:
                    if phrase.lower() in prediction.lower():
                        value = 1
                        break
                scores.append(value)
                record_level_metrics.append(
                    UnsuccessfulRequestsResult(
                        method="",
                        provider="",
                        record_id=record_id,
                        value=value,
                        thresholds=self.thresholds
                    )
                )

        mean = sum(scores) / len(scores)
        aggregate_metric_score = AggregateMetricResult(
            name=self.name,
            method="",
            provider="",
            min=min(scores),
            max=max(scores),
            mean=mean,
            value=mean,
            total_records=len(record_level_metrics),
            group=self.group,
            record_level_metrics=record_level_metrics,
            thresholds=self.thresholds
        )

        return aggregate_metric_score
