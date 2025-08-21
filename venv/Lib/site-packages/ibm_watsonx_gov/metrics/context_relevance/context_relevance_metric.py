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

from ibm_watsonx_gov.config.agentic_ai_configuration import \
    AgenticAIConfiguration
from ibm_watsonx_gov.config.gen_ai_configuration import GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup, TaskType
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.llm_judge import LLMJudge
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold
from ibm_watsonx_gov.providers.detectors_provider import DetectorsProvider
from ibm_watsonx_gov.providers.unitxt_provider import UnitxtProvider
from ibm_watsonx_gov.utils.python_utils import transform_str_to_list
from ibm_watsonx_gov.utils.validation_util import (validate_context,
                                                   validate_input,
                                                   validate_llm_as_judge,
                                                   validate_unitxt_method)

CONTEXT_RELEVANCE = "context_relevance"


class ContextRelevanceResult(RecordMetricResult):
    name: str = CONTEXT_RELEVANCE
    group: MetricGroup = MetricGroup.RETRIEVAL_QUALITY
    additional_info: dict[Literal["contexts_values"],
                          list[float]] = {"contexts_values": []}


unitxt_methods = [
    "token_precision",
    "sentence_bert_bge",
    "sentence_bert_mini_lm",
    "llm_as_judge",
    "granite_guardian"
]


class ContextRelevanceMetric(GenAIMetric):
    """
    Defines the Context Relevance metric class.

    The Context Relevance metric measures the relevance of the contexts to the given input query.
    It can be computed using the below methods:
        1. token_precision (default)
        2. sentence_bert_bge
        3. sentence_bert_mini_lm
        4. llm_as_judge
        5. granite_guardian
    If there are multiple context fields, the context relevance score is computed by combining all the contexts.
    To compute the individual context relevance scores, set the `compute_per_context` flag to True. The default value is False.
    When `compute_per_context` is set to True, the metric value is taken as the maximum of the combined context relevance score and the context relevance scores for each context.
    The other retrieval quality metrics use per context scores for computation. Its recommended to set the `compute_per_context` flag to True when computing the retrieval quality metrics for better accuracy.

    Examples:
        1. Create Context Relevance metric with default parameters and compute using metrics evaluator.
            .. code-block:: python

                metric = ContextRelevanceMetric()
                result = MetricsEvaluator().evaluate(data={"input_text": "...", "context": "..."}, 
                                                    metrics=[metric])
                # A list of contexts can also be passed as shown below
                result = MetricsEvaluator().evaluate(data={"input_text": "...", "context": ["...", "..."]}, 
                                                    metrics=[metric])

        2. Create Context Relevance metric with a custom thresholds and method.
            .. code-block:: python

                thresholds  = [MetricThreshold(type="lower_limit", value=0.5)]
                method = "sentence_bert_bge"
                metric = ContextRelevanceMetric(method=method, thresholds=thresholds)

        3. Create Context Relevance metric with llm_as_judge method.
            .. code-block:: python

                # Define LLM Judge using watsonx.ai
                # To use other frameworks and models as llm_judge, see :module:`ibm_watsonx_gov.entities.foundation_model`
                llm_judge = LLMJudge(model=WxAIFoundationModel(
                                            model_id="google/flan-ul2",
                                            project_id="<PROJECT_ID>"))
                metric = ContextRelevanceMetric(llm_judge=llm_judge)

        4. Create Context Relevance metric with granite_guardian method.
            .. code-block:: python

                metric = ContextRelevanceMetric(method="granite_guardian")
    """
    name: Annotated[Literal["context_relevance"],
                    Field(title="Name",
                          description="The context relevance metric name.",
                          default=CONTEXT_RELEVANCE, frozen=True)]
    tasks: Annotated[list[TaskType],
                     Field(title="Tasks",
                           description="The list of supported tasks.",
                           default=[TaskType.RAG])]
    thresholds: Annotated[list[MetricThreshold],
                          Field(title="Thresholds",
                                description="The metric thresholds.",
                                default=[MetricThreshold(type="lower_limit", value=0.7)])]
    method: Annotated[Literal["token_precision", "sentence_bert_bge", "sentence_bert_mini_lm", "llm_as_judge", "granite_guardian"],
                      Field(title="Method",
                            description="The method used to compute the metric. This field is optional and when `llm_judge` is provided, the method would be set to `llm_as_judge`.",
                            default="token_precision")]
    group: Annotated[MetricGroup,
                     Field(title="Group",
                           description="The metric group.",
                           default=MetricGroup.RETRIEVAL_QUALITY, frozen=True)]
    llm_judge: Annotated[LLMJudge | None,
                         Field(title="LLM Judge",
                               description="The LLM judge used to compute the metric.",
                               default=None)]
    compute_per_context: Annotated[bool,
                                   Field(title="Compute per context",
                                         description="The flag to compute the relevance score of each context. The default value is False. Setting the flag to True increases the latency and cost of metric computation.",
                                         default=False)]

    @model_validator(mode="after")
    def set_llm_judge_default_method(self) -> Self:
        # If llm_judge is set, set the method to llm_as_judge
        if self.llm_judge:
            self.method = "llm_as_judge"

        return self

    def __validate_context_relevance_inputs(self, data: pd.DataFrame | dict, configuration: GenAIConfiguration | AgenticAIConfiguration):
        data_cols = data.columns.to_list()
        validate_input(data_cols, configuration)
        validate_context(data_cols, configuration)
        validate_unitxt_method(self.name, self.method, unitxt_methods)
        validate_llm_as_judge(self.name, self.method,
                              self.llm_judge, configuration.llm_judge)

    def get_combined_context_scores(self, data: pd.DataFrame | dict, configuration: GenAIConfiguration | AgenticAIConfiguration, **kwargs):
        if self.method == "granite_guardian":
            self.__provider = "detectors"
            kwargs["detector_params"] = {
                "risk_name": CONTEXT_RELEVANCE, "threshold": 0.001}
            provider = DetectorsProvider(configuration=configuration,
                                         metric_name=self.name,
                                         metric_method=self.method,
                                         metric_group=self.group,
                                         thresholds=self.thresholds,
                                         **kwargs)
        else:
            self.__provider = "unitxt"
            provider = UnitxtProvider(
                configuration=configuration,
                metric_name=self.name,
                metric_method=self.method,
                metric_group=self.group,
                metric_prefix="metrics.rag.external_rag",
                llm_judge=self.llm_judge,
                thresholds=self.thresholds,
                **kwargs)

        return provider.evaluate(data=data)

    def get_per_context_scores(self, data: pd.DataFrame | dict, configuration: GenAIConfiguration | AgenticAIConfiguration, context_fields: list, **kwargs):
        contexts_result: list[AggregateMetricResult] = []
        for context in context_fields:
            context_config = configuration.model_copy()
            context_config.context_fields = [context]
            if self.method == "granite_guardian":
                kwargs["detector_params"] = {
                    "risk_name": CONTEXT_RELEVANCE, "threshold": 0.001}
                provider = DetectorsProvider(configuration=context_config,
                                             metric_name=self.name,
                                             metric_method=self.method,
                                             metric_group=self.group,
                                             thresholds=self.thresholds,
                                             **kwargs)
            else:
                provider = UnitxtProvider(
                    configuration=context_config,
                    metric_name=self.name,
                    metric_method=self.method,
                    metric_group=self.group,
                    metric_prefix="metrics.rag.external_rag",
                    llm_judge=self.llm_judge,
                    thresholds=self.thresholds,
                    **kwargs)
            res = provider.evaluate(data=data)
            contexts_result.append(res)
        return contexts_result

    def get_final_result(self, contexts_result, type):
        final_res: list[ContextRelevanceResult] = []

        if type == "combined_contexts":
            context_results = [contexts_result.record_level_metrics]
        else:
            index = 0
            context_results = [
                context_result.record_level_metrics for context_result in contexts_result]
        for record_metric in zip(*context_results):
            if type == "combined_contexts":
                # Get record level values
                values = [context_value.value for context_value in record_metric]
                self.__record_level_context_values.append(values)
            else:
                # Add combined context scores to individual context scores
                values = [context_value.value for context_value in record_metric] + \
                    self.__record_level_context_values[index]
                index += 1
            record_result = ContextRelevanceResult(
                method=self.method,
                provider=self.__provider,
                value=max(values),
                record_id=record_metric[0].record_id,
                additional_info={"contexts_values": values},
                thresholds=self.thresholds
            )
            final_res.append(record_result)
        return final_res

    def evaluate(self, data: pd.DataFrame | dict, configuration: GenAIConfiguration | AgenticAIConfiguration, **kwargs) -> AggregateMetricResult:
        # validate inputs
        self.__validate_context_relevance_inputs(data, configuration)

        context_fields = configuration.context_fields
        # Check if we need to expand the contexts column:
        if len(configuration.context_fields) == 1:
            context = context_fields[0]
            data[context] = data[context].apply(transform_str_to_list)
            contexts_count = len(data[context].iloc[0])
            context_fields = [f"context_{i}" for i in range(contexts_count)]
            data[context_fields] = pd.DataFrame(
                data[context].to_list(), index=data.index)

        self.__record_level_context_values = []

        # compute combined context scores
        contexts_result = self.get_combined_context_scores(
            data, configuration, **kwargs)
        final_res = self.get_final_result(
            contexts_result=contexts_result, type="combined_contexts")

        # compute per context score based on the toggle
        if self.compute_per_context:
            contexts_result = self.get_per_context_scores(
                data, configuration, context_fields, **kwargs)
            final_res = self.get_final_result(
                contexts_result=contexts_result, type="per_context")

        # Create the aggregate result
        values = [record.value for record in final_res]
        mean = sum(values) / len(values)
        aggregate_result = AggregateMetricResult(
            name=self.name,
            method=self.method,
            provider=self.__provider,
            group=MetricGroup.RETRIEVAL_QUALITY,
            value=mean,
            total_records=len(final_res),
            record_level_metrics=final_res,
            min=min(values),
            max=max(values),
            mean=mean,
            thresholds=self.thresholds
        )
        return aggregate_result
