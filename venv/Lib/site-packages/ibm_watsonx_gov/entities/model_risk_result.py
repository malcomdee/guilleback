# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import List

import pandas as pd
from pydantic import BaseModel


class RiskMetric(BaseModel):
    name: str
    value: float | str | List[float]


class Benchmark(BaseModel):
    name: str
    metrics: list[RiskMetric]

    def get_metric_df(self) -> pd.DataFrame:
        return pd.DataFrame(self.model_dump()["metrics"])


class Risk(BaseModel):
    name: str
    benchmarks: list[Benchmark]


class ModelRiskResult(BaseModel):
    risks: list[Risk]
    output_file_path: str | None = None

    def to_json(self, **kwargs):
        """
        Transform the model risk result to a json.
        The kwargs are passed to the model_dump_json method of pydantic model. All the arguments supported by pydantic model_dump_json can be passed.
        """
        return self.model_dump_json(**kwargs)
