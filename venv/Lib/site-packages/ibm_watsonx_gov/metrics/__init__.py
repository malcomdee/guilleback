# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from typing import Annotated, Union

from ibm_watsonx_gov.entities.metric import GenAIMetric
from pydantic import Field

from .answer_relevance.answer_relevance_metric import AnswerRelevanceMetric
from .answer_similarity.answer_similarity_metric import AnswerSimilarityMetric
from .average_precision.average_precision_metric import AveragePrecisionMetric
from .evasiveness.evasiveness_metric import EvasivenessMetric
from .faithfulness.faithfulness_metric import FaithfulnessMetric
from .hap.hap_metric import HAPMetric
from .harm.harm_metric import HarmMetric
from .harm_engagement.harm_engagement_metric import HarmEngagementMetric
from .hit_rate.hit_rate_metric import HitRateMetric
from .jailbreak.jailbreak_metric import JailbreakMetric
from .llm_validation.llm_validation_metric import LLMValidationMetric
from .ndcg.ndcg_metric import NDCGMetric
from .pii.pii_metric import PIIMetric
from .profanity.profanity_metric import ProfanityMetric
from .prompt_safety_risk.prompt_safety_risk_metric import \
    PromptSafetyRiskMetric
from .reciprocal_rank.reciprocal_rank_metric import ReciprocalRankMetric
from .retrieval_precision.retrieval_precision_metric import \
    RetrievalPrecisionMetric
from .sexual_content.sexual_content_metric import SexualContentMetric
from .social_bias.social_bias_metric import SocialBiasMetric
from .text_grade_level.text_grade_level_metric import TextGradeLevelMetric
from .text_reading_ease.text_reading_ease_metric import TextReadingEaseMetric
from .tool_call_parameter_accuracy.tool_call_parameter_accuracy_metric import \
    ToolCallParameterAccuracyMetric
from .tool_call_syntactic_accuracy.tool_call_syntactic_accuracy_metric import \
    ToolCallSyntacticAccuracyMetric
from .tool_selection_accuracy.tool_selection_accuracy_metric import \
    ToolSelectionAccuracyMetric
from .topic_relevance.topic_relevance_metric import TopicRelevanceMetric
from .unethical_behavior.unethical_behavior_metric import \
    UnethicalBehaviorMetric
from .unsuccessful_requests.unsuccessful_requests_metric import \
    UnsuccessfulRequestsMetric
from .violence.violence_metric import ViolenceMetric

from .context_relevance.context_relevance_metric import ContextRelevanceMetric  # isort:skip

METRICS_UNION = Annotated[Union[tuple(GenAIMetric.__subclasses__())], Field(
    discriminator="name")]
