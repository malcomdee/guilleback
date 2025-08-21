# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from functools import partial
from typing import Callable, Optional

from wrapt import decorator

from ibm_watsonx_gov.config import AgenticAIConfiguration
from ibm_watsonx_gov.entities.enums import EvaluatorFields, MetricGroup
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.metrics import (HAPMetric, PIIMetric,
                                     PromptSafetyRiskMetric)
from ibm_watsonx_gov.metrics.base_metric_decorator import BaseMetricDecorator
from ibm_watsonx_gov.metrics.evasiveness.evasiveness_metric import \
    EvasivenessMetric
from ibm_watsonx_gov.metrics.harm.harm_metric import HarmMetric
from ibm_watsonx_gov.metrics.harm_engagement.harm_engagement_metric import \
    HarmEngagementMetric
from ibm_watsonx_gov.metrics.jailbreak.jailbreak_metric import JailbreakMetric
from ibm_watsonx_gov.metrics.profanity.profanity_metric import ProfanityMetric
from ibm_watsonx_gov.metrics.sexual_content.sexual_content_metric import \
    SexualContentMetric
from ibm_watsonx_gov.metrics.social_bias.social_bias_metric import \
    SocialBiasMetric
from ibm_watsonx_gov.metrics.unethical_behavior.unethical_behavior_metric import \
    UnethicalBehaviorMetric
from ibm_watsonx_gov.metrics.violence.violence_metric import ViolenceMetric


class ContentSafetyDecorator(BaseMetricDecorator):
    def evaluate_content_safety(self,
                                func: Optional[Callable] = None,
                                *,
                                configuration: Optional[AgenticAIConfiguration] = None,
                                metrics: list[GenAIMetric] = []
                                ) -> dict:
        """
        An evaluation decorator for computing content safety metrics on an agentic node.
        """

        if func is None:
            return partial(self.evaluate_content_safety, configuration=configuration, metrics=metrics)

        if not metrics:
            metrics = MetricGroup.CONTENT_SAFETY.get_metrics()

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.validate(func=func, metrics=metrics,
                              valid_metric_types=(PromptSafetyRiskMetric, HAPMetric, PIIMetric, HarmMetric, SocialBiasMetric, ProfanityMetric, SexualContentMetric,
                                                  UnethicalBehaviorMetric, ViolenceMetric, HarmEngagementMetric, EvasivenessMetric, JailbreakMetric))

                metric_inputs = [EvaluatorFields.INPUT_FIELDS]

                original_result = self.compute_helper(func=func, args=args, kwargs=kwargs,
                                                      configuration=configuration,
                                                      metrics=metrics,
                                                      metric_inputs=metric_inputs,
                                                      metric_outputs=[],
                                                      metric_groups=[MetricGroup.CONTENT_SAFETY])

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating content safety metrics on {func.__name__},") from ex

        return wrapper(func)
