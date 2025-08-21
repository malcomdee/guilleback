from typing import Any, Dict, List, Optional, Union
from llmevalkit.function_calling.metrics.base import FunctionMetricsPrompt

_parameter_system: str = (
    "You are a semantic evaluator of parameter values in conversational-agent tool calls.\n"
    "Given the dialogue context, tool inventory, a proposed tool call, and a single "
    "parameter name and value, assess how well this parameter value satisfies the metric:\n"
    "{{ task_description }}\n\n"
    "Here is the JSONSchema for your response:\n"
    "{{ metric_jsonschema }}"
)

_parameter_user: str = (
    "Conversation context:\n"
    "{{ conversation_context }}\n\n"
    "Tools Inventory:\n"
    "{{ tool_inventory }}\n\n"
    "Proposed tool call:\n"
    "{{ tool_call }}\n\n"
    "Parameter name:\n"
    "{{ parameter_name }}\n\n"
    "Parameter value:\n"
    "{{ parameter_value }}\n\n"
    "Return a JSON object matching the schema above."
)


class ParameterMetricsPrompt(FunctionMetricsPrompt):
    """Prompt builder for parameter-level metrics."""

    system_template = _parameter_system
    user_template = _parameter_user


def get_parameter_metrics_prompt(
    prompt: ParameterMetricsPrompt,
    conversation_context: Union[str, List[Dict[str, str]]],
    tool_inventory: List[Dict[str, Any]],
    tool_call: Dict[str, Any],
    parameter_name: str,
    parameter_value: Any,
) -> List[Dict[str, str]]:
    """
    Build the messages for a parameter-level evaluation.
    """
    return prompt.build_messages(
        user_kwargs={
            "conversation_context": conversation_context,
            "tool_inventory": tool_inventory,
            "tool_call": tool_call,
            "parameter_name": parameter_name,
            "parameter_value": parameter_value,
        }
    )
