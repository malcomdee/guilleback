# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from ibm_watsonx_gov.entities.agentic_app import AgenticApp


class SpanNode:
    """
    Class to represent the structure of a single span and its children.
    """

    def __init__(self, service_name: str, agentic_app, span):
        self.service_name = service_name
        from opentelemetry.proto.trace.v1.trace_pb2 import Span
        self.span: Span = span
        self.agentic_app = None
        if agentic_app:
            self.agentic_app = AgenticApp.model_validate_json(agentic_app)

        self.children: list['SpanNode'] = []
        self._interaction_id = None
        self._conversation_id = None

    def add_child(self, child: 'SpanNode'):
        self.children.append(child)

    def get_interaction_id(self) -> str:
        if self._interaction_id is None:
            self._interaction_id = self.span.trace_id.hex()
        return self._interaction_id

    def get_conversation_id(self) -> str:
        if self._conversation_id is None:
            thread_id_key = "traceloop.association.properties.thread_id"
            from ibm_watsonx_gov.traces.span_util import get_attributes
            self._conversation_id = get_attributes(self.span.attributes, [
                thread_id_key]).get(thread_id_key) or self.get_interaction_id()
        return self._conversation_id

    def get_nodes_configuration(self) -> dict:
        nodes_config = {}
        if self.agentic_app:
            nodes_config = {
                n.name: n.metrics_configurations for n in self.agentic_app.nodes}
        return nodes_config

    def __repr__(self, level=0):
        indent = "  " * level
        s = f"{indent}- {self.span.name} (span_id={self.span.span_id.hex()}, parent_id={self.span.parent_span_id.hex() if self.span.parent_span_id else 'None'})\n"
        for child in self.children:
            s += child.__repr__(level + 1)
        return s
