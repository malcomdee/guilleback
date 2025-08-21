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
from ibm_watsonx_gov.providers.unitxt_provider import UnitxtProvider
from ibm_watsonx_gov.utils.validation_util import (validate_context,
                                                   validate_input,
                                                   validate_llm_as_judge,
                                                   validate_output,
                                                   validate_unitxt_method)

FAITHFULNESS = "faithfulness"

unitxt_methods = [
    "token_k_precision",
    "sentence_bert_mini_lm",
    "llm_as_judge",
    "granite_guardian"
]


class FaithfulnessMetric(GenAIMetric):
    """
    Defines the Faithfulness metric class.

    The faithfulness metrics can be computed using the below methods:
        1. token_k_precision (default)
        2. sentence_bert_mini_lm
        3. llm_as_judge
        4. granite_guardian

    Examples:
        1. Create Faithfulness metric with default parameters.
            .. code-block:: python

                metric = FaithfulnessMetric()
                result = MetricsEvaluator().evaluate(data={"input_text": "...", "context": "...", "generated_text": "..."}, 
                                                    metrics=[metric])
                # A list of contexts can also be passed as shown below
                result = MetricsEvaluator().evaluate(data={"input_text": "...", "context": ["...", "..."], "generated_text": "..."}, 
                                                    metrics=[metric])

        2. Create Faithfulness metric with a custom threshold and method.
            .. code-block:: python

                thresholds  = [MetricThreshold(type="lower_limit", value=0.5)]
                method = "sentence_bert_mini_lm"
                metric = FaithfulnessMetric(method=method, thresholds=thresholds)

        3. Create Faithfulness metric with llm_as_judge method.
            .. code-block:: python

                # Define LLM Judge using watsonx.ai
                # To use other frameworks and models as llm_judge, see :module:`ibm_watsonx_gov.entities.foundation_model`
                llm_judge = LLMJudge(model=WxAIFoundationModel(
                                            model_id="google/flan-ul2",
                                            project_id="<PROJECT_ID>"
                                    ))
                metric = FaithfulnessMetric(llm_judge=llm_judge)

        4. Create Faithfulness metric with granite_guardian method.
            .. code-block:: python

                metric = FaithfulnessMetric(method="granite_guardian")
    """
    name: Annotated[Literal["faithfulness"],
                    Field(title="Name",
                          description="The faithfulness metric name.",
                          default=FAITHFULNESS, frozen=True)]
    tasks: Annotated[list[TaskType],
                     Field(title="Tasks",
                           description="The list of supported tasks.",
                           default=[TaskType.RAG])]
    thresholds: Annotated[list[MetricThreshold],
                          Field(title="Thresholds",
                                description="The metric thresholds.",
                                default=[MetricThreshold(type="lower_limit", value=0.7)])]
    method: Annotated[Literal["token_k_precision", "sentence_bert_mini_lm", "llm_as_judge", "granite_guardian"],
                      Field(title="Method",
                            description="The method used to compute the metric. This field is optional and when `llm_judge` is provided, the method would be set to `llm_as_judge`.",
                            default="token_k_precision")]
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
        validate_context(data_cols, configuration)
        validate_unitxt_method(self.name, self.method, unitxt_methods)
        validate_llm_as_judge(self.name, self.method,
                              self.llm_judge, configuration.llm_judge)

        if self.method == "granite_guardian":
            kwargs["detector_params"] = {
                "risk_name": "groundedness", "threshold": 0.001}
            provider = DetectorsProvider(configuration=configuration,
                                         metric_name=self.name,
                                         metric_method=self.method,
                                         metric_group=self.group,
                                         thresholds=self.thresholds,
                                         **kwargs)
        else:
            provider = UnitxtProvider(configuration=configuration,
                                      metric_name=self.name,
                                      metric_method=self.method,
                                      metric_prefix="metrics.rag.external_rag",
                                      metric_group=self.group,
                                      llm_judge=self.llm_judge,
                                      thresholds=self.thresholds,
                                      **kwargs)
        aggregated_metric_result = provider.evaluate(data=data)
        return aggregated_metric_result
