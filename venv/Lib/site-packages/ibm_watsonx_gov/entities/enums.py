# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from enum import Enum
from typing import TYPE_CHECKING

from pydantic_core import PydanticUndefined

if TYPE_CHECKING:
    from ibm_watsonx_gov.entities.metric import GenAIMetric


class EvaluationProvider(Enum):
    """Supported evaluation providers for metrics computation"""
    UNITXT = "unitxt"
    WATSONX_GOV = "watsonx_governance"
    DETECTORS = "detectors"

    @staticmethod
    def values():
        """Get all values of the enum"""
        return [e.value for e in EvaluationProvider]


class TaskType(Enum):
    """Supported task types for generative AI models"""
    QA = "question_answering"
    CLASSIFICATION = "classification"
    SUMMARIZATION = "summarization"
    GENERATION = "generation"
    EXTRACTION = "extraction"
    RAG = "retrieval_augmented_generation"

    @staticmethod
    def values():
        return [e.value for e in TaskType]

    def get_metrics(self) -> list["GenAIMetric"]:
        """
        Helper method to return a list of metrics for the task type

        Returns:
            list[GenAIMetric]: list of gen AI metrics for the specified task type
        """
        # localized import to avoid circular import issues
        import ibm_watsonx_gov.metrics
        from ibm_watsonx_gov.entities.metric import GenAIMetric

        metrics_list = []
        for metric_class in GenAIMetric.__subclasses__():

            # Check if the class has required fields with no default value
            required_fields = {}
            metric_class_fields = metric_class.model_fields
            for field, field_info in metric_class_fields.items():
                if field_info.is_required() and field_info.default == PydanticUndefined:
                    required_fields[field] = None

            metric = metric_class.model_construct(**required_fields)
            if self in metric.tasks:
                metrics_list.append(metric)

        return metrics_list


class InputDataType(Enum):
    """Supported input data types"""
    STRUCTURED = "structured"
    TEXT = "unstructured_text"
    IMAGE = "unstructured_image"
    MULTIMODAL = "multimodal"


class ProblemType(Enum):
    """Supported problem types for predictive AI models"""
    BINARY = "binary"
    MULTICLASS = "multiclass"
    REGRESSION = "regression"


class EvaluationStage(Enum):
    """Supported evaluation stages"""
    DEVELOPMENT = "development"
    PRE_PRODUCTION = "pre_production"
    PRODUCTION = "production"


class ModelProviderType(Enum):
    """Supported model provider types for Generative AI"""
    IBM_WATSONX_AI = "ibm_watsonx.ai"
    AZURE_OPENAI = "azure_openai"
    RITS = "rits"
    OPENAI = "openai"
    CUSTOM = "custom"


class Region(Enum):
    """Supported IBM Cloud regions"""
    US_SOUTH = "us-south"
    EU_DE = "eu-de"
    AU_SYD = "au-syd"
    CA_TOR = "ca-tor"
    JP_TOK = "jp-tok"
    EU_GB = "eu-gb"

    @staticmethod
    def values():
        """Get all values of the enum"""
        return [e.value for e in Region]


class EvaluatorFields(Enum):
    """Fields used in the evaluator"""
    INPUT_FIELDS = "input_fields"
    OUTPUT_FIELDS = "output_fields"
    REFERENCE_FIELDS = "reference_fields"
    CONTEXT_FIELDS = "context_fields"
    RECORD_ID_FIELD = "record_id_field"
    RECORD_TIMESTAMP_FIELD = "record_timestamp_field"
    INTERACTION_ID_FIELD = "interaction_id_field"
    CONVERSATION_ID_FIELD = "conversation_id_field"
    TOOL_CALLS_FIELD = "tool_calls_field"
    PROMPT_FIELD = "prompt_field"

    @staticmethod
    def get_default_fields_mapping() -> dict["EvaluatorFields", str | list[str]]:
        """Get the default fields mapping for the evaluator"""
        return {
            EvaluatorFields.INPUT_FIELDS: ["input_text"],
            EvaluatorFields.OUTPUT_FIELDS: ["generated_text"],
            EvaluatorFields.REFERENCE_FIELDS: ["ground_truth"],
            EvaluatorFields.CONTEXT_FIELDS: ["context"],
            EvaluatorFields.RECORD_ID_FIELD: "record_id",
            EvaluatorFields.RECORD_TIMESTAMP_FIELD: "record_timestamp",
            EvaluatorFields.TOOL_CALLS_FIELD: "tool_calls",
            EvaluatorFields.INTERACTION_ID_FIELD: "interaction_id",
            EvaluatorFields.CONVERSATION_ID_FIELD: "conversation_id",
            EvaluatorFields.PROMPT_FIELD: "model_input"
        }


class ContainerType(Enum):
    PROJECT = "project"
    SPACE = "space"


class MistakeType(Enum):
    """Enum for TCH Mistake Type"""
    WRONG_NUMBER_OF_APIS = "Wrong number of APIs"
    NEED_MORE_APIS = "Need more APIs"
    WRONG_API_SELECTION = "Wrong API selection"
    NEED_MORE_INFORMATION = "Need more information"
    WRONG_PARAMETER_VALUE = "Wrong parameter value"
    WRONG_UNITS_TRANSFORMATION = "Wrong units transformation"
    HALLUCINATED_CALL = "Hallucinated API call"
    HALLUCINATED_PARAM = "Hallucinated parameter"
    PARAM_TYPE = "Incorrect parameter value type"
    ALLOWED_VALUES = "Allowed values"
    REQ_PARAM_MISSING = "Missing required parameter"
    NONE_FUNC = "Not able to identify the user's intent."


class MetricGroup(Enum):
    RETRIEVAL_QUALITY = "retrieval_quality"
    ANSWER_QUALITY = "answer_quality"
    CONTENT_SAFETY = "content_safety"
    PERFORMANCE = "performance"
    USAGE = "usage"
    TOOL_CALL_QUALITY = "tool_call_quality"
    READABILITY = "readability"

    def get_metrics(self) -> list["GenAIMetric"]:
        """
        Helper method to return a list of metrics under each metric group

        Returns:
            list[GenAIMetric]: list of gen AI metrics for the specified metric group
        """
        # localized import to avoid circular import issues
        from ibm_watsonx_gov.entities.metric import GenAIMetric

        metrics_list = []
        for metric_class in GenAIMetric.__subclasses__():

            # Check if the class has required fields with no default value
            required_fields = {}
            metric_class_fields = metric_class.model_fields
            for field, field_info in metric_class_fields.items():
                if field_info.is_required() and field_info.default == PydanticUndefined:
                    required_fields[field] = None

            metric = metric_class.model_construct(**required_fields)
            if metric.group == self:
                metrics_list.append(metric)

        return metrics_list


class GraniteGuardianRisks(Enum):
    HARM = "harm"
    SOCIAL_BIAS = "social_bias"
    PROFANITY = "profanity"
    SEXUAL_CONTENT = "sexual_content"
    UNETHICAL_BEHAVIOR = "unethical_behavior"
    VIOLENCE = "violence"
    HARM_ENGAGEMENT = "harm_engagement"
    EVASIVENESS = "evasiveness"
    JAILBREAK = "jailbreak"
    ANSWER_RELEVANCE = "answer_relevance"
    CONTEXT_RELEVANCE = "context_relevance"
    FAITHFULNESS = "faithfulness"

    @staticmethod
    def values():
        return [e.value for e in GraniteGuardianRisks]
