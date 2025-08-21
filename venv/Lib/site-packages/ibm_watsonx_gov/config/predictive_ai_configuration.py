# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from ibm_watsonx_gov.entities.base_classes import BaseConfiguration
from ibm_watsonx_gov.entities.enums import InputDataType, ProblemType


class PredictiveAIConfiguration(BaseConfiguration):
    problem_type: ProblemType
    input_data_type: InputDataType
    feature_fields: list[str]
    categorical_fields: list[str] = []
    text_fields: list[str] = []
