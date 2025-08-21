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
from ibm_watsonx_gov.providers.unitxt_provider import UnitxtProvider
from ibm_watsonx_gov.utils.validation_util import (validate_llm_as_judge,
                                                   validate_output,
                                                   validate_reference,
                                                   validate_unitxt_method)

UNITXT_METRIC_NAME = "answer_correctness"

unitxt_methods = ["token_recall",
                  "bert_score_recall",
                  "sentence_bert_mini_lm",
                  "llm_as_judge",
                  ]


class AnswerSimilarityMetric(GenAIMetric):
    """
    Defines the Answer Similarity metric class.

    The Answer Similarity metric measures the similarity between the generated text and the ground truth.
    It can be computed using the below methods:
        1. token_recall (default)
        2. bert_score_recall
        3. sentence_bert_mini_lm
        4. llm_as_judge

    Examples:
        1. Create Answer Similarity metric with default parameters and compute using metrics evaluator.
            .. code-block:: python

                metric = AnswerSimilarityMetric()
                result = MetricsEvaluator().evaluate(data={"generated_text": "...", "ground_truth": "..."}, 
                                                    metrics=[metric])

        2. Create Answer Similarity metric with a custom threshold and method.
            .. code-block:: python

                threshold  = MetricThreshold(type="lower_limit", value=0.5)
                method = "sentence_bert_mini_lm"
                metric = AnswerSimilarityMetric(method=method, threshold=threshold)

        3. Create Answer Similarity metric with llm_as_judge method.
            .. code-block:: python

                # Define LLM Judge using watsonx.ai
                # To use other frameworks and models as llm_judge, see :module:`ibm_watsonx_gov.entities.foundation_model`
                llm_judge = LLMJudge(model=WxAIFoundationModel(
                                            model_id="google/flan-ul2",
                                            project_id="<PROJECT_ID>"
                                    ))
                metric = AnswerSimilarityMetric(llm_judge=llm_judge)
    """
    name: Annotated[Literal["answer_similarity"],
                    Field(title="Name",
                          description="The answer similarity metric name.",
                          default="answer_similarity", frozen=True)]
    tasks: Annotated[list[TaskType],
                     Field(title="Tasks",
                           description="The list of supported tasks.",
                           default=[TaskType.RAG, TaskType.QA])]
    is_reference_free: Annotated[bool,
                                 Field(title="Is Reference free",
                                       description="The flag to indicate whether this metric needs a reference for computation. This metric needs reference value to compute.",
                                       default=False, frozen=True)]
    thresholds: Annotated[list[MetricThreshold],
                          Field(title="Thresholds",
                                description="The metric thresholds.",
                                default=[MetricThreshold(type="lower_limit", value=0.7)])]
    method: Annotated[Literal["token_recall", "bert_score_recall", "sentence_bert_mini_lm", "llm_as_judge"],
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
        validate_output(data_cols, configuration)
        validate_reference(data_cols, configuration)
        validate_unitxt_method(self.name, self.method, unitxt_methods)
        validate_llm_as_judge(self.name, self.method,
                              self.llm_judge, configuration.llm_judge)

        provider = UnitxtProvider(configuration=configuration,
                                  metric_name=self.name,
                                  metric_method=self.method,
                                  metric_prefix="metrics.rag.external_rag",
                                  metric_alias=UNITXT_METRIC_NAME,
                                  metric_group=self.group,
                                  llm_judge=self.llm_judge,
                                  thresholds=self.thresholds,
                                  **kwargs)
        aggregated_metric_result = provider.evaluate(data=data)

        return aggregated_metric_result
