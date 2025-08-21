# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from collections import defaultdict
from typing import List

import pandas as pd

from ibm_watsonx_gov.entities.ai_experiment import Node


AI_SERVICE_QUALITY = "ai_service_quality"

class AIExperimentUtils:
    """ Class for AI experiment related utility methods """

    @classmethod
    def construct_result_attachment_payload(cls, metric_results: list, nodes: List[Node] = None):
        """
        Constructs payload for result attachment from experiment run's result
        Args:
            - metric_results: The list of metrics for each node
        
        Returns: The payload for result attachment and total number of records processed
        """
        attachment_payload = {}
        node_name_to_id_map = {}
        if nodes is not None:
            node_name_to_id_map = {node.name: node.id for node in nodes}
        
        if not metric_results:
            raise ValueError("Evaluation result is empty or missing.")

        agent_level_metrics = []
        node_level_metrics = defaultdict(list)

        total_records = 0

        # Separating agent level and node level metrics using the applies_to field in the result.
        for metric_result in metric_results:
            result_applies_to = metric_result.get("applies_to", "")
            metric_id = metric_result.get("name", "")
            metric_result["id"] = metric_id
            metric_result["name"] = metric_id.capitalize().replace("_", " ")
            # If thresholds exist, add them to the run result
            thresholds = metric_result.pop("thresholds", [])
            if thresholds:
                for threshold in thresholds:
                    metric_result[threshold.get("type")] = threshold.get("value")

            if result_applies_to == "node":
                node_name = metric_result.pop("node_name", "")
                if node_name and result_applies_to == "node":
                    node_level_metrics[node_name].append(metric_result)

            # agentic_result_components ["conversation", "interaction"]
            else:
                if total_records == 0:
                    total_records = metric_result.get("count")
                metric_id = f"{result_applies_to}_{metric_id}"
                metric_result["id"] = metric_id
                metric_result["name"] = metric_id.capitalize().replace(
                    "_", " ")
                agent_level_metrics.append(metric_result)

        # Constructing the agent level metrics result
        agent_evaluation_result = {
            "evaluation_result": {
                AI_SERVICE_QUALITY: {
                    "metric_groups":  cls.get_result_with_metric_groups(
                        agent_level_metrics)
                }
            }
        }
        
        node_level_results = []
        for node_name, metrics in node_level_metrics.items():
            node_evaluation_result = {}
            # Get result organized wih metric groups
            metric_groups_result = cls.get_result_with_metric_groups(metrics)
            
            node_evaluation_result = {
                AI_SERVICE_QUALITY: {
                    "metric_groups":  metric_groups_result
                }
            }
            node_level_results.append({
                "type": "tool",
                "id": node_name_to_id_map.get(node_name, node_name),
                "name": node_name,
                "evaluation_result": node_evaluation_result
            })

        attachment_payload = {
            "ai_application": agent_evaluation_result,
            "nodes": node_level_results
        }

        return attachment_payload, total_records

    @classmethod
    def get_result_with_metric_groups(cls, metrics: list) -> list:
        """
        Organises the result based on metric groups
        Args:
            - metrics: The list of metrics
        
        Returns: The list containing metric groups and corresponding metrics for each group
        """
        metric_groups_map = defaultdict(list)
        for metric in metrics:
            metric_group = metric.pop("group", "Other metrics").capitalize().replace("_", " ")
            metric_groups_map[metric_group].append(metric)
        
        metric_groups_result = [
            {"name": group_name, "metrics": group_metrics} for group_name, group_metrics in metric_groups_map.items()]
        
        return metric_groups_result
