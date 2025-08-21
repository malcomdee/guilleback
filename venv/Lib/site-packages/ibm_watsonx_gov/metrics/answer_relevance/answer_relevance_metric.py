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
from pydantic import Field, model_validator
from typing_extensions import Self

from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.entities.evaluation_result import AggregateMetricResult
from ibm_watsonx_gov.entities.llm_judge import LLMJudge
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.providers.detectors_provider import DetectorsProvider
from ibm_watsonx_gov.providers.unitxt_provider import (UnitxtColumnMapping,
                                                       UnitxtProvider)
from ibm_watsonx_gov.utils.validation_util import (validate_input,
                                                   validate_llm_as_judge,
                                                   validate_output,
                                                   validate_unitxt_method)

ANSWER_RELEVANCE = "answer_relevance"
UNITXT_METRIC_NAME = ANSWER_RELEVANCE
unitxt_methods = [
    "token_recall",
    "llm_as_judge",
    "granite_guardian"
]


class AnswerRelevanceMetric(GenAIMetric):
    """
    Defines the Answer Relevance metric class.

    The Answer Relevance metric measures the relevance of the generated text to the given input query.
    It can be computed using the below methods:
        1. token_recall (default)
        2. llm_as_judge
        3. granite_guardian

    Examples:
        1. Create Answer Relevance metric with default parameters and compute using metrics evaluator.
            .. code-block:: python

                metric = AnswerRelevanceMetric()
                result = MetricsEvaluator().evaluate(data={"input_text": "...", "generated_text": "..."}, 
                                                    metrics=[metric])

        2. Create Answer Relevance metric with a custom thresholds and method.
            .. code-block:: python

                thresholds  = [MetricThreshold(type="lower_limit", value=0.5)]
                method = "token_recall"
                metric = AnswerRelevanceMetric(method=method, thresholds=thresholds)

        3. Create Answer Relevance metric with llm_as_judge method.
            .. code-block:: python

                # Define LLM Judge using watsonx.ai
                # To use other frameworks and models as llm_judge, see :module:`ibm_watsonx_gov.entities.foundation_model`
                llm_judge = LLMJudge(model=WxAIFoundationModel(
                                            model_id="google/flan-ul2",
                                            project_id="<PROJECT_ID>"))
                metric = AnswerRelevanceMetric(llm_judge=llm_judge)

        4. Create Answer Relevance metric with granite_guardian method.
            .. code-block:: python

                metric = AnswerRelevanceMetric(method="granite_guardian")

    """
    name: Annotated[Literal["answer_relevance"],
                    Field(title="Name",
                          description="The answer relevance metric name.",
                          default=ANSWER_RELEVANCE, frozen=True)]
    tasks: Annotated[list[TaskType],
                     Field(title="Tasks",
                           description="The list of supported tasks.",
                           default=[TaskType.RAG, TaskType.QA])]
    thresholds: Annotated[list[MetricThreshold],
                          Field(title="Thresholds",
                                description="The metric thresholds.",
                                default=[MetricThreshold(type="lower_limit", value=0.7)])]
    method: Annotated[Literal["token_recall", "llm_as_judge", "granite_guardian"],
                      Field(title="Method",
                            description="The method used to compute the metric. This field is optional and when `llm_judge` is provided, the method would be set to `llm_as_judge`.",
                            default="token_recall")]
    group: Annotated[MetricGroup,
                     Field(title="Group",
                           description="The metric group.",
                           default=MetricGroup.ANSWER_QUALITY, frozen=True)]
    llm_judge: Annotated[LLMJudge | None,
                         Field(title="LLM Judge",
                               description="The LLM judge used to compute the metric.",
                               default=None)]

    @model_validator(mode="after")
    def set_llm_judge_default_method(self) -> Self:
        # If llm_judge is set, set the method to llm_as_judge
        if self.llm_judge:
            self.method = "llm_as_judge"
        return self

    def evaluate(self, data: pd.DataFrame,
                 configuration: GenAIConfiguration | AgenticAIConfiguration,
                 **kwargs) -> AggregateMetricResult:

        data_cols = data.columns.to_list()
        validate_input(data_cols, configuration)
        validate_output(data_cols, configuration)
        validate_unitxt_method(self.name, self.method, unitxt_methods)
        validate_llm_as_judge(self.name, self.method,
                              self.llm_judge, configuration.llm_judge)

        # Define the mapping if the method is not using the default one
        if self.method == "token_recall":
            column_mapping = UnitxtColumnMapping(
                answer="prediction/answer",
                question="task_data/question",
            )
        else:
            column_mapping = UnitxtColumnMapping()
        if self.method == "granite_guardian":
            kwargs["detector_params"] = {
                "risk_name": ANSWER_RELEVANCE, "threshold": 0.001}
            provider = DetectorsProvider(configuration=configuration,
                                         metric_name=self.name,
                                         metric_method=self.method,
                                         metric_group=MetricGroup.ANSWER_QUALITY,
                                         thresholds=self.thresholds,
                                         **kwargs)
        else:
            provider = UnitxtProvider(
                configuration=configuration,
                metric_name=self.name,
                metric_method=self.method,
                metric_prefix="metrics.rag.external_rag",
                metric_alias=UNITXT_METRIC_NAME,
                metric_group=self.group,
                column_mapping=column_mapping,
                llm_judge=self.llm_judge,
                thresholds=self.thresholds,
                **kwargs,
            )
        aggregated_metric_result = provider.evaluate(data=data)

        return aggregated_metric_result
