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
import textstat
from pydantic import Field

from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.utils.python_utils import replace_none_with_empty_string
from ibm_watsonx_gov.utils.validation_util import validate_output

TEXT_GRADE_LEVEL = "text_grade_level"
FLESCH_KINCAID_GRADE = "flesch_kincaid_grade"
TEXTSTAT = "textstat"


class TextGradeLevelResult(RecordMetricResult):
    name: str = TEXT_GRADE_LEVEL
    group: MetricGroup = MetricGroup.READABILITY
    provider: str = TEXTSTAT
    method: str = FLESCH_KINCAID_GRADE


class TextGradeLevelMetric(GenAIMetric):
    """
    Defines the Text Grade Level metric class.

    The Text Grade Level metric measures the approximate reading US grade level of a text.
    It is computed using the flesch_kincaid_grade method.

    Examples:
        1. Create Text Grade Level metric with default parameters and compute using metrics evaluator.
            .. code-block:: python

                metric = TextGradeLevelMetric()
                result = MetricsEvaluator().evaluate(data={"generated_text": "..."}, 
                                                    metrics=[metric])

        2. Create Text Grade Level metric with a custom threshold.
            .. code-block:: python

                threshold  = MetricThreshold(type="lower_limit", value=0.5)
                metric = TextGradeLevelMetric(threshold=threshold)
    """
    name: Annotated[Literal["text_grade_level"],
                    Field(title="name",
                          description="The text grade level metric name.",
                          default=TEXT_GRADE_LEVEL, frozen=True)]
    method: Annotated[Literal["flesch_kincaid_grade"],
                      Field(title="Method",
                            description="The method used to compute text grade level metric.",
                            default=FLESCH_KINCAID_GRADE)]
    tasks: Annotated[list[TaskType],
                     Field(title="Tasks",
                           description="The list of supported tasks.",
                           default=TaskType.values(), frozen=True)]
    group: Annotated[MetricGroup,
                     Field(title="Group",
                           description="The metric group.",
                           default=MetricGroup.READABILITY, frozen=True)]

    def evaluate(
            self,
            data: pd.DataFrame,
            configuration: GenAIConfiguration | AgenticAIConfiguration,
            **kwargs,
    ) -> list[AggregateMetricResult]:
        from ibm_watsonx_gov.utils.aggregation_util import get_summaries

        validate_output(data.columns.to_list(), configuration)
        record_level_metrics = []
        predictions = data[configuration.output_fields[0]].to_list()
        record_ids = data[configuration.record_id_field].to_list()
        replace_none_with_empty_string(predictions)

        all_scores = self._compute(predictions=predictions)
        record_level_metrics = [
            TextGradeLevelResult(record_id=record_id, value=score)
            for score, record_id in zip(all_scores, record_ids)
        ]
        summary = get_summaries(all_scores)
        aggregate_metric_scores = AggregateMetricResult(
            name=self.name,
            provider=TEXTSTAT,
            method=self.method,
            group=self.group,
            min=summary.get("min"),
            max=summary.get("max"),
            mean=summary.get("mean"),
            value=summary.get("mean"),
            total_records=len(record_level_metrics),
            record_level_metrics=record_level_metrics,)

        return aggregate_metric_scores

    def _compute(self, predictions: list) -> list:
        return [textstat.flesch_kincaid_grade(pred) for pred in predictions]
