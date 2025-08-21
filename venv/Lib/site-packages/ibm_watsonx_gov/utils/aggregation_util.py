# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from collections import defaultdict
from copy import copy
from typing import List

import numpy as np

from ibm_watsonx_gov.entities.agentic_app import Node
from ibm_watsonx_gov.entities.enums import MetricGroup
from ibm_watsonx_gov.entities.evaluation_result import (
    AgenticEvaluationResult, AgentMetricResult, AggregateAgentMetricResult,
    RecordMetricResult)
from ibm_watsonx_gov.metrics.llm_validation.llm_validation_metric import \
    LLMValidationMetric


def __get_aggregation_result(values: List[AgentMetricResult]) -> AggregateAgentMetricResult:
    vals = []
    for v in values:
        if v.value is not None:
            vals.append(v.value)

    if vals:
        mv = values[0]
        mean = sum(vals) / len(vals)
        return AggregateAgentMetricResult(name=mv.name,
                                          method=mv.method,
                                          provider=mv.provider,
                                          node_name=mv.node_name,
                                          applies_to=mv.applies_to,
                                          group=mv.group,
                                          value=mean,
                                          min=min(vals),
                                          max=max(vals),
                                          count=len(vals),
                                          individual_results=values)

    return None


def __compute_aggregated_metrics_results(metrics_result: List[AgentMetricResult],
                                         nodes: List[Node],
                                         include_individual_results: bool = True) -> List[AggregateAgentMetricResult]:

    nodes_result_group, interaction_result_group, conversation_result_map = __get_grouped_metrics_result(
        metrics_result)

    aggregated_results = []
    aggregated_results.extend(__get_aggregated_node_metrics(
        include_individual_results, nodes, nodes_result_group))
    aggregated_results.extend(
        __get_aggregated_metrics(interaction_result_group))
    aggregated_results.extend(
        __get_aggregated_metrics(conversation_result_map))

    return aggregated_results


def __get_aggregated_metrics(interaction_results):
    aggregated_results = []
    # Aggregate interaction or conversation level metrics
    for values in list(interaction_results.values()):
        aggregated_result = __get_aggregation_result(
            values)
        if aggregated_result:
            aggregated_results.append(aggregated_result)
    return aggregated_results


def __get_grouped_metrics_result(metrics_result):
    """
    Group the metrics results based on node and interaction.
    """
    nodes_result_map, interaction_result_map = {}, {}
    conversation_result_map = defaultdict(list)
    conversation_metrics = defaultdict(lambda: defaultdict(float))
    for mr in metrics_result:
        key = mr.name+"_"+mr.method if mr.method else mr.name
        if mr.applies_to == "node":
            if mr.node_name in nodes_result_map:
                if key in nodes_result_map[mr.node_name]:
                    nodes_result_map[mr.node_name][key].append(mr)
                else:
                    nodes_result_map[mr.node_name][key] = [mr]
            else:
                nodes_result_map[mr.node_name] = {
                    key: [mr]
                }
        elif mr.applies_to == "interaction":
            if key in interaction_result_map:
                interaction_result_map[key].append(mr)
            else:
                interaction_result_map[key] = [mr]
            if key in ("duration", "cost", "input_token_count", "output_token_count"):
                conversation_metrics[mr.conversation_id][key] += mr.value
    for conversation_id, metric_value in conversation_metrics.items():
        for metric, value in metric_value.items():
            conversation_result_map[metric].append(AgentMetricResult(name=metric,
                                                                     value=value,
                                                                     group=MetricGroup.PERFORMANCE.value if metric == "duration" else MetricGroup.USAGE.value,
                                                                     interaction_id=None,
                                                                     applies_to="conversation",
                                                                     conversation_id=conversation_id))

    return nodes_result_map, interaction_result_map, dict(conversation_result_map)


def __get_aggregated_node_metrics(include_individual_results, nodes, nodes_results):
    aggregated_results = []

    # Create node metrics dict for easy access to metrics
    node_to_metrics = {}
    for n in nodes:
        mts = {}
        for mc in n.metrics_configurations:
            for m in mc.metrics:
                mts[m.id] = m
        node_to_metrics[n.name] = mts

    # Aggregate node level metrics
    for node, node_metrics in nodes_results.items():
        for metric_key, values in node_metrics.items():
            aggregated_result = None
            metric_obj = node_to_metrics.get(node, {}).get(metric_key)

            if isinstance(metric_obj, LLMValidationMetric):
                # convert metrics result from AgentMetricResult to RecordMetricResult used by the metric
                __get_llm_validation_metric_aggregation_result(
                    include_individual_results, values, metric_obj)
            else:
                aggregated_result = __get_aggregation_result(
                    values)
            if aggregated_result:
                aggregated_results.append(aggregated_result)
    return aggregated_results


def __get_llm_validation_metric_aggregation_result(include_individual_results, values, metric_obj):
    record_level_metrics = [RecordMetricResult(
        **v.__dict__, record_id=v.interaction_id) for v in values]
    aggregated_result = metric_obj.get_aggregated_results_from_individual_results(
        record_level_metrics)

    # convert updated record results to AgentMetricResult
    updated_record_level_metrics = aggregated_result.record_level_metrics
    agent_individual_results = []
    for record_result, agent_result in zip(updated_record_level_metrics, values):
        args = {**agent_result.__dict__,
                **record_result.__dict__}
        agent_individual_results.append(
            AgentMetricResult(**args))

    if aggregated_result:
        # convert AggregateMetricResult to AggregateAgentMetricResult
        mv = values[0]
        aggregated_result = AggregateAgentMetricResult(
            name=mv.name,
            method=mv.method,
            provider=mv.provider,
            node_name=mv.node_name,
            applies_to=mv.applies_to,
            group=mv.group,
            value=aggregated_result.mean,
            min=aggregated_result.min,
            max=aggregated_result.max,
            count=aggregated_result.total_records,
            individual_results=copy.deepcopy(
                agent_individual_results) if include_individual_results else [],
            additional_info=copy.deepcopy(
                aggregated_result.additional_info)
        )


def get_agentic_evaluation_result(metrics_result: list[AgentMetricResult], nodes: list[Node] = []) -> AgenticEvaluationResult:
    aggregated_metrics_results = __compute_aggregated_metrics_results(
        metrics_result, nodes)
    metrics_result = []
    for amr in aggregated_metrics_results:
        metrics_result.extend(amr.individual_results)

    return AgenticEvaluationResult(metrics_results=metrics_result,
                                   aggregated_metrics_results=aggregated_metrics_results)


def get_summaries(individual_metric_values: list):
    """
    Calculates statistical summaries for a list of numeric metric values.

    Args:
        individual_metric_values (list): A list of numeric values representing individual
                                       metrics. May contain None values which will be filtered out.

    Returns:
        dict: A dictionary containing the following statistical summaries:
            - "metric_value" (float): Mean of the values (same as "mean")
            - "mean" (float): Arithmetic mean of the values
            - "min" (float): Minimum value in the dataset
            - "max" (float): Maximum value in the dataset  
            - "std" (float): Standard deviation of the values

            If input is empty or contains only None values, returns:
            {"metric_value": 0, "mean": 0, "min": 0, "max": 0, "std": 0}
    """
    individual_metric_values = [
        ele for ele in individual_metric_values if ele is not None]

    if individual_metric_values is None or len(individual_metric_values) == 0:
        return {
            "metric_value": 0,
            "mean": 0,
            "min": 0,
            "max": 0,
            "std": 0
        }
    else:
        return {
            "metric_value": np.mean(individual_metric_values).item(),
            "mean": np.mean(individual_metric_values).item(),
            "min": np.min(individual_metric_values).item(),
            "max": np.max(individual_metric_values).item(),
            "std": np.std(individual_metric_values).item()
        }
