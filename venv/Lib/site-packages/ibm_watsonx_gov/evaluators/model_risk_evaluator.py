
# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------


from IPython.display import display
from pydantic import Field, PrivateAttr
from typing_extensions import Annotated

from ibm_watsonx_gov.clients.api_client import APIClient
from ibm_watsonx_gov.config.model_risk_configuration import \
    ModelRiskConfiguration
from ibm_watsonx_gov.entities.model_risk_result import ModelRiskResult
from ibm_watsonx_gov.evaluators.base_evaluator import BaseEvaluator
from ibm_watsonx_gov.utils.segment_batch_manager import SegmentBatchManager


class ModelRiskEvaluator(BaseEvaluator):
    """
    The class to evaluate the foundational model risk and display the results.

    Example:
        1. Basic usage
            .. code-block:: python

                configuration = ModelRiskConfiguration(
                    model_details=model_details,
                    risk_dimensions=risk_dimensions,
                    max_sample_size=max_sample_size,
                    pdf_report_output_path=pdf_report_output_path
                )
                wxgov_client = APIClient(credentials=Credentials(api_key=""))
                evaluator = ModelRiskEvaluator(
                    configuration=config, api_client=wxgov_client)

                result = evaluator.evaluate()

                # Get the results in the required format
                result.to_json()

                # Display the results
                evaluator.display_table()
                evaluator.download_model_risk_report()
    """
    configuration: Annotated[ModelRiskConfiguration,
                             Field(name="The configuration for model risk evaluation.")]
    api_client: Annotated[APIClient | None,
                          Field(name="The IBM watsonx.governance client.", default=None)]

    _result: Annotated[ModelRiskResult | None,
                       PrivateAttr(default=None)]

    def evaluate(self) -> ModelRiskResult:
        """
        Evaluates the risk of a Foundation model.

        Returns:
            ModelRiskResult: The result of the model risk evaluation.
        """
        from ibm_watsonx_gov.evaluators.impl.evaluate_model_risk_impl import \
            _evaluate_model_risk

        self._result = _evaluate_model_risk(
            self.configuration,
            self.api_client,
        )

        # Adding segment event
        # segment_manager = SegmentBatchManager()
        # segment_manager.add_event_to_shared_list(
        #     self.api_client.wos_client, properties={"objectType": "Evaluate Model Risk"})
        return self._result

    def display_table(self):
        for risk in self._result.risks:
            print(f"\n--- Risk: {risk.name} ---")
            for benchmark in risk.benchmarks:
                print(f"Benchmark: {benchmark.name}")
                display(benchmark.get_metric_df())

    def download_model_risk_report(self):
        """
        Downloads the model risk report and returns the download link.
        """
        from ibm_wos_utils.joblib.utils.notebook_utils import \
            create_download_link_for_file

        return create_download_link_for_file(
            self._result.output_file_path)
