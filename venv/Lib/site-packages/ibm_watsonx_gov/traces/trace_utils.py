# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, Generator, List

from ibm_watsonx_gov.clients.api_client import APIClient
from ibm_watsonx_gov.entities.agentic_app import MetricsConfiguration, Node
from ibm_watsonx_gov.entities.enums import MetricGroup
from ibm_watsonx_gov.entities.evaluation_result import AgentMetricResult
from ibm_watsonx_gov.evaluators.impl.evaluate_metrics_impl import \
    _evaluate_metrics
from ibm_watsonx_gov.traces.span_node import SpanNode
from ibm_watsonx_gov.traces.span_util import (get_attributes,
                                              get_span_nodes_from_json)
from ibm_watsonx_gov.utils.python_utils import add_if_unique

try:
    from opentelemetry.proto.trace.v1.trace_pb2 import Span
except:
    pass

TARGETED_USAGE_TRACE_NAMES = [
    "openai.embeddings",
    "ChatOpenAI.chat",
    # TODO: check attributes for other frameworks as well.
]
ONE_M = 1000000
COST_METADATA = {  # Costs per 1M tokens
    "openai": {
        "gpt-4o": {"input": 5.0, "output": 15.0},
        "gpt-4-turbo": {"input": 10.0, "output": 30.0},
        "gpt-4": {"input": 30.0, "output": 60.0},
        "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
        # Note: Added from web
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "text-embedding-3-small": {"input": 0.02, "output": 0.0},
    },
    "anthropic": {
        "claude-3-opus": {"input": 15.0, "output": 75.0},
        "claude-3-sonnet": {"input": 3.0, "output": 15.0},
        "claude-3-haiku": {"input": 0.25, "output": 1.25},
    },
    "google": {
        "gemini-1.5-pro": {"input": 7.0, "output": 21.0},
        "gemini-1.5-flash": {"input": 0.35, "output": 1.05},
    },
    "mistral": {
        "mistral-large": {"input": 8.0, "output": 24.0},
        "mistral-7b": {"input": 0.25, "output": 0.80},
        "mixtral-8x7b": {"input": 1.00, "output": 3.00},
    },
    "cohere": {
        "command-r": {"input": 1.00, "output": 3.00},
    },
    "ai21": {
        "jurassic-2": {"input": 10.0, "output": 20.0},
    },
}


class TraceUtils:

    @staticmethod
    def build_span_trees(spans: list[dict]) -> List[SpanNode]:
        root_spans: list[SpanNode] = []

        span_nodes: dict[str, SpanNode] = {}
        for span in spans:
            span_nodes.update(get_span_nodes_from_json(span))

        # Create tree
        for span_id, node in span_nodes.items():
            parent_id = node.span.parent_span_id
            if not parent_id:
                root_spans.append(node)  # Root span which will not have parent
            else:
                parent_node = span_nodes.get(parent_id)
                if parent_node:
                    parent_node.add_child(node)
                else:
                    # Orphan span where parent is not found
                    root_spans.append(node)

        return root_spans

    @staticmethod
    def convert_array_value(array_obj: Dict) -> List:
        """Convert OTEL array value to Python list"""
        return [
            item.get("stringValue")
            or int(item.get("intValue", ""))
            or float(item.get("doubleValue", ""))
            or bool(item.get("boolValue", ""))
            for item in array_obj.get("values", [])
        ]

    @staticmethod
    def stream_trace_data(file_path: Path) -> Generator:
        """Generator that yields spans one at a time."""
        with open(file_path) as f:
            for line in f:
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as e:
                    print(f"Failed to parse line: {line}\nError: {e}")

    @staticmethod
    def __extract_usage_meta_data(span: Span) -> dict:
        """
        Extract meta data required to calculate usage metrics from spans
        """
        meta_data = {}
        attributes = get_attributes(span.attributes)
        provider = attributes.get(
            "traceloop.association.properties.ls_provider", attributes.get("gen_ai.system"))
        llm_type = attributes.get("llm.request.type")
        model = attributes.get("gen_ai.request.model")

        if not llm_type or not model:
            return meta_data

        cost_key = (provider, llm_type, model)
        meta_data["cost"] = {
            "provider_details": cost_key,
            "total_prompt_tokens": attributes.get("gen_ai.usage.prompt_tokens", 0),
            "total_completion_tokens": attributes.get(
                "gen_ai.usage.completion_tokens", 0
            ),
            "total_tokens": attributes.get("llm.usage.total_tokens", 0),
        }
        meta_data["input_token_count"] = attributes.get(
            "gen_ai.usage.prompt_tokens", 0)
        meta_data["output_token_count"] = attributes.get(
            "gen_ai.usage.completion_tokens", 0)
        return meta_data

    @staticmethod
    def calculate_cost(usage_data: List[dict]) -> float:
        """Calculate cost for given list of usage."""
        total_cost = 0.0

        for data in usage_data:
            (provider, _, model) = data["provider_details"]
            provider = provider.lower()
            model = model.lower()

            try:
                model_pricing = COST_METADATA[provider][model]
            except KeyError:
                return 0
                # raise ValueError(
                #     f"Pricing not available for {provider}/{model}")

            # Calculate costs (per 1M tokens)
            input_cost = (data["total_prompt_tokens"] /
                          ONE_M) * model_pricing["input"]
            output_cost = (data["total_completion_tokens"] / ONE_M) * model_pricing[
                "output"
            ]
            total_cost += input_cost + output_cost

        return total_cost

    @staticmethod
    def compute_metrics_from_trace(span_tree: SpanNode, api_client: APIClient = None) -> tuple[list[AgentMetricResult], list[Node], list]:
        metric_results, edges = [], []

        # Add Interaction level metrics
        metric_results.extend(TraceUtils.__compute_interaction_level_metrics(
            span_tree, api_client))

        # Add node level metrics result
        node_metric_results, nodes_list, experiment_run_metadata = TraceUtils.__compute_node_level_metrics(
            span_tree, api_client)
        metric_results.extend(node_metric_results)

        return metric_results, nodes_list, edges, experiment_run_metadata

    @staticmethod
    def __compute_node_level_metrics(span_tree: SpanNode, api_client: APIClient | None):
        metric_results = []
        trace_metadata = defaultdict(list)
        experiment_run_metadata = defaultdict(lambda: defaultdict(list))
        nodes_list = []
        node_stack = list(span_tree.children)
        child_stack = list()
        node_execution_count = {}
        while node_stack or child_stack:
            is_parent = not child_stack
            node = child_stack.pop() if child_stack else node_stack.pop()
            if is_parent:
                parent_span: Span = node.span
                node_name, metrics_config_from_decorators, code_id, events, execution_order = None, [], "", [], None
                data = {}
                # inputs = get_nested_attribute_values(
                #     [node], "traceloop.entity.input")
                # outputs = get_nested_attribute_values(
                #     [node], "traceloop.entity.output")
            span: Span = node.span

            for attr in span.attributes:
                key = attr.key
                value = attr.value

                if is_parent:
                    if key == "traceloop.entity.name":
                        node_name = value.string_value
                    elif key == "gen_ai.runnable.code_id":
                        code_id = value.string_value
                    elif key == "traceloop.association.properties.langgraph_step":
                        execution_order = int(
                            value.int_value) if value else None
                    elif key in ("traceloop.entity.input", "traceloop.entity.output"):
                        try:
                            content = json.loads(value.string_value)
                            inputs_outputs = content.get(
                                "inputs" if key.endswith("input") else "outputs")
                            if isinstance(inputs_outputs, str):
                                inputs_outputs = json.loads(inputs_outputs)
                            if data:
                                data.update(inputs_outputs)
                            else:
                                data = inputs_outputs
                        except (json.JSONDecodeError, AttributeError) as e:
                            raise Exception(
                                "Unable to parse json string") from e
                if key.startswith("wxgov.config.metrics"):
                    metrics_config_from_decorators.append(
                        json.loads(value.string_value))
            if span.events:
                events.extend(span.events)

            if (not node_name) or (node_name == "__start__"):
                continue

            if span.name in TARGETED_USAGE_TRACE_NAMES:
                # Extract required details to calculate usage metrics from each span
                for k, v in TraceUtils.__extract_usage_meta_data(span).items():
                    trace_metadata[k].append(v)

            for k, v in TraceUtils.__get_run_metadata_from_span(span).items():
                experiment_run_metadata[node_name][k].append(v)

            child_stack.extend(node.children)

            if not child_stack:
                metrics_to_compute, all_metrics_config = TraceUtils.__get_metrics_to_compute(
                    span_tree.get_nodes_configuration(), node_name, metrics_config_from_decorators)

                add_if_unique(Node(name=node_name, func_name=code_id.split(":")[-1] if code_id else node_name, metrics_configurations=all_metrics_config), nodes_list,
                              ["name", "func_name"])

                if node_name in node_execution_count:
                    node_execution_count[node_name] += node_execution_count.get(
                        node_name)
                else:
                    node_execution_count[node_name] = 1

                for mc in metrics_to_compute:
                    metric_result = _evaluate_metrics(configuration=mc.configuration,
                                                      data=data,
                                                      metrics=mc.metrics,
                                                      metric_groups=mc.metric_groups,
                                                      api_client=api_client).to_dict()
                    for mr in metric_result:
                        node_result = {
                            "applies_to": "node",
                            "interaction_id": span_tree.get_interaction_id(),
                            "node_name": node_name,
                            "conversation_id": span_tree.get_conversation_id(),
                            "execution_count": node_execution_count.get(node_name),
                            "execution_order": execution_order,
                            ** mr
                        }

                        metric_results.append(AgentMetricResult(**node_result))

                # Add node latency metric result
                metric_results.append(AgentMetricResult(name="latency",
                                                        value=(int(
                                                            parent_span.end_time_unix_nano) - int(parent_span.start_time_unix_nano))/1e9,
                                                        group=MetricGroup.PERFORMANCE,
                                                        applies_to="node",
                                                        interaction_id=span_tree.get_interaction_id(),
                                                        conversation_id=span_tree.get_conversation_id(),
                                                        node_name=node_name,
                                                        execution_count=node_execution_count.get(
                                                            node_name),
                                                        execution_order=execution_order))

                # Get the node level metrics computed online during graph invocation from events
                metric_results.extend(TraceUtils.__get_metrics_results_from_events(
                    events=events,
                    interaction_id=span_tree.get_interaction_id(),
                    conversation_id=span_tree.get_conversation_id(),
                    node_name=node_name,
                    execution_count=node_execution_count.get(node_name),
                    execution_order=execution_order))

        metric_results.extend(
            TraceUtils.__compute_interaction_metrics_from_trace_metadata(trace_metadata, span_tree.get_interaction_id(), span_tree.get_conversation_id()))

        return metric_results, nodes_list, experiment_run_metadata

    @staticmethod
    def __compute_interaction_level_metrics(span_tree: SpanNode, api_client: APIClient | None) -> list[AgentMetricResult]:
        metric_results = []
        span = span_tree.span
        metric_results.append(AgentMetricResult(name="duration",
                                                value=(int(
                                                    span.end_time_unix_nano) - int(span.start_time_unix_nano))/1000000000,
                                                group=MetricGroup.PERFORMANCE,
                                                applies_to="interaction",
                                                interaction_id=span_tree.get_interaction_id(),
                                                conversation_id=span_tree.get_conversation_id()))

        if not span_tree.agentic_app:
            return metric_results

        data = {}

        attrs = get_attributes(
            span.attributes, ["traceloop.entity.input", "traceloop.entity.output"])
        inputs = json.loads(
            attrs.get("traceloop.entity.input", "{}")).get("inputs", {})

        if "messages" in inputs:
            for message in reversed(inputs["messages"]):
                if "kwargs" in message and "type" in message["kwargs"] and message["kwargs"]["type"].upper() == "HUMAN":
                    data["input_text"] = message["kwargs"]["content"]
                    break
        else:
            data.update(inputs)

        outputs = json.loads(
            attrs.get("traceloop.entity.output", "{}")).get("outputs", {})

        if "messages" in outputs:
            # The messages is a list depicting the history of interactions with the agent.
            # It need NOT be the whole list of interactions in the conversation though.
            # We will traverse the list from the end to find the human input of the interaction,
            # and the AI output.

            # If there was no input_text so far, find first human message
            if "input_text" not in data:
                for message in reversed(outputs["messages"]):
                    if "kwargs" in message and "type" in message["kwargs"] and message["kwargs"]["type"].upper() == "HUMAN":
                        data["input_text"] = message["kwargs"]["content"]
                        break

            # Find last AI message
            for message in reversed(outputs["messages"]):
                if "kwargs" in message and "type" in message["kwargs"] and message["kwargs"]["type"].upper() == "AI":
                    data["generated_text"] = message["kwargs"]["content"]
                    break
        else:
            data.update(outputs)

        metric_result = _evaluate_metrics(configuration=span_tree.agentic_app.metrics_configuration.configuration,
                                          data=data,
                                          metrics=span_tree.agentic_app.metrics_configuration.metrics,
                                          metric_groups=span_tree.agentic_app.metrics_configuration.metric_groups,
                                          api_client=api_client).to_dict()
        for mr in metric_result:
            node_result = {
                "applies_to": "interaction",
                "interaction_id": span_tree.get_interaction_id(),
                "conversation_id": span_tree.get_conversation_id(),
                **mr
            }

            metric_results.append(AgentMetricResult(**node_result))

        return metric_results

    @staticmethod
    def __get_metrics_to_compute(nodes_config, node_name, metrics_configurations):
        metrics_to_compute, all_metrics_config = [], []

        if nodes_config.get(node_name):
            metrics_config = nodes_config.get(node_name)
            for mc in metrics_config:
                mc_obj = MetricsConfiguration(configuration=mc.configuration,
                                              metrics=mc.metrics,
                                              metric_groups=mc.metric_groups)
                metrics_to_compute.append(mc_obj)
                all_metrics_config.append(mc_obj)

        for mc in metrics_configurations:
            mc_obj = MetricsConfiguration.model_validate(
                mc.get("metrics_configuration"))

            all_metrics_config.append(mc_obj)
            if mc.get("compute_real_time") == "false":
                metrics_to_compute.append(mc_obj)

        return metrics_to_compute, all_metrics_config

    @staticmethod
    def __get_metrics_results_from_events(events, interaction_id, conversation_id, node_name, execution_count, execution_order):
        results = []
        if not events:
            return results

        for event in events:
            for attr in event.attributes:
                if attr.key == "attr_wxgov.result.metric":
                    val = attr.value.string_value
                    if val:
                        mr = json.loads(val)
                        mr.update({
                            "node_name": node_name,
                            "interaction_id": interaction_id,
                            "conversation_id": conversation_id,
                            "execution_count": execution_count,
                            "execution_order": execution_order
                        })
                        results.append(AgentMetricResult(**mr))

        return results

    @staticmethod
    def __compute_interaction_metrics_from_trace_metadata(trace_metadata: dict, interaction_id: str, conversation_id: str) -> list:
        metrics_result = []

        for metric, data in trace_metadata.items():
            if metric == "cost":
                metric_value = TraceUtils.calculate_cost(data)
            elif metric == "input_token_count":
                metric_value = sum(data)
            elif metric == "output_token_count":
                metric_value = sum(data)
            else:
                continue
            agent_mr = {
                "name": metric,
                "value": metric_value,
                "interaction_id": interaction_id,
                "applies_to": "interaction",
                "conversation_id": conversation_id,
                "group": MetricGroup.USAGE.value
            }

            metrics_result.append(AgentMetricResult(**agent_mr))

        return metrics_result

    @staticmethod
    def __get_run_metadata_from_span(span: Span) -> dict:
        """
        Extract run specific metadata from traces
        1. Foundation model involved in run
        2. Tools involved in run
        """
        metadata = {}
        attributes = get_attributes(span.attributes)
        provider = attributes.get(
            "traceloop.association.properties.ls_provider", attributes.get("gen_ai.system"))
        llm_type = attributes.get("llm.request.type")
        model = attributes.get("gen_ai.request.model")

        if model:
            metadata["foundation_models"] = {
                "model": model,
                "provider": provider,
                "type": llm_type
            }

        return metadata
