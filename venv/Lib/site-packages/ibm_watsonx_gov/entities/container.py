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

from ibm_watsonx_gov.entities.enums import ContainerType, EvaluationStage
from ibm_watsonx_gov.entities.monitor import BaseMonitor


class BaseContainer(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True)
    container_id: Annotated[str, Field(description="Space or project id", examples=[
                                       "550547b0-1be2-4426-8e62-f3423b0b83dd"])]
    container_type: Annotated[ContainerType, Field(description="The container type, project or space", examples=[
                                                   ContainerType.PROJECT, ContainerType.SPACE])]
    stage: Annotated[EvaluationStage, Field(description="The stage of the container", examples=[
                                            EvaluationStage.DEVELOPMENT, EvaluationStage.PRODUCTION])]
    prompt_setup: Annotated[dict[str, Any] | None, Field(
        default=None, description="The prompt setup details for the container")]
    monitors: Annotated[list[BaseMonitor] | None, Field(
        default=None, description="List of monitors to set up for the container")]


class ProjectContainer(BaseContainer):
    model_config = ConfigDict(
        arbitrary_types_allowed=True)
    container_type: ContainerType = ContainerType.PROJECT
    stage: EvaluationStage = EvaluationStage.DEVELOPMENT


class SpaceContainer(BaseContainer):
    model_config = ConfigDict(
        arbitrary_types_allowed=True)
    container_type: ContainerType = ContainerType.SPACE
    stage: EvaluationStage = EvaluationStage.PRODUCTION
    serving_name: Annotated[str, Field(
        description="Serving name of the deployment. This should be unique per space")]
    base_model_id: Annotated[str, Field(
        description="The model id of the space deployment base model")]
    description: Annotated[str, Field(
        description="Space deployment description")]
    name: Annotated[str, Field(description="Space deployment name")]
    version_date: Annotated[str, Field(description="Space deployment version")]
