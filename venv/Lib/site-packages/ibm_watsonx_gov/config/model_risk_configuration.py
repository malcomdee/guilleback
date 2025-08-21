# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Optional, Tuple, List

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator

from ibm_watsonx_gov.entities.credentials import WxGovConsoleCredentials
from ibm_watsonx_gov.entities.foundation_model import FoundationModel


class WxGovConsoleConfiguration(BaseModel):
    """
    Defines the WxGovConsoleConfiguration class.

    This configuration is used to integrate with the watsonx Governance Console for storing model risk evaluation results.
    It includes the model identifier and the credentials required for authentication.

    Examples:
        1. Create configuration with explicit credentials:
            .. code-block:: python

                credentials = WxGovConsoleCredentials(
                    url="https://governance-console.example.com",
                    username="admin",
                    password="securepassword",
                    api_key="optional-api-key"
                )
                configuration = WxGovConsoleConfiguration(
                    model_id="model-12345",
                    credentials=credentials
                )
    """
    model_id: Annotated[
        str,
        Field(
            description="The watsonx Governance Console identifier of the model to store the model risk result."
        ),
    ]
    credentials: Annotated[
        WxGovConsoleCredentials,
        Field(
            description="The watsonx Governance Console credentials."
        ),
    ]
    model_config = ConfigDict(protected_namespaces=())


class ModelRiskConfiguration(BaseModel):
    """
    Defines the ModelRiskConfiguration class.

    This configuration class encapsulates all parameters required to perform model risk evaluation,
    including model metadata, evaluation scope, thresholds, and output/reporting preferences.

    Examples:
        1. Create a basic configuration:
            .. code-block:: python

                model_details = WxAIFoundationModel(
                    model_name="mymodel_flan",
                    model_id="google/flan-ul2",
                    project_id="project_id")

                model_config = ModelRiskConfiguration(
                    model_details=model_details,
                    risk_dimensions=["hallucination"],
                    max_sample_size=500,
                    thresholds=(20, 80),
                    pdf_report_output_path="/reports"                    
                )

        2. Include watsonx Governance Console integration:
            .. code-block:: python

                model_details = WxAIFoundationModel(
                    model_name="mymodel_flan",
                    model_id="google/flan-ul2",
                    project_id="project_id")

                wx_gc_credentials = WxGovConsoleCredentials(
                    url="https://governance.example.com",
                    username="admin",
                    password="securepass"
                    api_key="console API key"
                )        
                        
                wx_config = WxGovConsoleConfiguration(
                    model_id="model-abc123",
                    credentials=wx_gc_credentials
                )

                model_config = ModelRiskConfiguration(
                    model_details=model_details,
                    risk_dimensions=["hallucination"],
                    max_sample_size=500,
                    thresholds=(20, 80),
                    wx_gc_configuration=wx_config,
                    pdf_report_output_path="/reports"                    
                )                

    Validators:
        - `thresholds`: Ensures that the threshold values are between 0 and 100, and that the lower value is less than the upper value.
    """
    model_details: Annotated[
        FoundationModel,
        Field(
            title="Foundation Model Details",
            description="The details of the foundation model being evaluated.",
        )
    ]
    risk_dimensions: Annotated[
        Optional[List[str]],
        Field(
            title="Risk Dimensions",
            description="A list of risk categories to be evaluated for the model. These could include hallucination, jailbreaking etc.",
            default=None,
            examples=[["hallucination", "jailbreaking", "harmful-code-generation"]]
        )
    ]
    max_sample_size: Annotated[
        Optional[PositiveInt],
        Field(
            title="Maximum Sample Size",
            description="The maximum number of samples to be used during the evaluation process. Must be a positive integer.",
            default=None,
            examples=[50]
        )
    ]
    wx_gc_configuration: Annotated[
        Optional[WxGovConsoleConfiguration],
        Field(
            title="watsonx Governance Console Configuration",
            description="Optional configuration for storing results in watsonx Governance Console.",
            default=None,
        )
    ]
    pdf_report_output_path: Annotated[
        Optional[str],
        Field(
            title="PDF Report Output Path",
            description="The output file path to store the model risk evaluation PDF report.",
            default=None,
            examples=["/reports/"]
        )
    ]
    thresholds: Annotated[
        Optional[Tuple[int, int]],
        Field(
            title="Performance Thresholds",
            description="A tuple representing the percentile-based threshold configuration used for categorizing LLM performance. The first element is the lower percentile threshold, and the second is the upper percentile threshold",
            default=(25, 75),
            examples=[(25, 75)]
        )
    ]
    model_config = ConfigDict(protected_namespaces=())

    @field_validator("thresholds")
    @classmethod
    def validate_thresholds(cls, v):
        if v is not None:
            low, high = v
            if not (0 <= low < high <= 100):
                raise ValueError(
                    "Thresholds must be between 0 and 100, and the first must be less than the second.")
        return v
