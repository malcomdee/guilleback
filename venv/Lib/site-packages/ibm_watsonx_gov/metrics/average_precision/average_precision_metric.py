# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Any, Literal

import pandas as pd
from pydantic import Field, TypeAdapter, field_validator

from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.metrics.context_relevance.context_relevance_metric import (
    CONTEXT_RELEVANCE, ContextRelevanceMetric, ContextRelevanceResult)

AVERAGE_PRECISION = "average_precision"


class AveragePrecisionResult(RecordMetricResult):
    name: str = AVERAGE_PRECISION
    group: MetricGroup = MetricGroup.RETRIEVAL_QUALITY


class AveragePrecisionMetric(GenAIMetric):
    """
    Defines the Average Precision metric class.

    The Average Precision metric measures the quality of how a retrieval system ranks relevant contexts.
    The Context Relevance metric is computed as a pre requisite to compute this metric.

    Examples:
        1. Create Average Precision metric with default parameters and compute using metrics evaluator.
            .. code-block:: python

                metric = AveragePrecisionMetric()
                result = MetricsEvaluator().evaluate(data={"input_text": "...", "context": "..."}, 
                                                    metrics=[metric])
                # A list of contexts can also be passed as shown below
                result = MetricsEvaluator().evaluate(data={"input_text": "...", "context": ["...", "..."]}, 
                                                    metrics=[metric])

        2. Create Average Precision metric with a custom threshold.
            .. code-block:: python

                threshold  = MetricThreshold(type="lower_limit", value=0.5)
                metric = AveragePrecisionMetric(method=method, threshold=threshold)

        3. Create Average Precision metric with llm_as_judge method.
            .. code-block:: python

                # Define LLM Judge using watsonx.ai
                # To use other frameworks and models as llm_judge, see :module:`ibm_watsonx_gov.entities.foundation_model`
                llm_judge = LLMJudge(model=WxAIFoundationModel(
                                            model_id="google/flan-ul2",
                                            project_id="<PROJECT_ID>"
                                    ))
                cr_metric = ContextRelevanceMetric(llm_judge=llm_judge)
                ap_metric = AveragePrecisionMetric()
                result = MetricsEvaluator().evaluate(data={"input_text": "...", "context": ["...", "..."]}, 
                                                    metrics=[cr_metric, ap_metric])
    """
    name: Annotated[Literal["average_precision"],
                    Field(title="Name",
                          description="The average precision metric name.",
                          default=AVERAGE_PRECISION, frozen=True)]
    tasks: Annotated[list[TaskType],
                     Field(title="Tasks",
                           description="The list of supported tasks.",
                           default=[TaskType.RAG])]
    thresholds: Annotated[list[MetricThreshold],
                          Field(title="Thresholds",
                                description="The metric thresholds.",
                                default=[MetricThreshold(type="lower_limit", value=0.7)])]
    metric_dependencies: Annotated[list[GenAIMetric],
                                   Field(title="Metric dependencies",
                                         description="The list of metric dependencies",
                                         default=[ContextRelevanceMetric()])]
    group: Annotated[MetricGroup,
                     Field(title="Group",
                           description="The metric group.",
                           default=MetricGroup.RETRIEVAL_QUALITY, frozen=True)]

    @field_validator("metric_dependencies", mode="before")
    @classmethod
    def metric_dependencies_validator(cls, value: Any):
        if value:
            value = [TypeAdapter(Annotated[ContextRelevanceMetric, Field(
                discriminator="name")]).validate_python(
                m) for m in value]
        return value

    def evaluate(
            self,
            data: pd.DataFrame,
            configuration: GenAIConfiguration | AgenticAIConfiguration,
            metrics_result: list[AggregateMetricResult],
            **kwargs,
    ) -> AggregateMetricResult:
        record_level_metrics = []
        scores = []

        context_relevance_result: list[ContextRelevanceResult] = next(
            (metric_result.record_level_metrics for metric_result in metrics_result if metric_result.name == CONTEXT_RELEVANCE), None)

        if context_relevance_result is None:
            raise Exception(
                f"Failed to evaluate {self.name} metric. Missing context relevance metric result")

        for relevance_result in context_relevance_result:
            score = self.__compute(
                relevance_scores=relevance_result.additional_info.get(
                    "contexts_values", []),
                threshold=self.thresholds[0].value,
            )
            scores.append(score)
            record_level_metrics.append(
                AveragePrecisionResult(
                    method="",
                    provider="",
                    record_id=relevance_result.record_id,
                    value=score,
                    thresholds=self.thresholds
                )
            )

        mean = sum(scores) / len(scores)
        aggregate_metric_score = AggregateMetricResult(
            name=self.name,
            method="",
            provider="",
            group=self.group,
            min=min(scores),
            max=max(scores),
            mean=mean,
            value=mean,
            total_records=len(record_level_metrics),
            record_level_metrics=record_level_metrics,
            thresholds=self.thresholds
        )

        return aggregate_metric_score

    def __compute(self, relevance_scores: list[float], threshold: float) -> float:
        relevancy_at_k = []
        for i, score in enumerate(relevance_scores):
            if score >= threshold:
                relevancy_at_k.append(i + 1)
        total_relevant_items = len(relevancy_at_k)
        if total_relevant_items == 0:
            return 0
        precision_sum = 0
        relevant_rank = 0
        for k in relevancy_at_k:
            relevant_rank += 1
            precision_at_k = relevant_rank / k
            precision_sum += precision_at_k
        average_precision = precision_sum / total_relevant_items
        average_precision_rounded = round(average_precision, 1)
        return average_precision_rounded
