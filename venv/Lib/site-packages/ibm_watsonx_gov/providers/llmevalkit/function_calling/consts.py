# Metric name constants
# General metrics
# METRIC_FUNCTION_INTENT_ALIGNMENT = "function_intent_alignment"
METRIC_GENERAL_HALLUCINATION_CHECK = "general_hallucination_check"
# METRIC_PARAMETER_COMPLETENESS_CONSISTENCY = "parameter_completeness_consistency"
# METRIC_PREREQUISITE_SATISFACTION = "prerequisite_satisfaction"
# METRIC_OVERALL_CALL_CORRECTNESS = "overall_call_correctness"
METRIC_AGENTIC_CONSTRAINTS_SATISFACTION = "agentic_constraints_satisfaction"

# Function selection metrics
METRIC_FUNCTION_SELECTION_APPROPRIATENESS = "function_selection_appropriateness"

# Parameter metrics
METRIC_VALUE_FORMAT_ALIGNMENT = "value_format_alignment"
# METRIC_PARAMETER_INFO_SUFFICIENCY = "parameter_info_sufficiency"
METRIC_PARAMETER_HALLUCINATION_CHECK = "parameter_hallucination_check"
# METRIC_OVERALL_PARAMETER_CORRECTNESS = "overall_parameter_correctness"

# Metric category mapping
GENERAL_METRICS = [
    METRIC_GENERAL_HALLUCINATION_CHECK,
    METRIC_AGENTIC_CONSTRAINTS_SATISFACTION,
]

FUNCTION_SELECTION_METRICS = [
    METRIC_FUNCTION_SELECTION_APPROPRIATENESS,
]

PARAMETER_METRICS = [
    METRIC_VALUE_FORMAT_ALIGNMENT,
    METRIC_PARAMETER_HALLUCINATION_CHECK,
]
