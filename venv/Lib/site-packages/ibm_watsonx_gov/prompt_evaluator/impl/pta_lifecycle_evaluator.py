# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import json
import time
from dataclasses import dataclass
from datetime import datetime
from typing import Union

import pandas as pd
import requests
from ibm_watsonx_ai.foundation_models.prompts.prompt_template import (
    DetachedPromptTemplate, PromptTemplate, PromptTemplateManager)
from IPython.display import display

from ibm_watsonx_gov.entities.enums import EvaluationStage
from ibm_watsonx_gov.utils.authenticator import Authenticator
from ibm_watsonx_gov.utils.gov_sdk_logger import GovSDKLogger
from ibm_watsonx_gov.utils.rest_util import RestUtil
from ibm_watsonx_gov.visualizations.visualization_utils import \
    display_message_with_frame


@dataclass
class SpaceConfigurations:
    """Class for keeping track of spaces."""

    space_id: str = None
    prompt_template: PromptTemplate | DetachedPromptTemplate = None
    space_deployment: dict[str, str] = None
    prompt_setup: dict[str, str] = None


@dataclass
class ProjectConfigurations:
    """Class for keeping track of projects."""

    project_id: str = None
    prompt_template: PromptTemplate | DetachedPromptTemplate = None
    prompt_setup: dict[str, str] = None


@dataclass
class ModelUsecase:
    """Class for keeping track of model usecase"""

    usecase_id: str
    version: str
    catalog_id: str
    approach_id: str = None


class PTALifecycleEvaluator:
    """Class responsible to trigger the e2e lifecycle of pta with evaluation
    support."""

    def __init__(self):
        self.logger = GovSDKLogger.get_logger(__name__)
        self.config = None

        # Configuration details
        self.use_cpd: bool = None
        self.credentials: dict[str, str] = None
        self.use_ssl: bool = None
        self.service_instance_id: str = None
        self.wml_url = None
        self.platform_url = None
        self.wos_url = None
        self.dataplatform_url = None
        self.setup_stages: list[EvaluationStage] = None
        self.is_detached: bool = False
        self.ai_usecase: ModelUsecase = None

        # Authentication
        self.__authenticator: Authenticator = None
        self.__iam_access_token: str = None

        # Base urls
        self.__platform_url: str = None
        self.__wos_url: str = None
        self.__dataplatform_url: str = None

        # Parsed configurations
        self.__stage_configurations: dict[EvaluationStage, Union[ProjectConfigurations, SpaceConfigurations]] = {
            EvaluationStage.DEVELOPMENT: ProjectConfigurations(),
            EvaluationStage.PRE_PRODUCTION: SpaceConfigurations(),
            EvaluationStage.PRODUCTION: SpaceConfigurations(),
        }

        # Template ids
        self.__prompt_template_ids: dict[EvaluationStage, str] = {
            EvaluationStage.DEVELOPMENT: None,
            EvaluationStage.PRE_PRODUCTION: None,
            EvaluationStage.PRODUCTION: None,
        }

        # subscription ids
        self.__subscription_ids: dict[EvaluationStage, str] = {
            EvaluationStage.DEVELOPMENT: None,
            EvaluationStage.PRE_PRODUCTION: None,
            EvaluationStage.PRODUCTION: None,
        }

        # deployment ids
        self.__deployment_ids: dict[EvaluationStage, str] = {
            EvaluationStage.PRE_PRODUCTION: None,
            EvaluationStage.PRODUCTION: None,
        }

        # Scoring urls
        self.__scoring_urls: dict[EvaluationStage, str] = {
            EvaluationStage.DEVELOPMENT: None,
            EvaluationStage.PRE_PRODUCTION: None,
            EvaluationStage.PRODUCTION: None,
        }

        # monitors
        self.__monitors_info: dict[EvaluationStage, dict[str, any]] = {
            EvaluationStage.DEVELOPMENT: None,
            EvaluationStage.PRE_PRODUCTION: None,
            EvaluationStage.PRODUCTION: None,
        }

    def __send_request(self, method: str, **kwargs) -> requests.Response:
        """Helper method to wrap requests.request method.

        This will raise exception if the response status code is not 2xx.
        """
        self.logger.info(
            f"sending request. method '{method}', "
            f"url '{kwargs.get('url')}', "
            f"json payload: '{kwargs.get('json', {})}', "
            f"params: '{kwargs.get('params', {})}'."
        )

        # Check if kwargs has headers argument and use it, otherwise use the default values
        headers = kwargs.pop("headers", {})
        if not headers:
            headers["Authorization"] = f"Bearer {self.__iam_access_token}"
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"

        # Check if kwargs has verify, otherwise use the default value
        verify = kwargs.get("verify", self.use_ssl)

        # Send the request with retries,
        # this will raise exception if the the response is non 2xx or if there were any intermediate failure
        try:
            response = RestUtil.request_with_retry().request(
                method=method,
                headers=headers,
                verify=verify,
                **kwargs,
            )
            response.raise_for_status()
            self.logger.info(
                f"status code: {response.status_code}, response body: {response.text}"
            )
        except requests.exceptions.HTTPError as e:
            message = f"HTTP Error: {e}. Response body: {response.text}"
            self.logger.error(message)
            raise Exception(message)
        return response

    def __validate_dict_schema(
        self, object_in: dict[str, any], object_schema: dict[str, type]
    ) -> None:
        """Helper method to validate dicts against a schema. This will validate
        the following:

        - the types of dict members.
        - required keys
        - validate that members of type dict are non empty

        """
        missing_keys = object_schema.keys() - object_in.keys()
        if len(missing_keys) > 0:
            message = f"Missing required attributes: {missing_keys}"
            self.logger.error(message)
            raise Exception(message)

        for key, value_type in object_schema.items():
            if not isinstance(object_in[key], value_type):
                message = f"Invalid attribute `{key}` type. expected type: {value_type}, actual type: {type(object_in[key])}."
                self.logger.error(message)
                raise Exception(message)
            if value_type == dict and not object_in[key]:
                message = f"Attribute `{key}` of type `dict` can not be empty."
                self.logger.error(message)
                raise Exception(message)

    def __validate_configuration(self, config: dict) -> None:
        """
        Helper function to validate the configuration object.
        """
        self.logger.info(f"Validating configuration: {config}")

        # Validate that all the attributes in the configuration are recognized
        expected_config_attributes = set(
            ["common_configurations"] + [e.value for e in EvaluationStage])
        unexpected_config_attributes = config.keys() - expected_config_attributes
        if len(unexpected_config_attributes) > 0:
            self.logger.warning(
                f"Ignoring properties {unexpected_config_attributes} as these are not recognized.")

        # Validate the config
        configuration_schema = {
            "common_configurations": dict,
        }

        # Only validate the configuration of stages in setup_stages
        for stage in self.setup_stages:
            configuration_schema[stage.value] = dict

        # Check attributes types
        self.__validate_dict_schema(config, configuration_schema)

        # Validate common_configurations
        common_configurations = config["common_configurations"]
        common_configurations_schema = {
            "use_ssl": bool,
            "use_cpd": bool,
            "credentials": dict,
        }

        self.__validate_dict_schema(
            common_configurations,
            common_configurations_schema
        )

        # Validate CPD credentials
        if common_configurations["use_cpd"] is True:
            cpd_credentials_schema = {"url": str, "username": str}
            if "api_key" in common_configurations["credentials"].keys():
                cpd_credentials_schema["api_key"] = str
            elif "password" in common_configurations["credentials"].keys():
                cpd_credentials_schema["password"] = str
            else:
                message = (
                    "Please provide on of `api_key` or `password` for `credentials`"
                )
                self.logger.error(message)
                raise Exception(message)

            self.__validate_dict_schema(
                common_configurations["credentials"], cpd_credentials_schema
            )
        # Validate cloud credentials
        else:
            cloud_credentials_schema = {"iam_url": str, "apikey": str}

            # Validate cloud credentials
            self.__validate_dict_schema(
                common_configurations["credentials"], cloud_credentials_schema
            )

        # Validate ai_usecase
        if common_configurations.get("ai_usecase"):
            ai_usecase_schema = {
                "ai_usecase_id": str,
                "catalog_id": str,
                "approach_version": str,
            }
            self.__validate_dict_schema(
                common_configurations["ai_usecase"],
                ai_usecase_schema,
            )

        # Validate the development configuration
        if EvaluationStage.DEVELOPMENT in self.setup_stages:
            development_configurations = config[EvaluationStage.DEVELOPMENT.value]
            development_configurations_schema = {
                "project_id": str,
                "prompt_setup": dict,
            }
            self.__validate_dict_schema(development_configurations,
                                        development_configurations_schema)

        if EvaluationStage.PRE_PRODUCTION in self.setup_stages:
            # Check if the user provided project id or space id
            pre_production_configurations = config[EvaluationStage.PRE_PRODUCTION.value]
            if "project_id" in pre_production_configurations.keys():
                pre_production_configurations_schema = {
                    "project_id": str,
                    "prompt_setup": dict,
                }
            elif "space_id" in pre_production_configurations.keys():
                pre_production_configurations_schema = {
                    "space_id": str,
                    "space_deployment": dict,
                    "prompt_setup": dict,
                }
            else:
                message = "Please provide either `project_id` or `space_id` for `pre_production` configuration."
                self.logger.error(message)
                raise Exception(message)
            self.__validate_dict_schema(
                pre_production_configurations, pre_production_configurations_schema)

        # Validate the production configuration
        if EvaluationStage.PRODUCTION in self.setup_stages:
            production_configurations = config[EvaluationStage.PRODUCTION.value]
            production_configurations_schema = {
                "space_id": str,
                "space_deployment": dict,
                "prompt_setup": dict,
            }
            self.__validate_dict_schema(production_configurations,
                                        production_configurations_schema)

    def __get_prompt_template_input_variables_list(
            self,
            stage: EvaluationStage = EvaluationStage.DEVELOPMENT,
    ) -> list[str]:
        """
        Helper to return prompt template variable list

        Args:
            stage (EvaluationStage): evaluation stage for the prompt template. Defaults to EvaluationStage.DEVELOPMENT
        """
        try:
            input_variables = self.__stage_configurations[stage].prompt_template.input_variables

            if isinstance(input_variables, list):
                return input_variables
            else:
                return list(input_variables.keys())
        except Exception as e:
            message = f"Failed to parse prompt variables list. {e}"
            self.logger.error(message)
            raise Exception(message)

    def evaluate_df(self, input_df: pd.DataFrame, scoring_url: str) -> list[dict[str, any]]:
        """
        Method to evaluate the prompt. This will take the scoring url and
        will process input_df.

        Args:
            input_df (pd.DataFrame): Input DataFrame to be evaluated.
            scoring_url (str): Scoring URL to send requests to.

        Returns:
            list[dict[str, any]]: List of dictionaries containing request and response data for each record in the input DataFrame.

        Raises:
            Exception: If the input DataFrame is empty or if there is an error during the evaluation process.

        """
        self.logger.info("Running evaluation")

        if input_df.empty:
            message = "Input dataframe is empty."
            self.logger.error(message)
            raise Exception(message)

        # process the dataframe to take only the prompt template variables
        try:
            prompt_template_variables = self.__get_prompt_template_input_variables_list()
            df = input_df[prompt_template_variables]
        except Exception as e:
            message = f"Unable to parse the prompt template variables from the dataframe. {e}"
            self.logger.error(message)
            raise Exception(message)

        prompt_data = df.to_dict(orient="records")

        pl_data = []
        for row in prompt_data:
            json_request = {"parameters": {"template_variables": row}}
            params = {"version": datetime.today().strftime("%Y-%m-%d")}
            try:
                response = self.__send_request(
                    "post", url=scoring_url, json=json_request, params=params
                )

                try:
                    pl_data.append(
                        {
                            "request": json_request,
                            "response": response.json()
                        }
                    )
                except Exception as e:
                    message = f"Failed to parse evaluation response. {e}"
                    self.logger.error(message)
                    raise Exception(message)
            except Exception as e:
                message = f"Failed to evaluate record. {e}"
                self.logger.error(message)
                raise Exception(message)

        self.logger.info("Records evaluation is done")

        return pl_data

    def __build_wxai_credentials_dict(self) -> dict[str, str]:
        if self.use_cpd:
            return {
                "username": self.credentials["username"],
                "url": self.credentials["url"],
                "api_key": self.credentials["api_key"],
                "verify": self.use_ssl,
                "instance_id": "openshift",
            }

        return {
            "url": self.__wml_url,
            "api_key": self.credentials["apikey"],
            "verify": self.use_ssl,
        }

    def create_prompt_template_using_wxai(
        self,
        prompt_template: PromptTemplate | DetachedPromptTemplate,
        stage: EvaluationStage
    ) -> str:
        """Method to create prompt template using ibm_watsonx_ai"""
        self.logger.info("Creating Prompt Template")
        display_message_with_frame("Creating Prompt Template Asset...")

        try:
            if isinstance(self.__stage_configurations[stage], ProjectConfigurations):
                prompt_manager = PromptTemplateManager(
                    credentials=self.__build_wxai_credentials_dict(),
                    project_id=self.__stage_configurations[stage].project_id,
                )
            else:
                prompt_manager = PromptTemplateManager(
                    credentials=self.__build_wxai_credentials_dict(),
                    space_id=self.__stage_configurations[stage].space_id,
                )

            self.__stage_configurations[stage].prompt_template = prompt_manager.store_prompt(
                prompt_template)
        except Exception as e:
            message = f"Failed to create prompt template. {e}"
            self.logger.error(message)
            raise Exception(message)

        prompt_template_id = self.__stage_configurations[stage].prompt_template.prompt_id

        display_message_with_frame(
            message=f"Prompt template created successfully. Prompt template id: {prompt_template_id}",
        )

        return prompt_template_id

    def get_prompt_template_details_from_wxai(
            self,
            prompt_template_id: str,
            stage: EvaluationStage,
    ) -> str:
        """Helper to get the details of an existing prompt template. This will set the prompt template self.stage_configurations"""
        self.logger.info("Loading Prompt Template")
        display_message_with_frame("Loading Prompt Template Asset...")

        try:
            prompt_manager = PromptTemplateManager(
                credentials=self.__build_wxai_credentials_dict(),
                project_id=self.__stage_configurations[EvaluationStage.DEVELOPMENT].project_id,
            )
            self.__stage_configurations[stage].prompt_template = prompt_manager.load_prompt(
                prompt_id=prompt_template_id)
        except Exception as e:
            message = f"Failed to load prompt template. {e}"
            self.logger.error(message)
            raise Exception(message)

        prompt_template_id = self.__stage_configurations[stage].prompt_template.prompt_id

        display_message_with_frame(
            message=f"Prompt template loaded successfully. Prompt template id: {prompt_template_id}",
        )

        return prompt_template_id

    def get_scoring_url(self, subscription_id: str) -> str:
        """Method to get the scoring url for a subscription id."""
        try:
            response = self.__send_request(
                method="get",
                url=f"{self.__wos_url}/openscale/{self.service_instance_id}/v2/subscriptions/{subscription_id}",
            )
        except Exception as e:
            message = f"Failed to get subscription details, subscription_id: {subscription_id}. {e}"
            self.logger.error(message)
            raise Exception(message)

        # Get scoring url
        try:
            json_response = response.json()
            if self.use_cpd:
                deployment_id = json_response["entity"]["deployment"]["deployment_id"]
                scoring_url = f"{self.__wml_url}/ml/v1/deployments/{deployment_id}/text/generation"
            else:
                scoring_url = json_response["entity"]["deployment"]["url"]
            self.logger.info(f"scoring url: {scoring_url}")
        except Exception as e:
            message = (
                f"Failed to parse scoring url from subscription details response. {e}"
            )
            self.logger.error(message)
            raise Exception(message)
        return scoring_url

    def get_available_datamarts(self) -> None:
        """Method to get the available datamarts."""
        try:
            response = self.__send_request(
                method="get",
                url=f"{self.__wos_url}/openscale/{self.service_instance_id}/v2/data_marts",
            )
        except Exception as e:
            message = f"Failed to get available data marts. {e}"
            self.logger.error(message)
            raise Exception(message)

        display_message_with_frame(
            f"Available datamarts:\n{json.dumps(response.json(),indent=2)}"
        )

    def trigger_prompt_setup(self, stage: EvaluationStage) -> None:
        """Method to trigger prompt set up for prompt template in a given
        evaluation stage.

        This will poll until the prompt template is set up successfully.
        """
        self.logger.info(f"Triggering prompt setup for {stage}")

        display_message_with_frame(
            message=f"Setting up prompt for evaluation stage '{stage.value}'..."
        )

        if stage == EvaluationStage.DEVELOPMENT:
            params = {
                "prompt_template_asset_id": self.__prompt_template_ids[stage],
                "project_id": self.__stage_configurations[stage].project_id,
            }
            payload = self.__stage_configurations[stage].prompt_setup

        elif stage == EvaluationStage.PRE_PRODUCTION:
            params = {
                "prompt_template_asset_id": self.__prompt_template_ids[stage],
                "space_id": self.__stage_configurations[stage].space_id,
                "deployment_id": self.__deployment_ids[stage],
            }
            payload = self.__stage_configurations[stage].prompt_setup

        elif stage == EvaluationStage.PRODUCTION:
            params = {
                "prompt_template_asset_id": self.__prompt_template_ids[stage],
                "space_id": self.__stage_configurations[stage].space_id,
                "deployment_id": self.__deployment_ids[stage],
            }
            payload = self.__stage_configurations[stage].prompt_setup
        else:
            message = f"Prompt setup for stage: '{stage}' is not supported yet"
            self.logger.error(message)
            raise Exception(message)

        try:
            self.logger.info(
                f"setting up prompt template for '{stage}'. parameters {params}"
            )
            response = self.__send_request(
                method="post",
                url=f"{self.__wos_url}/openscale/{self.service_instance_id}/v2/prompt_setup",
                json=payload,
                params=params,
            )
        except Exception as e:
            message = f"Prompt setup failed for the stage {stage}. {e}"
            self.logger.info(message)
            raise Exception(message)

        display_message_with_frame(
            message=f"Started prompt set up for '{stage.value}':\n\n{json.dumps(response.json(), indent=2)}",
        )

        # Check the prompt set up progress
        self.logger.info(
            f"Checking prompt set up progress for the stage {stage}...")
        for attempt in range(10):
            try:
                response = self.__send_request(
                    method="get",
                    url=f"{self.__wos_url}/openscale/{self.service_instance_id}/v2/prompt_setup",
                    params=params,
                )
            except Exception as e:
                message = (
                    f"Failed to check for prompt setup status in the stage {stage}. {e}"
                )
                self.logger.error(message)
                raise Exception(message)

            try:
                json_response = response.json()
                prompt_setup_status = json_response["status"]["state"]
            except Exception as e:
                message = f"Failed to parse prompt set up status response. {e}"
                self.logger.error(message)
                raise Exception(message)

            if prompt_setup_status.lower() == "finished":
                self.logger.info(
                    f"prompt template set up for the stage {stage} is done. Status {prompt_setup_status}"
                )
                break
            elif prompt_setup_status.lower() == "error":
                message = f"Prompt set up failed due to an error. {response.text}"
                self.logger.error(message)
                raise Exception(message)
            else:
                self.logger.info(f"Attempt {attempt+1} not done. Retrying...")
                time.sleep(5)
        else:
            message = "Prompt template set up status did not update after 10 attempts. aborting..."
            self.logger.error(message)
            raise Exception(message)

        # Parse items needed from the response get the subscription id from the response
        try:
            subscription_id = json_response["subscription_id"]
            self.logger.info(
                f"subscription id for the stage {stage}: {subscription_id}"
            )
        except Exception as e:
            message = f"Failed to get subscription id from the response. {e}"
            self.logger.error(message)
            raise Exception(message)

        self.__subscription_ids[stage] = subscription_id

        display_message_with_frame(
            message=f"Prompt set up for the stage {stage} finished successfully:\n\n{json.dumps(json_response, indent=2)}",
        )

    def promote_prompt_to_space(
        self,
        project_id: str,
        project_prompt_template_id: str,
        space_id: str,
    ) -> str:
        """Method to promote a prompt from project to space."""
        self.logger.info("Promoting prompt template assets to space")
        display_message_with_frame(
            message=f"Promoting prompt from project id: {project_id} to space id {space_id}"
        )
        """
        Payload Sample:
            {
                "space_id": "d7fc6056-a06b-4de0-bae5-7c97fa06c862"
            }
        """
        payload = {"space_id": space_id}
        params = {"project_id": project_id}

        try:
            response = self.__send_request(
                method="post",
                url=f"{self.__dataplatform_url}/v2/assets/{project_prompt_template_id}/promote",
                json=payload,
                params=params,
            )
        except Exception as e:
            message = f"Failed to promote template asset to space. {e}"
            self.logger.error(message)
            raise Exception(message)

        try:
            json_response = response.json()
            space_prompt_template_id = json_response["metadata"]["asset_id"]
            self.logger.info(
                f"Prompt template id promoted to space. Space prompt template asset id: {space_prompt_template_id}"
            )
        except Exception as e:
            message = f"Failed to parse the response of promoting template asset from project to space. {e}"
            self.logger.error(message)
            raise Exception(message)

        display_message_with_frame(
            message=f"Template promoted to space successfully. Prompt template id: {space_prompt_template_id}",
        )

        return space_prompt_template_id

    def create_pta_space_deployment(
        self,
        space_configurations: SpaceConfigurations,
        space_prompt_template_id: str,
    ) -> str:
        """Method to create prompt template asset space deployment."""

        """
        payload sample:
            {
                "prompt_template": {
                    "id": "81ad403c-df8b-41c0-87bb-68fea6717411",
                },
                "online": {
                    "parameters": {"serving_name": "serving_name"}
                },
                "base_model_id": "ibm/granite-13b-chat-v2",
                "name": "deployment_name",
                "description": "deployment_description",
                "space_id": "74a51b1a-a83a-4e0b-b5b4-88e97b3a14a1",
            }

        """
        payload = {
            "prompt_template": {
                "id": space_prompt_template_id,
            },
            "base_model_id": space_configurations.space_deployment["base_model_id"],
            "name": space_configurations.space_deployment["name"],
            "description": space_configurations.space_deployment["description"],
            "space_id": space_configurations.space_id,
        }

        if self.is_detached:
            payload["detached"] = {}
        else:
            payload["online"] = {
                "parameters": {"serving_name": space_configurations.space_deployment["serving_name"]}
            }

        params = {
            "version": space_configurations.space_deployment["version_date"],
            "space_id": space_configurations.space_id,
        }

        display_message_with_frame(
            message=f"Creating space deployment for space id {space_configurations.space_id} and prompt template id {space_prompt_template_id}",
        )

        try:
            response = self.__send_request(
                method="post",
                url=f"{self.__wml_url}/ml/v4/deployments",
                params=params,
                json=payload,
            )
        except Exception as e:
            message = f"Failed to create space deployment. {e}"
            self.logger.error(message)
            raise Exception(message)

        try:
            json_response = response.json()
            space_deployment_id = json_response["metadata"]["id"]
            self.logger.info(
                f"Space deployment id: {space_deployment_id}")
        except Exception as e:
            message = f"Failed to parse space deployment creation response. {e}"
            self.logger.error(message)
            raise Exception(message)

        display_message_with_frame(
            message=f"Deployment created successfully. Space deployment id: {space_deployment_id}",
        )

        return space_deployment_id

    def risk_evaluation_for_pta_subscription(
        self,
        input_df: pd.DataFrame,
        monitor_instance_id: str,
    ) -> str:
        """Function to trigger risk evaluation for PTA subscription.

        Args:
            input_df (pd.Dataframe): dataframe of the dataset
            monitor_instance_id (str): monitor instance id

        Returns:
            str: measurement_id
        """
        self.logger.info(
            f"Starting risk evaluation for PTA subscription. monitor_instance_id: {monitor_instance_id}"
        )
        display_message_with_frame(
            message=f"Evaluating risk of MRM monitor id {monitor_instance_id}"
        )

        url = f"{self.__wos_url}/openscale/{self.service_instance_id}/v2/monitoring_services/mrm/monitor_instances/{monitor_instance_id}/risk_evaluations"
        try:
            file_payload = [
                ("data", ("risk_evaluation_for_pta.csv", input_df.to_csv()))]
            params = {"test_data_set_name": "risk_evaluation_for_pta"}
            headers = {
                "Authorization": f"Bearer {self.__iam_access_token}"}
            self.__send_request(
                method="post",
                url=url,
                files=file_payload,
                params=params,
                headers=headers,
            )
        except Exception as e:
            message = f"Failed to do risk evaluation for PTA subscription. {e}"
            self.logger.error(message)
            raise Exception(message)

        self.logger.info("Waiting for risk evaluation result")

        # Retry for 15 minutes (180 retry, 5 seconds apart)
        for attempt in range(180):
            response = self.__send_request(
                method="get",
                url=url,
            )

            try:
                json_response = response.json()
                state = json_response["entity"]["status"]["state"]

            except Exception as e:
                message = f"Failed to parse risk evaluation status response. {e}"
                self.logger.error(message)
                raise Exception(e)

            if state.lower() == "finished":
                self.logger.info(
                    f"prompt template set up is done. Status {state}")
                break
            elif state.lower() == "error":
                message = f"Risk evaluation failed due to an error. {response.text}"
                self.logger.error(message)
                raise Exception(message)
            else:
                self.logger.info(
                    f"Attempt {attempt+1} not done. Retrying...")
                time.sleep(5)
        else:
            message = "Risk evaluation status did not update after 15 minutes. Aborting..."
            self.logger.error(message)
            raise Exception(message)

        try:
            measurement_id = json_response["entity"]["parameters"]["measurement_id"]
        except Exception as e:
            message = f"Failed to parse measurement id. {e}"
            self.logger.error(message)
            raise Exception(message)

        display_message_with_frame(
            message=f"Successfully finished the risk evaluation.\nMeasurement id for risk evaluation for PTA subscription: {measurement_id}",
        )
        return measurement_id

    def risk_evaluation_for_pta_subscription_in_space(
        self, monitor_instance_id: str
    ) -> str:
        """Function to trigger risk evaluation for PTA subscription in space.
        This assumes that payload logging and feedback data sets are populated.

        Args:
            monitor_instance_id (str): monitor instance id

        Returns:
            str: measurement_id
        """
        self.logger.info(
            f"Starting risk evaluation for PTA subscription in space. monitor_instance_id: {monitor_instance_id}"
        )
        display_message_with_frame(
            message=f"Evaluating risk of MRM monitor id {monitor_instance_id}"
        )
        url = f"{self.__wos_url}/openscale/{self.service_instance_id}/v2/monitoring_services/mrm/monitor_instances/{monitor_instance_id}/risk_evaluations"
        headers = {
            "Authorization": f"Bearer {self.__iam_access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        try:
            self.__send_request(
                method="post",
                url=url,
                headers=headers,
                json={}
            )
        except Exception as e:
            message = f"Failed to do risk evaluation for PTA subscription. {e}"
            self.logger.error(message)
            raise Exception(message)

        self.logger.info("Waiting for risk evaluation result")
        # Retry for 15 minutes (180 retry, 5 seconds apart)
        for attempt in range(180):
            response = self.__send_request(
                method="get",
                url=url,
            )

            try:
                json_response = response.json()
                state = json_response["entity"]["status"]["state"]

            except Exception as e:
                message = f"Failed to parse risk evaluation status response. {e}"
                self.logger.error(message)
                raise Exception(e)

            if state.lower() == "finished":
                self.logger.info(
                    f"prompt template set up is done. Status {state}")
                break
            elif state.lower() == "error":
                message = f"Risk evaluation failed due to an error. {response.text}"
                self.logger.error(message)
                raise Exception(message)
            else:
                self.logger.info(
                    f"Attempt {attempt+1} not done. Retrying...")
                time.sleep(5)
        else:
            message = "Risk evaluation status did not update after 15 minutes. Aborting..."
            self.logger.error(message)
            raise Exception(message)

        try:
            measurement_id = json_response["entity"]["parameters"]["measurement_id"]
        except Exception as e:
            message = f"Failed to parse measurement id. {e}"
            self.logger.error(message)
            raise Exception(message)

        display_message_with_frame(
            message=f"Successfully finished the risk evaluation.\nMeasurement id for risk evaluation for PTA subscription: {measurement_id}",
        )
        return measurement_id

    def get_monitor_metrics(
        self,
        monitor_instance_id: str,
        measurement_id: str
    ) -> dict[str, any]:
        """Function to get the monitor metrics for a given measurement id.

        Args:
            monitor_instance_id (str): monitor instance id
            measurement_id (str): measurement id

        Returns:
            dict: response body for the monitor
        """
        self.logger.info(
            f"Retrieving metrics for measurement_id: {measurement_id}")

        try:
            response = self.__send_request(
                method="get",
                url=f"{self.__wos_url}/openscale/{self.service_instance_id}/v2/monitor_instances/{monitor_instance_id}/measurements/{measurement_id}",
            )
        except Exception as e:
            message = f"Failed to retrieve monitor metrics. {e}"
            self.logger.error(message)
            raise Exception(message)

        try:
            json_response = response.json()
        except Exception as e:
            message = f"Failed to parse metrics response. {e}"
            self.logger.error(message)
            raise Exception(message)
        return json_response

    def get_monitor_instances(
        self, subscription_id: str, monitor_definition_id: str = None
    ) -> list[dict[str, any]]:
        """Function to get the monitor instances."""
        self.logger.info(
            f"Getting all monitors for subscription_id {subscription_id}, monitor_definition_id: {monitor_definition_id}"
        )

        params = {
            "target.target_id": subscription_id,
        }

        if monitor_definition_id is not None:
            params["monitor_definition_id"] = monitor_definition_id

        # Send request to get all monitors
        try:
            response = self.__send_request(
                method="get",
                url=f"{self.__wos_url}/openscale/{self.service_instance_id}/v2/monitor_instances",
                params=params,
            )
        except Exception as e:
            message = f"Failed to retrieve all monitor instances. {e}"
            self.logger.error(message)
            raise Exception(message)

        # Parse the response to get the needed monitor information
        monitor_instances = []
        try:
            json_response = response.json()
            for instance in json_response["monitor_instances"]:
                monitor_instances.append(
                    {
                        "monitor_name": instance["entity"]["monitor_definition_id"],
                        "data_mart_id": instance["entity"]["data_mart_id"],
                        "status": instance["entity"]["status"]["state"],
                        "monitor_instance_id": instance["metadata"]["id"],
                        "measurement_id": None,
                    }
                )
        except Exception as e:
            message = f"Failed to parse monitors instances json response. {e}"
            self.logger.error(message)
            raise Exception(message)

        self.logger.info(f"monitor instances: {monitor_instances}")

        return monitor_instances

    def get_measurement_ids(
        self, subscription_id: str, monitor_definition_id: str = None
    ) -> list[dict[str, str]]:
        """Retrieve measurement IDs for a given subscription ID and monitor
        definition ID.

        Parameters:
        - subscription_id (str): Required. The ID of the subscription.
        - monitor_definition_id (str, optional): The ID of the monitor definition. Defaults to None.

        Returns:
        - List[Dict[str, str]]: A list of dictionaries containing the measurement IDs.

        Raises:
        - Exception: If there is an error retrieving the measurements.
        """
        self.logger.info(
            f"Getting measurement ids for subscription id {subscription_id}. monitor definition id: {monitor_definition_id}"
        )

        params = {
            "target_id": subscription_id,
            "target_type": "subscription",
        }
        if monitor_definition_id is not None:
            params["monitor_definition_id"] = monitor_definition_id

        try:
            response = self.__send_request(
                method="get",
                url=f"{self.__wos_url}/openscale/{self.service_instance_id}/v2/measurements",
                params=params,
            )
        except Exception as e:
            message = f"Failed to get the measurements. {e}"
            self.logger.error(message)
            raise Exception(message)

        try:
            json_response = response.json()
            monitor_measurements = []
            for instance in json_response["measurements"]:
                monitor_measurements.append(
                    {
                        "monitor_name": instance["entity"]["monitor_definition_id"],
                        "monitor_instance_id": instance["entity"][
                            "monitor_instance_id"
                        ],
                        "measurement_id": instance["metadata"]["id"],
                    }
                )

        except Exception as e:
            message = f"Failed to parse the measurements response. {e}"
            self.logger.error(message)
            raise Exception(message)

        self.logger.info(f"monitor measurements: {monitor_measurements}")
        return monitor_measurements

    def display_evaluation_url(
            self, stage: EvaluationStage
    ) -> None:
        """Helper function to build the evaluation url based in the given
        stage. This will raise an exception if the stage is not part of the
        setup.

        Args:
            stage (EvaluationStage): The stage which we need its evaluation url.
        """

        if stage not in self.setup_stages:
            message = f"the stage {stage} must be part of the setup stages"
            self.logger.error(message)
            raise Exception(message)

        # Build the url
        if stage == EvaluationStage.DEVELOPMENT:
            self.logger.info(
                f"Building evaluation url for {stage.value} stage with project id: {self.__stage_configurations[stage].project_id}")
            evaluation_url = f"{self.__platform_url}/wx/prompt-details/{self.__prompt_template_ids[stage]}/evaluate?context=wx&project_id={self.__stage_configurations[stage].project_id}"
            evaluation_url_message = (
                f"User can navigate to the evaluations page in project {evaluation_url}"
            )

        else:
            self.logger.info(
                f"Building evaluation url for {stage.value} stage with space id: {self.__stage_configurations[stage].space_id}")
            evaluation_url = f"{self.__platform_url}/ml-runtime/deployments/{self.__deployment_ids[stage]}/evaluations?space_id={self.__stage_configurations[stage].space_id}&context=wx&flush=true"
            evaluation_url_message = (
                f"User can navigate to the evaluations page in space {evaluation_url}"
            )

        # Display the url
        display_message_with_frame(message=evaluation_url_message)

    def display_factsheet_url(
            self, stage: EvaluationStage
    ) -> None:
        """Helper function to build the factsheet url based in the given stage.
        This will raise an exception if the stage is not part of the setup.

        Args:
            stage (EvaluationStage): The stage which we need its factsheet url.
        """

        if stage not in self.setup_stages:
            message = f"the stage {stage} must be part of the setup stages"
            self.logger.error(message)
            raise Exception(message)

        # Build the url
        if stage == EvaluationStage.DEVELOPMENT:
            self.logger.info(
                f"Building factsheet url for {stage.value} stage with project id: {self.__stage_configurations[stage].project_id}")
            factsheet_url = f"{self.__platform_url}/wx/prompt-details/{self.__prompt_template_ids[stage]}/factsheet?context=wx&project_id={self.__stage_configurations[stage].project_id}"
            factsheet_url_message = (
                f"User can navigate to the published facts in project {factsheet_url}"
            )

        else:
            self.logger.info(
                f"Building factsheet url for {stage.value} stage with space id: {self.__stage_configurations[stage].space_id}")
            factsheet_url = f"{self.__platform_url}/ml-runtime/deployments/{self.__deployment_ids[stage]}/details?space_id={self.__stage_configurations[stage].space_id}&context=wx&flush=true"
            factsheet_url_message = (
                f"User can navigate to the published facts in space {factsheet_url}"
            )

        # Display the url
        display_message_with_frame(message=factsheet_url_message)

    def get_monitors_with_measurements_info(
            self, stage: EvaluationStage, show_table: bool = False
    ) -> list[dict[str, any]]:
        """This function will retrieve the data from the backend and will
        return a dictionary of the monitor data that was retrieved. Optionally,
        the function would display the response as a table. This will also
        update the object state to store the recent value for the monitors
        info.

        Args:
            stage (EvaluationStage): the evaluation stage
            show_table (bool, optional): whether to display the table or not. Defaults to False.

        Returns:
            list[dict[str, any]]: a list of dictionaries containing the monitor data.
        """

        subscription_id = self.__subscription_ids.get(stage, None)

        if subscription_id is None:
            message = f"Missing subscription_id for {stage}. Ensure the set up process is done for it."
            self.logger.error(message)
            raise Exception(message)

        # Get the monitors info
        monitors_list = self.get_monitor_instances(
            subscription_id=subscription_id)

        # Get the measurements
        measurements_list = self.get_measurement_ids(
            subscription_id=subscription_id)

        # Add the measurement id to the monitors list
        try:
            self.logger.info("Joining monitors list with measurements list.")
            for monitor in monitors_list:
                for measurement in measurements_list:
                    if monitor["monitor_name"] == measurement["monitor_name"]:
                        monitor["measurement_id"] = measurement["measurement_id"]
        except Exception as e:
            message = f"Failed to append measurement ids to monitors list. {e}"
            self.logger.error(message)
            raise Exception(message)

        # Optionally display the table
        if show_table:
            try:
                print(f"Monitors list for subscription_id {subscription_id}:")
                display(pd.DataFrame.from_dict(monitors_list))
            except Exception as e:
                message = f"Failed to display monitors table. {e}"
                self.logger.error(message)
                raise Exception(message)

        self.logger.info(f"Updating the monitors info for {stage}")
        self.__monitors_info[stage] = monitors_list

        self.logger.info(f"Monitors with measurements ids: {monitors_list}")
        return monitors_list

    def get_metrics_from_monitor_list(
        self,
        stage: EvaluationStage,
        monitor_name: str,
        show_table: bool = False,
    ) -> dict[str, any]:
        """Retrieves metrics from a list of monitors based on the provided
        monitor name.

        Args:
            stage (EvaluationStage): the evaluation stage
            monitor_name (str): The name of the monitor to retrieve metrics for.
            show_table (bool, optional): Whether to display the metrics in a table format. Defaults to False.

        Returns:
            dict[str, any]: A dictionary containing the retrieved metrics data.
        """

        monitors_list = self.__monitors_info.get(stage, None)

        if monitors_list is None:
            message = f"Monitors list for {stage} is not set. Ensure the setup and evaluation steps are done for it."
            self.logger.error(message)
            raise Exception(message)

        monitor = next(
            (
                monitor
                for monitor in monitors_list
                if monitor["monitor_name"] == monitor_name
            ),
            {},
        )

        if (
            monitor.get("monitor_instance_id") is None
            or monitor.get("measurement_id") is None
        ):
            message = f"Missing {monitor_name} monitor details. {monitor}"
            self.logger.error(message)
            raise Exception(message)

        monitor_metrics = self.get_monitor_metrics(
            monitor_instance_id=monitor["monitor_instance_id"],
            measurement_id=monitor["measurement_id"],
        )

        table_data = []
        values = monitor_metrics.get("entity", {}).get("values", {})
        try:
            for value in values:
                metrics_values = value["metrics"]
                tags_list = value["tags"]
                tags = [f"{t['id']}:{t['value']}" for t in tags_list]
                for v in metrics_values:
                    table_data.append(
                        {
                            "ts": monitor_metrics["entity"]["timestamp"],
                            "id": v["id"],
                            "measurement_id": monitor_metrics["metadata"]["id"],
                            "value": v["value"],
                            "lower_limit": v.get("lower_limit", None),
                            "upper_limit": v.get("upper_limit", None),
                            "tags": tags,
                            "monitor_definition_id": monitor_metrics["entity"][
                                "monitor_definition_id"
                            ],
                            "run_id": monitor_metrics["entity"]["run_id"],
                            "target_id": monitor_metrics["entity"]["target"]["target_id"],
                            "target_type": monitor_metrics["entity"]["target"][
                                "target_type"
                            ],
                        }
                    )
        except Exception as e:
            message = f"Failed to parse monitor metrics. {e}"
            self.logger.error(message)
            raise Exception(message)

        self.logger.info(f"metrics for {monitor_name}: {table_data}")

        if show_table:
            try:
                display_message_with_frame(f"Metrics for {monitor_name}")
                display(pd.DataFrame.from_dict(table_data)[
                        ["id", "value", "monitor_definition_id", "ts"]])
            except Exception as e:
                message = f"Failed to display metrics for {monitor_name}. {e}"
                self.logger.error(message)
                raise Exception(message)

        return table_data

    def get_data_set_records_by_id(
        self,
        data_set_id: str,
        show_table: bool = False,
    ) -> dict[str, any]:
        """Retrieves records from a data set using the provided data set ID.

        Args:
            data_set_id (str): The ID of the data set to retrieve records from.
            show_table (bool, optional): Whether to display the records in a table format. Defaults to False.

        Returns:
            dict: The JSON response containing the records.

        Raises:
            Exception: If an error occurs while retrieving or parsing the records.
        """
        try:
            response = self.__send_request(
                method="get",
                url=f"{self.__wos_url}/openscale/{self.service_instance_id}/v2/data_sets/{data_set_id}/records",
            )
        except Exception as e:
            message = f"Failed to get records for data set id: {data_set_id}. {e}"
            self.logger.error(message)
            raise Exception(message)

        try:
            json_response = response.json()
        except Exception as e:
            message = (
                f"Failed to parse records response for data set id: {data_set_id}. {e}"
            )
            self.logger.error(message)
            raise Exception(message)

        if show_table:
            try:
                records = [
                    record["entity"]["values"] for record in json_response["records"]
                ]
                display_message_with_frame(
                    message=f"Records from data set id {data_set_id}"
                )
                display(pd.DataFrame.from_dict(records))
            except Exception as e:
                message = f"Failed to display data sets records. {e}"
                self.logger.error(message)
                raise Exception(message)

        return json_response

    def get_monitor_data_set_records(
        self,
        stage: EvaluationStage,
        data_set_type: str,
        show_table: bool = False
    ) -> dict[str, any]:
        """Retrieves monitor data set records for a given data set type and
        evaluation stage.

        Parameters:
        - stage (EvaluationStage): The evaluation stage for which to retrieve the data set records.
        - data_set_type (str): The type of data set for which to retrieve the records.
        - show_table (bool, optional): Whether to display the data set records in a table. Defaults to False.

        Returns:
        dict[str, any]: A dictionary containing the data set records.
        """
        self.logger.info(
            f"Getting data set records for {data_set_type} for {stage} stage.")
        subscription_id = self.__subscription_ids.get(stage, None)

        if subscription_id is None:
            message = f"Missing subscription_id for {stage}. Ensure the set up process is done for it."
            self.logger.error(message)
            raise Exception(message)

        display_message_with_frame(
            message=f"Getting monitor data set records for data set type '{data_set_type}' from subscription id {subscription_id}",
        )

        # Get the data set for generative ai quality metrics
        datasets = self.get_all_data_sets(
            subscription_id=subscription_id,
            data_set_type=data_set_type,
        )

        try:
            data_set_id = datasets["data_sets"][0]["metadata"]["id"]
        except Exception as e:
            message = f"Failed to parse dataset id. {e}"
            self.logger.error(message)
            raise Exception(message)

        return self.get_data_set_records_by_id(
            data_set_id=data_set_id,
            show_table=show_table,
        )

    def get_all_data_sets(
        self,
        subscription_id: str,
        space_id: str = None,
        project_id: str = None,
        data_set_type: str = None,
    ):
        """Retrieves all data sets for a given subscription ID.

        Args:
            subscription_id (str): The ID of the subscription.
            space_id (str, optional): The ID of the space. Defaults to None.
            project_id (str, optional): The ID of the project. Defaults to None.
            data_set_type (str, optional): The type of data set. Defaults to None.

        Returns:
            dict: The JSON response containing the data sets.

        Raises:
            Exception: If there is an error retrieving or parsing the data sets.
        """
        params = {
            "target.target_id": subscription_id,
            "target.target_type": "subscription",
        }
        if project_id is not None:
            params["project_id"] = project_id
        if space_id is not None:
            params["space_id"] = space_id
        if data_set_type is not None:
            params["type"] = data_set_type

        try:
            response = self.__send_request(
                method="get",
                url=f"{self.__wos_url}/openscale/{self.service_instance_id}/v2/data_sets",
                params=params,
            )
        except Exception as e:
            message = f"Failed to retrieve data sets. {e}"
            self.logger.error(message)
            raise Exception(message)

        try:
            json_response = response.json()
        except Exception as e:
            message = f"Failed to parse data sets response. {e}"
            self.logger.error(message)
            raise Exception(message)

        return json_response

    def add_records_to_data_set(
        self,
        data_set_id: str,
        payload_data: list[dict[str, any]],
        project_id: str = None,
        space_id: str = None,
    ) -> list[dict[str, any]]:
        """Adds records to a data set in the Watson Knowledge Catalog.

        Args:
            data_set_id (str): The ID of the data set to add records to.
            payload_data (list[dict[str, any]]): A list of dictionaries containing the records to add.
            project_id (str, optional): The ID of the project to associate the records with. Defaults to None.
            space_id (str, optional): The ID of the space to associate the records with. Defaults to None.

        Returns:
            list[dict[str, any]]: A list of dictionaries containing the added records.

        Raises:
            Exception: If there is an error adding the records to the data set.
        """
        self.logger.info(
            f"Adding records to data set id: {data_set_id}\nrecords: {payload_data}")
        params = {}
        if space_id is not None:
            params["space_id"] = space_id
        if project_id is not None:
            params["project_id"] = project_id

        try:
            response = self.__send_request(
                method="post",
                url=f"{self.__wos_url}/openscale/{self.service_instance_id}/v2/data_sets/{data_set_id}/records",
                params=params,
                json=payload_data,
            )
        except Exception as e:
            message = f"Failed to add records to data set id {data_set_id}. {e}"
            self.logger.error(message)
            raise Exception(message)

        try:
            json_response = response.json()
        except Exception as e:
            message = f"Failed to parse add records to data set response, {e}"
            self.logger.error(message)
            raise Exception(message)

        return json_response

    def space_deployment_risk_evaluation_data_set_setup(
        self,
        subscription_id: str,
        pl_data: list[dict[str, any]],
        prompt_setup: dict[str, any],
        input_df: pd.DataFrame,
    ):
        """Sets up a data set for evaluating model risk.

        Parameters:
        - subscription_id (str): The ID of the subscription.
        - pl_data (list[dict[str, any]]): A list of dictionaries representing payload logging data.
        - prompt_setup (dict[str, any]): A dictionary representing prompt setup.
        - input_df (pd.Dataframe): The input data frame.

        Returns:
        None
        """
        self.logger.info(
            f"Evaluating model risk for subscription id: {subscription_id}")

        # upload records to data set records to do mrm evaluation
        payload_logging_data_set_list = self.get_all_data_sets(
            subscription_id=subscription_id,
            data_set_type="payload_logging",
        )

        # Parse the data set id
        try:
            payload_logging_data_set_id = payload_logging_data_set_list[
                "data_sets"][0]["metadata"]["id"]
        except Exception as e:
            message = f"Failed to parse payload logging data set id. {e}"
            self.logger.error(message)

        message = f"payload logging data set id: {payload_logging_data_set_id}"
        self.logger.info(message)
        display_message_with_frame(message=message)

        # check if the records are in the data set
        data_set = self.get_data_set_records_by_id(payload_logging_data_set_id)

        # check length if 0, then we need to do add the data
        if len(data_set["records"]) != 0:
            return

        # Now we need to do the upload and wait for the set up to be done
        self.add_records_to_data_set(
            data_set_id=payload_logging_data_set_id,
            payload_data=pl_data,
        )
        print(
            f"Adding payload logging data to data set id: {payload_logging_data_set_id}")
        time.sleep(5)

        # Do the feedback data flow
        feedback_data_set_list = self.get_all_data_sets(
            subscription_id=subscription_id,
            data_set_type="feedback",
        )

        # Parse the data set id
        try:
            feedback_data_set_id = feedback_data_set_list["data_sets"][0]["metadata"]["id"]
        except Exception as e:
            message = f"Failed to parse payload logging data set id. {e}"
            self.logger.error(message)

        message = f"feedback data set id: {feedback_data_set_id}"
        self.logger.info(message)
        display_message_with_frame(message=message)

        # check if the records are in the data set
        feedback_data_set = self.get_data_set_records_by_id(
            feedback_data_set_id)

        # check length if 0, then we need to do add pl data
        if len(feedback_data_set["records"]) != 0:
            return

        # Build the payload and add the data to the data set
        feedback_data = self.__generate_feedback_data(
            input_df=input_df,
            pl_data=pl_data,
            prompt_setup=prompt_setup,
        )

        # Add the feedback data set and wait for the upload to be done
        self.add_records_to_data_set(
            data_set_id=feedback_data_set_id,
            payload_data=feedback_data,
        )
        print(f"Adding feedback data to data set id: {feedback_data_set_id}")
        time.sleep(5)

    def __generate_feedback_data(
            self,
            input_df: pd.DataFrame,
            pl_data: list[dict[str, any]],
            prompt_setup: dict[str, any]
    ) -> list[dict[str, any]]:
        """Generates feedback data for a given input file path, prediction
        data, and prompt setup.

        Args:
            input_df(str): A pandas DataFrame containing the input data.
            pl_data (list[dict[str, any]]): A list of dictionaries containing prediction data.
            prompt_setup (dict[str, any]): A dictionary containing the necessary information for generating the feedback data.

        Returns:
            list[dict[str, any]]: A list of dictionaries containing the generated feedback data.
        """
        self.logger.info(
            f"Generating add feedback dataset payload. prompt setup: {prompt_setup}")

        try:
            prompt_template_variables = self.__get_prompt_template_input_variables_list()
            fields = prompt_template_variables + [prompt_setup["label_column"]]
        except Exception as e:
            message = f"Failed to retrieve fields from the prompt set up. {e}"
            self.logger.error(message)
            raise Exception(message)

        # Build the payload based on the supplied file and the evaluation response
        feedback_data_values = []
        for row, prediction in zip(input_df.to_dict(orient="records"), pl_data):
            result_row = [row[key] for key in fields if key in row.keys()]
            result_row.append(
                prediction["response"]["results"][0]["generated_text"]
            )
            feedback_data_values.append(result_row)

        fields.append("_original_prediction")

        return [
            {
                "fields": fields,
                "values": feedback_data_values,
            }
        ]

    def __instance_mapping_for_cpd(
        self,
        stage: EvaluationStage,
    ) -> None:
        """Function to check if the given stage has a cpd instance mapping. If
        not it will be set to the default service instance id would be
        "00000000-0000-0000-0000-000000000000".

        Args:
           stage (EvaluationStage): The stage where the instance mapping is checked and set.
        """

        url = f"{self.__wos_url}/openscale/v2/instance_mappings"
        params = {}
        if stage == EvaluationStage.DEVELOPMENT:
            params["project_id"] = self.__stage_configurations[stage].project_id
        else:
            params["space_id"] = self.__stage_configurations[stage].space_id

        try:
            self.logger.info(
                f"Checking instance mapping for {stage} stage. {params}")
            response = self.__send_request(
                method="get",
                url=url,
                params=params,
            )
        except Exception as e:
            message = f"Failed to get instance mapping. {e}"
            self.logger.error(message)
            raise Exception(message)

        try:
            # Check if the instance mapping already exists and return, otherwise use the instance mapping from the configuration
            json_response = response.json()
            if len(json_response.get("instance_mappings", [])) > 0:
                self.logger.info(
                    f"Instance mapping already done for {stage} stage.")
                return
        except Exception as e:
            message = f"Failed to parse instance mapping response. {e}"
            self.logger.error(message)
            raise Exception(message)

        # Build the payload
        # Sample payload
        # {
        #     "service_instance_id": "00000000-0000-0000-0000-000000000000",
        #     "target": {
        #         "target_type": "space/project",
        #         "target_id": "space_id/project_id",
        #     },
        # }
        if stage == EvaluationStage.DEVELOPMENT:
            target = {
                "target_type": "project",
                "target_id": self.__stage_configurations[stage].project_id
            }
        else:
            target = {
                "target_type": "space",
                "target_id": self.__stage_configurations[stage].space_id
            }
        payload = {
            "service_instance_id": self.service_instance_id,
            "target": target
        }

        try:
            response = self.__send_request(
                method="post",
                url=url,
                json=payload
            )
        except Exception as e:
            message = f"Failed to map service instance id. {e}"
            self.logger.error(message)
            raise Exception(message)

        self.logger.info("Instance mapping done successfully.")

    def setup(
        self,
        configuration: dict,
        prompt_template: PromptTemplate | DetachedPromptTemplate = None,
        prompt_template_id: str = None,
        setup_stages: list[EvaluationStage] = [
            EvaluationStage.DEVELOPMENT, EvaluationStage.PRODUCTION],
    ) -> None:
        """Function to create do the set up based on the configuration
        provided.

        This will do the following:
           - By default, the set up will be done for the development and production stages.
           - Create the prompt template asset
           - Prompt set up in the provided projects and spaces
           - Monitor set up
           - Associate the prompt template with a usecase -- optional

        Args:
            configuration (dict): The configuration dictionary
                Configurations structure:
                configurations =
                    {
                        "common_configurations": {
                            "credentials": {
                                "iam_url": "",
                                "apikey": "",
                            },
                            "ai_usecase": { // optional
                                "ai_usecase_id": str,
                                "catalog_id": str,
                                "approach_version": str,
                                "approach_id": str,
                            }
                            "service_instance_id": "",
                            "use_ssl": bool,
                            "use_cpd": bool,
                            "wml_url": str,
                            "platform_url": str,
                            "wos_url": str,
                            "dataplatform_url": str,
                        },
                        "development": {
                            "project_id": "",
                            "prompt_setup": {...},
                        },
                        "pre_production": {
                            "space_id": "",
                            "space_deployment": {...},
                            "prompt_setup": {...},
                        },
                        "production": {
                            "space_id": "",
                            "space_deployment": {...},
                            "prompt_setup": {...},
                        },
                    }
            prompt_template (PromptTemplate): The prompt template to evaluate.
            prompt_template_id (str): Prompt template id for an existing prompt.
            setup_stages (list[EvaluationStage]): list of stages to do the prompt set up, development stage will always be required. Defaults to [ EvaluationStage.development, EvaluationStage.production]
        """

        if prompt_template is None and prompt_template_id is None:
            raise Exception(
                "Please provide either prompt_template or prompt_template_id")

        # set setup stages
        self.setup_stages = setup_stages

        # Validate inputs before parsing the config
        self.__validate_configuration(config=configuration)

        # Parse the configuration
        self.__parse_configuration(config=configuration)

        # Authenticate
        try:
            self.__authenticator = Authenticator(
                credentials=self.credentials,
                use_cpd=self.use_cpd,
                use_ssl=self.use_ssl,
            )
            self.__iam_access_token = self.__authenticator.authenticate()
        except Exception as e:
            message = f"Failed to authenticate the client. {e}"
            self.logger.error(message)
            raise Exception(message)

        # Development stage should be set up first
        for stage in [EvaluationStage.DEVELOPMENT, EvaluationStage.PRE_PRODUCTION, EvaluationStage.PRODUCTION]:
            if stage not in self.setup_stages:
                continue

            message = f"Starting setup process for {stage.value}"
            self.logger.info(message)
            display_message_with_frame(message=message)

            # If using CPD, check the instance mapping and set it up if it does not exist
            if self.use_cpd:
                self.__instance_mapping_for_cpd(stage=stage)

            # If we are doing the set up for development, use the setup flow for a project
            if stage == EvaluationStage.DEVELOPMENT:
                # Do the setup for project
                self.logger.info(f"Setting up {stage.value} environment")

                # If the user provided a prompt template, use it, otherwise use the prompt template id
                if prompt_template:
                    self.__prompt_template_ids[stage] = self.create_prompt_template_using_wxai(
                        prompt_template=prompt_template,
                        stage=stage,
                    )
                else:
                    self.__prompt_template_ids[stage] = self.get_prompt_template_details_from_wxai(
                        prompt_template_id=prompt_template_id,
                        stage=stage,
                    )

                self.is_detached = isinstance(
                    self.__stage_configurations[stage].prompt_template, DetachedPromptTemplate)

                self.trigger_prompt_setup(stage)

                if not self.is_detached:
                    self.__scoring_urls[stage] = self.get_scoring_url(
                        self.__subscription_ids[stage])

                    display_message_with_frame(
                        message=f"Development scoring url: {self.__scoring_urls[stage]}"
                    )

                display_message_with_frame(
                    message=f"{stage.value} monitors:"
                )
                self.__monitors_info[stage] = (
                    self.get_monitors_with_measurements_info(
                        stage=stage,
                        show_table=True,
                    )
                )
                display_message_with_frame(
                    message=f"{stage.value} prompt set up finished successfully"
                )

            # If we are doing the set up for production or pre_production, use the setup flow for a space
            elif stage in [EvaluationStage.PRE_PRODUCTION, EvaluationStage.PRODUCTION]:
                # Do the setup for space
                self.logger.info(f"Setting up {stage.value} space environment")

                if prompt_template_id or self.__stage_configurations[EvaluationStage.DEVELOPMENT].project_id:
                    # If the prompt template id was provided by the user, retrieve the prompt details.
                    if prompt_template_id:
                        self.__prompt_template_ids[EvaluationStage.DEVELOPMENT] = self.get_prompt_template_details_from_wxai(
                            prompt_template_id=prompt_template_id,
                            stage=EvaluationStage.DEVELOPMENT,
                        )

                        self.is_detached = isinstance(
                            self.__stage_configurations[EvaluationStage.DEVELOPMENT].prompt_template, DetachedPromptTemplate)

                        self.__stage_configurations[stage].space_deployment["base_model_id"] = self.__stage_configurations[
                            EvaluationStage.DEVELOPMENT].prompt_template.model_id

                    self.__prompt_template_ids[stage] = self.promote_prompt_to_space(
                        # Always promote the template from the development environment
                        project_id=self.__stage_configurations[EvaluationStage.DEVELOPMENT].project_id,
                        project_prompt_template_id=self.__prompt_template_ids[
                            EvaluationStage.DEVELOPMENT],
                        space_id=self.__stage_configurations[stage].space_id,
                    )
                else:
                    self.__prompt_template_ids[stage] = self.create_prompt_template_using_wxai(
                        prompt_template=prompt_template,
                        stage=stage,
                    )
                    self.is_detached = isinstance(
                        self.__stage_configurations[stage].prompt_template, DetachedPromptTemplate)

                self.__deployment_ids[stage] = self.create_pta_space_deployment(
                    space_configurations=self.__stage_configurations[stage],
                    space_prompt_template_id=self.__prompt_template_ids[stage],
                )
                self.trigger_prompt_setup(stage)

                if not self.is_detached:
                    self.__scoring_urls[stage] = self.get_scoring_url(
                        self.__subscription_ids[stage])

                display_message_with_frame(
                    message=f"{stage.value} scoring url: {self.__scoring_urls[stage]}"
                )

                display_message_with_frame(
                    message=f"{stage.value} monitors:"
                )
                self.__monitors_info[stage] = (
                    self.get_monitors_with_measurements_info(
                        stage=stage,
                        show_table=True,
                    )
                )
                display_message_with_frame(
                    message=f"{stage.value} prompt set up finished successfully"
                )

            # Track the prompt template with a usecase
            if self.ai_usecase:
                self.__track_pta_with_usecase(stage)

    def __parse_configuration(self, config: dict) -> None:
        """Function to parse the configuration. This assumes that the
        configuration object is already validated.

        Args:
            config (dict): validated configuration object.
        """
        # Parse the config
        self.config = config

        # Parse common_configurations
        self.use_cpd: bool = self.config["common_configurations"]["use_cpd"]
        self.credentials: dict[str, str] = self.config["common_configurations"][
            "credentials"
        ]
        self.use_ssl: bool = self.config["common_configurations"]["use_ssl"]
        self.service_instance_id: str = self.config["common_configurations"].get(
            "service_instance_id", "00000000-0000-0000-0000-000000000000"
        )
        self.wml_url: str = self.config["common_configurations"].get(
            "wml_url", "https://us-south.ml.cloud.ibm.com")
        self.platform_url: str = self.config["common_configurations"].get(
            "platform_url", "https://dataplatform.cloud.ibm.com")
        self.wos_url: str = self.config["common_configurations"].get(
            "wos_url", "https://api.aiopenscale.cloud.ibm.com")
        self.dataplatform_url: str = self.config["common_configurations"].get(
            "dataplatform_url", "https://api.dataplatform.cloud.ibm.com"
        )

        # Parse model usecase details if provided by the user
        if self.config["common_configurations"].get("ai_usecase"):
            usecase = self.config["common_configurations"].get("ai_usecase")
            self.ai_usecase = ModelUsecase(
                usecase_id=usecase.get("ai_usecase_id"),
                catalog_id=usecase.get("catalog_id"),
                version=usecase.get("approach_version"),
                approach_id=usecase.get("approach_id"),
            )

        # Parse development related configurations
        self.__stage_configurations[EvaluationStage.DEVELOPMENT].prompt_setup = self.config.get(
            "development", {}).get("prompt_setup")
        self.__stage_configurations[EvaluationStage.DEVELOPMENT].project_id = self.config.get(
            "development", {}).get("project_id")

        # Parse pre_production related configurations
        if EvaluationStage.PRE_PRODUCTION in self.setup_stages:
            # Check if we have project or space, then init the config option
            self.__stage_configurations[EvaluationStage.PRE_PRODUCTION].space_id = self.config["pre_production"]["space_id"]
            self.__stage_configurations[EvaluationStage.PRE_PRODUCTION].space_deployment = self.config["pre_production"]["space_deployment"]
            self.__stage_configurations[EvaluationStage.PRE_PRODUCTION].prompt_setup = self.config["pre_production"]["prompt_setup"]

        # Parse production related configurations
        if EvaluationStage.PRODUCTION in self.setup_stages:
            self.__stage_configurations[EvaluationStage.PRODUCTION].space_id = self.config["production"]["space_id"]
            self.__stage_configurations[EvaluationStage.PRODUCTION].space_deployment = self.config["production"]["space_deployment"]
            self.__stage_configurations[EvaluationStage.PRODUCTION].prompt_setup = self.config["production"]["prompt_setup"]

        # Parse the credentials
        if self.use_cpd:
            self.__platform_url = self.credentials["url"]
            self.__wos_url = self.credentials["url"]
            self.__dataplatform_url = self.credentials["url"]
            self.__wml_url = self.credentials["url"]
        else:
            self.__wml_url = self.wml_url
            self.__platform_url = self.platform_url
            self.__wos_url = self.wos_url
            self.__dataplatform_url = self.dataplatform_url

    def get_monitors_info(self, stage: EvaluationStage):
        """Retrieves monitor information based on the provided stage.

        Args:
            stage (EvaluationStage): The stage for which monitor information is required.

        Returns:
            dict: A dictionary containing monitor information.

        Raises:
            Exception: If the monitor info is not set
        """
        self.logger.info(f"Retrieving monitors info for {stage}")
        monitors_info = self.__monitors_info.get(stage, None)
        if monitors_info is None:
            message = f"monitors info for the stage {stage} is not set"
            self.logger.error(message)
            raise Exception(message)

        return monitors_info

    def __generate_detached_prompt_payload_data(self, input_df: pd.DataFrame, prediction_field: str = "generated_text") -> list[dict[str, any]]:
        """
        Helper method to generate the payload data for detached prompt

        Args:
            input_df (pd.DataFrame): The detached prompt dataframe
            prediction_field (str): column name for the prediction value. Defaults to "generated_text"

        Returns:
            list[dict[str, any]]: payload data
        """
        self.logger.info("Generating payload data for detached prompt")

        prompt_template_variables = self.__get_prompt_template_input_variables_list()

        pl_data = []
        for _, row in input_df.iterrows():
            pl_data.append(
                {
                    "request": {
                        "parameters": {
                            "template_variables": {
                                k: str(row[k]) for k in prompt_template_variables
                            }
                        }
                    },
                    "response": {
                        "results": [{"generated_text": str(row[prediction_field])}]
                    }
                }
            )
        return pl_data

    def evaluate(
        self,
        input_df: pd.DataFrame,
        evaluation_stages: list[EvaluationStage] = [
            EvaluationStage.DEVELOPMENT,
            EvaluationStage.PRODUCTION,
        ],
    ) -> None:
        """Evaluate the input data in the specified stages.

        Args:
            input_df (pd.DataFrame): The input dataframe to be evaluated. This should only contain the columns required by the prompt template.
            evaluation_stages (list[EvaluationStage], optional): list of environment stages to evaluate the dataframe in.
                    The stages here must exist in setup_stages in setup() too. Defaults to [ EvaluationStage.development, EvaluationStage.production].
        """
        self.logger.info(
            f"Evaluating the input data in {[stage.value for stage in evaluation_stages]} environments"
        )
        if self.config is None:
            message = "Configuration is not set yet."
            self.logger.error(message)
            raise Exception(message)

        # Validate the we have the evaluation stage as part of the setup stages
        for stage in evaluation_stages:
            if stage not in self.setup_stages:
                message = f"The set up step for stage {stage} was not done."
                self.logger.error(message)
                raise Exception(message)

        for stage in evaluation_stages:
            display_message_with_frame(
                message=f"Starting evaluation for {stage.value} stage",
            )

            if stage == EvaluationStage.DEVELOPMENT:
                if not self.is_detached and not self.__scoring_urls[stage]:
                    raise Exception(f"{stage.value} scoring url is not set")

                # Get the MRM monitor id
                mrm_monitors = self.get_monitor_instances(
                    subscription_id=self.__subscription_ids[stage],
                    monitor_definition_id="mrm",
                )
                if not mrm_monitors:
                    message = "MRM monitor is not configured"
                    self.logger.error(message)
                    raise Exception(message)

                mrm_monitor_id = mrm_monitors[0]["monitor_instance_id"]

                # Do the risk evaluations
                self.risk_evaluation_for_pta_subscription(
                    input_df=input_df,
                    monitor_instance_id=mrm_monitor_id,
                )

                # Get all the monitors with measurements ids and display its table
                self.__monitors_info[stage] = (
                    self.get_monitors_with_measurements_info(
                        stage=stage,
                        show_table=True,
                    )
                )

                # Display the factsheet url
                self.display_factsheet_url(stage=stage)

            elif stage in [EvaluationStage.PRE_PRODUCTION, EvaluationStage.PRODUCTION]:

                if self.is_detached:
                    # Get the payload_data from the cvs file
                    pl_data = self.__generate_detached_prompt_payload_data(
                        input_df=input_df,
                        prediction_field=self.__stage_configurations[stage].prompt_setup.get(
                            "prediction_field", "generated_text")
                    )
                else:
                    if not self.__scoring_urls[stage]:
                        raise Exception(
                            f"{stage.value} scoring url is not set")
                    # Evaluate the dataframe
                    pl_data = self.evaluate_df(
                        input_df=input_df,
                        scoring_url=self.__scoring_urls[stage],
                    )

                self.space_deployment_risk_evaluation_data_set_setup(
                    subscription_id=self.__subscription_ids[stage],
                    pl_data=pl_data,
                    prompt_setup=self.__stage_configurations[stage].prompt_setup,
                    input_df=input_df,
                )

                # Get the MRM monitor id
                mrm_monitors = self.get_monitor_instances(
                    subscription_id=self.__subscription_ids[stage],
                    monitor_definition_id="mrm",
                )
                if not mrm_monitors:
                    message = "MRM monitor is not configured"
                    self.logger.error(message)
                    raise Exception(message)

                mrm_monitor_id = mrm_monitors[0]["monitor_instance_id"]

                # Evaluate mrm monitor
                if stage == EvaluationStage.PRE_PRODUCTION:
                    self.risk_evaluation_for_pta_subscription(
                        input_df=input_df,
                        monitor_instance_id=mrm_monitor_id,
                    )
                else:
                    self.risk_evaluation_for_pta_subscription_in_space(
                        monitor_instance_id=mrm_monitor_id
                    )

                # Get the pre production monitors info with their measurement id
                self.__monitors_info[stage] = (
                    self.get_monitors_with_measurements_info(
                        stage=stage,
                        show_table=True,
                    )
                )

                # display the factsheet url
                self.display_factsheet_url(stage=stage)

            display_message_with_frame(
                message=f"Finished evaluation for {stage.value} stage",
            )

    def get_prompt_template_id(self, stage: EvaluationStage = EvaluationStage.DEVELOPMENT):
        return self.__prompt_template_ids[stage]

    def __is_workspace_associated_with_usecase(
        self,
        usecase_id: str,
        catalog_id: str,
        workspace_id: str
    ):
        """Helper to check if workspace is associated with a usecase"""

        display_message_with_frame(
            f"Checking if workspace {workspace_id} is associated with usecase {usecase_id}."
        )

        try:
            response = self.__send_request(
                method="get",
                url=f"{self.__dataplatform_url}/v1/aigov/factsheet/ai_usecases/{usecase_id}/workspaces",
                params={"inventory_id": catalog_id},
            )
        except Exception as e:
            raise Exception(
                f"Failed to check if workspace is associated with usecase. {e}")

        try:
            json_response = response.json()
            for associated_workspace in json_response["associated_workspaces"]:
                for workspace in associated_workspace["workspaces"]:
                    if workspace["id"] == workspace_id:
                        return True
        except Exception as e:
            raise Exception(f"Failed to parse workspaces ids response. {e}")

        return False

    def __associate_workspace_with_usecase(
        self,
        usecase_id: str,
        catalog_id: str,
        workspace: Union[ProjectConfigurations, SpaceConfigurations],
    ):
        """Helper to associate a workspace with a usecase"""
        if isinstance(workspace, ProjectConfigurations):
            workspace_id = workspace.project_id
            workspace_type = "project"
            phase_name = "Develop"
        else:
            workspace_id = workspace.space_id
            workspace_type = "space"
            phase_name = "Operate"

        display_message_with_frame(
            f"Associating workspace id {workspace_id} with usecase {usecase_id}"
        )

        payload = {
            "phase_name": phase_name,
            "workspaces": [
                {
                    "id": workspace_id,
                    "type": workspace_type,

                }
            ],
        }

        try:
            self.__send_request(
                method="post",
                url=f"{self.__dataplatform_url}/v1/aigov/factsheet/ai_usecases/{usecase_id}/workspaces",
                params={"inventory_id": catalog_id},
                json=payload,
            )
        except Exception as e:
            raise Exception(f"Failed to associate workspace with usecase. {e}")

        display_message_with_frame(
            "Workspace associated with usecase successfully")

    def __track_pta_with_usecase(self, stage):
        """
        Helper function to associate workspace with usecase in factsheet
        """
        display_message_with_frame(
            "Starting Prompt template usecase tracking process")

        if isinstance(self.__stage_configurations[stage], ProjectConfigurations):
            params = {
                "project_id": self.__stage_configurations[stage].project_id}
            workspace_id = self.__stage_configurations[stage].project_id
        else:
            params = {"space_id": self.__stage_configurations[stage].space_id}
            workspace_id = self.__stage_configurations[stage].space_id

        if not self.__is_workspace_associated_with_usecase(
            usecase_id=self.ai_usecase.usecase_id,
            catalog_id=self.ai_usecase.catalog_id,
            workspace_id=workspace_id,
        ):
            self.__associate_workspace_with_usecase(
                usecase_id=self.ai_usecase.usecase_id,
                catalog_id=self.ai_usecase.catalog_id,
                workspace=self.__stage_configurations[stage],

            )

        payload = {
            "model_entry_catalog_id": self.ai_usecase.catalog_id,
            "model_entry_asset_id": self.ai_usecase.usecase_id,
            "version_details": {
                "number": self.ai_usecase.version,
            }
        }

        if self.ai_usecase.approach_id:
            payload["version_details"]["approach_id"] = self.ai_usecase.approach_id

        try:
            self.__send_request(
                method="post",
                url=f"{self.__dataplatform_url}/v1/aigov/model_inventory/models/{self.__prompt_template_ids[stage]}/model_entry",
                json=payload,
                params=params,

            )
        except Exception as e:
            message = f"Failed to track usecase. {e}"
            self.logger.debug(message)
            return

        display_message_with_frame(
            message=f"Prompt template id {self.__prompt_template_ids[stage]} is tracked with usecase id {self.ai_usecase.usecase_id} successfully."
        )
