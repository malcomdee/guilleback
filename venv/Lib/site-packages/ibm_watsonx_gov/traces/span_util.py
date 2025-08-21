# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Any

from ibm_watsonx_gov.traces.span_node import SpanNode

try:
    from google.protobuf.json_format import ParseDict
    from opentelemetry.proto.collector.trace.v1.trace_service_pb2 import \
        ExportTraceServiceRequest
except:
    pass


def get_attributes(attributes, keys: list[str] = []) -> dict[str, Any]:
    """
    Get the attribute value for the given keys from a list of attributes.
    """
    attrs = {}
    for attr in attributes:
        key = attr.key
        value = attr.value
        val = None
        if value.HasField("string_value"):
            val = value.string_value
        elif value.HasField("bool_value"):
            val = value.bool_value
        elif value.HasField("int_value"):
            val = value.int_value
        elif value.HasField("double_value"):
            val = value.double_value
        if keys:
            if key in keys:
                attrs[key] = val
        else:
            attrs[key] = val

    return attrs


def get_span_nodes_from_json(span_json: str) -> dict[str, SpanNode]:
    """
    Convert a JSON string containing a list of spans into a dictionary of SpanNode objects, keyed by span_id.
    """
    span_nodes: dict[str, SpanNode] = {}
    span_msg = ParseDict(span_json, ExportTraceServiceRequest())
    for resource_span in span_msg.resource_spans:
        attrs = get_attributes(
            resource_span.resource.attributes, ["service.name", "wxgov.config.agentic_app"])
        service_name = attrs.get("service.name")
        agentic_app = attrs.get("wxgov.config.agentic_app")
        for scope_span in resource_span.scope_spans:
            for span in scope_span.spans:
                node = SpanNode(service_name=service_name,
                                agentic_app=agentic_app,
                                span=span)
                span_nodes[span.span_id] = node
    return span_nodes
