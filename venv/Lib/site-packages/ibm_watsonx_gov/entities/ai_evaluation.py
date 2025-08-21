# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Dict, List
from pydantic import BaseModel, Field

from ibm_watsonx_gov.entities.ai_experiment import Node


class EvaluationAsset(BaseModel):
    id: Annotated[
        str,
        Field(
            description="The id of the AI Experiment asset",
            examples=["asset-001"],
            default="",
        ),
    ]
    container_id: Annotated[
        str,
        Field(
            description="The project id or space id.", examples=["proj-01"], default=""
        ),
    ]
    container_type: Annotated[
        str,
        Field(
            description="The container type of AI Experiment",
            examples=["project", "spcae"],
            default="",
        ),
    ]
    name: Annotated[
        str,
        Field(
            description="The name of the AI Experiment.",
            examples=["AI_experiment_1"],
            default="",
        ),
    ]
    run_id: Annotated[
        str,
        Field(
            description="The experiment run id of the AI Experiment.",
            examples=["run-01"],
            default="",
        ),
    ]
    run_name: Annotated[
        str,
        Field(
            description="The experiment run name of the AI Experiment.",
            examples=["Test run 1"],
            default="",
        ),
    ]
    attachment_id: Annotated[
        str,
        Field(
            description="the attachment id for the evaluation result for that experiment run.",
            examples=["att-01"],
            default="",
        ),
    ]
    test_data: Annotated[
        Dict,
        Field(
            description="The test data of that experiment run.", examples=[], default={}
        ),
    ]
    nodes: Annotated[
        List[Node],
        Field(
            description="List of the node for that experiment run.",
            examples=[{"id": "node-001", "name": "Node_1", "type": "tool"}],
            default="",
        ),
    ]


class EvaluationConfig(BaseModel):
    monitors: Annotated[
        Dict,
        Field(
            description="The monitors configuration of for that AI Evaluation.",
            examples=[
                {"agentic_ai_quality": {"parameters": {"metrics_configuration": {}}}}
            ],
            default={},
        ),
    ]
    evaluation_assets: Annotated[
        List[EvaluationAsset],
        Field(
            description="The evaluation asset details.",
            examples=[
                [
                    {
                        "id": "d4d6ac43-0bec-47f9-8924-0b74ea1b8ec3",
                        "container_id": "b76d2ebb-4e05-496e-b377-557d409e8c45",
                        "container_type": "project",
                        "name": "AI_Experiment asset",
                        "run_id": "fa7629e9-e1bb-4779-9198-9a6343dab1ad",
                        "run_name": "Experiment run 1",
                        "attachment_id": "ab914f9b-9475-4c10-88d8-480b6c9f4963",
                        "test_data": {"total_rows": 0},
                        "nodes": [],
                    }
                ]
            ],
            default=[],
        ),
    ]


class AIEvaluationAsset(BaseModel):
    """
    The class for AIEvaluationAsset.

    Examples
    --------
    Create AIEvaluationAsset instance:
        .. code-block:: python

            # Define evaluation configuration
            evaluation_config = EvaluationConfig(
                monitors={
                    "agentic_ai_quality": {
                        "parameters": {
                            "metrics_configuration": {}
                        }
                    }
                }
            )

            # Create the evaluation asset
            ai_evaluation_asset = AIEvaluationAsset(
                name="AI Evaluation for agent",
                evaluation_configuration=evaluation_config
            )

            # Compare two or more AI experiments using the evaluation asset
            response = ai_experiment_client.compare_ai_experiments(
                ai_experiment_ids=["experiment_id_1", "experiment_id_2"],
                ai_evaluation_asset=ai_evaluation_asset
            )
    """

    container_id: Annotated[
        str,
        Field(
            description="The project or space id for the AI Evaluation.",
            examples=["proj--1"],
            default="",
        ),
    ]
    container_type: Annotated[
        str,
        Field(
            description="The container type for the AI Evaluation.",
            examples=["project", "space"],
            default="",
        ),
    ]
    container_name: Annotated[
        str,
        Field(
            description="The name of the project or the space.",
            examples=["Project_1"],
            default="",
        ),
    ]
    name: Annotated[
        str,
        Field(
            description="The name of the AI Evaluation asset.",
            examples=["AI agents evaluation"],
            default="",
        ),
    ]
    description: Annotated[
        str,
        Field(
            description="The description of the AI Evaluation asset.",
            examples=["AI agents evaluation"],
            default="",
        ),
    ]
    asset_type: Annotated[
        str,
        Field(
            description="The asset type of the AI Evaluation.",
            examples=["ai_evaluation"],
            default="ai_evaluation",
        ),
    ]
    created_at: Annotated[
        str,
        Field(
            description="The timestamp of creation of AI Evaluation asset.",
            examples=["2025-04-01T12:00:00Z"],
            default="",
        ),
    ]
    owner_id: Annotated[
        str,
        Field(
            description="The owner of the AI Evaluation.",
            examples=["user-123"],
            default="",
        ),
    ]
    asset_id: Annotated[
        str,
        Field(
            description="The asset id of the AI Evaluation.",
            examples=["43676d70-1ecc-412e-832f-8762aa899247"],
            default="",
        ),
    ]
    creator_id: Annotated[
        str,
        Field(
            description="The creator id of the AI Evaluation.",
            examples=["user-123"],
            default="",
        ),
    ]
    asset_details: Annotated[
        Dict,
        Field(
            description="The asset details of the AI Evluation asset.",
            examples=[
                {
                    "task_ids": [],
                    "label_column": "",
                    "operational_space_id": "development",
                    "input_data_type": "unstructured_text",
                    "job_id": "",
                    "service_instance_id": "",
                    "evaluation_asset_type": "ai_experiment|prompt",
                }
            ],
            default={},
        ),
    ]
    evaluation_configuration: Annotated[
        EvaluationConfig,
        Field(
            description="The list of the evaluation configuration",
            examples=[
                {
                    "monitors": {
                        "agentic_ai_quality": {
                            "parameters": {"metrics_configuration": {}}
                        }
                    },
                    "evaluation_assets": [
                        {
                            "id": "d4d6ac43-0bec-47f9-8924-0b74ea1b8ec3",
                            "container_id": "b76d2ebb-4e05-496e-b377-557d409e8c45",
                            "container_type": "project",
                            "name": "AI_Experiment asset for Agent governence",
                            "run_id": "fa7629e9-e1bb-4779-9198-9a6343dab1ad",
                            "run_name": "Experiment run 1",
                            "attachment_id": "ab914f9b-9475-4c10-88d8-480b6c9f4963",
                            "test_data": {"total_rows": 0},
                            "nodes": [],
                        }
                    ],
                }
            ],
            default=[],
        ),
    ]
    href: Annotated[
        str, Field(description="The link of the AI Evaluation Asset", default="")
    ]

    def to_json(self):
        """
        Transform the AIEvaluationAsset instance to json
        """
        return self.model_dump(mode="json")
