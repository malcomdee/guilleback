from typing import Any, Dict, List, Union
from llmevalkit.function_calling.metrics.base import FunctionMetricsPrompt

_function_system: str = (
    "You are a semantic evaluator of function selection for conversational agents.\n"
    "Given the dialogue context, tool inventory, and chosen function name, assess "
    "how well it was selected by this metric:\n"
    "{{ task_description }}\n\n"
    "Here is the JSONSchema for your response:\n"
    "{{ metric_jsonschema }}"
)

_function_user: str = (
    "Conversation context:\n"
    "{{ conversation_context }}\n\n"
    "Tools Inventory:\n"
    "{{ tools_inventory }}\n\n"
    "Proposed tool call:\n"
    "{{ tool_call }}\n\n"
    "Chosen function name:\n"
    "{{ function_name }}\n\n"
    "Return a JSON object matching the schema above."
)


class FunctionSelectionPrompt(FunctionMetricsPrompt):
    """Prompt builder for function-selection metrics."""

    system_template = _function_system
    user_template = _function_user


def get_function_selection_prompt(
    prompt: FunctionSelectionPrompt,
    conversation_context: Union[str, List[Dict[str, str]]],
    tools_inventory: List[Dict[str, Any]],
    tool_call: Dict[str, Any],
    function_name: str,
) -> List[Dict[str, str]]:
    """
    Build the messages for a function-selection evaluation.
    """
    return prompt.build_messages(
        user_kwargs={
            "conversation_context": conversation_context,
            "tools_inventory": tools_inventory,
            "tool_call": tool_call,
            "function_name": function_name,
        }
    )
