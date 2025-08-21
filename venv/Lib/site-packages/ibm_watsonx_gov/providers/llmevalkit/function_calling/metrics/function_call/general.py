from typing import Any, Dict, List, Union
from llmevalkit.function_calling.metrics.base import FunctionMetricsPrompt

_general_system: str = (
    "You are a semantic evaluator for conversational-agent tool calls.\n"
    "Given the dialogue context and a proposed tool call, judge how well this call "
    "using the following metric:\n"
    "{{ task_description }}\n\n"
    "Here is the JSONSchema for your response:\n"
    "{{ metric_jsonschema }}"
)

_general_user: str = (
    "Conversation context:\n"
    "{{ conversation_context }}\n\n"
    "Tools Inventory:\n"
    "{{ tools_inventory }}\n\n"
    "Proposed tool call:\n"
    "{{ tool_call }}\n\n"
    "Return a JSON object matching the schema above."
)


class GeneralMetricsPrompt(FunctionMetricsPrompt):
    """Prompt builder for general tool-call semantic metrics."""

    system_template = _general_system
    user_template = _general_user


def get_general_metrics_prompt(
    prompt: GeneralMetricsPrompt,
    conversation_context: Union[str, List[Dict[str, str]]],
    tools_inventory: List[Dict[str, Any]],
    tool_call: Dict[str, Any],
) -> List[Dict[str, str]]:
    """
    Build the messages for a general semantic evaluation.

    Returns the list of chat messages (system -> [few-shot] -> user).
    """
    return prompt.build_messages(
        user_kwargs={
            "conversation_context": conversation_context,
            "tools_inventory": tools_inventory,
            "tool_call": tool_call,
        }
    )
