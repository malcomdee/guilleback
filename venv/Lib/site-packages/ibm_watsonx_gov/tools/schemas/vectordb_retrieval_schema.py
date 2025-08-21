# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from typing import Annotated, Any, Callable, Optional

from pydantic import BaseModel, Field, model_validator


class ChromaDbRetrieverConfig(BaseModel):
    """
        Configuration for retrieval tool
    """

    path: Annotated[str, Field(
        description="Path to the database")]
    host: Annotated[Optional[str], Field(
        description="The hostname of the Chroma server. Defaults to 'localhost'. Required if path is not provided", default='localhost')]
    port: Annotated[Optional[int], Field(
        description="The port of the Chroma server. Defaults to 8000. Required if path is not provided", default=8000)]
    ssl: Annotated[Optional[bool], Field(
        description="Whether to use SSL to connect to the Chroma server. Defaults to False", default=False)]
    headers: Annotated[Optional[dict], Field(
        description="A dictionary of headers to send to the Chroma server. Defaults to {}", default={})]
    settings: Annotated[Optional[dict], Field(
        description="A dictionary of settings to communicate with the chroma server. Chromadb Settings object", default={})]
    tenant: Annotated[Optional[str], Field(
        description="The tenant to use for this Chroma server. Defaults to the default tenant.", default=None)]
    database: Annotated[Optional[str], Field(
        description="The database to use for this client. Defaults to the default database.", default=None)]
    collection_name: Annotated[str, Field(
        description="Name of the collection where documents are stored")]
    embedding_function: Annotated[Callable, Field(
        description="Function to use for embedded documents")]
    n_results: Annotated[Optional[int], Field(
        description="Optional number of results to return", default=3)]

    @model_validator(mode="after")
    def validate_config(self) -> "ChromaDbRetrieverConfig":
        if self.path is None or (self.host is None and self.port is None):
            raise Exception(
                "Connection information for Chromadb is missing. Provide either the path to the database or provide host and port where it is running.")

        if self.collection_name is None:
            raise Exception("Provide name of the collection to work with.")

        if self.embedding_function is None:
            raise Exception("Missing embedding function")

        return self
