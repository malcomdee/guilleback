# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import os
from typing import Annotated, Optional

from pydantic import BaseModel, Field, model_validator
from typing_extensions import Self

from ibm_watsonx_gov.config.gen_ai_configuration import GenAIConfiguration
from ibm_watsonx_gov.entities.enums import EvaluatorFields


class OTLPCollectorConfiguration(BaseModel):
    """
    Defines the OTLPCollectorConfiguration class.
    It contains the configuration settings for the OpenTelemetry Protocol collector.

    Examples:
        1. Create OTLPCollectorConfiguration with default parameters
            .. code-block:: python

                oltp_config = OTLPCollectorConfiguration()

        1. Create OTLPCollectorConfiguration by providing server endpoint details.
            .. code-block:: python

                oltp_config = OTLPCollectorConfiguration(app_name="app",
                                                         endpoint="https://hostname/ml/v1/traces",
                                                         timeout=10,
                                                         headers={"Authorization": "Bearer token"})
    """
    app_name: Annotated[str | None,
                        Field(title="App Name",
                              description="Application name for tracing.")]
    endpoint: Annotated[str | None,
                        Field(title="OTLP Endpoint",
                              description="The OTLP collector endpoint URL for sending trace data. Default value is 'http://localhost:4318/v1/traces'",
                              default="http://localhost:4318/v1/traces")]
    insecure: Annotated[bool | None,
                        Field(title="Insecure Connection",
                              description="Whether to disable TLS for the exporter (i.e., use an insecure connection). Default is False.",
                              default=False)]
    is_grpc: Annotated[bool | None,
                       Field(title="Use gRPC",
                             description="If True, use gRPC for exporting traces instead of HTTP. Default is False.",
                             default=False)]
    timeout: Annotated[int | None,
                       Field(title="Timeout",
                             description="Timeout in milliseconds for sending telemetry data to the collector. Default is 100ms.",
                             default=100)]
    headers: Annotated[dict[str, str] | None,
                       Field(title="Headers",
                             description="Headers needed to call the server.",
                             default_factory=dict)]


class TracingConfiguration(BaseModel):
    """
    Defines the tracing configuration class. 
    Tracing configuration is required if the the evaluations are needed to be tracked in an experiment or if the agentic application traces should be sent to a Open Telemetry Collector.
    One of project_id or space_id is required.
    If the otlp_collector_config is provided, the traces are logged to Open Telemetry Collector, otherwise the traces are logged to file on disk.
    If its required to log the traces to both collector and local file, provide the otlp_collector_config and set the flag log_traces_to_file to True.

    Examples:
        1. Create Tracing configuration to track the results in an experiment
            .. code-block:: python

                tracing_config = TracingConfiguration(project_id="...")
                agentic_evaluator = AgenticEvaluator(tracing_configuration=tracing_config)
                agentic_evaluator.track_experiment(name="my_experiment")
                ...

        2. Create Tracing configuration to send traces to collector
            .. code-block:: python

                oltp_collector_config = OTLPCollectorConfiguration(endpoint="http://hostname:4318/v1/traces")
                tracing_config = TracingConfiguration(space_id="...",
                                                      resource_attributes={
                                                            "wx-deployment-id": deployment_id,
                                                            "wx-instance-id": "wml-instance-id1",
                                                            "wx-ai-service-id": "ai-service-id1"},
                                                       otlp_collector_config=oltp_collector_config)
                agentic_evaluator = AgenticEvaluator(tracing_configuration=tracing_config)
                ...
    """
    project_id: Annotated[str | None,
                          Field(title="Project ID",
                                description="The project id.",
                                default=None)]
    space_id: Annotated[str | None,
                        Field(title="Space ID",
                              description="The space id.",
                              default=None)]
    resource_attributes: Annotated[dict[str, str] | None,
                                   Field(title="Resource Attributes",
                                         description="The resource attributes set in all the spans.",
                                         default_factory=dict)]
    otlp_collector_config: Annotated[OTLPCollectorConfiguration | None,
                                     Field(title="OTLP Collector Config",
                                           description="OTLP Collector configuration.",
                                           default=None)]
    log_traces_to_file: Annotated[bool | None,
                                  Field(title="Log Traces to file",
                                        description="The flag to enable logging of traces to a file. If set to True, the traces are logged to a file. Use the flag when its needed to log the traces to file and to be sent to the server simultaneously.",
                                        default=False)]

    @model_validator(mode="after")
    def validate_fields(self) -> Self:
        if not (self.project_id or self.space_id):
            raise ValueError(
                "The project or space id is required. Please provide one of them and retry.")

        return self

    @classmethod
    def create_from_env(cls):
        # TODO get the default value and validate the tracing url env variable
        tracing_url = os.getenv("WATSONX_TRACING_URL") or ""
        project_id = os.getenv("PROJECT_ID")
        space_id = os.getenv("SPACE_ID")

        return TracingConfiguration(
            tracing_url=tracing_url,
            project_id=project_id,
            space_id=space_id
        )

    @property
    def enable_server_traces(self) -> bool:
        # Check if otlp_collector_config field was set
        return self.otlp_collector_config is not None

    @property
    def enable_local_traces(self) -> bool:
        # if otlp_collector_config is not set, enable local traces
        return self.log_traces_to_file or self.otlp_collector_config is None


class AgenticAIConfiguration(GenAIConfiguration):
    """
    Defines the AgenticAIConfiguration class.

    The configuration interface for Agentic AI tools and applications.
    This is used to specify the fields mapping details in the data and other configuration parameters needed for evaluation.

    Examples:
        1. Create configuration with default parameters
            .. code-block:: python

                configuration = AgenticAIConfiguration()

        2. Create configuration with parameters
            .. code-block:: python

                configuration = AgenticAIConfiguration(input_fields=["input"], 
                                                       output_fields=["output"])

        2. Create configuration with dict parameters
            .. code-block:: python

                config = {"input_fields": ["input"],
                          "output_fields": ["output"],
                          "context_fields": ["contexts"],
                          "reference_fields": ["reference"]}
                configuration = AgenticAIConfiguration(**config)
    """
    interaction_id_field: Annotated[Optional[str], Field(title="Interaction id field",
                                                         description="The interaction identifier field name. Default value is 'interaction_id'.",
                                                         examples=[
                                                             "interaction_id"],
                                                         default="interaction_id")]

    conversation_id_field: Annotated[Optional[str], Field(title="Conversation id field",
                                                          description="The conversation identifier field name. Default value is 'conversation_id'.",
                                                          examples=[
                                                              "conversation_id"],
                                                          default="conversation_id")]

    @classmethod
    def create_configuration(cls, *, app_config: Optional[Self],
                             method_config: Optional[Self],
                             defaults: list[EvaluatorFields],
                             add_record_fields: bool = True) -> Self:
        """
        Creates a configuration object based on the provided parameters.

        Args:
            app_config(Optional[Self]): The application configuration.
            method_config(Optional[Self]): The method configuration.
            defaults(list[EvaluatorFields]): The default fields to include in the configuration.
            add_record_fields(bool, optional): Whether to add record fields to the configuration. Defaults to True.

        Returns:
            Self: The created configuration object.
        """

        if method_config is not None:
            return method_config

        if app_config is not None:
            return app_config

        mapping = EvaluatorFields.get_default_fields_mapping()
        config = {field.value: mapping[field] for field in defaults}

        if not add_record_fields:
            return cls(**config)

        system_fields = [EvaluatorFields.RECORD_ID_FIELD,
                         EvaluatorFields.RECORD_TIMESTAMP_FIELD,
                         EvaluatorFields.INTERACTION_ID_FIELD,
                         EvaluatorFields.CONVERSATION_ID_FIELD]
        for field in system_fields:
            if field not in defaults:
                config[field.value] = EvaluatorFields.get_default_fields_mapping()[
                    field]
        return cls(**config)
