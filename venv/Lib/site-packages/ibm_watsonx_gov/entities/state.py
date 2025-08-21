# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Optional

from pydantic import BaseModel


class EvaluationState(BaseModel):
    input_text: str
    context: Optional[list[str]] = []
    generated_text: Optional[str] = None
    ground_truth: Optional[str] = None
    record_id: Optional[str] = None
    record_timestamp: Optional[str] = None
    interaction_id: Optional[str] = None
