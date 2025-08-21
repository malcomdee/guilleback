# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Literal

from pydantic import BaseModel, Field


class MetricThreshold(BaseModel):
    """
    The class that defines the threshold for a metric.
    """
    type: Annotated[Literal["lower_limit", "upper_limit"], Field(
        description="Threshold type. One of 'lower_limit', 'upper_limit'")]
    value: Annotated[float, Field(
        title="Threshold value", description="The value of metric threshold", default=0)]
