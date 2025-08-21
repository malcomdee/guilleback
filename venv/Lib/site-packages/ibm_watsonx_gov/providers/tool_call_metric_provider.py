# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
import asyncio
import json

import nest_asyncio
import pandas as pd
from ibm_watsonx_gov.config import AgenticAIConfiguration, GenAIConfiguration
from ibm_watsonx_gov.entities.evaluation_result import (AggregateMetricResult,
                                                        RecordMetricResult)
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.utils.python_utils import (
    get, parse_functions_to_openai_schema)
from llmevalkit.function_calling.pipeline.pipeline import ReflectionPipeline
from llmevalkit.function_calling.pipeline.types import ToolCall, ToolSpec

nest_asyncio.apply()


class ToolCallMetricProvider():
    """
    Base class for Tool Call Metrics Computation.
    """

    def __init__(self, configuration: GenAIConfiguration | AgenticAIConfiguration, metric: GenAIMetric):
        """
        Initialize the ToolCallMetricProvider with the configuration.

        Args:
            configuration (GenAIConfiguration | AgenticAIConfiguration): The configuration for the metric computation.
            metric (GenAIMetric): The metric to be computed.
        """
        self.configuration = configuration
        self.metric = metric

    def pre_process(self, data: pd.DataFrame):
        """
        Preprocess the dataframe and tool list for metrics computation

        Args:
            data (pd.DataFrame): Input dataframe

        Returns:
            pd.Dataframe: Processed dataframe
        """
        # Get the specification of tools used in the application
        # in proper format if it is a list of Callable
        if isinstance(self.configuration.tools, list) and all(callable(item) for item in self.configuration.tools):
            self.configuration.tools = self.get_tools_list_schema(
                configuration.tools)

        # TODO: Add validation for the tool_call_field data schema
        tool_call_field = self.configuration.tool_calls_field
        if tool_call_field:
            data[tool_call_field] = data[tool_call_field].apply(
                lambda x: json.loads(x) if isinstance(x, str) else x)
        return data

    @staticmethod
    def get_tools_list_schema(tools: list) -> list:
        """
        Convert the list of callable objects to the
        format needed for the TCH computation

        Args:
            tools (list): List of Callable objects

        Returns:
            list: List of dictionary containing the tool
            specifications
        """
        tools_specifications = []
        for func in tools:
            tool_schema = parse_functions_to_openai_schema(func)
            if not tool_schema:
                continue
            tools_specifications.append(ToolSpec.model_validate(tool_schema))

        return tools_specifications

    def compute_metrics(self, data: pd.DataFrame, syntactic_only: bool = True, metric_result_mapping_name: str = None, **kwargs):
        """
        Compute the Tool Call Metrics for the given data

        Args:
            data (pd.DataFrame): Input data including the tools used for the application
            syntactic_only (bool): If True, compute only syntactic metrics.
            metric_result_mapping_name (str): The mapping name for the metric result with the llmevalkit
            kwargs: Additional keyword arguments for the pipeline

        Returns:
            list: List of metrics calculated for each record
        """
        try:

            data = self.pre_process(data)
            tool_calls_field = self.configuration.tool_calls_field
            record_id_field = self.configuration.record_id_field
            record_level_metrics = []

            # Do not compute metrics if llm_judge is not set
            # and trying to compute a non syntactic metrics
            if not getattr(self.metric, "llm_judge", None) and not syntactic_only:
                return []

            if not all(isinstance(t, ToolSpec) for t in self.configuration.tools):
                self.configuration.tools = [ToolSpec.model_validate(
                    func) for func in self.configuration.tools]

            for _, row in data.iterrows():
                tool_calls = self.extract_tool_calls_from_response(
                    row[tool_calls_field])

                if not tool_calls:
                    record_level_metrics.append({
                        "value": 0.0,  # Treat no tool calls as 0 score
                        "record_id": row[record_id_field],
                        "explanations": "LLM did not make any tool calls"
                    })
                    continue

                if syntactic_only:
                    tool_call_level_explanation = self.compute_syntactic_metrics(
                        data=row, tool_calls=tool_calls)
                    record_level_metrics.append({
                        "value": 1.0 if tool_call_level_explanation else 0.0,
                        "record_id": row[record_id_field],
                        "explanations": tool_call_level_explanation
                    })
                else:
                    tool_call_level_explanation = self.compute_semantic_metrics(
                        data=row, tool_calls=tool_calls, metric_result_mapping_name=metric_result_mapping_name, **kwargs)
                    record_level_metrics.append({
                        "value": 1.0 if any(
                            entry.get("is_issue") is True
                            for entry in tool_call_level_explanation
                        ) else 0.0,
                        "record_id": row[record_id_field],
                        "explanations": tool_call_level_explanation
                    })

            metric_result = self.post_process(
                record_level_metrics)

            return metric_result
        except Exception as ex:
            raise Exception(
                f"Error while computing metrics: '{self.metric.name}' using '{self.metric.method}'. Reason: {str(ex)}")

    def compute_syntactic_metrics(self, data: pd.DataFrame, tool_calls: list):
        """
        Compute the Tool Call Metrics for the given data
        in static mode

        Args:
            data (pd.DataFrame): Input data including the tools used for the application
            tool_calls (list): List of tool calls made by the LLM

        Returns:
            list: List of metrics calculated for each record
        """
        tool_call_level_explanation = []
        for call in tool_calls:
            explanations = ReflectionPipeline.static_only(
                inventory=self.configuration.tools, call=ToolCall.model_validate(call))
            explanations = explanations.model_dump()
            if explanations.get("final_decision") is False:
                tool_call_level_explanation.append({
                    "tool_name": call.get("function").get("name"),
                    "hallucinations": {
                        key: val for key, val in explanations["metrics"].items() if not val["valid"]
                    }
                })
        return tool_call_level_explanation

    def compute_semantic_metrics(self, data: pd.DataFrame, tool_calls: list, metric_result_mapping_name: str, **kwargs):
        """
        Compute the Tool Call Metrics for the given data
        in semantic mode

        Args:
            data (pd.DataFrame): Input data including the tools used for the application
            configuration (GenAIConfiguration | AgenticAIConfiguration): Metrics configuration
            metric_result_mapping_name (str): The mapping name for the metric result with the llmevalkit
            kwargs: Additional keyword arguments for the pipeline

        Returns:
            list: List of metrics calculated for each record
        """
        import json
        tool_call_level_explanation = []
        for call in tool_calls:
            pipeline = ReflectionPipeline(
                metrics_client=self.get_llm_metric_client(
                    self.metric.llm_judge),
                **kwargs
            )

            result = asyncio.run(pipeline.semantic_async(
                conversation=data[self.configuration.input_fields[0]],
                inventory=self.configuration.tools,
                call=ToolCall.model_validate(call),
                retries=2
            ))

            explanations = get(
                result.model_dump(), f"{metric_result_mapping_name}.metrics.{self.metric.metric_mapping_name}")

            if explanations:
                tool_call_level_explanation.append({
                    "tool_name": get(call, "function.name"),
                    "is_issue": get(explanations, "is_issue"),
                    "explanation": get(explanations, "raw_response.explanation"),
                    "evidence": get(explanations, "raw_response.evidence"),
                    "correction": get(explanations, "raw_response.correction")
                })
        return tool_call_level_explanation

    def extract_tool_calls_from_response(self, tool_calls_response) -> list:
        """
        Extracts the tool calls from the response

        Args:
            tool_calls_response (Any): The tool calls response
            can be a list of dictionary, an AIMessage object
            or a dictionary

        Returns:
            list: List of openai formatted tool call
        """
        if isinstance(tool_calls_response, dict):
            tool_calls = get(tool_calls_response, "kwargs.tool_calls")
        elif hasattr(tool_calls_response, "tool_calls"):
            tool_calls = tool_calls_response.tool_calls
        else:
            tool_calls = tool_calls_response
        converted = []
        for call in tool_calls:
            converted.append({
                "id": call["id"],
                "type": "function",
                "function": {
                    "name": call["name"],
                    "arguments": json.dumps(call["args"])
                }
            })
        return converted

    def post_process(self, results: pd.DataFrame):
        """
        Post process the computed metrics to get the Aggregated Result and
        Record level metric result in the proper format

        Args:
            results (pd.DataFrame): Computed metric results
            configuration (GenAIConfiguration | AgenticAIConfiguration): Metric configuration

        Returns:
            AggregateMetricResult: The AggregateMetricResult object containing the calculated
            metrics information
        """

        # Preparing the record level metrics
        record_level_metrics: list[RecordMetricResult] = []

        for row in results:
            record_level_metrics.append(
                RecordMetricResult(
                    name=self.metric.name,
                    method=self.metric.method,
                    value=row.get("value"),
                    provider="ibm",
                    group=self.metric.group,
                    record_id=row["record_id"],
                    thresholds=self.metric.thresholds,
                    additional_info={"explanations": row.get("explanations")}
                )
            )

        # Get the number of records are violated, min, max
        values = [item.get("value", 0.0) for item in results]
        count_invalid = sum(val == 1.0 for val in values)
        min_value = min(values, default=0.0)
        max_value = max(values, default=0.0)
        value = int(count_invalid)/int(len(results))

        # creating AggregateMetricResult
        aggregated_result = AggregateMetricResult(
            name=self.metric.name,
            method=self.metric.method,
            provider="ibm",
            group=self.metric.group,
            value=value,
            total_records=len(results),
            record_level_metrics=record_level_metrics,
            min=min_value,
            max=max_value,
            thresholds=self.metric.thresholds
        )

        # return the aggregated result
        return aggregated_result

    def get_llm_metric_client(self, llm_judge):
        """
        Based on the llm_judge return the
        metrics client for semantic metrics
        """
        from llmevalkit.llm import get_llm

        if llm_judge.get_model_provider() == "ibm_watsonx.ai":
            MetricsClientCls = get_llm("litellm.watsonx.output_val")
        elif llm_judge.get_model_provider() == "openai":
            MetricsClientCls = get_llm("openai.async")

        metrics_client = MetricsClientCls(
            model_name=llm_judge.model.model_id)

        return metrics_client

    def extract_parameter_info(self, data, metric_mapping_name):
        """
        Extract parameter metrics into a list

        Args:
            data (dict): Response data to be extracted
            metric_mapping_name (str): Metric mapping name

        Returns:
            List: List of Parameter based explanation
        """
        result = {
            "is_issue": False,
            "raw_response": []
        }

        for param_name, param_data in data.get("parameter", {}).items():
            metrics = get(param_data, f"metrics.{metric_mapping_name}")
            raw_response = metrics['raw_response']
            is_issue = metrics.get('is_issue', False)

            if is_issue:
                result["is_issue"] = True

            param_info = {
                "parameter": param_name,
                "explanation": raw_response['explanation'],
                "evidence": raw_response['evidence'],
                "output": raw_response['output'],
                "confidence": raw_response['confidence'],
                "correction": raw_response['correction'],
                "is_issue": is_issue
            }

            result["raw_response"].append(param_info)

        return result
