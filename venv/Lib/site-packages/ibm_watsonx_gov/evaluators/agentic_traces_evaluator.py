# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Optional

from pydantic import Field

from ibm_watsonx_gov.entities.agentic_app import AgenticApp
from ibm_watsonx_gov.entities.evaluation_result import AgentMetricResult
from ibm_watsonx_gov.evaluators.base_evaluator import BaseEvaluator
from ibm_watsonx_gov.traces.span_util import get_attributes
from ibm_watsonx_gov.traces.trace_utils import TraceUtils
from ibm_watsonx_gov.utils.aggregation_util import \
    get_agentic_evaluation_result
from ibm_watsonx_gov.utils.python_utils import add_if_unique


class AgenticTracesEvaluator(BaseEvaluator):
    """
    The class to evaluate agentic applications based on the traces generated.
    """
    agentic_app: Annotated[Optional[AgenticApp], Field(
        title="Agentic application configuration details", description="The agentic application configuration details.", default=None)]

    def compute_metrics(self, spans: list[dict], **kwargs) -> list[dict]:
        """
        Computes the agentic metrics based on the spans/traces provided as a list.

        Args:
            spans (list[dict]): The spans on which the metrics need to be computed

        Returns:
            list[dict]: The computed metric results
        """

        nodes = []
        metrics_result = []
        span_trees = TraceUtils.build_span_trees(spans=spans)
        for span_tree in span_trees:
            # Process only the spans that are associated with the agent application
            attrs = get_attributes(span_tree.span.attributes, [
                "traceloop.span.kind"])
            if not attrs.get("traceloop.span.kind") == "workflow":
                continue

            mr, ns, _ = TraceUtils.compute_metrics_from_trace(
                span_tree=span_tree)
            metrics_result.extend(mr)
            for n in ns:
                add_if_unique(n, nodes, ["name", "func_name"])

        agentic_result = get_agentic_evaluation_result(
            metrics_result=metrics_result, nodes=nodes)
        applies_to = kwargs.get("applies_to", ["interaction", "node"])
        return agentic_result.get_metrics_results(applies_to=applies_to, format="json")
