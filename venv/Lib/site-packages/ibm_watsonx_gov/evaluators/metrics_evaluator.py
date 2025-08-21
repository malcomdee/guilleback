# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import pandas as pd
from pydantic import Field, PrivateAttr
from typing_extensions import Annotated

from ibm_watsonx_gov.config.gen_ai_configuration import GenAIConfiguration
from ibm_watsonx_gov.entities.enums import MetricGroup
from ibm_watsonx_gov.entities.evaluation_result import MetricsEvaluationResult
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.evaluators.base_evaluator import BaseEvaluator


class MetricsEvaluator(BaseEvaluator):
    """
    The class to evaluate the metrics and display the results.

    Examples:
        1. Evaluate metrics by passing data as a dataframe and default configuration
            .. code-block:: python

                os.environ["WATSONX_APIKEY"] = "..."

                evaluator = MetricsEvaluator()
                df = pd.read_csv("")
                metrics = [AnswerSimilarityMetric()]

                result = evaluator.evaluate(data=df, metrics=metrics)

        2. Evaluate metrics by passing data as a json and default configuration
            .. code-block:: python

                os.environ["WATSONX_APIKEY"] = "..."

                evaluator = MetricsEvaluator()
                json_data = {"input_text": "..."}
                metrics=[HAPMetric()]

                result = evaluator.evaluate(data=json_data, metrics=metrics)

        3. Evaluate metrics by passing configuration and api_client
            .. code-block:: python

                config = GenAIConfiguration(input_fields=["question"],
                                    context_fields=["context"],
                                    output_fields=["generated_text"],
                                    reference_fields=["reference_answer"])
                wxgov_client = APIClient(credentials=Credentials(api_key=""))
                evaluator = MetricsEvaluator(configuration=config, api_client=wxgov_client)
                df = pd.read_csv("")
                metrics = [AnswerSimilarityMetric()]

                result = evaluator.evaluate(data=df, metrics=metrics)

        4. Evaluate metrics by passing metric groups
            .. code-block:: python

                os.environ["WATSONX_APIKEY"] = "..."

                evaluator = MetricsEvaluator()
                df = pd.read_csv("")
                metrics = [AnswerSimilarityMetric()]
                metric_groups = [MetricGroup.RETRIEVAL_QUALITY]

                result = evaluator.evaluate(data=df, metrics=metrics, metric_groups=metric_groups)

        5. Display the results
            .. code-block:: python

                # Get the results in the required format from the output of the evaluate method
                result.to_json()
                result.to_df()
                result.to_dict()

                # Display the results
                evaluator.display_table()
                evaluator.display_insights()



    """
    configuration: Annotated[GenAIConfiguration,
                             Field(title="Generative AI Configuration",
                                   description="The configuration for metrics evaluation.",
                                   default=GenAIConfiguration())]
    _data: Annotated[pd.DataFrame | dict | None,
                     PrivateAttr(default=None)]
    _metrics: Annotated[list[GenAIMetric] | None,
                        PrivateAttr(default=None)]
    _metric_groups: Annotated[list[MetricGroup] | None,
                              PrivateAttr(default=None)]
    _result: Annotated[MetricsEvaluationResult | None,
                       PrivateAttr(default=None)]

    def evaluate(
            self,
            data: pd.DataFrame | dict,
            metrics: list[GenAIMetric] = [],
            metric_groups: list[MetricGroup] = [],
            **kwargs) -> MetricsEvaluationResult:
        """
        Evaluate the metrics for the given data.

        Args:
            data (pd.DataFrame | dict): The data to be evaluated.
            metrics (list[GenAIMetric], optional): The metrics to be evaluated. Defaults to [].
            metric_groups (list[MetricGroup], optional): The metric groups to be evaluated. Defaults to [].
            **kwargs: Additional keyword arguments.

        Returns:
            MetricsEvaluationResult: The result of the evaluation.
        """
        from ibm_watsonx_gov.evaluators.impl.evaluate_metrics_impl import (
            _evaluate_metrics, _resolve_metric_dependencies)
        self._data = data
        self._metrics = _resolve_metric_dependencies(
            metrics=metrics, metric_groups=metric_groups)
        self._metric_groups = metric_groups,
        self._result: MetricsEvaluationResult = _evaluate_metrics(configuration=self.configuration,
                                                                  data=data,
                                                                  metrics=self._metrics,
                                                                  api_client=self.api_client,
                                                                  ** kwargs)
        return self._result

    def display_table(self):
        """
        Display the metrics result as a table.
        """
        try:
            from ibm_watsonx_gov.visualizations import display_table
        except:
            ImportError(
                "Please install the required dependencies 'ibm-watsonx-gov[visualization]' to display the results.")
        display_table(self._result.to_df(data=self._data))

    def display_insights(self):
        """
        Display the metrics result in a venn diagram based on the metrics threshold.
        """
        try:
            from ibm_watsonx_gov.visualizations import ModelInsights
        except:
            ImportError(
                "Please install the required dependencies 'ibm-watsonx-gov[visualization]' to display the results.")
        model_insights = ModelInsights(
            configuration=self.configuration, metrics=self._metrics)
        model_insights.display_metrics(
            metrics_result=self._result.to_df(data=self._data))
