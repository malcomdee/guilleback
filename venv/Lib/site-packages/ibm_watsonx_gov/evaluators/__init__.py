# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

try:
    from .agentic_evaluator import AgenticEvaluator
except Exception:
    # Ignore any exception to support extra requires install when MetricsEvaluator or ModelRiskEvaluator is used.
    AgenticEvaluator = None

try:
    from .metrics_evaluator import MetricsEvaluator
except Exception:
    # Ignore any exception to support extra requires install when ModelRiskEvaluator is used.
    MetricsEvaluator = None

try:
    from .model_risk_evaluator import ModelRiskEvaluator
except Exception:
    # Ignore any exception to support extra requires install when MetricsEvaluator or AgenticEvaluator is used.
    ModelRiskEvaluator = None
