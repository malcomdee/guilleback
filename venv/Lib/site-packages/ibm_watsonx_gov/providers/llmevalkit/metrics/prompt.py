import json
from typing import Any, Dict, List, Tuple, Type, Optional
from jinja2 import Template

import jsonschema
from jinja2 import Environment, BaseLoader
from pydantic import BaseModel, create_model, ValidationError

from llmevalkit.metrics.metric import Metric
from llmevalkit.metrics.field import (
    ExplanationField,
    EvidenceField,
    CorrectionField,
    NumericField,
)

# Jinja2 environment for string templates
_jinja_env = Environment(loader=BaseLoader(), autoescape=False)


class MetricPrompt:
    """
    Combines a Metric with system and user prompt templates, plus optional few-shot examples.

    Attributes:
        metric: Metric instance describing the schema to validate outputs.
        system_template: Jinja2 Template for the system message.
        user_template: Jinja2 Template for the user message.
        examples: List of (user_kwargs, output_dict) pairs.
    """

    def __init__(
        self,
        metric: Metric,
        system_template: str,
        user_template: str,
        *,
        system_kwargs_defaults: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Args:
            metric: Metric whose JSONSchema will be used for validation.
            system_template: Template string for the system message; may reference keys.
            user_template: Template string for the user message; may reference user_kwargs keys.
            system_kwargs_defaults: Optional default context for system template.
        """
        self.metric = metric
        self._system_tmpl: Template = _jinja_env.from_string(system_template)
        self._user_tmpl: Template = _jinja_env.from_string(user_template)
        self.system_kwargs_defaults: Dict[str, Any] = system_kwargs_defaults or {}
        self.examples: List[Tuple[Dict[str, Any], Dict[str, Any]]] = []

    # --- Getters and Setters ---

    def get_system_template(self) -> str:
        return self._system_tmpl.source

    def set_system_template(self, template_str: str) -> None:
        self._system_tmpl = _jinja_env.from_string(template_str)

    def get_user_template(self) -> str:
        return self._user_tmpl.source

    def set_user_template(self, template_str: str) -> None:
        """
        Setting a new user template clears existing examples.
        """
        self._user_tmpl = _jinja_env.from_string(template_str)
        self.examples.clear()

    def get_system_kwargs_defaults(self) -> Dict[str, Any]:
        return dict(self.system_kwargs_defaults)

    def set_system_kwargs_defaults(self, defaults: Dict[str, Any]) -> None:
        self.system_kwargs_defaults = defaults

    # --- Example Management ---

    def add_example(self, user_kwargs: Dict[str, Any], output: Dict[str, Any]) -> None:
        """
        Add a few-shot example.

        Validates that `output` adheres to this.metric's JSONSchema.

        Args:
            user_kwargs: Variables for rendering the user_template.
            output: Dict matching the metric's schema.

        Raises:
            ValidationError if output invalid.
        """
        schema = self.metric.to_jsonschema()
        # 1) JSONSchema structural validation
        jsonschema.validate(instance=output, schema=schema)
        # 2) Pydantic type/enum validation
        Model: Type[BaseModel] = self._build_response_model()
        try:
            Model.model_validate(output)
        except ValidationError as e:
            raise ValueError(f"Example output failed validation: {e}")
        self.examples.append((user_kwargs, output))

    # --- Prompt Building ---

    def build_messages(
        self,
        user_kwargs: Dict[str, Any],
        system_kwargs: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, str]]:
        """
        Build the full chat messages sequence:

        1. System message rendered with:
             - metric_jsonschema
             - plus any system_kwargs (overrides defaults)
        2. For each example:
             - User message from user_template with example user_kwargs
             - Assistant message: JSON dump of example output
        3. Final user message with provided user_kwargs

        Args:
            user_kwargs: Variables for the final user prompt.
            system_kwargs: Optional overrides for system template context.

        Returns:
            List of {"role": "...", "content": "..."} dicts.
        """
        msgs: List[Dict[str, str]] = []
        # Prepare system context
        ctx: Dict[str, Any] = {
            "metric_jsonschema": json.dumps(self.metric.to_jsonschema(), indent=2)
        }
        # merge defaults and overrides
        ctx.update(self.system_kwargs_defaults)
        if system_kwargs:
            ctx.update(system_kwargs)

        # 1) System message
        sys_text = self._system_tmpl.render(**ctx)
        msgs.append({"role": "system", "content": sys_text})

        # 2) Few-shot examples
        for ex_user_kwargs, ex_output in self.examples:
            user_text = self._user_tmpl.render(**ex_user_kwargs)
            msgs.append({"role": "user", "content": user_text})
            assistant_text = json.dumps(ex_output, indent=None)
            msgs.append({"role": "assistant", "content": assistant_text})

        # 3) Final user message
        final_user = self._user_tmpl.render(**user_kwargs)
        msgs.append({"role": "user", "content": final_user})

        return msgs

    def _build_response_model(self) -> Type[BaseModel]:
        """
        Dynamically construct a Pydantic model matching metric.to_jsonschema().
        Used to enforce types beyond JSONSchema.
        """
        schema = self.metric.to_jsonschema()
        props = schema.get("properties", {})
        fields: Dict[str, Tuple[Any, Any]] = {}
        for name, subs in props.items():
            jtype = subs.get("type")
            # map JSONSchema types -> Python types
            if jtype == "integer":
                py = (int, ...)
            elif jtype == "number":
                py = (float, ...)
            elif jtype == "string":
                py = (str, ...)
            elif jtype == "boolean":
                py = (bool, ...)
            elif jtype == "object":
                py = (dict, ...)
            else:
                py = (Any, ...)
            # handle enums
            if "enum" in subs:
                from typing import Literal

                enum_vals = subs["enum"]
                py = (Literal[tuple(enum_vals)], ...)
            fields[name] = py

        Model = create_model(schema.get("title", "ResponseModel"), **fields)
        return Model


# --- Example Subclass: RelevancePrompt ---


class RelevanceMetric(Metric):
    """
    Metric for assessing relevance of a response to its context.
    """

    def __init__(self) -> None:
        desc = "Rate how relevant the response is to the given context on a 0-1 scale."
        super().__init__(
            name="Relevance",
            description=desc,
            fields=[
                ExplanationField(
                    name="explanation",
                    json_type="string",
                    description="Why the response is or is not relevant, step by step.",
                ),
                EvidenceField(
                    name="evidence",
                    json_type="string",
                    description="Portion of context or response that supports your relevance rating.",
                ),
                NumericField(
                    name="output",
                    json_type="number",
                    description="Relevance score from 0.0 (not relevant) to 1.0 (fully relevant).",
                    jsonschema_extra={"minimum": 0.0, "maximum": 1.0},
                    extra_params={"threshold_low": 0.0, "threshold_high": 1.0},
                ),
                NumericField(
                    name="confidence",
                    json_type="number",
                    description="Confidence in your relevance judgment (0.0-1.0).",
                    jsonschema_extra={"minimum": 0.0, "maximum": 1.0},
                    extra_params={"threshold_low": 0.0, "threshold_high": 1.0},
                ),
                CorrectionField(
                    name="correction",
                    json_type="object",
                    description="If relevance is low, suggest how to improve relevance.",
                ),
            ],
        )


class RelevancePrompt(MetricPrompt):
    """
    Prompt builder specialized for the RelevanceMetric.
    Provides default templates and example usage.
    """

    def __init__(self) -> None:
        metric = RelevanceMetric()
        system_tmpl = (
            "You are an expert judge that assesses response relevance. "
            "Here is the JSONSchema for your response:\n"
            "{{ metric_jsonschema }}"
        )
        user_tmpl = (
            "Context: {{ context }}\n"
            "Response: {{ response }}\n"
            "Provide your evaluation as JSON matching the schema above."
        )
        super().__init__(metric, system_tmpl, user_tmpl)

        # Initialize default few-shot examples
        self.add_example(
            {
                "context": "The sky is blue.",
                "response": "The sky appears azure due to Rayleigh scattering.",
            },
            {
                "explanation": "The response directly addresses sky color by naming scattering physics.",
                "evidence": "The sky appears azure due to Rayleigh scattering.",
                "output": 1.0,
                "confidence": 0.9,
                "correction": {},
            },
        )
        self.add_example(
            {
                "context": "What is the capital of France?",
                "response": "The moon orbits Earth every 27 days.",
            },
            {
                "explanation": "The response is about lunar orbit, unrelated to capitals.",
                "evidence": "The moon orbits Earth every 27 days.",
                "output": 0.0,
                "confidence": 0.8,
                "correction": {"suggestion": "The capital of France is Paris."},
            },
        )
