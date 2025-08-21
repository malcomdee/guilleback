# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import os
import time
from pathlib import Path
from threading import Lock
from typing import Annotated, Callable, List, Optional, Set
from uuid import uuid4

from pydantic import Field, PrivateAttr

from ibm_watsonx_gov.ai_experiments.ai_experiments_client import \
    AIExperimentsClient
from ibm_watsonx_gov.config import AgenticAIConfiguration
from ibm_watsonx_gov.config.agentic_ai_configuration import \
    TracingConfiguration
from ibm_watsonx_gov.entities import ai_experiment as ai_experiment_entity
from ibm_watsonx_gov.entities.agentic_app import AgenticApp, Node
from ibm_watsonx_gov.entities.ai_evaluation import AIEvaluationAsset
from ibm_watsonx_gov.entities.ai_experiment import (AIExperiment,
                                                    AIExperimentRun,
                                                    AIExperimentRunRequest)
from ibm_watsonx_gov.entities.enums import MetricGroup
from ibm_watsonx_gov.entities.evaluation_result import (
    AgenticEvaluationResult, AgentMetricResult)
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.evaluators.base_evaluator import BaseEvaluator
from ibm_watsonx_gov.metric_groups.answer_quality.answer_quality_decorator import \
    AnswerQualityDecorator
from ibm_watsonx_gov.metric_groups.content_safety.content_safety_decorator import \
    ContentSafetyDecorator
from ibm_watsonx_gov.metric_groups.readability.readability_decorator import \
    ReadabilityDecorator
from ibm_watsonx_gov.metric_groups.retrieval_quality.retrieval_quality_decorator import \
    RetrievalQualityDecorator
from ibm_watsonx_gov.metrics import (AnswerRelevanceMetric,
                                     AnswerSimilarityMetric,
                                     AveragePrecisionMetric,
                                     ContextRelevanceMetric, EvasivenessMetric,
                                     FaithfulnessMetric, HAPMetric,
                                     HarmEngagementMetric, HarmMetric,
                                     HitRateMetric, JailbreakMetric,
                                     NDCGMetric, PIIMetric, ProfanityMetric,
                                     PromptSafetyRiskMetric,
                                     ReciprocalRankMetric,
                                     RetrievalPrecisionMetric,
                                     SexualContentMetric, SocialBiasMetric,
                                     TextGradeLevelMetric,
                                     TextReadingEaseMetric,
                                     ToolCallParameterAccuracyMetric,
                                     ToolCallSyntacticAccuracyMetric,
                                     ToolSelectionAccuracyMetric,
                                     TopicRelevanceMetric,
                                     UnethicalBehaviorMetric,
                                     UnsuccessfulRequestsMetric,
                                     ViolenceMetric)
from ibm_watsonx_gov.metrics.answer_relevance.answer_relevance_decorator import \
    AnswerRelevanceDecorator
from ibm_watsonx_gov.metrics.answer_similarity.answer_similarity_decorator import \
    AnswerSimilarityDecorator
from ibm_watsonx_gov.metrics.average_precision.average_precision_decorator import \
    AveragePrecisionDecorator
from ibm_watsonx_gov.metrics.context_relevance.context_relevance_decorator import \
    ContextRelevanceDecorator
from ibm_watsonx_gov.metrics.evasiveness.evasiveness_decorator import \
    EvasivenessDecorator
from ibm_watsonx_gov.metrics.faithfulness.faithfulness_decorator import \
    FaithfulnessDecorator
from ibm_watsonx_gov.metrics.hap.hap_decorator import HAPDecorator
from ibm_watsonx_gov.metrics.harm.harm_decorator import HarmDecorator
from ibm_watsonx_gov.metrics.harm_engagement.harm_engagement_decorator import \
    HarmEngagementDecorator
from ibm_watsonx_gov.metrics.hit_rate.hit_rate_decorator import \
    HitRateDecorator
from ibm_watsonx_gov.metrics.jailbreak.jailbreak_decorator import \
    JailbreakDecorator
from ibm_watsonx_gov.metrics.llm_validation.llm_validation_decorator import \
    LLMValidationDecorator
from ibm_watsonx_gov.metrics.ndcg.ndcg_decorator import NDCGDecorator
from ibm_watsonx_gov.metrics.pii.pii_decorator import PIIDecorator
from ibm_watsonx_gov.metrics.profanity.profanity_decorator import \
    ProfanityDecorator
from ibm_watsonx_gov.metrics.prompt_safety_risk.prompt_safety_risk_decorator import \
    PromptSafetyRiskDecorator
from ibm_watsonx_gov.metrics.reciprocal_rank.reciprocal_rank_decorator import \
    ReciprocalRankDecorator
from ibm_watsonx_gov.metrics.retrieval_precision.retrieval_precision_decorator import \
    RetrievalPrecisionDecorator
from ibm_watsonx_gov.metrics.sexual_content.sexual_content_decorator import \
    SexualContentDecorator
from ibm_watsonx_gov.metrics.social_bias.social_bias_decorator import \
    SocialBiasDecorator
from ibm_watsonx_gov.metrics.text_grade_level.text_grade_level_decorator import \
    TextGradeLevelDecorator
from ibm_watsonx_gov.metrics.text_reading_ease.text_reading_ease_decorator import \
    TextReadingEaseDecorator
from ibm_watsonx_gov.metrics.tool_call_parameter_accuracy.tool_call_parameter_accuracy_decorator import \
    ToolCallParameterAccuracyDecorator
from ibm_watsonx_gov.metrics.tool_call_syntactic_accuracy.tool_call_syntactic_accuracy_decorator import \
    ToolCallSyntacticAccuracyDecorator
from ibm_watsonx_gov.metrics.tool_selection_accuracy.tool_selection_accuracy_decorator import \
    ToolSelectionAccuracyDecorator
from ibm_watsonx_gov.metrics.topic_relevance.topic_relevance_decorator import \
    TopicRelevanceDecorator
from ibm_watsonx_gov.metrics.unethical_behavior.unethical_behavior_decorator import \
    UnethicalBehaviorDecorator
from ibm_watsonx_gov.metrics.unsuccessful_requests.unsuccessful_requests_decorator import \
    UnsuccessfulRequestsDecorator
from ibm_watsonx_gov.metrics.violence.violence_decorator import \
    ViolenceDecorator
from ibm_watsonx_gov.traces.span_util import get_attributes
from ibm_watsonx_gov.traces.trace_utils import TraceUtils
from ibm_watsonx_gov.utils.aggregation_util import \
    get_agentic_evaluation_result
from ibm_watsonx_gov.utils.gov_sdk_logger import GovSDKLogger
from ibm_watsonx_gov.utils.python_utils import (
    add_if_unique, combine_and_deduplicate_metadata, get)
from ibm_watsonx_gov.utils.singleton_meta import SingletonMeta

try:
    from ibm_watsonx_gov.traces.span_exporter import WxGovSpanExporter
except:
    pass

logger = GovSDKLogger.get_logger(__name__)
PROCESS_TRACES = True


try:
    from ibm_agent_analytics.instrumentation import agent_analytics_sdk
    from ibm_agent_analytics.instrumentation.configs import OTLPCollectorConfig
    from ibm_agent_analytics.instrumentation.utils import get_current_trace_id
except ImportError as e:
    logger.warning(str(e))
    PROCESS_TRACES = False


update_lock = Lock()
TRACE_LOG_FILE_NAME = os.getenv(
    "TRACE_LOG_FILE_NAME", f"experiment_traces_{str(uuid4())}")
TRACE_LOG_FILE_PATH = os.getenv("TRACE_LOG_FILE_PATH", "./wxgov_traces")


class AgenticEvaluator(BaseEvaluator, metaclass=SingletonMeta):
    """
    The class to evaluate agentic application.

    Examples:
        1. Evaluate Agent with default parameters. This will compute only the performance(latency, duration) and usage(cost, input_token_count, output_token_count) metrics.
            .. code-block:: python

                agentic_evaluator = AgenticEvaluator()
                agentic_evaluator.start_run()
                # Invoke the agentic application
                agentic_evaluator.end_run()
                result = agentic_evaluator.get_result()

        2. Evaluate Agent by specifying the agent or interaction level metrics and the node level metrics which will be computed post graph invocation when end_run() is called.
            .. code-block:: python

                # Below example provides the node configuration to compute the ContextRelevanceMetric and all the Retrieval Quality group metrics. 
                nodes = [Node(name="Retrieval Node",
                            metrics_configurations=[MetricsConfiguration(metrics=[ContextRelevanceMetric()],
                                                                         metric_groups=[MetricGroup.RETRIEVAL_QUALITY])])]
                # Please refer to MetricsConfiguration class for advanced usage where the fields details can be specified, in case the graph state has the attributes with non default names.

                # Below example provides the agent configuration to compute the AnswerRelevanceMetric and all the Content Safety group metrics on agent or interaction level.
                agentic_app = AgenticApp(name="Agentic App",
                                    metrics_configuration=MetricsConfiguration(metrics=[AnswerRelevanceMetric()],
                                                                                metric_groups=[MetricGroup.CONTENT_SAFETY]),
                                    nodes=nodes)

                agentic_evaluator = AgenticEvaluator(agentic_app=agentic_app)
                agentic_evaluator.start_run()
                # Invoke the agentic application
                agentic_evaluator.end_run()
                result = agentic_evaluator.get_result()

        3. Evaluate Agent by specifying the agent or interaction level metrics and use decorator to compute node level metrics which will be computed during graph invocation.
            .. code-block:: python

                # Below example provides the agent configuration to compute the AnswerRelevanceMetric and all the Content Safety group metrics on agent or interaction level.
                # Agent or interaction level metrics will be computed post graph invocation when end_run() is called.
                agentic_app = AgenticApp(name="Agentic App",
                                    metrics_configuration=MetricsConfiguration(metrics=[AnswerRelevanceMetric()],
                                                                                metric_groups=[MetricGroup.CONTENT_SAFETY]))

                agentic_evaluator = AgenticEvaluator(agentic_app=agentic_app)

                # Add decorator when defining the node functions
                @evaluator.evaluate_retrieval_quality(configuration=AgenticAIConfiguration(**{"input_fields": ["input_text"], "context_fields": ["local_context"]}))
                @evaluator.evaluate_content_safety() # Here the default AgenticAIConfiguration is used
                def local_search_node(state: GraphState, config: RunnableConfig) -> dict:
                    # Retrieve data from vector db
                    # ...
                    return {"local_context": []}

                agentic_evaluator.start_run()
                # Invoke the agentic application
                agentic_evaluator.end_run()
                result = agentic_evaluator.get_result()

        4. Evaluate agent with experiment tracking
            .. code-block:: python

                tracing_config = TracingConfiguration(project_id=project_id)
                agentic_evaluator = AgenticEvaluator(tracing_configuration=tracing_config)

                agentic_evaluator.track_experiment(name="my_experiment")
                agentic_evaluator.start_run(AIExperimentRunRequest(name="run1"))
                # Invoke the agentic application
                agentic_evaluator.end_run()
                result = agentic_evaluator.get_result()


    """
    agentic_app: Annotated[Optional[AgenticApp],
                           Field(title="Agentic application configuration details",
                                 description="The agentic application configuration details.",
                                 default=None)]
    tracing_configuration: Annotated[Optional[TracingConfiguration],
                                     Field(title="Tracing Configuration",
                                           description="The tracing configuration details.",
                                           default=None)]
    ai_experiment_client: Annotated[Optional[AIExperimentsClient],
                                    Field(title="AI experiments client",
                                          description="The AI experiment client object.",
                                          default=None)]
    __latest_experiment_name: Annotated[Optional[str], PrivateAttr(
        default=None)]
    __latest_experiment_id: Annotated[Optional[str], PrivateAttr(
        default=None)]
    __experiment_results: Annotated[dict,
                                    PrivateAttr(default={})]
    __run_results: Annotated[dict[str, AgenticEvaluationResult],
                             PrivateAttr(default={})]
    __online_metric_results: Annotated[list[AgentMetricResult],
                                       PrivateAttr(default=[])]
    """__metric_results holds the results of all the evaluations done for a particular evaluation instance."""
    __execution_counts: Annotated[dict[str, dict[str, int]],
                                  PrivateAttr(default={})]
    """__execution_counts holds the execution count for a particular node, for a given record_id."""
    __nodes_being_run: Annotated[dict[str, Set[str]],
                                 PrivateAttr(default={})]
    """__nodes_being_run holds the name of the current nodes being run for a given record_id. Multiple decorators can be applied on a single node using chaining. We don't want to hold multiple copies of same node here."""
    __latest_run_name: Annotated[str, PrivateAttr(default=None)]
    __nodes: Annotated[list[Node], PrivateAttr(default=[])]
    __experiment_run_details: Annotated[AIExperimentRun, PrivateAttr(
        default=None)]

    def __init__(self, /, **data):
        """
        Initialize the AgenticEvaluator object and start the tracing framework.
        """
        super().__init__(**data)
        # Initialize the agent analytics sdk
        if PROCESS_TRACES:
            tracing_params = self.__get_tracing_params(
                data.get("tracing_configuration"))

            agent_analytics_sdk.initialize_logging(
                tracer_type=agent_analytics_sdk.SUPPORTED_TRACER_TYPES.CUSTOM,
                custom_exporter=WxGovSpanExporter(
                    tracing_params.get("enable_local_traces"),
                    tracing_params.get("enable_server_traces"),
                    file_name=TRACE_LOG_FILE_NAME,
                    storage_path=TRACE_LOG_FILE_PATH,
                    # manually passing endpoint and timeout
                    endpoint=tracing_params.get("endpoint"),
                    timeout=tracing_params.get("timeout"),
                    headers=tracing_params.get("headers"),
                ),
                new_trace_on_workflow=True,
                resource_attributes={
                    "wxgov.config.agentic_app": self.agentic_app.model_dump_json(exclude_none=True) if self.agentic_app else "",
                    **tracing_params.get("resource_attributes")
                },
                # Check: does this config has any effect on CUSTOM exporters
                config=OTLPCollectorConfig(
                    **tracing_params.get("otlp_config_dict")) if tracing_params.get("otlp_config_dict") else None
            )

        self.__latest_experiment_name = "experiment_1"

    def __get_tracing_params(self, tracing_config):
        tracing_params = {
            "enable_local_traces": True,
            "enable_server_traces": False,
            "endpoint": None,
            "timeout": None,
            "headers": None,
            "resource_attributes": {},
            "otlp_config_dict": {}
        }

        if tracing_config:
            resource_attributes = tracing_config.resource_attributes
            if tracing_config.project_id:
                resource_attributes["wx-project-id"] = tracing_config.project_id
            elif tracing_config.space_id:
                resource_attributes["wx-space-id"] = tracing_config.space_id
            tracing_params["resource_attributes"] = resource_attributes
            otlp_collector_config = tracing_config.otlp_collector_config

            if otlp_collector_config:
                tracing_params["endpoint"] = otlp_collector_config.endpoint
                tracing_params["timeout"] = otlp_collector_config.timeout
                tracing_params["headers"] = otlp_collector_config.headers
                tracing_params["otlp_config_dict"] = {k: v for k, v in otlp_collector_config.dict().items()
                                                      if k != "headers"}
                tracing_params["enable_server_traces"] = True
                tracing_params["enable_local_traces"] = tracing_config.log_traces_to_file

        return tracing_params

    def track_experiment(self, name: str = "experiment_1", description: str = None, use_existing: bool = True) -> str:
        """
        Start tracking an experiment for the metrics evaluation. 
        The experiment will be created if it doesn't exist. 
        If an existing experiment with the same name is found, it will be reused based on the flag use_existing. 

        Args:
            project_id (string): The project id to store the experiment.
            name (string): The name of the experiment.
            description (str): The description of the experiment.
            use_existing (bool): The flag to specify if the experiment should be reused if an existing experiment with the given name is found.

        Returns:
            The ID of AI experiment asset
        """
        self.__latest_experiment_name = name
        # Checking if the ai_experiment_name already exists with given name if use_existing is enabled.
        # If it does reuse it, otherwise creating a new ai_experiment
        # Set the experiment_name and experiment_id
        self.ai_experiment_client = AIExperimentsClient(
            api_client=self.api_client,
            project_id=self.tracing_configuration.project_id
        )
        ai_experiment = None
        if use_existing:
            ai_experiment = self.ai_experiment_client.search(name)

        # If no AI experiment exists with specified name or use_existing is False, create new AI experiment
        if not ai_experiment:
            ai_experiment_details = AIExperiment(
                name=name,
                description=description or "AI experiment for Agent governance"
            )
            ai_experiment = self.ai_experiment_client.create(
                ai_experiment_details)

        ai_experiment_id = ai_experiment.asset_id

        # Experiment id will be set when the experiment is tracked and not set when the experiment is not tracked
        self.__latest_experiment_id = ai_experiment_id
        self.__run_results = {}
        return ai_experiment_id

    def start_run(self, run_request: AIExperimentRunRequest = AIExperimentRunRequest(name="run_1")) -> AIExperimentRun:
        """
        Start a run to track the metrics computation within an experiment.
        This method is required to be called before any metrics computation.

        Args:
            run_request (AIExperimentRunRequest): The run_request instance containing name, source_name, source_url, custom_tags

        Returns:
            The details of experiment run like id, name, description etc.
        """
        name = run_request.name
        self.__latest_run_name = name
        self.__experiment_results[self.__latest_experiment_name] = self.__run_results
        self.__start_time = time.time()
        # Having experiment id indicates user is tracking experiments
        if self.__latest_experiment_id:
            # Create run object, having experiment id indicates user is tracking experiments
            self.__experiment_run_details = AIExperimentRun(
                run_id=str(uuid4()),
                run_name=name,
                source_name=run_request.source_name,
                source_url=run_request.source_url,
                custom_tags=run_request.custom_tags
            )

        return self.__experiment_run_details

    def end_run(self, track_notebook: Optional[bool] = False):
        """
        End a run to collect and compute the metrics within the current run.

        Args:
            track_notebook (bool): flag to specify storing the notebook with current run

        """
        eval_result, trace_metadata = self.__compute_metrics_from_traces()
        self.__run_results[self.__latest_run_name] = eval_result
        # Having experiment id indicates user is tracking experiments and its needed to submit the run details
        if self.__latest_experiment_id:
            self.__store_run_results(track_notebook, trace_metadata)

        self.__reset_results()

    def compare_ai_experiments(self,
                               ai_experiments: List[AIExperiment] = None,
                               ai_evaluation_details: AIEvaluationAsset = None
                               ) -> str:
        """
        Creates an AI Evaluation asset to compare AI experiment runs.

        Args:
            ai_experiments (List[AIExperiment], optional):
                List of AI experiments to be compared. If all runs for an experiment need to be compared, then specify the runs value as empty list for the experiment.
            ai_evaluation_details (AIEvaluationAsset, optional):
                An instance of AIEvaluationAsset having details (name, description and metrics configuration)
        Returns:
            An instance of AIEvaluationAsset.

        Examples:
            1. Create AI evaluation with list of experiment IDs

            .. code-block:: python

                # Initialize the API client with credentials
                api_client = APIClient(credentials=Credentials(api_key="", url="wos_url"))

                # Create the instance of Agentic evaluator
                evaluator = AgenticEvaluator(api_client=api_client, tracing_configuration=TracingConfiguration(project_id=project_id))

                # [Optional] Define evaluation configuration
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
                ai_evaluation_details = AIEvaluationAsset(
                    name="AI Evaluation for agent",
                    evaluation_configuration=evaluation_config
                )

                # Compare two or more AI experiments using the evaluation asset
                ai_experiment1 = AIExperiment(
                    asset_id = ai_experiment_id_1,
                    runs = [<Run1 details>, <Run2 details>] # Run details are returned by the start_run method
                )
                ai_experiment2 = AIExperiment(
                    asset_id = ai_experiment_id_2,
                    runs = [] # Empty list means all runs for this experiment will be compared
                )
                ai_evaluation_asset_href = evaluator.compare_ai_experiments(
                    ai_experiments = [ai_experiment_1, ai_experiment_2],
                    ai_evaluation_details=ai_evaluation_asset
                )
        """
        # If experiment runs to be compared are not provided, using all runs from the latest tracked experiment
        if not ai_experiments:
            ai_experiments = [AIExperiment(
                asset_id=self.__latest_experiment_id, runs=[])]

        # Construct experiment_runs map
        ai_experiment_runs = {exp.asset_id: exp.runs for exp in ai_experiments}

        ai_evaluation_asset = self.ai_experiment_client.create_ai_evaluation_asset(
            ai_experiment_runs=ai_experiment_runs,
            ai_evaluation_details=ai_evaluation_details
        )
        ai_evaluation_asset_href = self.ai_experiment_client.get_ai_evaluation_asset_href(
            ai_evaluation_asset)

        return ai_evaluation_asset_href

    def __compute_metrics_from_traces(self):
        """
        Computes the metrics using the traces collected in the log file.
        """
        if not PROCESS_TRACES:
            return

        trace_log_file_path = Path(
            f"{TRACE_LOG_FILE_PATH}/{TRACE_LOG_FILE_NAME}.log")
        spans = []
        for span in TraceUtils.stream_trace_data(trace_log_file_path):
            spans.append(span)

        metrics_result = []
        all_metadata = []
        span_trees = TraceUtils.build_span_trees(spans=spans)
        for span_tree in span_trees:
            # Process only the spans that are associated with the agent application
            attrs = get_attributes(span_tree.span.attributes, [
                "traceloop.span.kind"])
            if not attrs.get("traceloop.span.kind") == "workflow":
                continue

            mr, ns, _, i_experiment_run_metadata = TraceUtils.compute_metrics_from_trace(span_tree=span_tree,
                                                                                         api_client=self.api_client)
            all_metadata.append(i_experiment_run_metadata)

            metrics_result.extend(mr)
            for n in ns:
                add_if_unique(n, self.__nodes, ["name", "func_name"])
        deduplicated_metadata = combine_and_deduplicate_metadata(*all_metadata)
        return get_agentic_evaluation_result(
            metrics_result=metrics_result, nodes=self.__nodes), deduplicated_metadata

    def __store_run_results(self, track_notebook: Optional[bool] = False, trace_metadata: dict = None):

        aggregated_results = self.get_result().get_aggregated_metrics_results()
        # Fetchig the nodes details to update in experiment run
        nodes = []
        for node in self.get_nodes():
            nodes.append(ai_experiment_entity.Node(
                id=node.func_name, name=node.name, foundation_models=get(trace_metadata, f"{node.name}.foundation_models", [])))
        self.__experiment_run_details.nodes = nodes
        # Duration of run in seconds
        self.__experiment_run_details.duration = int(
            time.time() - self.__start_time)

        # Storing the run result as attachment and update the run info in AI experiment
        # Todo - keeping the List[AggregateAgentMetricResult] - is that compatible? should store full AgenticEvaluationResult?
        self.ai_experiment_client.update(
            self.__latest_experiment_id,
            self.__experiment_run_details,
            aggregated_results,
            track_notebook,
        )

    def get_nodes(self) -> list[Node]:
        """
        Get the list of nodes used in the agentic application

        Return:
            nodes (list[Node]): The list of nodes used in the agentic application
        """
        return self.__nodes

    def get_result(self, run_name: Optional[str] = None) -> AgenticEvaluationResult:
        """
        Get the AgenticEvaluationResult for the run. By default the result for the latest run is returned.
        Specify the run name to get the result for a specific run.
        Args:
            run_name (string): The evaluation run name
        Return:
            agentic_evaluation_result (AgenticEvaluationResult): The AgenticEvaluationResult object for the run.
        """
        if run_name:
            result = self.__run_results.get(run_name)
        else:
            result = self.__run_results.get(self.__latest_run_name)

        return result

    def get_metric_result(self, metric_name: str, node_name: str) -> AgentMetricResult:
        """
        Get the AgentMetricResult for the given metric and node name. 
        This is used to get the result of the metric computed during agent execution.

        Args:
            metric_name (string): The metric name
            node_name (string): The node name
        Return:
            agent_metric_result (AgentMetricResult): The AgentMetricResult object for the metric.
        """
        for metric in self.__online_metric_results:
            if metric.applies_to == "node" and metric.name == metric_name \
                    and metric.node_name == node_name and metric.interaction_id == get_current_trace_id():
                return metric

        return None

    def __reset_results(self):
        self.__online_metric_results.clear()
        self.__execution_counts.clear()
        self.__nodes_being_run.clear()
        trace_log_file_path = Path(
            f"{TRACE_LOG_FILE_PATH}/{TRACE_LOG_FILE_NAME}.log")
        if os.path.exists(trace_log_file_path):
            os.remove(trace_log_file_path)

    def evaluate_context_relevance(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [],
                                   compute_real_time: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing context relevance metric on an agentic node.

        For more details, see :class:`ibm_watsonx_gov.metrics.ContextRelevanceMetric`

        Args:
            func (Optional[Callable], optional): The node on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ContextRelevanceMetric() ].
            compute_real_time (Optional[bool], optional): The flag to indicate whether the metric should be computed along with the node execution or not.

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped node.

        Examples:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_context_relevance
                    def agentic_node(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = ContextRelevanceMetric(
                        method="sentence_bert_bge", thresholds=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(
                        method="sentence_bert_mini_lm", thresholds=MetricThreshold(type="lower_limit", value=0.6))
                    metric_3 = ContextRelevanceMetric(
                        method="granite_guardian", thresholds=MetricThreshold(type="lower_limit", value=0.6))
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_context_relevance(metrics=[metric_1, metric_2, metric_3])
                    def agentic_node(*args, *kwargs):
                        pass
        """
        return ContextRelevanceDecorator(api_client=self.api_client,
                                         configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                         metric_results=self.__online_metric_results,
                                         execution_counts=self.__execution_counts,
                                         nodes_being_run=self.__nodes_being_run,
                                         lock=update_lock,
                                         compute_real_time=compute_real_time).evaluate_context_relevance(func, configuration=configuration, metrics=metrics)

    def evaluate_average_precision(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [],
                                   compute_real_time: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing average precision metric on an agentic tool.
        This metric uses context relevance values for computation, context relevance metric would be computed as a prerequisite.

        For more details, see :class:`ibm_watsonx_gov.metrics.AveragePrecisionMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ AveragePrecisionMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_average_precision
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = AveragePrecisionMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_average_precision(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return AveragePrecisionDecorator(api_client=self.api_client,
                                         configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                         metric_results=self.__online_metric_results,
                                         execution_counts=self.__execution_counts,
                                         nodes_being_run=self.__nodes_being_run,
                                         lock=update_lock,
                                         compute_real_time=compute_real_time).evaluate_average_precision(func, configuration=configuration, metrics=metrics)

    def evaluate_ndcg(self,
                      func: Optional[Callable] = None,
                      *,
                      configuration: Optional[AgenticAIConfiguration] = None,
                      metrics: list[GenAIMetric] = [],
                      compute_real_time: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing ndcg metric on an agentic tool.
        This metric uses context relevance values for computation, context relevance metric would be computed as a prerequisite.

        For more details, see :class:`ibm_watsonx_gov.metrics.NDCGMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ NDCGMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_ndcg
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = NDCGMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_ndcg(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return NDCGDecorator(api_client=self.api_client,
                             configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                             metric_results=self.__online_metric_results,
                             execution_counts=self.__execution_counts,
                             nodes_being_run=self.__nodes_being_run,
                             lock=update_lock,
                             compute_real_time=compute_real_time).evaluate_ndcg(func, configuration=configuration, metrics=metrics)

    def evaluate_reciprocal_rank(self,
                                 func: Optional[Callable] = None,
                                 *,
                                 configuration: Optional[AgenticAIConfiguration] = None,
                                 metrics: list[GenAIMetric] = [],
                                 compute_real_time: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing reciprocal precision metric on an agentic tool.
        This metric uses context relevance values for computation, context relevance metric would be computed as a prerequisite.

        For more details, see :class:`ibm_watsonx_gov.metrics.ReciprocalRankMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ReciprocalRankMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_reciprocal_rank
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = ReciprocalRankMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_reciprocal_rank(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return ReciprocalRankDecorator(api_client=self.api_client,
                                       configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                       metric_results=self.__online_metric_results,
                                       execution_counts=self.__execution_counts,
                                       nodes_being_run=self.__nodes_being_run,
                                       lock=update_lock,
                                       compute_real_time=compute_real_time).evaluate_reciprocal_rank(func, configuration=configuration, metrics=metrics)

    def evaluate_retrieval_precision(self,
                                     func: Optional[Callable] = None,
                                     *,
                                     configuration: Optional[AgenticAIConfiguration] = None,
                                     metrics: list[GenAIMetric] = [],
                                     compute_real_time: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing retrieval precision metric on an agentic tool.
        This metric uses context relevance values for computation, context relevance metric would be computed as a prerequisite.

        For more details, see :class:`ibm_watsonx_gov.metrics.RetrievalPrecisionMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ RetrievalPrecisionMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_retrieval_precision
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = AveragePrecisionMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_retrieval_precision(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return RetrievalPrecisionDecorator(api_client=self.api_client,
                                           configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                           metric_results=self.__online_metric_results,
                                           execution_counts=self.__execution_counts,
                                           nodes_being_run=self.__nodes_being_run,
                                           lock=update_lock,
                                           compute_real_time=compute_real_time).evaluate_retrieval_precision(func, configuration=configuration, metrics=metrics)

    def evaluate_hit_rate(self,
                          func: Optional[Callable] = None,
                          *,
                          configuration: Optional[AgenticAIConfiguration] = None,
                          metrics: list[GenAIMetric] = [],
                          compute_real_time: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing hit rate metric on an agentic tool.
        This metric uses context relevance values for computation, context relevance metric would be computed as a prerequisite.

        For more details, see :class:`ibm_watsonx_gov.metrics.HitRateMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ HitRateMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_hit_rate
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = HitRateMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_hit_rate(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return HitRateDecorator(api_client=self.api_client,
                                configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                metric_results=self.__online_metric_results,
                                execution_counts=self.__execution_counts,
                                nodes_being_run=self.__nodes_being_run,
                                lock=update_lock,
                                compute_real_time=compute_real_time).evaluate_hit_rate(func, configuration=configuration, metrics=metrics)

    def evaluate_answer_similarity(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [],
                                   compute_real_time: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing answer similarity metric on an agentic node.

        For more details, see :class:`ibm_watsonx_gov.metrics.AnswerSimilarityMetric`

        Args:
            func (Optional[Callable], optional): The node on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ AnswerSimilarityMetric() ].
            compute_real_time (Optional[bool], optional): The flag to indicate whether the metric should be computed along with the node execution or not.

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped node.

        Examples:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_answer_similarity
                    def agentic_node(*args, *kwargs):
                        pass


            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = AnswerSimilarityMetric(
                        method="token_k_precision", threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = AnswerSimilarityMetric(
                        method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_answer_similarity(metrics=[metric_1, metric_2])
                    def agentic_node(*args, *kwargs):
                        pass
        """

        return AnswerSimilarityDecorator(api_client=self.api_client,
                                         configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                         metric_results=self.__online_metric_results,
                                         execution_counts=self.__execution_counts,
                                         nodes_being_run=self.__nodes_being_run,
                                         lock=update_lock,
                                         compute_real_time=compute_real_time).evaluate_answer_similarity(func, configuration=configuration, metrics=metrics)

    def evaluate_faithfulness(self,
                              func: Optional[Callable] = None,
                              *,
                              configuration: Optional[AgenticAIConfiguration] = None,
                              metrics: list[GenAIMetric] = [],
                              compute_real_time: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing faithfulness metric on an agentic node.

        For more details, see :class:`ibm_watsonx_gov.metrics.FaithfulnessMetric`

        Args:
            func (Optional[Callable], optional): The node on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ FaithfulnessMetric() ].
            compute_real_time (Optional[bool], optional): The flag to indicate whether the metric should be computed along with the node execution or not.

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped node.

        Examples:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_faithfulness
                    def agentic_node(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = FaithfulnessMetric(method="token_k_precision", threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = FaithfulnessMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_faithfulness(metrics=[metric_1, metric_2])
                    def agentic_node(*args, *kwargs):
                        pass
        """

        return FaithfulnessDecorator(api_client=self.api_client,
                                     configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                     metric_results=self.__online_metric_results,
                                     execution_counts=self.__execution_counts,
                                     nodes_being_run=self.__nodes_being_run,
                                     lock=update_lock,
                                     compute_real_time=compute_real_time).evaluate_faithfulness(func, configuration=configuration, metrics=metrics)

    def evaluate_unsuccessful_requests(self,
                                       func: Optional[Callable] = None,
                                       *,
                                       configuration: Optional[AgenticAIConfiguration] = None,
                                       metrics: list[GenAIMetric] = [],
                                       compute_real_time: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing unsuccessful requests metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.UnsuccessfulRequestsMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ UnsuccessfulRequestsMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_unsuccessful_requests
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = UnsuccessfulRequestsMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_unsuccessful_requests(metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        return UnsuccessfulRequestsDecorator(api_client=self.api_client,
                                             configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                             metric_results=self.__online_metric_results,
                                             execution_counts=self.__execution_counts,
                                             nodes_being_run=self.__nodes_being_run,
                                             lock=update_lock,
                                             compute_real_time=compute_real_time).evaluate_unsuccessful_requests(func, configuration=configuration, metrics=metrics)

    def evaluate_answer_relevance(self,
                                  func: Optional[Callable] = None,
                                  *,
                                  configuration: Optional[AgenticAIConfiguration] = None,
                                  metrics: list[GenAIMetric] = [],
                                  compute_real_time: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing answer relevance metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.AnswerRelevanceMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ AnswerRelevanceMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_answer_relevance
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods
                .. code-block:: python

                    metric_1 = AnswerRelevanceMetric(method="token_recall", thresholds=[MetricThreshold(type="lower_limit", value=0.5)])
                    metric_2 = AnswerRelevanceMetric(method="granite_guardian", thresholds=[MetricThreshold(type="lower_limit", value=0.5)])

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_answer_relevance(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        return AnswerRelevanceDecorator(api_client=self.api_client,
                                        configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                        metric_results=self.__online_metric_results,
                                        execution_counts=self.__execution_counts,
                                        nodes_being_run=self.__nodes_being_run,
                                        lock=update_lock,
                                        compute_real_time=compute_real_time).evaluate_answer_relevance(func, configuration=configuration, metrics=metrics)

    # def evaluate_general_quality_with_llm(self,
    #                                       func: Optional[Callable] = None,
    #                                       *,
    #                                       configuration: Optional[AgenticAIConfiguration] = None,
    #                                       metrics: list[GenAIMetric] = [],
    #                                       compute_real_time: Optional[bool] = True) -> dict:
    #     """
    #     An evaluation decorator for computing llm validation metric on an agentic node.

    #     For more details, see :class:`ibm_watsonx_gov.metrics.LLMValidationMetric`

    #     Args:
    #         func (Optional[Callable], optional): The node on which the metric is to be computed.
    #         configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
    #         metrics (list[GenAIMetric]): The list of metrics to compute as part of this evaluator.
    #         compute_real_time (Optional[bool], optional): The flag to indicate whether the metric should be computed along with the node execution or not.
    #                                            When online is set to False, evaluate_metrics method should be invoked on the AgenticEvaluator to compute the metric.

    #     Raises:
    #         Exception: If there is any error while evaluation.

    #     Returns:
    #         dict: The result of the wrapped node.

    #     Examples:
    #         1. Basic usage
    #             .. code-block:: python

    #                 evaluator = AgenticEvaluator()
    #                 @evaluator.evaluate_general_quality_with_llm
    #                 def agentic_node(*args, *kwargs):
    #                     pass
    #     """
    #     return LLMValidationDecorator(api_client=self.api_client,
    #                                   configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
    #                                   metric_results=self.__online_metric_results,
    #                                   execution_counts=self.__execution_counts,
    #                                   nodes_being_run=self.__nodes_being_run,
    #                                   lock=update_lock,
    #                                   compute_real_time=compute_real_time).evaluate_general_quality_with_llm(func,
    #                                                                                                    configuration=configuration,
    #                                                                                                    metrics=metrics)

    def evaluate_tool_call_parameter_accuracy(self,
                                              func: Optional[Callable] = None,
                                              *,
                                              configuration: Optional[AgenticAIConfiguration] = None,
                                              metrics: list[GenAIMetric] = [],
                                              compute_real_time: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing tool_call_parameter_accuracy metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolCallParameterAccuracyMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolCallParameterAccuracyMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    tool_calls_metric_config={
                        "tools":[get_weather, fetch_stock_price], # List of tools available to the agent
                    }
                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolCallParameterAccuracyMetric(llm_judge=llm_judge)
                    @evaluator.evaluate_tool_call_parameter_accuracy(configuration=AgenticAIConfiguration(**tool_calls_metric_config), metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with custom tool calls field
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    tool_calls_metric_config={
                        "tools":[get_weather, fetch_stock_price], # List of tools available to the agent
                        "tool_calls_field": "tool_calls" # Graph state field to store the Agent's response/tool calls
                    }
                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolCallParameterAccuracyMetric(llm_judge=llm_judge)
                    @evaluator.evaluate_tool_call_parameter_accuracy(configuration=AgenticAIConfiguration(**tool_calls_metric_config), metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass

            3. Usage with different thresholds
                .. code-block:: python

                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolCallParameterAccuracyMetric(llm_judge=llm_judge, threshold=MetricThreshold(type="upper_limit", value=0.7))
                    evaluator = AgenticEvaluator()
                    tool_calls_metric_config={
                        "tools":[get_weather, fetch_stock_price], # List of tools available to the agent
                        "tool_calls_field": "tool_calls" # Graph state field to store the Agent's response/tool calls
                    }
                    @evaluator.evaluate_tool_call_parameter_accuracy(configuration=AgenticAIConfiguration(**tool_calls_metric_config),metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        return ToolCallParameterAccuracyDecorator(api_client=self.api_client,
                                                  configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                                  metric_results=self.__online_metric_results,
                                                  execution_counts=self.__execution_counts,
                                                  nodes_being_run=self.__nodes_being_run,
                                                  lock=update_lock,
                                                  compute_real_time=compute_real_time).evaluate_tool_call_parameter_accuracy(func, configuration=configuration, metrics=metrics)

    def evaluate_tool_selection_accuracy(self,
                                         func: Optional[Callable] = None,
                                         *,
                                         configuration: Optional[AgenticAIConfiguration] = None,
                                         metrics: list[GenAIMetric] = [],
                                         compute_real_time: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing tool_selection_accuracy metric on an agent tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolSelectionAccuracyMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolSelectionAccuracyMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    tool_selection_metric_config={
                        "tools":[get_weather, fetch_stock_price], # List of tools available to the agent
                    }
                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolSelectionAccuracyMetric(llm_judge=llm_judge)
                    @evaluator.evaluate_tool_selection_accuracy(configuration=AgenticAIConfiguration(**tool_selection_metric_config), metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with custom tool calls field
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    tool_selection_metric_config={
                        "tools":[get_weather, fetch_stock_price], # List of tools available to the agent
                        "tool_calls_field": "tool_calls" # Graph state field to store the Agent's response/tool calls
                    }
                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolSelectionAccuracyMetric(llm_judge=llm_judge)
                    @evaluator.evaluate_tool_selection_accuracy(configuration=AgenticAIConfiguration(**tool_selection_metric_config), metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass

            3. Usage with different thresholds
                .. code-block:: python

                    llm_judge = LLMJudge(
                        model=WxAIFoundationModel(
                            model_id="meta-llama/llama-3-3-70b-instruct",
                            project_id=os.getenv("WATSONX_PROJECT_ID"),
                        )
                    )
                    metric_1 = ToolSelectionAccuracyMetric(llm_judge=llm_judge, threshold=MetricThreshold(type="upper_limit", value=0.7))
                    evaluator = AgenticEvaluator()
                    tool_selection_metric_config={
                        "tools":[get_weather, fetch_stock_price], # List of tools available to the agent
                        "tool_calls_field": "tool_calls" # Graph state field to store the Agent's response/tool calls
                    }
                    @evaluator.evaluate_tool_selection_accuracy(configuration=AgenticAIConfiguration(**tool_selection_metric_config),metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        return ToolSelectionAccuracyDecorator(api_client=self.api_client,
                                              configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                              metric_results=self.__online_metric_results,
                                              execution_counts=self.__execution_counts,
                                              nodes_being_run=self.__nodes_being_run,
                                              lock=update_lock,
                                              compute_real_time=compute_real_time).evaluate_tool_selection_accuracy(func, configuration=configuration, metrics=metrics)

    def evaluate_tool_call_syntactic_accuracy(self,
                                              func: Optional[Callable] = None,
                                              *,
                                              configuration: Optional[AgenticAIConfiguration] = None,
                                              metrics: list[GenAIMetric] = [],
                                              compute_real_time: Optional[bool] = True) -> dict:
        """
        An evaluation decorator for computing tool_call_syntactic_accuracy metric on an agent tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.ToolCallSyntacticAccuracyMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [ ToolCallSyntacticAccuracyMetric() ].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    tool_call_syntactic_metric_config={
                        "tools":[get_weather, fetch_stock_price], # List of tools available to the agent
                    }
                    @evaluator.evaluate_tool_call_syntactic_accuracy(configuration=AgenticAIConfiguration(**tool_call_syntactic_metric_config))
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with custom tool calls field
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    tool_call_syntactic_metric_config={
                        "tools":[get_weather, fetch_stock_price], # List of tools available to the agent
                        "tool_calls_field": "tool_calls" # Graph state field to store the Agent's response/tool calls
                    }
                    @evaluator.evaluate_tool_call_syntactic_accuracy(configuration=AgenticAIConfiguration(**tool_call_syntactic_metric_config))
                    def agentic_tool(*args, *kwargs):
                        pass

            3. Usage with different thresholds
                .. code-block:: python

                    metric_1 = ToolCallSyntacticAccuracyMetric(threshold=MetricThreshold(type="upper_limit", value=0.7))
                    evaluator = AgenticEvaluator()
                    tool_call_syntactic_metric_config={
                        "tools":[get_weather, fetch_stock_price], # List of tools available to the agent
                        "tool_calls_field": "tool_calls" # Graph state field to store the Agent's response/tool calls
                    }
                    @evaluator.evaluate_tool_call_syntactic_accuracy(configuration=AgenticAIConfiguration(**tool_call_syntactic_metric_config),metrics=[metric_1])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return ToolCallSyntacticAccuracyDecorator(api_client=self.api_client,
                                                  configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                                  metric_results=self.__online_metric_results,
                                                  execution_counts=self.__execution_counts,
                                                  nodes_being_run=self.__nodes_being_run,
                                                  lock=update_lock,
                                                  compute_real_time=compute_real_time).evaluate_tool_call_syntactic_accuracy(func, configuration=configuration, metrics=metrics)

    def evaluate_prompt_safety_risk(self,
                                    func: Optional[Callable] = None,
                                    *,
                                    configuration: Optional[AgenticAIConfiguration] = None,
                                    metrics: list[GenAIMetric],
                                    compute_real_time: Optional[bool] = True,
                                    ) -> dict:
        """
        An evaluation decorator for computing prompt safety risk metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.PromptSafetyRiskMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric]): The list of metrics to compute as part of this evaluator.

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Create evaluate_prompt_safety_risk decorator with default parameters. By default, the metric uses the "input_text" from the graph state as the input.
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_prompt_safety_risk(metrics=[PromptSafetyRiskMetric(system_prompt="...")])
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Create evaluate_prompt_safety_risk decorator with thresholds and configuration
                .. code-block:: python

                    metric = PromptSafetyRiskMetric(system_prompt="...", thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    config = {"input_fields": ["input"]}
                    configuration = AgenticAIConfiguration(**config)
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_prompt_safety_risk(metrics=[metric], configuration=configuration)
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return PromptSafetyRiskDecorator(api_client=self.api_client,
                                         configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                         metric_results=self.__online_metric_results,
                                         execution_counts=self.__execution_counts,
                                         nodes_being_run=self.__nodes_being_run,
                                         lock=update_lock,
                                         compute_real_time=compute_real_time).evaluate_prompt_safety_risk(func, configuration=configuration, metrics=metrics)

    def evaluate_hap(self,
                     func: Optional[Callable] = None,
                     *,
                     configuration: Optional[AgenticAIConfiguration] = None,
                     metrics: list[GenAIMetric] = [],
                     compute_real_time: Optional[bool] = True,
                     ) -> dict:
        """
        An evaluation decorator for computing HAP metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.HAPMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [HAPMetric()].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Create evaluate_hap decorator with default parameters. By default, the metric uses the "input_text" from the graph state as the input.
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_hap
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Create evaluate_hap decorator with thresholds and configuration
                .. code-block:: python

                    metric = HAPMetric(thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    config = {"input_fields": ["input"]}
                    configuration = AgenticAIConfiguration(**config)
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_hap(metrics=[metric], configuration=configuration)
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return HAPDecorator(api_client=self.api_client,
                            configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                            metric_results=self.__online_metric_results,
                            execution_counts=self.__execution_counts,
                            nodes_being_run=self.__nodes_being_run,
                            lock=update_lock,
                            compute_real_time=compute_real_time).evaluate_hap(func, configuration=configuration, metrics=metrics)

    def evaluate_pii(self,
                     func: Optional[Callable] = None,
                     *,
                     configuration: Optional[AgenticAIConfiguration] = None,
                     metrics: list[GenAIMetric] = [],
                     compute_real_time: Optional[bool] = True,
                     ) -> dict:
        """
        An evaluation decorator for computing PII metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.PIIMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [PIIMetric()].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Create evaluate_pii decorator with default parameters. By default, the metric uses the "input_text" from the graph state as the input.
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_pii
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Create evaluate_pii decorator with thresholds and configuration
                .. code-block:: python

                    metric = PIIMetric(thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    config = {"input_fields": ["input"]}
                    configuration = AgenticAIConfiguration(**config)
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_pii(metrics=[metric], configuration=configuration)
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return PIIDecorator(api_client=self.api_client,
                            configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                            metric_results=self.__online_metric_results,
                            execution_counts=self.__execution_counts,
                            nodes_being_run=self.__nodes_being_run,
                            lock=update_lock,
                            compute_real_time=compute_real_time).evaluate_pii(func, configuration=configuration, metrics=metrics)

    def evaluate_harm(self,
                      func: Optional[Callable] = None,
                      *,
                      configuration: Optional[AgenticAIConfiguration] = None,
                      metrics: list[GenAIMetric] = [],
                      compute_real_time: Optional[bool] = True,
                      ) -> dict:
        """
        An evaluation decorator for computing harm risk on an agentic tool via granite guardian.

        For more details, see :class:`ibm_watsonx_gov.metrics.HarmMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator.  Defaults to [ HarmMetric() ]

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Create evaluate_harm decorator with default parameters. By default, the metric uses the "input_text" from the graph state as the input.
                .. code-block:: python 

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_harm
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Create evaluate_harm decorator with thresholds and configuration
                .. code-block:: python

                    metric = HarmMetric(thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    config = {"input_fields": ["input"]}
                    configuration = AgenticAIConfiguration(**config)
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_harm(metrics=[metric], configuration=configuration)
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return HarmDecorator(api_client=self.api_client,
                             configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                             metric_results=self.__online_metric_results,
                             execution_counts=self.__execution_counts,
                             nodes_being_run=self.__nodes_being_run,
                             lock=update_lock,
                             compute_real_time=compute_real_time).evaluate_harm(func, configuration=configuration, metrics=metrics)

    def evaluate_social_bias(self,
                             func: Optional[Callable] = None,
                             *,
                             configuration: Optional[AgenticAIConfiguration] = None,
                             metrics: list[GenAIMetric] = [],
                             compute_real_time: Optional[bool] = True,
                             ) -> dict:
        """
        An evaluation decorator for computing social bias on an agentic tool via granite guardian.

        For more details, see :class:`ibm_watsonx_gov.metrics.SocialBiasMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator.  Defaults to [ HarmMetric() ]

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Create evaluate_social_bias decorator with default parameters. By default, the metric uses the "input_text" from the graph state as the input.
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_social_bias
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Create evaluate_social_bias decorator with thresholds and configuration
                .. code-block:: python

                    metric = SocialBiasMetric(thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    config = {"input_fields": ["input"]}
                    configuration = AgenticAIConfiguration(**config)
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_social_bias(metrics=[metric], configuration=configuration)
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return SocialBiasDecorator(api_client=self.api_client,
                                   configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                   metric_results=self.__online_metric_results,
                                   execution_counts=self.__execution_counts,
                                   nodes_being_run=self.__nodes_being_run,
                                   lock=update_lock,
                                   compute_real_time=compute_real_time).evaluate_social_bias(func, configuration=configuration, metrics=metrics)

    def evaluate_profanity(self,
                           func: Optional[Callable] = None,
                           *,
                           configuration: Optional[AgenticAIConfiguration] = None,
                           metrics: list[GenAIMetric] = [],
                           compute_real_time: Optional[bool] = True,
                           ) -> dict:
        """
        An evaluation decorator for computing profanity on an agentic tool via granite guardian.

        For more details, see :class:`ibm_watsonx_gov.metrics.ProfanityMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator.  Defaults to [ ProfanityMetric() ]

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Create evaluate_profanity decorator with default parameters. By default, the metric uses the "input_text" from the graph state as the input.
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_profanity
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Create evaluate_profanity decorator with thresholds and configuration
                .. code-block:: python

                    metric = ProfanityMetric(thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    config = {"input_fields": ["input"]}
                    configuration = AgenticAIConfiguration(**config)
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_profanity(metrics=[metric], configuration=configuration)
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return ProfanityDecorator(api_client=self.api_client,
                                  configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                  metric_results=self.__online_metric_results,
                                  execution_counts=self.__execution_counts,
                                  nodes_being_run=self.__nodes_being_run,
                                  lock=update_lock,
                                  compute_real_time=compute_real_time).evaluate_profanity(func, configuration=configuration, metrics=metrics)

    def evaluate_sexual_content(self,
                                func: Optional[Callable] = None,
                                *,
                                configuration: Optional[AgenticAIConfiguration] = None,
                                metrics: list[GenAIMetric] = [],
                                compute_real_time: Optional[bool] = True,
                                ) -> dict:
        """
        An evaluation decorator for computing sexual content on an agentic tool via granite guardian.

        For more details, see :class:`ibm_watsonx_gov.metrics.SexualContentMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator.  Defaults to [ ProfanityMetric() ]

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Create evaluate_sexual_content decorator with default parameters. By default, the metric uses the "input_text" from the graph state as the input.
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_sexual_content
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Create evaluate_sexual_content decorator with thresholds and configuration
                .. code-block:: python

                    metric = SexualContentMetric(thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    config = {"input_fields": ["input"]}
                    configuration = AgenticAIConfiguration(**config)
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_sexual_content(metrics=[metric], configuration=configuration)
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return SexualContentDecorator(api_client=self.api_client,
                                      configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                      metric_results=self.__online_metric_results,
                                      execution_counts=self.__execution_counts,
                                      nodes_being_run=self.__nodes_being_run,
                                      lock=update_lock,
                                      compute_real_time=compute_real_time).evaluate_sexual_content(func, configuration=configuration, metrics=metrics)

    def evaluate_unethical_behavior(self,
                                    func: Optional[Callable] = None,
                                    *,
                                    configuration: Optional[AgenticAIConfiguration] = None,
                                    metrics: list[GenAIMetric] = [],
                                    compute_real_time: Optional[bool] = True,
                                    ) -> dict:
        """
        An evaluation decorator for computing unethical behavior on an agentic tool via granite guardian.

        For more details, see :class:`ibm_watsonx_gov.metrics.UnethicalBehaviorMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator.  Defaults to [ ProfanityMetric() ]

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Create evaluate_unethical_behavior decorator with default parameters. By default, the metric uses the "input_text" from the graph state as the input.
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_unethical_behavior
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Create evaluate_unethical_behavior decorator with thresholds and configuration
                .. code-block:: python

                    metric = UnethicalBehaviorMetric(thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    config = {"input_fields": ["input"]}
                    configuration = AgenticAIConfiguration(**config)
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_unethical_behavior(metrics=[metric], configuration=configuration)
                    def agentic_tool(*args, *kwargs):
                        pass
        """

        return UnethicalBehaviorDecorator(api_client=self.api_client,
                                          configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                          metric_results=self.__online_metric_results,
                                          execution_counts=self.__execution_counts,
                                          nodes_being_run=self.__nodes_being_run,
                                          lock=update_lock,
                                          compute_real_time=compute_real_time).evaluate_unethical_behavior(func, configuration=configuration, metrics=metrics)

    def evaluate_violence(self,
                          func: Optional[Callable] = None,
                          *,
                          configuration: Optional[AgenticAIConfiguration] = None,
                          metrics: list[GenAIMetric] = [],
                          compute_real_time: Optional[bool] = True,
                          ) -> dict:
        """
        An evaluation decorator for computing violence on an agentic tool via granite guardian.

        For more details, see :class:`ibm_watsonx_gov.metrics.ViolenceMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator.  Defaults to [ ProfanityMetric() ]

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Create evaluate_violence decorator with default parameters. By default, the metric uses the "input_text" from the graph state as the input.
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_violence
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Create evaluate_violence decorator with thresholds and configuration
                .. code-block:: python

                    metric = ViolenceMetric(thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    config = {"input_fields": ["input"]}
                    configuration = AgenticAIConfiguration(**config)
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_violence(metrics=[metric], configuration=configuration)
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return ViolenceDecorator(api_client=self.api_client,
                                 configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                 metric_results=self.__online_metric_results,
                                 execution_counts=self.__execution_counts,
                                 nodes_being_run=self.__nodes_being_run,
                                 lock=update_lock,
                                 compute_real_time=compute_real_time).evaluate_violence(func, configuration=configuration, metrics=metrics)

    def evaluate_harm_engagement(self,
                                 func: Optional[Callable] = None,
                                 *,
                                 configuration: Optional[AgenticAIConfiguration] = None,
                                 metrics: list[GenAIMetric] = [],
                                 compute_real_time: Optional[bool] = True,
                                 ) -> dict:
        """
        An evaluation decorator for computing harm engagement on an agentic tool via granite guardian.

        For more details, see :class:`ibm_watsonx_gov.metrics.HarmEngagementMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator.  Defaults to [ ProfanityMetric() ]

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Create evaluate_harm_engagement decorator with default parameters. By default, the metric uses the "input_text" from the graph state as the input.
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_harm_engagement
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Create evaluate_harm_engagement decorator with thresholds and configuration
                .. code-block:: python

                    metric = HarmEngagementMetric(thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    config = {"input_fields": ["input"]}
                    configuration = AgenticAIConfiguration(**config)
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_harm_engagement(metrics=[metric], configuration=configuration)
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return HarmEngagementDecorator(api_client=self.api_client,
                                       configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                       metric_results=self.__online_metric_results,
                                       execution_counts=self.__execution_counts,
                                       nodes_being_run=self.__nodes_being_run,
                                       lock=update_lock,
                                       compute_real_time=compute_real_time).evaluate_harm_engagement(func, configuration=configuration, metrics=metrics)

    def evaluate_evasiveness(self,
                             func: Optional[Callable] = None,
                             *,
                             configuration: Optional[AgenticAIConfiguration] = None,
                             metrics: list[GenAIMetric] = [],
                             compute_real_time: Optional[bool] = True,
                             ) -> dict:
        """
        An evaluation decorator for computing evasiveness on an agentic tool via granite guardian.

        For more details, see :class:`ibm_watsonx_gov.metrics.EvasivenessMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator.  Defaults to [ ProfanityMetric() ]

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Create evaluate_evasiveness decorator with default parameters. By default, the metric uses the "input_text" from the graph state as the input.
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_evasiveness
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Create evaluate_evasiveness decorator with thresholds and configuration
                .. code-block:: python

                    metric = EvasivenessMetric(thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    config = {"input_fields": ["input"]}
                    configuration = AgenticAIConfiguration(**config)
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_evasiveness(metrics=[metric], configuration=configuration)
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return EvasivenessDecorator(api_client=self.api_client,
                                    configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                    metric_results=self.__online_metric_results,
                                    execution_counts=self.__execution_counts,
                                    nodes_being_run=self.__nodes_being_run,
                                    lock=update_lock,
                                    compute_real_time=compute_real_time).evaluate_evasiveness(func, configuration=configuration, metrics=metrics)

    def evaluate_jailbreak(self,
                           func: Optional[Callable] = None,
                           *,
                           configuration: Optional[AgenticAIConfiguration] = None,
                           metrics: list[GenAIMetric] = [],
                           compute_real_time: Optional[bool] = True,
                           ) -> dict:
        """
        An evaluation decorator for computing jailbreak on an agentic tool via granite guardian.

        For more details, see :class:`ibm_watsonx_gov.metrics.JailbreakMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator.  Defaults to [ ProfanityMetric() ]

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Create evaluate_jailbreak decorator with default parameters. By default, the metric uses the "input_text" from the graph state as the input.
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_jailbreak
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Create evaluate_jailbreak decorator with thresholds and configuration
                .. code-block:: python

                    metric = JailbreakMetric(thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    config = {"input_fields": ["input"]}
                    configuration = AgenticAIConfiguration(**config)
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_jailbreak(metrics=[metric], configuration=configuration)
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return JailbreakDecorator(api_client=self.api_client,
                                  configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                  metric_results=self.__online_metric_results,
                                  execution_counts=self.__execution_counts,
                                  nodes_being_run=self.__nodes_being_run,
                                  lock=update_lock,
                                  compute_real_time=compute_real_time).evaluate_jailbreak(func, configuration=configuration, metrics=metrics)

    def evaluate_topic_relevance(self,
                                 func: Optional[Callable] = None,
                                 *,
                                 configuration: Optional[AgenticAIConfiguration] = None,
                                 metrics: list[GenAIMetric],
                                 compute_real_time: Optional[bool] = True,
                                 ) -> dict:
        """
        An evaluation decorator for computing topic relevance on an agentic tool via off-topic detector.

        For more details, see :class:`ibm_watsonx_gov.metrics.TopicRelevanceMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric]): The list of metrics to compute as part of this evaluator.

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Create evaluate_topic_relevance decorator with default parameters. By default, the metric uses the "input_text" from the graph state as the input.
                .. code-block:: python

                    metric = TopicRelevanceMetric(system_prompt="...")
                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_topic_relevance(metrics=[metric])
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Create evaluate_topic_relevance decorator with thresholds and configuration
                .. code-block:: python

                    metric = TopicRelevanceMetric(system_prompt="...", thresholds=MetricThreshold(type="lower_limit", value=0.7))
                    evaluator = AgenticEvaluator()
                    config = {"input_fields": ["input"]}
                    configuration = AgenticAIConfiguration(**config)
                    @evaluator.evaluate_topic_relevance(metrics=[metric], configuration=configuration)
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return TopicRelevanceDecorator(api_client=self.api_client,
                                       configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                       metric_results=self.__online_metric_results,
                                       execution_counts=self.__execution_counts,
                                       nodes_being_run=self.__nodes_being_run,
                                       lock=update_lock,
                                       compute_real_time=compute_real_time).evaluate_topic_relevance(func, configuration=configuration, metrics=metrics)

    def evaluate_answer_quality(self,
                                func: Optional[Callable] = None,
                                *,
                                configuration: Optional[AgenticAIConfiguration] = None,
                                metrics: list[GenAIMetric] = [],
                                compute_real_time: Optional[bool] = True
                                ) -> dict:
        """
        An evaluation decorator for computing answer quality metrics on an agentic tool.
        Answer Quality metrics include Answer Relevance, Faithfulness, Answer Similarity, Unsuccessful Requests

        For more details, see :class:`ibm_watsonx_gov.metrics.AnswerRelevanceMetric`, :class:`ibm_watsonx_gov.metrics.FaithfulnessMetric`, 
        :class:`ibm_watsonx_gov.metrics.UnsuccessfulRequestsMetric`, see :class:`ibm_watsonx_gov.metrics.AnswerSimilarityMetric`,

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to MetricGroup.ANSWER_QUALITY.get_metrics().

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_answer_quality
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods for some of the metrics in the group
                .. code-block:: python

                    metric_1 = FaithfulnessMetric(thresholds=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = AnswerRelevanceMetric(method="token_recall", thresholds=MetricThreshold(type="lower_limit", value=0.5))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_answer_quality(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return AnswerQualityDecorator(api_client=self.api_client,
                                      configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                      metric_results=self.__online_metric_results,
                                      execution_counts=self.__execution_counts,
                                      nodes_being_run=self.__nodes_being_run,
                                      lock=update_lock,
                                      compute_real_time=compute_real_time).evaluate_answer_quality(func, configuration=configuration, metrics=metrics)

    def evaluate_content_safety(self,
                                func: Optional[Callable] = None,
                                *,
                                configuration: Optional[AgenticAIConfiguration] = None,
                                metrics: list[GenAIMetric] = [],
                                compute_real_time: Optional[bool] = True
                                ) -> dict:
        """
        An evaluation decorator for computing content safety metrics on an agentic tool.
        Content Safety metrics include HAP, PII, Evasiveness, Harm, HarmEngagement, Jailbreak, Profanity, SexualContent, Social Bias, UnethicalBehavior and  Violence

        For more details, see :class:`ibm_watsonx_gov.metrics.HAPMetric`, 
        :class:`ibm_watsonx_gov.metrics.PIIMetric`, :class:`ibm_watsonx_gov.metrics.EvasivenessMetric`, :class:`ibm_watsonx_gov.metrics.HarmMetric`, 
        :class:`ibm_watsonx_gov.metrics.HarmEngagementMetric`, :class:`ibm_watsonx_gov.metrics.JailbreakMetric`, :class:`ibm_watsonx_gov.metrics.ProfanityMetric`,
        :class:`ibm_watsonx_gov.metrics.SexualContentMetric`, :class:`ibm_watsonx_gov.metrics.SocialBiasMetric`, :class:`ibm_watsonx_gov.metrics.UnethicalBehaviorMetric`,
        :class:`ibm_watsonx_gov.metrics.ViolenceMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to MetricGroup.CONTENT_SAFETY.get_metrics().

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_content_safety
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods for some of the metrics in the group
                .. code-block:: python

                    metric_1 = PIIMetric(thresholds=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = HAPMetric(thresholds=MetricThreshold(type="lower_limit", value=0.5))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_content_safety(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return ContentSafetyDecorator(api_client=self.api_client,
                                      configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                      metric_results=self.__online_metric_results,
                                      execution_counts=self.__execution_counts,
                                      nodes_being_run=self.__nodes_being_run,
                                      lock=update_lock,
                                      compute_real_time=compute_real_time).evaluate_content_safety(func, configuration=configuration, metrics=metrics)

    def evaluate_retrieval_quality(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [],
                                   compute_real_time: Optional[bool] = True
                                   ) -> dict:
        """
        An evaluation decorator for computing retrieval quality metrics on an agentic tool.
        Retrieval Quality metrics include Context Relevance, Retrieval Precision, Average Precision, Hit Rate, Reciprocal Rank, NDCG

        For more details, see :class:`ibm_watsonx_gov.metrics.ContextRelevanceMetric`, :class:`ibm_watsonx_gov.metrics.RetrievalPrecisionMetric`, 
        :class:`ibm_watsonx_gov.metrics.AveragePrecisionMetric`, :class:`ibm_watsonx_gov.metrics.ReciprocalRankMetric`, :class:`ibm_watsonx_gov.metrics.HitRateMetric`,
        :class:`ibm_watsonx_gov.metrics.NDCGMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to MetricGroup.RETRIEVAL_QUALITY.get_metrics().

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_retrieval_quality
                    def agentic_tool(*args, *kwargs):
                        pass

            2. Usage with different thresholds and methods for some of the metrics in the group
                .. code-block:: python

                    metric_1 = NDCGMetric(threshold=MetricThreshold(type="lower_limit", value=0.5))
                    metric_2 = ContextRelevanceMetric(method="sentence_bert_mini_lm", threshold=MetricThreshold(type="lower_limit", value=0.6))

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_retrieval_quality(metrics=[metric_1, metric_2])
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return RetrievalQualityDecorator(api_client=self.api_client,
                                         configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                         metric_results=self.__online_metric_results,
                                         execution_counts=self.__execution_counts,
                                         nodes_being_run=self.__nodes_being_run,
                                         lock=update_lock,
                                         compute_real_time=compute_real_time).evaluate_retrieval_quality(func, configuration=configuration, metrics=metrics)

    def evaluate_text_grade_level(self,
                                  func: Optional[Callable] = None,
                                  *,
                                  configuration: Optional[AgenticAIConfiguration] = None,
                                  metrics: list[GenAIMetric] = [],
                                  compute_real_time: Optional[bool] = True,
                                  ) -> dict:
        """
        An evaluation decorator for computing text grade level metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.TextGradeLevelMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [TextGradeLevelMetric()].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_text_grade_level
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return TextGradeLevelDecorator(api_client=self.api_client,
                                       configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                       metric_results=self.__online_metric_results,
                                       execution_counts=self.__execution_counts,
                                       nodes_being_run=self.__nodes_being_run,
                                       lock=update_lock,
                                       compute_real_time=compute_real_time).evaluate_text_grade_level(func, configuration=configuration, metrics=metrics)

    def evaluate_text_reading_ease(self,
                                   func: Optional[Callable] = None,
                                   *,
                                   configuration: Optional[AgenticAIConfiguration] = None,
                                   metrics: list[GenAIMetric] = [],
                                   compute_real_time: Optional[bool] = True,
                                   ) -> dict:
        """
        An evaluation decorator for computing text reading ease ease metric on an agentic tool.

        For more details, see :class:`ibm_watsonx_gov.metrics.TextReadingEaseMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to [TextReadingEaseMetric()].

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_text_reading_ease
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return TextReadingEaseDecorator(api_client=self.api_client,
                                        configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                        metric_results=self.__online_metric_results,
                                        execution_counts=self.__execution_counts,
                                        nodes_being_run=self.__nodes_being_run,
                                        lock=update_lock,
                                        compute_real_time=compute_real_time).evaluate_text_reading_ease(func, configuration=configuration, metrics=metrics)

    def evaluate_readability(self,
                             func: Optional[Callable] = None,
                             *,
                             configuration: Optional[AgenticAIConfiguration] = None,
                             metrics: list[GenAIMetric] = [],
                             compute_real_time: Optional[bool] = True
                             ) -> dict:
        """
        An evaluation decorator for computing answer readability metrics on an agentic tool.
        Readability metrics include TextReadingEaseMetric and TextGradeLevelMetric

        For more details, see :class:`ibm_watsonx_gov.metrics.TextReadingEaseMetric`, :class:`ibm_watsonx_gov.metrics.TextGradeLevelMetric`

        Args:
            func (Optional[Callable], optional): The tool on which the metric is to be computed.
            configuration (Optional[AgenticAIConfiguration], optional): The configuration specific to this evaluator. Defaults to None.
            metrics (list[GenAIMetric], optional): The list of metrics to compute as part of this evaluator. Defaults to MetricGroup.READABILITY.get_metrics().

        Raises:
            Exception: If there is any error while evaluation.

        Returns:
            dict: The result of the wrapped tool.

        Example:
            1. Basic usage
                .. code-block:: python

                    evaluator = AgenticEvaluator()
                    @evaluator.evaluate_readability
                    def agentic_tool(*args, *kwargs):
                        pass
        """
        return ReadabilityDecorator(api_client=self.api_client,
                                    configuration=self.agentic_app.metrics_configuration.configuration if self.agentic_app else None,
                                    metric_results=self.__online_metric_results,
                                    execution_counts=self.__execution_counts,
                                    nodes_being_run=self.__nodes_being_run,
                                    lock=update_lock,
                                    compute_real_time=compute_real_time).evaluate_readability(func, configuration=configuration, metrics=metrics)
