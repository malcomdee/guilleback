# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import copy
import uuid
from dataclasses import Field
from datetime import datetime
from typing import Annotated, Any, List, Literal, Optional

import pandas as pd
from pydantic import BaseModel, Field

from ibm_watsonx_gov.entities.base_classes import BaseMetricResult

AGENTIC_RESULT_COMPONENTS = Literal["conversation", "interaction", "node"]


class RecordMetricResult(BaseMetricResult):
    record_id: Annotated[str, Field(
        description="The record identifier.", examples=["record1"])]
    record_timestamp: Annotated[str | None, Field(
        description="The record timestamp.", examples=["2025-01-01T00:00:00.000000Z"], default=None)]


class ToolMetricResult(RecordMetricResult):
    tool_name: Annotated[str, Field(
        title="Tool Name", description="Name of the tool for which this result is computed.")]
    execution_count: Annotated[int, Field(
        title="Execution count", description="The execution count for this tool name.", gt=0, default=1)]

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, ToolMetricResult):
            return False

        return (self.record_id, self.tool_name, self.execution_count, self.name, self.method, self.value, self.record_timestamp) == \
            (other.record_id, other.tool_name, other.execution_count,
             other.name, other.method, other.value, other.record_timestamp)

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, ToolMetricResult):
            raise NotImplemented

        return (self.record_id, self.tool_name, self.execution_count, self.name, self.method, self.value, self.record_timestamp) < \
            (other.record_id, other.tool_name, other.execution_count,
             other.name, other.method, other.value, other.record_timestamp)

    def __gt__(self, other: Any) -> bool:
        if not isinstance(other, ToolMetricResult):
            raise NotImplemented

        return (self.record_id, self.tool_name, self.execution_count, self.name, self.method, self.value, self.record_timestamp) > \
            (other.record_id, other.tool_name, other.execution_count,
             other.name, other.method, other.value, other.record_timestamp)

    def __le__(self, other: Any) -> bool:
        if not isinstance(other, ToolMetricResult):
            raise NotImplemented

        return (self.record_id, self.tool_name, self.execution_count, self.name, self.method, self.value, self.record_timestamp) <= \
            (other.record_id, other.tool_name, other.execution_count,
             other.name, other.method, other.value, other.record_timestamp)

    def __ge__(self, other: Any) -> bool:
        if not isinstance(other, ToolMetricResult):
            raise NotImplemented

        return (self.record_id, self.tool_name, self.execution_count, self.name, self.method, self.value, self.record_timestamp) >= \
            (other.record_id, other.tool_name, other.execution_count,
             other.name, other.method, other.value, other.record_timestamp)


class AggregateMetricResult(BaseMetricResult):
    min: float | None = None
    max: float | None = None
    mean: float | None = None
    total_records: int
    record_level_metrics: list[RecordMetricResult] = []


class MetricsEvaluationResult(BaseModel):
    metrics_result: list[AggregateMetricResult]

    def to_json(self, indent: int | None = None, **kwargs):
        """
        Transform the metrics evaluation result to a json.
        The kwargs are passed to the model_dump_json method of pydantic model. All the arguments supported by pydantic model_dump_json can be passed.

        Args:
            indent (int, optional): The indentation level for the json. Defaults to None.

        Returns:
            string of the result json.
        """
        if kwargs.get("exclude_unset") is None:
            kwargs["exclude_unset"] = True
        return self.model_dump_json(
            exclude={
                "metrics_result": {
                    "__all__": {
                        "record_level_metrics": {
                            "__all__": {"provider", "name", "method", "group"}
                        }
                    }
                }
            },
            indent=indent,
            **kwargs,
        )

    def to_df(self, data: pd.DataFrame | None = None, include_additional_info: bool = False) -> pd.DataFrame:
        """
        Transform the metrics evaluation result to a dataframe.

        Args:
            data (pd.DataFrame): the input dataframe, when passed will be concatenated to the metrics result
            include_additional_info (bool): wether to include additional info in the metrics result
        Returns:
            pd.DataFrame: new dataframe of the input and the evaluated metrics
        """
        values_dict: dict[str, list[float | str | bool]] = {}
        for result in self.metrics_result:
            metric_key = f"{result.name}.{result.method}" if result.method else result.name

            values_dict[metric_key] = [
                record_metric.value for record_metric in result.record_level_metrics]

            if include_additional_info and len(result.record_level_metrics) > 0:
                additional_info = result.record_level_metrics[0].additional_info
                if additional_info:
                    for k in additional_info.keys():
                        values_dict[f"{metric_key}.{k}"] = [
                            record_metric.additional_info[k] for record_metric in result.record_level_metrics
                        ]

        if data is None:
            return pd.DataFrame.from_dict(values_dict)
        else:
            return pd.concat([data, pd.DataFrame.from_dict(values_dict)], axis=1)

    def to_dict(self) -> list[dict]:
        """
        Transform the metrics evaluation result to a list of dict containing the record level metrics.
        """
        result = []
        for aggregate_metric_result in self.metrics_result:
            for record_level_metric_result in aggregate_metric_result.record_level_metrics:
                result.append(record_level_metric_result.model_dump())
        return result




class AgentMetricResult(BaseMetricResult):
    """
    This is the data model for metric results in the agentic app.
    It stores evaluation results for conversations, interactions and nodes.
    """
    id: Annotated[str, Field(
        description="The unique identifier for the metric result record. UUID.",
        default_factory=lambda: str(uuid.uuid4()))]

    ts: Annotated[datetime, Field(
        description="The timestamp when the metric was recorded.",
        default_factory=datetime.now)]

    applies_to: Annotated[AGENTIC_RESULT_COMPONENTS, Field(
        description="The type of component the metric result applies to.",
    )]

    interaction_id: Annotated[str | None, Field(
        description="The ID of the interaction being evaluated.")]

    interaction_ts: Annotated[datetime | None, Field(
        description="The timestamp of the interaction being evaluated.", default=None)]

    conversation_id: Annotated[str | None, Field(
        description="The ID of the conversation containing the interaction.", default=None)]

    node_name: Annotated[str | None, Field(
        description="The name of the node being evaluated.", default=None)]

    execution_count: Annotated[int | None, Field(
        title="Execution count", description="The execution count of the node in an interaction.", default=None)]

    execution_order: Annotated[int | None, Field(
        title="Execution order", description="The execution order number in the sequence of nodes executed in an interaction.", default=None)]


class AggregateAgentMetricResult(BaseMetricResult):
    min: Annotated[float | None, Field(
        description="The minimum value of the metric.", default=None)]
    max: Annotated[float | None, Field(
        description="The maximum value of the metric.", default=None)]
    mean: Annotated[float | None, Field(
        description="The mean value of the metric.", default=None)]
    value: Annotated[float | None, Field(
        description="The value of the metric. Defaults to mean.", default=None)]
    count: Annotated[int | None, Field(
        description="The count for metric results used for aggregation.", default=None)]
    node_name: Annotated[str | None, Field(
        description="The name of the node being evaluated.", default=None)]
    applies_to: Annotated[AGENTIC_RESULT_COMPONENTS, Field(
        description="The type of component the metric result applies to.",
    )]
    individual_results: Annotated[list[AgentMetricResult], Field(
        description="The list individual metric results.", default=[]
    )]


class AgenticEvaluationResult(BaseModel):
    metrics_results: Annotated[List[AgentMetricResult], Field(
        title="Metrics result", description="The list of metrics result.")]
    aggregated_metrics_results: Annotated[List[AggregateAgentMetricResult], Field(
        title="Aggregated metrics result", description="The list of aggregated metrics result. The metrics are aggregated for each node in the agent.")]

    def get_aggregated_metrics_results(self,
                                       applies_to: list[AGENTIC_RESULT_COMPONENTS] = [
                                           "conversation", "interaction", "node"],
                                       node_name: Optional[str] = None,
                                       include_individual_results: bool = True,
                                       format: Literal["json",
                                                       "object"] = "json",
                                       **kwargs) -> list[AggregateAgentMetricResult] | list[dict]:
        """
        Get the aggregated agentic metrics results based on the specified arguments.

        Args:
            applies_to (AGENTIC_RESULT_COMPONENTS, optional): The type of component the metric result applies to. Defaults to ["conversation", "interaction", "node"].
            node_name (str, optional): The name of the node to get the aggregated results for. Defaults to None.
            include_individual_results (bool, optional): Whether to return the individual metrics results. Defaults to False.
            format (Literal["json", "object"], optional): The format of the output. Defaults to "json".
        Return:
            returns: list[AggregateAgentMetricResult] | list [dict]
        """

        aggregated_results = []
        for amr in self.aggregated_metrics_results:
            if amr.applies_to in applies_to and (not node_name or amr.node_name == node_name):
                if format == "json":
                    if kwargs.get("exclude_unset") is None:
                        kwargs["exclude_unset"] = True
                    if kwargs.get("exclude_none") is None:
                        kwargs["exclude_none"] = True
                    if include_individual_results:
                        aggregated_results.append(
                            amr.model_dump(mode="json", **kwargs))
                    else:
                        aggregated_results.append(
                            amr.model_dump(mode="json", exclude=["individual_results"], **kwargs))
                else:
                    aggregated_results.append(copy.deepcopy(amr))

        return aggregated_results

    def get_metrics_results(self,
                            applies_to: list[AGENTIC_RESULT_COMPONENTS] = [
                                "conversation", "interaction", "node"],
                            node_name: Optional[str] = None,
                            format: Literal["json", "object"] = "json",
                            **kwargs) -> list[AgentMetricResult] | list[dict]:
        """
        Get the agentic metrics results based on the specified arguments.

        Args:
            applies_to (AGENTIC_RESULT_COMPONENTS, optional): The type of component the metrics results applies to. Defaults to ["conversation", "interaction", "node"].
            node_name (str, optional): The name of the node to get the metrics results for. Defaults to None.
            format (Literal["json", "object"], optional): The format of the output. Defaults to "json".
        Return:
            returns: list[AgentMetricResult] | list [dict]
        """

        metrics_results = []
        for amr in self.metrics_results:
            if amr.applies_to in applies_to and (not node_name or amr.node_name == node_name):
                if format == "json":
                    if kwargs.get("exclude_unset") is None:
                        kwargs["exclude_unset"] = True
                    if kwargs.get("exclude_none") is None:
                        kwargs["exclude_none"] = True
                    metrics_results.append(
                        amr.model_dump(mode="json", **kwargs))
                else:
                    metrics_results.append(copy.deepcopy(amr))

        return metrics_results

    def to_json(self, **kwargs) -> dict:
        """
        Get the AgenticEvaluationResult as json

        Returns:
            dict: The AgenticEvaluationResult
        """

        if kwargs.get("exclude_unset") is None:
            kwargs["exclude_unset"] = True

        if kwargs.get("exclude_none") is None:
            kwargs["exclude_none"] = True

        return self.model_dump(mode="json", **kwargs)

    def to_df(self, input_data: Optional[pd.DataFrame] = None,
              interaction_id_field: str = "interaction_id",  wide_format: bool = True) -> pd.DataFrame:
        """
        Get individual metrics dataframe.

        If the input dataframe is provided, it will be merged with the metrics dataframe.

        Args:
            input_data (Optional[pd.DataFrame], optional): Input data to merge with metrics dataframe.. Defaults to None.
            interaction_id_field (str, optional): Field to use for merging input data and metrics dataframe.. Defaults to "interaction_id".
            wide_format (bool): Determines whether to display the results in a pivot table format. Defaults to True

        Returns:
            pd.DataFrame: Metrics dataframe.
        """

        def converter(m): return m.model_dump(
            exclude={"provider"}, exclude_none=True)

        metrics_df = pd.DataFrame(list(map(converter, self.metrics_results)))
        if input_data is not None:
            metrics_df = input_data.merge(metrics_df, on=interaction_id_field)

        # Return the metric result dataframe
        # if the wide_format is False
        if not wide_format:
            return metrics_df

        # Prepare the dataframe for pivot table view
        def col_name(row):
            if row["applies_to"] == "node":
                return f"{row['node_name']}.{row['name']}"
            if row["applies_to"] == "interaction":
                return f"interaction.{row['name']}"
            # TODO support other types

        metrics_df["idx"] = metrics_df.apply(col_name, axis=1)

        # Pivot the table
        metrics_df_wide = metrics_df.pivot_table(
            index="interaction_id",
            columns="idx",
            values="value"
        ).reset_index().rename_axis("", axis=1)

        # if input_data is provided add
        # it to the pivot table
        if input_data is not None:
            metrics_df_wide = input_data.merge(
                metrics_df_wide, on=interaction_id_field)
        return metrics_df_wide
