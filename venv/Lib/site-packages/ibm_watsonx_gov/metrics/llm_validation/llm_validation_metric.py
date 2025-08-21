# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import copy
from typing import Annotated, List, Literal

import pandas as pd

from ibm_watsonx_gov.entities.metric_threshold import MetricThreshold

try:
    from langchain_ibm import ChatWatsonx
    from langchain_openai import AzureChatOpenAI, ChatOpenAI
except:
    pass
from pydantic import Field

from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.enums import ModelProviderType, TaskType
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.llm_judge import LLMJudge
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.metrics.llm_validation.evaluation_criteria import (
    EvaluationCriteria, get_default_evaluation_criteria)
from ibm_watsonx_gov.metrics.llm_validation.llm_validation_constants import (
    LLMValidation, LLMValidationFields)
from ibm_watsonx_gov.metrics.llm_validation.llm_validation_impl import (
    generate_issues_and_map_to_records, llm_validation_per_record,
    reverse_mapping)


def get_prompt_field(configuration: GenAIConfiguration, available_fields=None):
    if available_fields is None:
        available_fields = []
    prompt_field = configuration.prompt_field
    if not prompt_field:
        prompt_field = LLMValidationFields.INPUT_FIELD.value
    if not prompt_field:
        raise ValueError("Model input not found in data")
    if available_fields and prompt_field not in available_fields:
        raise ValueError(
            f"prompt_field {prompt_field} not found in data. available fields: {available_fields}")
    return prompt_field


class LLMValidationMetric(GenAIMetric):
    """Defines the implementation for computing the LLMValidation metric.

    .. code-block:: python

        from ibm_watsonx_gov.entities.foundation_model import WxAIFoundationModel
        llm_judge=LLMJudge(model=WxAIFoundationModel(model_id="model_id"))

    .. code-block:: python

        metric = LLMValidationMetric(llm_judge=llm_judge)
    """
    name: Annotated[Literal["llm_validation"],
                    Field(default=LLMValidation)]
    tasks: Annotated[list[TaskType], Field(
        default=[TaskType.RAG, TaskType.SUMMARIZATION])]
    thresholds: Annotated[list[MetricThreshold], Field(default=[MetricThreshold(
        type="lower_limit", value=0.7)])]
    method: Annotated[Literal["llm_as_judge"],
                      Field(description=f"The method used to compute the metric.",
                            default="llm_as_judge")]
    llm_judge: Annotated[LLMJudge | None, Field(
        description=f"The LLM judge used to compute the metric.")]
    evaluation_criteria: Annotated[EvaluationCriteria | None, Field(
        description=f"Evaluation Criteria for metric the computation", default_factory=get_default_evaluation_criteria)]

    def evaluate(self, data: pd.DataFrame,
                 configuration: GenAIConfiguration | AgenticAIConfiguration,
                 **kwargs) -> AggregateMetricResult:
        record_level_metrics = self.get_record_level_metrics(
            data, configuration)
        aggregated_results = self.get_aggregated_results_from_individual_results(
            record_level_metrics)
        return aggregated_results

    def get_record_level_metrics(self, data: pd.DataFrame | dict,
                                 configuration: GenAIConfiguration | AgenticAIConfiguration) \
            -> List[RecordMetricResult]:
        # generate evaluator llm
        llm = self.generate_evaluating_model()

        # prepare the data
        eval_df = copy.deepcopy(data)
        prompt_field = get_prompt_field(
            configuration, available_fields=list(eval_df.columns))
        eval_df[LLMValidationFields.INPUT_FIELD.value] = eval_df.apply(
            lambda r: r[prompt_field], axis=1)
        eval_df = eval_df.fillna("")
        eval_df[LLMValidationFields.OUTPUT_FIELD.value] = eval_df.apply(lambda r: "\n".join([r[output_field]
                                                                                             for output_field in
                                                                                             configuration.output_fields]),
                                                                        axis=1)

        # # call the per-record evaluating function
        eval_df = llm_validation_per_record(
            df=eval_df,
            llm=llm,
            input_col=LLMValidationFields.INPUT_FIELD.value,
            output_col=LLMValidationFields.OUTPUT_FIELD.value,
            text_col=LLMValidationFields.TEXT_FIELD.value,
            score_col=LLMValidationFields.SCORE_FIELD.value,
            summary_col=LLMValidationFields.SUMMARY_FIELD.value,
            evaluation_criteria=self.evaluation_criteria
        )

        record_level_metrics = []
        for _, row in eval_df.iterrows():
            record_level_metrics.append(
                RecordMetricResult(
                    name=self.name,
                    method=self.method,
                    provider="",
                    value=row[LLMValidationFields.SCORE_FIELD.value],
                    record_id=row[configuration.record_id_field],
                    additional_info={
                        LLMValidationFields.TEXT_FIELD.value: row[LLMValidationFields.TEXT_FIELD.value],
                        LLMValidationFields.SUMMARY_FIELD.value: row[LLMValidationFields.SUMMARY_FIELD.value],
                        LLMValidationFields.RECURRING_ISSUE_FIELD.value: "",
                        LLMValidationFields.RECURRING_ISSUE_IDS_FIELD.value: ""
                    },
                    thresholds=self.thresholds,
                )
            )

        return record_level_metrics

    def get_aggregated_results_from_individual_results(self, record_level_metrics: List[RecordMetricResult]) \
            -> AggregateMetricResult:
        summaries_list = [r.additional_info[LLMValidationFields.SUMMARY_FIELD.value]
                          if r.value is not None and r.value < 1 else "" # TODO!!!! use and map only records with score < 1
                          for r in record_level_metrics]
        llm = self.generate_evaluating_model()
        recurring_issues_to_record_ids = generate_issues_and_map_to_records(
            summaries_list=summaries_list,
            llm=llm,
        )
        recurring_issues = list(recurring_issues_to_record_ids.keys())
        record_to_matching_issues_ids = reverse_mapping(
            recurring_issues_to_record_ids)

        for i, r in enumerate(record_level_metrics):
            matching_issues_ids = record_to_matching_issues_ids.get(i, [])
            matching_issues = [recurring_issues[i] for i in matching_issues_ids]
            r.additional_info[LLMValidationFields.RECURRING_ISSUE_IDS_FIELD.value] = matching_issues_ids
            r.additional_info[LLMValidationFields.RECURRING_ISSUE_FIELD.value] = matching_issues

        values = [record.value for record in record_level_metrics if record.value is not None]
        mean = sum(values) / len(values)
        evaluation_criteria = self.evaluation_criteria.to_dict() if self.evaluation_criteria else {}
        recurring_issues_count = {k: len(v) for k, v in recurring_issues_to_record_ids.items()}
        aggregate_result = AggregateMetricResult(
            name=self.name,
            method=self.method,
            provider="",
            value=mean,
            total_records=len(record_level_metrics),
            record_level_metrics=record_level_metrics,
            min=min(values),
            max=max(values),
            mean=mean,
            thresholds=self.thresholds,
            additional_info={"recurring_issues": recurring_issues_to_record_ids,
                             "evaluation_criteria": evaluation_criteria,
                             "recurring_issues_count": recurring_issues_count,
                            }
        )

        return aggregate_result

    def generate_evaluating_model(self):
        provider_type = self.llm_judge.model.provider.type
        if provider_type == ModelProviderType.IBM_WATSONX_AI:
            parameters = {
                "decoding_method": "greedy",
                "max_new_tokens": 512,
                "min_new_tokens": 1,
                "stop_sequences": [".", "<|eom_id|>"],
                "enable-auto-tool-choice": False,
                "tool-call-parser": False
            }
            return ChatWatsonx(
                model_id=self.llm_judge.model.model_id,
                url=self.llm_judge.model.provider.credentials.url,
                apikey=self.llm_judge.model.provider.credentials.api_key,
                project_id=self.llm_judge.model.project_id,
                params=parameters,
            )
        elif provider_type == ModelProviderType.AZURE_OPENAI:
            credentials = self.llm_judge.model.provider.credentials
            model_id = self.llm_judge.model.model_name
            azure_openapi_host = credentials.url
            api_version = credentials.api_version
            model_base = model_id.split("/")[-1].replace(".", "-")
            azure_endpoint = \
                f'{azure_openapi_host}/openai/deployments/{model_base}/chat/completions?api-version={api_version}'
            parameters = {"temperature": 0}
            return AzureChatOpenAI(api_key=credentials.api_key,
                                   azure_endpoint=azure_endpoint,
                                   api_version=api_version,
                                   max_retries=2,
                                   **parameters
                                   )
        elif provider_type == ModelProviderType.RITS:
            credentials = self.llm_judge.model.provider.credentials
            judge_model_id = self.llm_judge.model.model_name
            model_base = judge_model_id.split("/")[-1].replace(".", "-")
            rits_base_url = f'{credentials.hostname}/{model_base}/v1'
            return ChatOpenAI(
                model=judge_model_id,
                api_key='/',
                base_url=rits_base_url,
                default_headers={'RITS_API_KEY': credentials.api_key},
                max_retries=2,
                temperature=0.0
            )
        elif provider_type == ModelProviderType.OPENAI:
            model_name = self.llm_judge.model.model_name
            return ChatOpenAI(
                model=model_name,
                max_retries=2,
                temperature=0.0
            )
        raise Exception(f"Unknown provider type {provider_type}.")

