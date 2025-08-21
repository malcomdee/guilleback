# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2025
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------


from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Annotated

from ibm_watsonx_gov.entities.metric import MetricThreshold


class MonitorThreshold(MetricThreshold):
    metric_id: Annotated[str, Field(
        description="Metric id", examples=["faithfulness"])]


class BaseMonitor(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True)
    monitor_name: Annotated[str, Field(description="Monitor name", examples=[
                                       "generative_ai_quality", "drift_v2"])]
    thresholds: Annotated[list[MonitorThreshold] | None, Field(
        default=None, description="List of metric thresholds")]
    parameters: Annotated[dict[str, Any] | None, Field(
        default=None, description="Monitor parameters")]


class GenerativeAIQualityMonitor(BaseMonitor):
    monitor_name: str = "generative_ai_quality"
    parameters: dict[str, Any] = {
        "metrics_configuration": {
            "rouge_score": {},
            "exact_match": {},
            "bleu": {},
            "unsuccessful_requests": {},
            "hap_input_score": {},
            "hap_score": {},
            "pii": {},
            "pii_input": {},
        },
    }


class DriftV2Monitor(BaseMonitor):
    monitor_name: str = "drift_v2"


class QualityMonitor(BaseMonitor):
    monitor_name: str = "quality"
    parameters: dict[str, Any] = {
        "min_feedback_data_size": 10,
    }


class FairnessMonitor(BaseMonitor):
    monitor_name: str = "fairness"


class DriftMonitor(BaseMonitor):
    monitor_name: str = "drift"


class ModelHealthMonitor(BaseMonitor):
    monitor_name: str = "model_health"
