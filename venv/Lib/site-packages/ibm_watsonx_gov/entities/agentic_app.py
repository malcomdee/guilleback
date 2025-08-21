
# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from json import loads
from typing import Annotated, Optional

from pydantic import BaseModel, Field, TypeAdapter, field_serializer
from typing_extensions import Annotated

from ibm_watsonx_gov.config.agentic_ai_configuration import \
    AgenticAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.metrics import METRICS_UNION


class MetricsConfiguration(BaseModel):
    """
    The class representing the metrics to be computed and the configuration details required for them.

    Examples:
        1. Create MetricsConfiguration with default agentic ai configuration
            .. code-block:: python

                metrics_configuration = MetricsConfiguration(metrics=[ContextRelevanceMetric()],
                                                             metric_groups=[MetricGroup.RETRIEVAL_QUALITY])])

        2. Create MetricsConfiguration by specifying agentic ai configuration
            .. code-block:: python

                config = {
                    "input_fields": ["input"],
                    "context_fields": ["contexts"]
                }
                metrics_configuration = MetricsConfiguration(configuration=AgenticAIConfiguration(**config)
                                                               metrics=[ContextRelevanceMetric()],
                                                               metric_groups=[MetricGroup.RETRIEVAL_QUALITY])])
    """
    configuration: Annotated[AgenticAIConfiguration,
                             Field(title="Metrics configuration",
                                   description="The configuration of the metrics to compute. The configuration contains the fields names to be read when computing the metrics.",
                                   default=AgenticAIConfiguration())]
    metrics: Annotated[Optional[list[GenAIMetric]],
                       Field(title="Metrics",
                             description="The list of metrics to compute.",
                             default=[])]
    metric_groups: Annotated[Optional[list[MetricGroup]],
                             Field(title="Metric Groups",
                                   description="The list of metric groups to compute.",
                                   default=[])]

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if "metrics" in obj:
            obj["metrics"] = [TypeAdapter(METRICS_UNION).validate_python(
                m) for m in obj.get("metrics")]
        return super().model_validate(obj, **kwargs)

    @field_serializer("metrics", when_used="json")
    def metrics_serializer(self, metrics: list[GenAIMetric]):
        return [metric.model_dump(mode="json") for metric in metrics]


class Node(BaseModel):
    """
    The class representing a node in an agentic application.

    Examples:
        1. Create Node with metrics configuration and default agentic ai configuration
            .. code-block:: python

                metrics_configurations = [MetricsConfiguration(metrics=[ContextRelevanceMetric()],
                                                               metric_groups=[MetricGroup.RETRIEVAL_QUALITY])])]
                node = Node(name="Retrieval Node",
                            metrics_configurations=metrics_configurations)

        2. Create Node with metrics configuration and specifying agentic ai configuration
            .. code-block:: python

                node_config = {"input_fields": ["input"],
                               "output_fields": ["output"],
                               "context_fields": ["contexts"],
                               "reference_fields": ["reference"]}
                metrics_configurations = [MetricsConfiguration(configuration=AgenticAIConfiguration(**node_config)
                                                               metrics=[ContextRelevanceMetric()],
                                                               metric_groups=[MetricGroup.RETRIEVAL_QUALITY])])]
                node = Node(name="Retrieval Node",
                            metrics_configurations=metrics_configurations)
    """
    name: Annotated[str,
                    Field(title="Name",
                          description="The name of the node.")]
    func_name: Annotated[Optional[str],
                         Field(title="Node function name",
                               description="The name of the node function.",
                               default=None)]
    metrics_configurations: Annotated[list[MetricsConfiguration],
                                      Field(title="Metrics configuration",
                                            description="The list of metrics and their configuration details.",
                                            default=[])]

    @classmethod
    def model_validate(cls, obj, **kwargs):
        if "metrics_configurations" in obj:
            obj["metrics_configurations"] = [MetricsConfiguration.model_validate(
                m) for m in obj.get("metrics_configurations")]
        return super().model_validate(obj, **kwargs)


class AgenticApp(BaseModel):
    """
    The configuration class representing an agentic application.
    An agent is composed of a set of nodes.
    The metrics to be computed at the agent or interaction level should be specified in the metrics_configuration and the metrics to be computed for the node level should be specifed in the nodes list.

    Examples:
        1. Create AgenticApp with agent level metrics configuration. 
            .. code-block:: python

                # Below example provides the agent configuration to compute the AnswerRelevanceMetric and all the metrics in Content Safety group on agent or interaction level.
                agentic_app = AgenticApp(name="Agentic App",
                                    metrics_configuration=MetricsConfiguration(metrics=[AnswerRelevanceMetric()],
                                                                                metric_groups=[MetricGroup.CONTENT_SAFETY]))
                agentic_evaluator = AgenticEvaluator(agentic_app=agentic_app)
                ...

        2. Create AgenticApp with agent and nodel level metrics configuration and default agentic ai configuration for metrics. 
            .. code-block:: python

                # Below example provides the node configuration to compute the ContextRelevanceMetric and all the metrics in Retrieval Quality group. 
                nodes = [Node(name="Retrieval Node",
                            metrics_configurations=[MetricsConfiguration(metrics=[ContextRelevanceMetric()],
                                                                         metric_groups=[MetricGroup.RETRIEVAL_QUALITY])])]

                # Below example provides the agent configuration to compute the AnswerRelevanceMetric and all the metrics in Content Safety group on agent or interaction level.
                agentic_app = AgenticApp(name="Agentic App",
                                    metrics_configuration=MetricsConfiguration(metrics=[AnswerRelevanceMetric()],
                                                                                metric_groups=[MetricGroup.CONTENT_SAFETY]),
                                    nodes=nodes)
                agentic_evaluator = AgenticEvaluator(agentic_app=agentic_app)
                ...

        3. Create AgenticApp with agent and nodel level metrics configuration and with agentic ai configuration for metrics. 
            .. code-block:: python

                # Below example provides the node configuration to compute the ContextRelevanceMetric and all the metrics in Retrieval Quality group.
                node_fields_config = {
                    "input_fields": ["input"],
                    "context_fields": ["web_context"]
                }
                nodes = [Node(name="Retrieval Node",
                            metrics_configurations=[MetricsConfiguration(configuration=AgenticAIConfiguration(**node_fields_config)
                                                                         metrics=[ContextRelevanceMetric()],
                                                                         metric_groups=[MetricGroup.RETRIEVAL_QUALITY])])]

                # Below example provides the agent configuration to compute the AnswerRelevanceMetric and all the metrics in Content Safety group on agent or interaction level.
                agent_fields_config = {
                    "input_fields": ["input"],
                    "output_fields": ["output"]
                }
                agentic_app = AgenticApp(name="Agentic App",
                                    metrics_configuration=MetricsConfiguration(configuration=AgenticAIConfiguration(**agent_fields_config)
                                                                               metrics=[AnswerRelevanceMetric()],
                                                                               metric_groups=[MetricGroup.CONTENT_SAFETY]),
                                    nodes=nodes)
                agentic_evaluator = AgenticEvaluator(agentic_app=agentic_app)
                ...
    """
    name: Annotated[str, Field(title="Agentic application name",
                               description="The name of the agentic application.",
                               default="Agentic App")]
    metrics_configuration: Annotated[Optional[MetricsConfiguration],
                                     Field(title="Metrics configuration",
                                           description="The list of metrics to be computed on the agentic application and their configuration details.",
                                           default=MetricsConfiguration())]
    nodes: Annotated[Optional[list[Node]],
                     Field(title="Node details",
                           description="The nodes details.",
                           default=[])]

    @classmethod
    def model_validate_json(cls, json_data, **kwargs):
        data = loads(json_data)
        if "metrics_configuration" in data:
            data["metrics_configuration"] = MetricsConfiguration.model_validate(
                data.get("metrics_configuration"))
        if "nodes" in data:
            data["nodes"] = [Node.model_validate(node)
                             for node in data.get("nodes", [])]
        return cls.model_validate(data, **kwargs)
