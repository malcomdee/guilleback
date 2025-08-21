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

from ibm_watsonx_gov.config.agentic_ai_configuration import \
    AgenticAIConfiguration
from ibm_watsonx_gov.entities.enums import EvaluatorFields
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.metrics.base_metric_decorator import BaseMetricDecorator
from ibm_watsonx_gov.metrics.harm.harm_metric import HarmMetric


class HarmDecorator(BaseMetricDecorator):

    def evaluate_harm(self,
                      func: Optional[Callable] = None,
                      *,
                      configuration: Optional[AgenticAIConfiguration] = None,
                      metrics: list[GenAIMetric] = []
                      ) -> dict:
        """
        An evaluation decorator for computing harm risk on an agentic node via granite guardian.
        """
        if func is None:
            return partial(self.evaluate_harm, configuration=configuration, metrics=metrics)

        if not metrics:
            metrics = [HarmMetric()]

        @decorator
        def wrapper(func, instance, args, kwargs):

            try:
                self.validate(func=func, metrics=metrics,
                              valid_metric_types=(HarmMetric,))

                metric_inputs = [EvaluatorFields.INPUT_FIELDS]

                original_result = self.compute_helper(func=func, args=args, kwargs=kwargs,
                                                      configuration=configuration,
                                                      metrics=metrics,
                                                      metric_inputs=metric_inputs,
                                                      metric_outputs=[])

                return original_result
            except Exception as ex:
                raise Exception(
                    f"There was an error while evaluating harm risk on {func.__name__},") from ex

        return wrapper(func)
