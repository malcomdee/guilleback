# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2025
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from pydantic import (BaseModel, ConfigDict, Field, ValidationError,
                      model_validator)
from typing_extensions import Annotated, Self

from ibm_watsonx_gov.entities.enums import InputDataType, TaskType


class PromptSetup(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True)
    task_type: Annotated[TaskType, Field(description="Prompt task type", examples=[
                                         TaskType.RAG, TaskType.CLASSIFICATION])]
    question_field: Annotated[str | None, Field(
        description="Question column name from the input", examples=["question"])] = None
    context_fields: Annotated[list[str] | None, Field(
        description="List of context column names from the input", examples=[["context1", "context2"]])] = None
    prediction_field: Annotated[str | None, Field(
        description="Prediction field name from the input", examples=["generated_text"], default="generated_text"
    )]

    label_column: Annotated[str, Field(
        description="reference output column name", examples=["answer", "ground_truth"])]
    input_data_type: Annotated[InputDataType, Field(
        default=InputDataType.TEXT, description="Prompt input data type", examples=[InputDataType.TEXT, InputDataType.STRUCTURED])]

    @model_validator(mode="after")
    def require_context_and_question_columns_for_rag(self) -> Self:
        if self.task_type == TaskType.RAG and (self.question_field is None or self.context_fields is None):
            raise ValidationError(
                "question_field and context_fields are required for RAG task type")
        return self
