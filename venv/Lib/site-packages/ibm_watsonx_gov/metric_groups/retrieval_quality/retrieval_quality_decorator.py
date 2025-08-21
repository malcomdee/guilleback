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
from ibm_watsonx_gov.metrics import (AveragePrecisionMetric,
                                     ContextRelevanceMetric, HitRateMetric,
                                     NDCGMetric, ReciprocalRankMetric,
                                     RetrievalPrecisionMetric)
from ibm_watsonx_gov.metrics.base_metric_decorator import BaseMetricDecorator


class RetrievalQualityDecorator(BaseMetricDecorator):
    def evaluate_retrieval_quality(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = []
                                   ) -> dict:
        """
        An evaluation decorator for computing retrieval quality metrics on an agentic node.
        """
        if func is None:
            return partial(self.evaluate_retrieval_quality, configuration=configuration, metrics=metrics)

        if not metrics:
            metrics = MetricGroup.RETRIEVAL_QUALITY.get_metrics()

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.validate(func=func, metrics=metrics,
                              valid_metric_types=(NDCGMetric, ContextRelevanceMetric, ReciprocalRankMetric, RetrievalPrecisionMetric, AveragePrecisionMetric, HitRateMetric))

                metric_inputs = [EvaluatorFields.INPUT_FIELDS]
                metric_outputs = [EvaluatorFields.CONTEXT_FIELDS]

                original_result = self.compute_helper(func=func, args=args, kwargs=kwargs,
                                                      configuration=configuration,
                                                      metrics=metrics,
                                                      metric_inputs=metric_inputs,
                                                      metric_outputs=metric_outputs,
                                                      metric_groups=[MetricGroup.RETRIEVAL_QUALITY])

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating retrieval quality metrics on {func.__name__},") from ex

        return wrapper(func)
