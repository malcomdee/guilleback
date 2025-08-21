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


class Node(BaseModel):
    id: Annotated[
        str,
        Field(
            description="The ID of node for AI Experiemnt.",
            examples=["node-001"],
            default="",
        ),
    ]
    name: Annotated[
        str,
        Field(
            description="The name of node for AI Experiment.",
            examples=["Node_1"],
            default="",
        ),
    ]
    type: Annotated[
        str,
        Field(
            description="The type of node for AI Experiment.",
            examples=["tool", "agent"],
            default="tool",
        ),
    ]
    foundation_models: Annotated[
        list[dict],
        Field(
            description="The Foundation models invoked by the node",
            examples=[{'model': 'text-embedding-3-small',
                       'provider': 'OpenAI', 'type': 'embedding'}],
            default=[],
        ),
    ]

    def to_json(self):
        """
        Transform the Node instance to json.
        """
        return self.model_dump(mode="json")


class AIExperimentRun(BaseModel):
    """
    The class for AIExperimentRun

    Example:
    --------
        .. code-block:: python

            experiment_run_details = AIExperimentRun(
                                        run_id=str(uuid.uuid4()),
                                        run_name="",
                                        test_data={},
                                        node=[]
                                        )
    """

    run_id: Annotated[
        str, Field(description="The ID of the AI experiment run.",
                   examples=["run-001"])
    ]
    run_name: Annotated[
        str,
        Field(
            description="The name of the AI experiment run.", examples=["Test run 1"]
        ),
    ]
    created_at: Annotated[
        str,
        Field(
            description="The timestamp of the AI experiment run.",
            examples=["2025-04-01T12:00:00Z"],
            default="",
        ),
    ]
    created_by: Annotated[
        str,
        Field(
            description="The ID of the user creating AI experiment run.",
            examples=["user-123"],
            default="",
        ),
    ]
    test_data: Annotated[
        dict,
        Field(description="The test data used for the evaluation run.", default={}),
    ]
    tracked: Annotated[
        bool,
        Field(
            description="The experiment run is tracked or not.",
            examples=[False, True],
            default=False,
        ),
    ]
    id_deleted: Annotated[
        bool,
        Field(
            description="The experiment run is deleted or not.",
            examples=[False, True],
            default=False,
        ),
    ]
    attachment_id: Annotated[
        str,
        Field(
            description="The ID of attachment of evaluation result of the AI experiment run.",
            examples=["att-456"],
            default="",
        ),
    ]
    nodes: Annotated[
        List[Node],
        Field(
            description="The list of nodes for AI Experiment run.",
            examples=[{"id": "node-001", "name": "Node_1", "type": "tool"}],
            default=[],
        ),
    ]

    description: Annotated[
        str,
        Field(
            description="The description of AI Experiment run.",
            examples=["This is the experiment run for AI Experiment"],
            default="",
        ),
    ]

    source_name: Annotated[
        str,
        Field(
            description="The name of the notebook used to create experiment run",
            examples=[""],
            default="",
        ),
    ]

    source_url: Annotated[
        str,
        Field(
            description="The URL of the notebook used to create experiment run",
            examples=[""],
            default="",
        ),
    ]

    duration: Annotated[
        int,
        Field(
            description="The time taken to complete the run.",
            examples=[""],
            default=None,
        ),
    ]
    custom_tags: Annotated[
        List[Dict],
        Field(
            description="The list of custom tags key value pair.",
            examples=[""],
            default=[],
        ),
    ]
    properties: Annotated[
        Dict,
        Field(
            description="Freeform field to store additional metadata related to runs",
            default={},
        ),
    ]

    def to_json(self):
        """
        Transform the AIExperimentRun instance to json.
        """
        return self.model_dump(mode="json")


class AIExperiment(BaseModel):
    """
    The class for AIExperiment

    Example:
    --------
    Creating instance of AIExperiment
        .. code-block:: python

            ai_experiment = AIExperiment(name="",
                             description="",
                             component_type="agent",
                             component_name="")
    """

    container_id: Annotated[
        str,
        Field(
            description="The container ID of the AI Experiment",
            examples=["proj-001"],
            default="",
        ),
    ]
    container_type: Annotated[
        str,
        Field(
            description="The container type of the AI Experiment.",
            examples=["project", "space"],
            default="",
        ),
    ]
    container_name: Annotated[
        str,
        Field(
            description="The container name of the AI Experiment.",
            examples=["project_1"],
            default="",
        ),
    ]
    name: Annotated[
        str,
        Field(
            description="The name of the AI Experiment.",
            examples=["AI Experiment for Agent 1"],
            default="AI Experiment for Agent",
        ),
    ]
    description: Annotated[
        str,
        Field(
            description="The description of the AI Experiment",
            examples=["AI Experiment asset for Agent governance"],
            default="",
        ),
    ]
    asset_type: Annotated[
        str, Field(description="", examples=["ai_experiment"], default="")
    ]
    created_at: Annotated[
        str,
        Field(
            description="The timestamp of the AI Experiment creation.",
            examples=["2025-04-08T10:00:43Z"],
            default="",
        ),
    ]
    owner_id: Annotated[
        str,
        Field(
            description="The owner of the AI Experiment.",
            examples=["user-123"],
            default="",
        ),
    ]
    asset_id: Annotated[
        str,
        Field(
            description="The ID of the AI Experiment.",
            examples=["ai_experimet-001"],
            default="",
        ),
    ]
    creator_id: Annotated[
        str,
        Field(
            description="The ID of the user creating AI Experiment.",
            examples=["user-123"],
            default="",
        ),
    ]
    component_id: Annotated[
        str,
        Field(
            description="The ID of the component of the AI Experiemnt.",
            examples=["comp-001"],
            default="",
        ),
    ]
    component_type: Annotated[
        str,
        Field(
            description="The type of AI component for which the AI Experiment is to be created.",
            examples=["agent"],
            default="agent",
        ),
    ]
    component_name: Annotated[
        str,
        Field(
            description="The name of AI component of AI Experiment.",
            examples=["Test agent"],
            default="Test agent",
        ),
    ]
    runs: Annotated[
        List[AIExperimentRun],
        Field(
            description="Experiment runs for the AI Experiment",
            examples=[
                {
                    "run_id": "run-001",
                    "run_name": "Test run 1",
                    "created_at": "2025-04-01T12:00:00Z",
                    "created_by": "user-123",
                    "test_data": {},
                    "attachment_id": "att-456",
                    "nodes": [
                        {
                            "id": "node-001",
                            "name": "Node_1",
                            "type": "example_type",
                        }
                    ],
                }
            ],
            default=[],
        ),
    ]

    def to_json(self):
        """
        Transform the AI Experiment instance to json.
        """
        return self.model_dump(mode="json")


class AIExperimentRunRequest(BaseModel):
    """ The class for AIExperimentRunRequest

    Example:
    --------
    Creating instance of AIExperiment
        .. code-block:: python

            ai_experiment_run_request = AIExperimentRunRequest(name="",
                             description="",
                             source_name="",
                             source_url="",
                             custom_tags=[])
    """

    name: Annotated[
        str,
        Field(
            description="The name of experiment run.",
            examples=["run_1"],
            default="run_1",
        ),
    ]

    description: Annotated[
        str,
        Field(
            description="The description of AI Experiment run.",
            examples=["This is the experiment run for AI Experiment"],
            default="",
        ),
    ]

    source_name: Annotated[
        str,
        Field(
            description="The name of the notebook used to create experiment run",
            examples=[""],
            default="",
        ),
    ]

    source_url: Annotated[
        str,
        Field(
            description="The URL of the notebook used to create experiment run",
            examples=[""],
            default="",
        ),
    ]

    custom_tags: Annotated[
        List[Dict],
        Field(
            description="The list of custom tags key value pair.",
            examples=[""],
            default=[],
        ),
    ]
