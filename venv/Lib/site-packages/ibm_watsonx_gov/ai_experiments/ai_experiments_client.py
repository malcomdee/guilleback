# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import requests

from ibm_watsonx_gov.ai_experiments.utils.ai_experiment_utils import \
    AIExperimentUtils
from ibm_watsonx_gov.clients.api_client import APIClient
from ibm_watsonx_gov.entities.ai_evaluation import (AIEvaluationAsset,
                                                    EvaluationConfig)
from ibm_watsonx_gov.entities.ai_experiment import (AIExperiment,
                                                    AIExperimentRun)
from ibm_watsonx_gov.utils.gov_sdk_logger import GovSDKLogger
from ibm_watsonx_gov.utils.python_utils import get
from ibm_watsonx_gov.utils.rest_util import RestUtil
from ibm_watsonx_gov.utils.url_mapping import WOS_URL_MAPPING


class AIExperimentsClient:

    def __init__(
        self, api_client: APIClient, project_id: str = None, space_id: str = None
    ) -> None:
        """
        Initialize the AIExperimentsClient class.

        Args:
            - api_client: The watsonx.governance client, used for authentication.
            - project_id: The project id.
            - space_id: The space id.

        Example:
        -------
        Initialize AIExperimentsClient:
            .. code-block:: python

            # Initialize the API client
            api_client = APIClient(credentials=Credentials(api_key="", url="wos_url"))

            # Create the AI Experiment client
            ai_experiment_client = AIExperimentClient(api_client=api_client, project_id="your_project_id")
        """
        self.logger = GovSDKLogger.get_logger(__name__)
        if not api_client:
            api_client = APIClient()
        self.api_client = api_client
        self.dataplatform_url = api_client.credentials.url
        # Fetching URL map to get dataplatform url for cloud environments
        if not self.api_client.is_cpd:
            url_map = WOS_URL_MAPPING.get(api_client.credentials.url)
            self.dataplatform_url = url_map.dai_url

        self.ai_experiment_url = (
            f"{self.dataplatform_url}/v1/aigov/factsheet/ai_experiments"
        )
        self.project_id = project_id
        self.verify_ssl = not self.api_client.credentials.disable_ssl
        # container checks
        self.__container_checks(project_id, space_id)

    def create(self, experiment_details: AIExperiment) -> AIExperiment:
        """
        Creates AI experiment asset with specified details

        Args:
            - experiment_details: The instance of AIExperiment having details of the experiment to be created.

        Returns: An instance of AIExperiment.

        Examples:
        ---------
        Create an AI Experiment:
            .. code-block:: python

            # Initialize the API client with credentials
            api_client = APIClient(credentials=Credentials(api_key="", url=""))

            # Create the AI Experiment client with your project ID
            ai_experiment_client = AIExperimentClient(api_client=api_client, project_id="your_project_id")

            # Create the AIExperiment instance
            ai_experiment = AIExperiment(name="", description="", component_type="agent", component_name="")

            ai_experiment_asset = ai_experiment_client.create(ai_experiment)
        """

        ai_experiment_payload = experiment_details.to_json()

        response = RestUtil.request_with_retry().post(
            self.ai_experiment_url,
            json=ai_experiment_payload,
            headers=self.__get_headers(),
            params=self.container_params,
            verify=self.verify_ssl
        )

        if not response.ok:
            message = f"Error occurred while creating AI experiment asset. Status code: {response.status_code}, Error: {response.text}"
            self.logger.error(message)
            raise Exception(message)

        response_json = response.json()

        ai_experiment = self.__map_ai_experiment(response_json)

        ai_experiment_id = response_json.get("asset_id")
        print(f"Created AI experiment asset with id {ai_experiment_id}.\n")
        return ai_experiment

    def get(self, ai_experiment_id: str) -> AIExperiment:
        """
        Retrieves AI experiment asset details
        Args:
            - ai_experiment_id: The ID of AI experiment asset.
        Returns: An instance of AIExperiment.
        """
        ai_experiment_url = f"{self.ai_experiment_url}/{ai_experiment_id}"
        response = RestUtil.request_with_retry().get(
            ai_experiment_url,
            headers=self.__get_headers(),
            params=self.container_params,
            verify=self.verify_ssl
        )

        if not response.ok:
            message = f"Error occurred while retrieving AI experiment asset. Status code: {response.status_code}, Error: {response.text}"
            self.logger.error(message)
            raise Exception(message)

        response_json = response.json()

        asset_details = response_json.pop("asset_details", {})
        ai_experiment_runs = response_json.pop("ai_experiment_runs", [])

        ai_experiment_response = {
            **response_json,
            **asset_details,
            "runs": ai_experiment_runs,
        }

        ai_experiment = AIExperiment(**ai_experiment_response)

        print(f"Retrieved AI experiment asset {ai_experiment_id}.\n")
        return ai_experiment

    def search(self, ai_experiment_name: str) -> AIExperiment:
        """
        Searches AI experiment with specified name
        Args:
            - ai_experiment_name: The name of AI experiment to be searched.
        Returns: An instance of AIExperiment.
        """
        ai_experiment = None
        # Search using asset search API
        search_url = f"{self.dataplatform_url}/v2/asset_types/ai_experiment/search"

        search_payload = {
            "query": f"asset.name:\"{ai_experiment_name}\"",
            "sort": "asset.name<string>"
        }

        response = RestUtil.request_with_retry().post(
            search_url,
            json=search_payload,
            headers=self.__get_headers(),
            params=self.container_params,
            verify=self.verify_ssl
        )
        if not response.ok:
            message = f"Error occurred while searching AI experiment with name {ai_experiment_name}. Status code: {response.status_code}, Error: {response.text}"
            self.logger.error(message)
            raise Exception(message)

        response_json = response.json()
        if response_json.get("results"):
            ai_experiment_details = response_json.get("results")[0]
            ai_experiment = AIExperiment(
                **ai_experiment_details.get("metadata"))
            print(
                f"Using existing AI experiment with id {ai_experiment.asset_id}.\n")

        return ai_experiment

    def update(
        self,
        ai_experiment_id: str,
        experiment_run_details: AIExperimentRun,
        evaluation_results=None,
        track_notebook=False,
    ) -> AIExperiment:
        """
        Updates AI experiment asset details, with the given experiment run details.
        Args:
            - ai_experiment_id: The ID of AI experiment asset to be updated
            - experiment_run_details : An instance of AIExperimentRun, payload to create attachment
            - evaluation_result:(DataFrame|ToolMetricResult) The content of attachment to be uploaded as file (Optional)
            - track_notebook:(bool) If set to True the notebook will be stored as attachment
        Returns: The updated AI experiment asset details

        Examples:
        -----------
        Updating a AI Experiment with the evaluation results:
            .. code-block:: python

                # Initialize the API client with credentials
                api_client = APIClient(credentials=Credentials(api_key="", url="wos_url"))

                # Create the AI Experiment client with your project ID
                ai_experiment_client = AIExperimentClient(api_client=api_client, project_id="your_project_id")

                # Define ai_experiment_runs
                experiment_run_details = AIExperimentRun(run_id=str(uuid.uuid4()), run_name="", test_data={}, node=[])

                # evaluation_result will be an instnace of ToolMetricResult or DataFrame

                # Update the AI experiment asset with run results
                updated_ai_experiment_details = ai_experiment_client.update(
                    ai_experiment_asset_id="",
                    experiment_run_details=experiment_run_details,
                    evaluation_result=run_result
                )

        """
        ai_experiment_url = f"{self.ai_experiment_url}/{ai_experiment_id}"

        attachment_id = None
        notebook_attachment_id = None
        # If evaluation_result is not None, this method will upload the result and create an attachment for it.
        if evaluation_results:
            # Convert the evaluator result into attachment format.
            result_attachment, total_records = AIExperimentUtils.construct_result_attachment_payload(
                evaluation_results, experiment_run_details.nodes)
            attachment_id = self.__store_experiment_run_result(
                ai_experiment_id, experiment_run_details, result_attachment
            )
        if track_notebook:
            try:
                notebook_file_path = Path(experiment_run_details.source_url)
                notebook = AIExperimentsClient.__process_notebook(
                    notebook_file_path)
                notebook_payload = {
                    "asset_type": "ai_experiment",
                    "name": f"AI experiment notebook for {experiment_run_details.run_id}",
                    "description": f"AI experiment notebook for {experiment_run_details.run_name}, notebook name: {experiment_run_details.source_name}",
                    "mime": "json/txt",
                    "user_data": {},
                }
                notebook_attachment_id = self.__create_asset_attachment(
                    ai_experiment_id, notebook_payload, notebook
                ).get("attachment_id")
            except Exception as e:
                message = f"Failed to track the notebook for experiment run {experiment_run_details.run_id}. Error: {str(e)}"
                self.logger.error(message)
                raise Exception(message)

        test_data = experiment_run_details.test_data or {}
        test_data["total_rows"] = total_records
        # Updating run details in the AI experiment asset
        update_payload = {
            "run_id": experiment_run_details.run_id,
            "run_name": experiment_run_details.run_name,
            "test_data": test_data,
            "nodes": [node.to_json() for node in experiment_run_details.nodes] or [],
            "attachment_id": attachment_id,
            "source_url": experiment_run_details.source_url,
            "source_name": experiment_run_details.source_name,
            "duration": experiment_run_details.duration,
            "custom_tags": experiment_run_details.custom_tags,
            "properties": {
                "notebook_attachment_id": notebook_attachment_id,
            }
        }
        print(
            f"Updated experiment run details for run {experiment_run_details.run_name} of AI experiment {ai_experiment_id}.\n"
        )

        response = RestUtil.request_with_retry().put(
            ai_experiment_url,
            json=update_payload,
            headers=self.__get_headers(),
            params=self.container_params,
            verify=self.verify_ssl
        )

        if not response.ok:
            message = f"Error occurred while updating AI experiment asset. Status code: {response.status_code}, Error: {response.text}"
            self.logger.error(message)
            raise Exception(message)

        response_json = response.json()

        ai_experiment = AIExperiment(**response_json)

        print(f"Updated AI experiment asset {ai_experiment_id}.\n")
        return ai_experiment

    def create_ai_evaluation_asset(
        self,
        ai_experiment_ids: List[str] = None,
        ai_experiment_runs: Dict[str, List[AIExperimentRun]] = None,
        ai_evaluation_details: AIEvaluationAsset = None,
    ) -> AIEvaluationAsset:
        """
        Creates an AI Evaluation asset from either experiment IDs or experiment run mappings.

        Args:
            ai_experiment_ids (List[str], optional):
                A list of AI experiment IDs for which the evaluation asset should be created.
            ai_experiment_runs (Dict[str, List[AIExperimentRun]], optional):
                A list of dictionaries where each dictionary maps an experiment ID (str)
                to an AIExperimentRun object.
            ai_evaluation_details (AIEvaluationAsset, optional):
                An instance of AIEvaluationAsset having details (name, description and metrics configuration)
        Returns:
            An instance of AIEvaluationAsset.

        Note:
            Only one of `ai_experiment_ids` or `ai_experiment_runs` should be provided.

        Examples:
        -----------
        Comparing a list of AI experiments:
            .. code-block:: python

                # Initialize the API client with credentials
                api_client = APIClient(credentials=Credentials(api_key="", url="wos_url"))

                # Create the AI Experiment client with your project ID
                ai_experiment_client = AIExperimentClient(api_client=api_client, project_id="your_project_id")

                # Create AI Experiments
                ai_experiment = ai_experiment_client.create(name="",description="",component_type="",component_name="")

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
                # Link for AIEvaluationAsset
                response.href
        """

        if ai_experiment_ids and ai_experiment_runs:
            message = f"Both 'ai_experiment_ids' and 'ai_experiment_runs' cannot be passed together."
            self.logger.error(message)
            raise Exception(message)

        start_time = time.time()
        time_str = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(start_time))

        evaluation_assets = []
        total_runs = 0

        if ai_experiment_ids:
            for experiment_id in ai_experiment_ids:
                ai_experiment = self.get(ai_experiment_id=experiment_id)
                experiment_name = ai_experiment.name
                runs_data = ai_experiment.runs
                for run in runs_data:
                    evaluation_assets.append(
                        self.__build_evaluation_asset(
                            experiment_id, experiment_name, run.to_json()
                        )
                    )

        elif ai_experiment_runs:
            for experiment_id, runs in ai_experiment_runs.items():
                ai_experiment = self.get(ai_experiment_id=experiment_id)
                experiment_name = ai_experiment.name
                if not runs:
                    runs = ai_experiment.runs
                for run in runs:
                    # If specified run details does not contain attachment_id, get it from experiment asset
                    # incresing the total runs count to keep track of runs across experiments
                    total_runs += 1
                    if not run.attachment_id:
                        for run_info in ai_experiment.runs:
                            if run_info.run_id == run.run_id:
                                run = run_info
                                break

                    run_data = run.to_json() if hasattr(run, "to_json") else {}
                    evaluation_assets.append(
                        self.__build_evaluation_asset(
                            experiment_id, experiment_name, run_data
                        )
                    )

            if total_runs > 20 or total_runs < 2:
                message = f"Error occurred while creating AI evaluation asset. Error: The number of runs across experiments should be minimum 2 and maximum 20."
                self.logger.error(message)
                raise Exception(message)

        # setting the default valve of monitors, name and description
        monitors = {"agentic_ai_quality": {
            "parameters": {"metrics_configuration": {}}}}
        evaluation_asset_name = f"AI Agents evaluation created at {time_str}"
        evaluation_asset_description = "AI Agents evaluation"
        # updating the monitors, name and description if provided
        if ai_evaluation_details:
            monitors = ai_evaluation_details.evaluation_configuration.monitors if ai_evaluation_details.evaluation_configuration.monitors != {} else monitors
            evaluation_asset_name = ai_evaluation_details.name if ai_evaluation_details.name != "" else evaluation_asset_name
            evaluation_asset_description = ai_evaluation_details.description if ai_evaluation_details.description != "" else evaluation_asset_description

        payload = {
            "operational_space_id": "development",
            "name": evaluation_asset_name,
            "description": evaluation_asset_description,
            "evaluation_asset_type": "ai_experiment",
            "input_data_type": "unstructured_text",
            "evaluation_run": {
                "monitors": monitors,
                "evaluation_assets": evaluation_assets,
            },
        }

        ai_evaluation_url = f"{self.dataplatform_url}/v1/aigov/factsheet/ai_evaluations"

        response = RestUtil.request_with_retry().post(
            ai_evaluation_url,
            json=payload,
            headers=self.__get_headers(),
            params=self.container_params,
            verify=self.verify_ssl
        )

        if not response.ok:
            message = f"Error occurred while creating AI Evaluation asset. Status code: {response.status_code}, Error: {response.text}"
            self.logger.error(message)
            raise Exception(message)

        response_json = response.json()
        ai_evaluation_asset_id = get(response_json, "asset_id")

        ai_evaluation_asset = self.__map_post_response_to_ai_evaluation_asset(
            response_json)

        print(f"Created AI Evaluation asset with id {ai_evaluation_asset_id}.")

        return ai_evaluation_asset

    def get_ai_evaluation_asset(self, ai_evaluation_asset_id: str) -> AIEvaluationAsset:
        """
        Return an instance of the AIEvaluation with the given id.

        Args:
            - ai_evaluation_asset_id: The asset id of the AI Evaluation asset.
        Return:
            An instance of AIEvaluationAsset with the given asset id.
        """

        ai_evaluation_asset_url = f"{self.dataplatform_url}/v1/aigov/factsheet/ai_evaluations/{ai_evaluation_asset_id}"

        response = RestUtil.request_with_retry().get(
            ai_evaluation_asset_url,
            headers=self.__get_headers(),
            params=self.container_params,
            verify=self.verify_ssl
        )

        if not response.ok:
            message = f"Error occurred while retriving AI Evaluation asset. Status code: {response.status_code}, Error: {response.text}"
            self.logger.error(message)
            raise Exception(message)

        response_json = response.json()

        ai_evaluation_asset = AIEvaluationAsset(**response_json)

        print(
            f"Retrieved AI Evaluation asset with id {ai_evaluation_asset_id}.\n")
        return ai_evaluation_asset

    def get_ai_evaluation_asset_href(self, ai_evaluation_asset: AIEvaluationAsset) -> str:
        """
        Returns the URL of Evaluation studio UI for the given AI evaluation asset.

        Args:
            - ai_evaluation_asset: The AI Evaluation asset details.
        Return:
            URL of Evaluation studio UI
        """
        ai_evaluation_asset_href = f"{self.dataplatform_url.replace('api.', '')}/aiopenscale/studioPage?"\
            f"container_type={ai_evaluation_asset.container_type}&container_id={ai_evaluation_asset.container_id}&asset_id={ai_evaluation_asset.asset_id}&tearsheet_mode=true"

        print(
            f"AI Evaluation can be viewed in Evaluation Studio UI at URL: {ai_evaluation_asset_href}\n")
        return ai_evaluation_asset_href

    def list_experiments(self) -> List[AIExperiment]:
        """
        List all AI Experiments under selected project.

        Returns: List of AIExperiment instances.
        """
        # Search using asset search API
        search_url = f"{self.dataplatform_url}/v2/asset_types/ai_experiment/search"

        search_payload = {"query": "*:*"}

        response = RestUtil.request_with_retry().post(
            search_url, json=search_payload,
            headers=self.__get_headers(),
            params=self.container_params,
            verify=self.verify_ssl
        )

        if not response.ok:
            message = f"Error occurred while searching AI experiments for project_id {self.project_id}. Status code: {response.status_code}, Error: {response.text}"
            self.logger.error(message)
            raise Exception(message)

        response_json = response.json()
        total_ai_experiments = get(response_json, "total_rows")

        result = []
        if total_ai_experiments > 0:
            experiments = get(response_json, "results")
            for experiment in experiments:
                result.append(self.__map_ai_experiment(experiment))
        print(
            f"Found {total_ai_experiments} AI Experiment in project with id {self.project_id}.\n")
        return result

    def list_experiment_runs(self, ai_experiment_id) -> List[AIExperimentRun]:
        """
        List all ai_experiment_runs for a given ai_experiment_id in a project.

        Args: 
            -ai_experiment_id: The ID of ai experiment asset.
        Return: List of AIExperimentRun instances.
        """

        ai_experiment = self.get(ai_experiment_id=ai_experiment_id)

        ai_experiment_runs = ai_experiment.runs

        print(
            f"Found {len(ai_experiment_runs)} runs for given ai_experiment with id {ai_experiment_id}.\n")
        return ai_experiment_runs

    def __build_evaluation_asset(
        self, experiment_id: str, experiment_name: str, run_data: dict
    ) -> dict:
        """
        Helper method to construct a single evaluation asset dictionary.

        Args:
            experiment_id (str): The ID of the experiment.
            experiment_name (str): The name of the experiment.
            run_data (dict): Serialized data from the experiment run.

        Returns:
            dict: A complete evaluation asset dictionary.
        """
        return {
            "id": experiment_id,
            "name": experiment_name,
            "container_type": self.container_type,
            "container_id": self.container_id,
            **run_data,
        }

    def __store_experiment_run_result(
        self,
        ai_experiment_id: str,
        experiment_run_details: AIExperimentRun,
        evaluation_result,
    ) -> dict:
        """
        Stores evaluation result for an experiment run
        1. Create attachment for storing the evaluation result
        2. Update AI experiment with run details and corresponding attachment_id
        Args:
            - ai_experiment_id: The ID of AI experiment for which run result is to be stored
            - experiment_run_details: An instance of AIExperimentRun, payload to create attachment
            - evaluation_result: The content of attachment to be uploaded as file
        Returns: The attachment details.
        """
        run_id = experiment_run_details.run_id
        run_name = experiment_run_details.run_name

        print(
            f"\nStoring evaluation result for experiment run {run_id} of AI experiment {ai_experiment_id}.\n")

        # Creating attachment for AI experiment asset to store run result
        attachment_payload = {
            "asset_type": "ai_experiment",
            "name": f"AI experiment run result for {run_name}",
            "description": f"AI experiment run result for {run_name}",
            "mime": "json/txt",
            "user_data": {},
        }
        attachment_details = self.__create_asset_attachment(
            ai_experiment_id, attachment_payload, evaluation_result
        )
        attachment_id = attachment_details.get("attachment_id")

        return attachment_id

    def __create_asset_attachment(
        self, asset_id: str, attachment_payload: dict, attachment_content
    ) -> dict:
        """
        Creates asset attachment for specified asset as a file containing the attachment_content

        Args:
            - asset_id: The ID of asset for which attachment is to be created
            - attachment_payload: The payload to create attachment
            - attachment_content: The content of attachment to be uploaded as file
        Returns: The attachment details.
        """

        start_time = time.time()
        print(f"Creating attachment for asset {asset_id}.\n")

        # Building the attachment URL
        attachments_url = f"{self.dataplatform_url}/v2/assets/{asset_id}/attachments"

        # Creating the attachment
        response = RestUtil.request_with_retry().post(
            attachments_url,
            json=attachment_payload,
            headers=self.__get_headers(),
            params=self.container_params,
            verify=self.verify_ssl
        )

        if not response.ok:
            message = f"Failed to create attachment for asset {asset_id}. Status code: {response.status_code}, Error: {response.text}"
            self.logger.error(message)
            raise Exception(message)

        attachment_details = json.loads(response.text)

        # Fetch the attachment_id and upload URL from the details
        attachment_id = attachment_details.get("attachment_id")
        upload_url = attachment_details.get("url1")

        # Upload the attachment content as a file
        # In case of CPD, the attachment is uploaded to asset_files WI #https://github.ibm.com/aiopenscale/tracker/issues/51158
        if self.api_client.is_cpd:
            upload_url = f"{self.dataplatform_url}/{upload_url}"
            file_path = ""
            try:
                with open("metrics_result.json", 'w') as file:
                    file.write(json.dumps(attachment_content))
                    file_path = file.name
                file_stream = open(file_path, 'r')
                files = {"file": ("metrics_result.json",
                                  file_stream, "application/json")}

                headers = self.__get_headers()
                if headers.get("Content-Type"):
                    del headers["Content-Type"]

                response = RestUtil.request_with_retry().put(
                    upload_url,
                    files=files,
                    headers=headers,
                    verify=self.verify_ssl
                )
                if not response.ok:
                    message = f"Failed to upload attachment content for asset {asset_id}. Status code: {response.status_code}, Error: {response.text}"
                    self.logger.error(message)
                    raise Exception(message)
            except Exception as e:
                self.logger.error(str(e))
                raise
            finally:
                # Deleting the temporary file created for run result
                try:
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception as e:
                    self.logger.error(
                        f"An error occurred while deleting the attachment file. Error: {str(e)}")

        else:
            content_bytes = json.dumps(attachment_content).encode("utf-8")
            response = RestUtil.request_with_retry().put(
                upload_url,
                data=content_bytes,
                headers=self.__get_headers(),
                params=self.container_params,
                verify=self.verify_ssl
            )

            if not response.ok:
                message = f"Failed to upload attachment content for asset {asset_id}. Status code: {response.status_code}, Error: {response.text}"
                self.logger.error(message)
                raise Exception(message)

        # Marking attachment as transfer complete
        attachment_url = f"{attachments_url}/{attachment_id}/complete"
        response = RestUtil.request_with_retry().post(
            attachment_url,
            json={},
            headers=self.__get_headers(),
            params=self.container_params,
            verify=self.verify_ssl
        )

        if not response.ok:
            message = f"Failed to mark attachment as transfer-complete for asset {asset_id}. Status code: {response.status_code}, Error: {response.text}"
            self.logger.error(message)
            raise Exception(message)
        print(
            f"Successfully created attachment {attachment_id} for asset {asset_id}. Time taken: {time.time() - start_time}.\n")

        return attachment_details

    def __get_headers(self) -> dict:
        """
        This method will create the headers with the iam access token.
        """

        headers = {}
        token = self.api_client.wos_client.authenticator.token_manager.get_token()
        headers["Authorization"] = f"Bearer {token}"
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
        return headers

    def __container_checks(self, project_id, space_id) -> None:
        """This method check the container type and update the container_id.

        Args
            - project_id: The project id.
            - space_id: The space_id.
        """
        if project_id and space_id:
            message = "Both 'project_id' and 'space_id' cannot be passed together."
            self.logger.error(message)
            raise Exception(message)

        self.container_type, self.container_id = (
            ("project", project_id) if project_id else ("space", space_id)
        )
        self.container_params = {
            f"{self.container_type}_id": self.container_id}

    def __map_post_response_to_ai_evaluation_asset(self, post_response: Dict) -> AIEvaluationAsset:
        """
        This method is for mapping the response of post ai_evaluation call to AIEvluationAsset entity.
        Args:
            - post_response: The response of POST '/v1/aigov/factsheet/ai_evaluations' call.
        Returns:
            An Instance of AIEvaluationAsset.
        """

        metadata = get(post_response, "metadata", {})
        ai_evaluation = get(post_response, "entity.ai_evaluation", {})
        evaluation_run = get(ai_evaluation, "evaluation_run", {})

        return AIEvaluationAsset(
            container_id=get(
                metadata, f"{self.container_type}_id", default=""),
            container_type=self.container_type,
            container_name=get(metadata, "name", ""),
            name=get(metadata, "name", ""),
            description=get(metadata, "description", ""),
            asset_type=get(metadata, "asset_type", "ai_evaluation"),
            created_at=get(metadata, "created_at", ""),
            owner_id=get(metadata, "owner_id", ""),
            asset_id=get(metadata, "asset_id", ""),
            creator_id=get(metadata, "creator_id", ""),
            asset_details={
                "task_ids": get(ai_evaluation, "task_ids", []),
                "operational_space_id": get(ai_evaluation, "operational_space_id", ""),
                "input_data_type": get(ai_evaluation, "input_data_type", ""),
                "evaluation_asset_type": get(ai_evaluation, "evaluation_asset_type", ""),
            },
            evaluation_configuration=EvaluationConfig(
                monitors=get(evaluation_run, "monitors", {}),
                evaluation_assets=get(evaluation_run, "evaluation_assets", []),
            ),
            href=get(post_response, "href", ""),
        )

    def __map_ai_experiment(self, experiment) -> AIExperiment:
        """
        This method is for mapping the experiment json to AIExperiment entity.
        Args:
            - experiment: ai_experiment details in json.
        Return: An instance of AIExperiment
        """
        metadata = get(experiment, "metadata", default={})
        ai_experiment_data = get(
            experiment, "entity.ai_experiment", default={})

        ai_experiment_details = {
            "container_id": get(metadata, f"{self.container_type}_id", default=""),
            "container_type": self.container_type,
            "name": get(metadata, "name", default=""),
            "description": get(metadata, "description", default=""),
            "asset_type": get(metadata, "asset_type", default=""),
            "created_at": get(metadata, "created_at", default=""),
            "owner_id": get(metadata, "owner_id", default=""),
            "asset_id": get(metadata, "asset_id", default=""),
            "creator_id": get(metadata, "creator_id", default=""),
            "component_id": get(ai_experiment_data, "component_id", default=""),
            "component_type": get(ai_experiment_data, "component_type", default=""),
            "component_name": get(ai_experiment_data, "component_name", default=""),
            "runs": get(ai_experiment_data, "runs", default=[]),
        }

        ai_experiment = AIExperiment(**ai_experiment_details)

        return ai_experiment

    @staticmethod
    def __process_notebook(file_path: Path):
        """
        Reads the notebook from the specified path and removes all output cells before saving it as an attachment.
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)

        for cell in notebook["cells"]:
            if "outputs" in cell:
                cell["outputs"] = []
            if "execution_count" in cell:
                cell["execution_count"] = None

        return notebook

    def get_experiment_notebook(self, ai_experiment_id: str, run_id: str, custom_filename: Optional[str] = None) -> str:
        """
        Download an experiment notebook from a specific AI experiment run.

        Args:
            ai_experiment_id (str): The unique identifier for the AI experiment
            run_id (str): The specific run ID within the experiment
            custom_filename (Optional[str]): Custom filename for the downloaded file.
                                        If None, uses format: "{ai_experiment.source_name}"

        Example:
            >>> client.get_experiment_asset("exp_123", "run_456")
            Downloaded: my_notebook.ipynb
        """

        ai_experiment = self.get(ai_experiment_id)
        run_detail = next(
            (run for run in ai_experiment.runs if run.run_id == run_id),
            None
        )
        if run_detail is None:
            error_msg = f"Run '{run_id}' not found in experiment '{ai_experiment_id}'"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        attachment_id = run_detail.properties.get("notebook_attachment_id")
        if not attachment_id:
            error_msg = f"No notebook found for run '{run_id}' in experiment '{ai_experiment_id}'"
            self.logger.error(error_msg)
            raise Exception(error_msg)

        attachment_details = self.__get_attachment_details(
            ai_experiment_id, attachment_id)

        s3_url = attachment_details.get("url")
        filename = custom_filename or f"{run_detail.source_name}"

        self.__download_file_from_s3(s3_url, filename, attachment_id)

        print(f"Successfully downloaded experiment notebook as '{filename}'")

    def __get_attachment_details(self, ai_experiment_id: str, attachment_id: str) -> Dict[str, Any]:
        """
        Retrieve attachment details from the data platform API.
        """
        attachments_url = f"{self.dataplatform_url}/v2/assets/{ai_experiment_id}/attachments/{attachment_id}"

        response = RestUtil.request_with_retry().get(
            attachments_url,
            headers=self.__get_headers(),
            params=self.container_params,
            verify=self.verify_ssl
        )
        if not response.ok:
            error_msg = (
                f"Failed to retrieve attachment '{attachment_id}' for experiment '{ai_experiment_id}'. "
                f"Status: {response.status_code}, Error: {response.text}"
            )
            self.logger.error(error_msg)
            raise Exception(error_msg)

        return json.loads(response.text)

    def __download_file_from_s3(self, s3_url: str, filename: str, attachment_id: str) -> None:
        """
        Download file from S3 URL and save locally.
        """
        try:
            response = requests.get(s3_url, stream=True, timeout=30)
            if not response.ok:
                error_msg = (
                    f"Failed to download notebook attachment '{attachment_id}'. "
                    f"Status: {response.status_code}, Error: {response.text}"
                )
                self.logger.error(error_msg)
                raise Exception(error_msg)

            with open(filename, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)
        except requests.RequestException as e:
            error_msg = f"Error downloading file: {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
