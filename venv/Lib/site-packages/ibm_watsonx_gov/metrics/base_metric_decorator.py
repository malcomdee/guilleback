# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from functools import partial
from json import dumps
from threading import Lock
from typing import Any, Callable, Set

from ibm_watsonx_gov.clients.api_client import APIClient
from ibm_watsonx_gov.config.agentic_ai_configuration import \
    AgenticAIConfiguration
from ibm_watsonx_gov.entities.agentic_app import MetricsConfiguration
from ibm_watsonx_gov.entities.enums import EvaluatorFields, MetricGroup
from ibm_watsonx_gov.entities.evaluation_result import AgentMetricResult
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.evaluators.impl.evaluate_metrics_impl import \
    _evaluate_metrics
from ibm_watsonx_gov.utils.python_utils import get_argument_value

try:
    from ibm_agent_analytics.instrumentation.utils import (
        AIEventRecorder, get_current_trace_id, record_span_attributes)
except:
    pass


class BaseMetricDecorator():
    """
    Base class for all metric decorators
    """

    def __init__(self, api_client: APIClient = None, configuration: AgenticAIConfiguration = None,
                 compute_real_time: bool = True, metric_results: list[AgentMetricResult] = [],
                 execution_counts: dict[str, dict[str, int]] = {},
                 nodes_being_run: dict[str, Set[str]] = {}, lock: Lock = None):
        self.api_client = api_client
        self.configuration = configuration
        self.compute_real_time = compute_real_time
        self.metric_results = metric_results
        self.execution_counts = execution_counts
        self.nodes_being_run = nodes_being_run
        self.lock = lock

    def validate(self, *, func: Callable, metrics: list[GenAIMetric], valid_metric_types: tuple[Any]):
        if not metrics:
            raise ValueError(
                "The 'metrics' argument can not be empty.")

        invalid_metrics = [metric.name for metric in metrics if not isinstance(
            metric, valid_metric_types)]
        if len(invalid_metrics):
            raise ValueError(
                f"The evaluator '{func.__name__}' is not applicable for "
                f"computing the metrics: {', '.join(invalid_metrics)}")

    def compute_helper(self, *, func: Callable,
                       args: tuple,
                       kwargs: dict[str, Any],
                       configuration: AgenticAIConfiguration,
                       metrics: list[GenAIMetric],
                       metric_inputs: list[EvaluatorFields],
                       metric_outputs: list[EvaluatorFields],
                       metric_references: list[EvaluatorFields] = [],
                       metric_groups: list[MetricGroup] = []) -> dict:
        """
        Helper method for computing metrics.

        Does the following:
            1. Computes node latency metric, and appends the result to the :py:attr:`AgenticEvaluation.metric_results` attribute.
            2. Calls the original node.
            3. Computes the list of metrics given, and appends the result to the :py:attr:`AgenticEvaluation.metric_results` attribute.
            4. Returns the result of the original node without any changes.

        Args:
            func (Callable): The node on which the metric is to be computed
            args (tuple): The tuple of positional arguments passed to the node
            kwargs (dict[str, Any]): The dictionary of keyword arguments passed to the node
            configuration (AgenticAIConfiguration): The node specific configuration
            metrics (list[GenAIMetric]): The list of metrics to compute.
            metric_inputs (list[EvaluatorFields]): The list of inputs for the metric.
            metric_outputs (list[EvaluatorFields]): The list of outputs for the metric.
            metric_references (list[EvaluatorFields], optional): The optional list of references for the metric. Defaults to [].

        Raises:
            ValueError: If the record id field is missing from the node inputs.

        Returns:
            dict: The result of the wrapped node.
        """

        get_arg_value = partial(
            get_argument_value, func=func, args=args, kwargs=kwargs)

        defaults = metric_inputs + metric_outputs + metric_references
        _configuration = AgenticAIConfiguration.create_configuration(app_config=self.configuration,
                                                                     method_config=configuration,
                                                                     defaults=defaults)
        _configuration.record_id_field = _configuration.interaction_id_field

        _data = {}
        # Add record id to the data
        _field = getattr(_configuration, EvaluatorFields.INTERACTION_ID_FIELD.value,
                         EvaluatorFields.get_default_fields_mapping()[EvaluatorFields.INTERACTION_ID_FIELD])

        try:
            _interaction_id_value = get_arg_value(
                param_name=_field) or get_current_trace_id()
        except ValueError:
            _interaction_id_value = get_current_trace_id()

        if _interaction_id_value is None:
            raise ValueError(
                f"The {_field} is required for evaluation. Please add it while invoking the application.")

        _data[_field] = _interaction_id_value

        if _interaction_id_value not in self.nodes_being_run:
            self.nodes_being_run[_interaction_id_value] = set()
        if _interaction_id_value not in self.execution_counts:
            self.execution_counts[_interaction_id_value] = dict()

        if func.__name__ not in self.nodes_being_run[_interaction_id_value]:
            self.nodes_being_run[_interaction_id_value].add(func.__name__)
            self.execution_counts[_interaction_id_value][func.__name__] = self.execution_counts[_interaction_id_value].get(
                func.__name__, 0) + 1

        original_result = func(*args, **kwargs)

        metric_result = []
        if self.compute_real_time:
            for field in metric_inputs + metric_references:
                _field = getattr(_configuration, field.value)
                if not (isinstance(_field, list)):
                    _field = [_field]
                _data.update(dict(map(lambda f: (
                    f, get_arg_value(param_name=f)), _field)))

            for field in metric_outputs:
                _field = getattr(_configuration, field.value)
                if not (isinstance(_field, list)):
                    _field = [_field]
                _data.update(dict(map(lambda f: (
                    f, original_result.get(f)), _field)))

            metric_result = _evaluate_metrics(configuration=_configuration, data=_data,
                                              metrics=metrics, metric_groups=metric_groups,
                                              api_client=self.api_client).to_dict()

            for mr in metric_result:
                node_result = {
                    "applies_to": "node",
                    "node_name": func.__name__,
                    **mr
                }
                node_result["interaction_id"] = node_result["record_id"]
                amr = AgentMetricResult(**node_result)

                AIEventRecorder.record_metric(name=amr.name,
                                              value=amr.value,
                                              attributes={"wxgov.result.metric": amr.model_dump_json(exclude_unset=True)})
                metrics_configuration = MetricsConfiguration(
                    configuration=_configuration, metrics=metrics)
                record_span_attributes({"wxgov.config.metrics."+str(type(self)).split(".")[2]: dumps({
                    "metrics_configuration": metrics_configuration.model_dump(mode="json"),
                    "compute_real_time": "true"
                })})

                with self.lock:
                    self.metric_results.append(amr)

        else:
            metrics_configuration = MetricsConfiguration(
                configuration=_configuration, metrics=metrics)
            # Store the configuration of metrics to compute in traces
            record_span_attributes({"wxgov.config.metrics."+str(type(self)).split(".")[2]: dumps({
                "metrics_configuration": metrics_configuration.model_dump(mode="json"),
                "compute_real_time": "false"
            })})

        return original_result
