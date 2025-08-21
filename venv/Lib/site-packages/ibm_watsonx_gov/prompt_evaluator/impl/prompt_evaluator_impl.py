# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2025
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

import calendar
import time
from urllib.parse import urlparse, urlunparse

import pandas as pd
from ibm_watsonx_ai.foundation_models.prompts.prompt_template import (
    DetachedPromptTemplate, PromptTemplate)

from ibm_watsonx_gov.entities.container import (BaseMonitor, ProjectContainer,
                                                SpaceContainer)
from ibm_watsonx_gov.entities.credentials import Credentials
from ibm_watsonx_gov.entities.enums import (ContainerType, EvaluationStage,
                                            TaskType)
from ibm_watsonx_gov.entities.monitor import (GenerativeAIQualityMonitor,
                                              QualityMonitor)
from ibm_watsonx_gov.entities.prompt_setup import PromptSetup
from ibm_watsonx_gov.prompt_evaluator.impl.pta_lifecycle_evaluator import \
    PTALifecycleEvaluator
from ibm_watsonx_gov.utils.url_mapping import WOS_URL_MAPPING


class PromptEvaluatorImpl:
    DEFAULT_MODEL_ID = "ibm/granite-3-2-8b-instruct"
    DEFAULT_PROMPT_NAME = "Insurance RAG ChatBot Prompt"
    DEFAULT_PROMPT_URL = "https://us-south.ml.cloud.ibm.com/ml/v1/deployments/insurance_test_deployment/text/generation?version=2021-05-01"
    DEFAULT_APPROACH_VERSION = "0.0.1"

    def __init__(self, credentials: Credentials | None = None):
        if not credentials:
            self.credentials = Credentials.create_from_env()
        else:
            self.credentials = credentials

        self.__pta_evaluator = PTALifecycleEvaluator()

    def __get_credentials_dict(self) -> dict[str, any]:
        if self.credentials.version:
            # Use use cpd
            return {
                "url": self.credentials.url,
                "username": self.credentials.username,
                "api_key": self.credentials.api_key,
            }

        # Use cloud
        if not self.credentials.service_instance_id:
            raise Exception("Missing service_instance_id from the credentials")
        return {
            "iam_url": WOS_URL_MAPPING.get(self.credentials.url).iam_url,
            "apikey": self.credentials.api_key,
        }

    def e2e_prompt_evaluation(
        self,
        config: dict[str, any],
        input_file_path: str = None,
    ):
        parsed_config = self.__parse_simplified_config_dict(config)

        if input_file_path:
            try:
                input_df = pd.read_csv(input_file_path)
            except Exception as e:
                raise Exception(
                    f"Failed to open the file {input_file_path}. {e}")

        if not parsed_config["prompt_template_id"] and EvaluationStage.DEVELOPMENT in parsed_config["setup_stages"]:
            self.__pta_evaluator.setup(
                configuration=parsed_config["configuration"],
                setup_stages=[EvaluationStage.DEVELOPMENT],
                prompt_template=parsed_config["prompt_template"],
            )

            if input_file_path:
                self.__pta_evaluator.evaluate(
                    input_df=input_df,
                    evaluation_stages=[EvaluationStage.DEVELOPMENT],
                )

            prompt_template_id = self.__pta_evaluator.get_prompt_template_id()
        else:
            prompt_template_id = parsed_config["prompt_template_id"]

        if EvaluationStage.PRODUCTION in parsed_config["setup_stages"]:
            self.__pta_evaluator.setup(
                configuration=parsed_config["configuration"],
                setup_stages=[EvaluationStage.PRODUCTION],
                prompt_template_id=prompt_template_id,
                prompt_template=parsed_config["prompt_template"],
            )

            if input_file_path:
                self.__pta_evaluator.evaluate(
                    input_df=input_df,
                    evaluation_stages=[EvaluationStage.PRODUCTION],
                )

    def evaluate_risk(
        self,
        containers: list[ProjectContainer | SpaceContainer],
        evaluation_stages: list[EvaluationStage],
        input_file_path: str,
        prompt_setup: PromptSetup,
        prompt_template: PromptTemplate | DetachedPromptTemplate = None,
        prompt_template_id: str = None,
    ):
        if prompt_template is None and prompt_template_id is None:
            raise Exception(
                "Please provide Either prompt_template or prompt_template_id"
            )

        prompt_setup_base = {
            "label_column": prompt_setup.label_column,
            "context_fields": prompt_setup.context_fields,
            "question_field": prompt_setup.question_field,
            "problem_type": prompt_setup.task_type.value,
            "input_data_type": prompt_setup.input_data_type.value,
            "prediction_field": prompt_setup.prediction_field,
        }

        stages = {}

        for container in containers:
            stage = {"prompt_setup": prompt_setup_base.copy()}
            stage["prompt_setup"]["operational_space_id"] = container.stage.value

            if container.monitors:
                monitors = {}
                for monitor in container.monitors:
                    monitors[monitor.monitor_name] = {}
                    if monitor.thresholds:
                        monitors[monitor.monitor_name][
                            "thresholds"
                        ] = monitor.thresholds
                    if monitor.parameters:
                        monitors[monitor.monitor_name][
                            "parameters"
                        ] = monitor.parameters

                stage["prompt_setup"]["monitors"] = monitors

            if container.stage == EvaluationStage.DEVELOPMENT:
                stage["project_id"] = container.container_id

            elif container.stage in [
                EvaluationStage.PRE_PRODUCTION,
                EvaluationStage.PRODUCTION,
            ]:
                if container.container_type == ContainerType.PROJECT:
                    stage["project_id"] = container.container_id
                else:
                    stage["space_id"] = container.container_id
                    stage["space_deployment"] = {
                        "serving_name": container.serving_name,
                        "base_model_id": container.base_model_id,
                        "description": container.description,
                        "name": container.name,
                        "version_date": container.version_date,
                    }

            stages[container.stage.value] = stage

        pta_evaluator_config = {
            "common_configurations": {
                "credentials": self.__get_credentials_dict(),
                "use_cpd": self.credentials.version is not None,
                "use_ssl": not self.credentials.disable_ssl,
                "service_instance_id": (
                    self.credentials.service_instance_id
                    if self.credentials.service_instance_id
                    else "00000000-0000-0000-0000-000000000000"
                ),
            },
            **stages,
        }

        self.__pta_evaluator.setup(
            configuration=pta_evaluator_config,
            setup_stages=evaluation_stages,
            prompt_template=prompt_template,
            prompt_template_id=prompt_template_id,
        )

        try:
            input_df = pd.read_csv(input_file_path)
        except Exception as e:
            raise Exception(f"Failed to open the file {input_file_path}. {e}")

        self.__pta_evaluator.evaluate(
            input_df=input_df,
            evaluation_stages=evaluation_stages,
        )

    def get_monitor_metrics(
        self,
        monitor: BaseMonitor,
        evaluation_stage: EvaluationStage = EvaluationStage.DEVELOPMENT,
        show_table: bool = False,
    ) -> dict[str, any]:
        return self.__pta_evaluator.get_metrics_from_monitor_list(
            stage=evaluation_stage,
            monitor_name=monitor.monitor_name,
            show_table=show_table,
        )

    def get_dataset_records(
        self,
        dataset_type: str,
        evaluation_stage: EvaluationStage = EvaluationStage.DEVELOPMENT,
        show_table: bool = False,
    ) -> dict[str, any]:
        return self.__pta_evaluator.get_monitor_data_set_records(
            stage=evaluation_stage,
            data_set_type=dataset_type,
            show_table=show_table,
        )

    def __get_setup_stages_from_config(self, config: dict[str, any]):
        evaluation_stages = []

        if "development_project_id" in config.keys():
            evaluation_stages.append(EvaluationStage.DEVELOPMENT)

        if "production_space_id" in config.keys():
            evaluation_stages.append(EvaluationStage.PRODUCTION)

        return evaluation_stages

    def __parse_prompt_config_from_dict(self, config: dict[str, any]):
        if "prompt_template" in config.keys():
            return self.__build_prompt_template_object(
                config.get("prompt_template")
            )

        if "detached_prompt_template" in config.keys():
            return self.__build_detached_prompt_template_object(
                config.get("detached_prompt_template")
            )

        return None

    def __parse_simplified_config_dict(
        self,
        config: dict[str, any]
    ):
        return {
            "configuration": self.__build_pta_evaluator_config(config),
            "setup_stages": self.__get_setup_stages_from_config(config),
            "prompt_template": self.__parse_prompt_config_from_dict(config),
            "prompt_template_id": config.get("prompt_template_id", config.get("detached_prompt_template_id")),
        }

    def __build_prompt_template_object(
        self, prompt_template_dict: dict[str, any]
    ) -> PromptTemplate:
        required_fields = [
            "input_text",
            "input_variables",
            "task_ids",
        ]
        missing_fields = required_fields - prompt_template_dict.keys()

        if len(missing_fields) > 0:
            raise Exception(f"Missing required values: {missing_fields}")

        return PromptTemplate(
            name=prompt_template_dict.get("name", self.DEFAULT_PROMPT_NAME),
            description=prompt_template_dict.get("description", ""),
            model_id=prompt_template_dict.get(
                "model_id", self.DEFAULT_MODEL_ID),
            input_text=prompt_template_dict.get("input_text", ""),
            input_variables=prompt_template_dict.get("input_variables", []),
            task_ids=prompt_template_dict.get("task_ids", []),
        )

    def __build_detached_prompt_template_object(
        self, detached_prompt_dict: dict[str, any]
    ) -> DetachedPromptTemplate:
        required_fields = [
            "input_text",
            "input_variables",
            "task_ids",
        ]
        missing_fields = required_fields - detached_prompt_dict.keys()

        if len(missing_fields) > 0:
            raise Exception(f"Missing required values: {missing_fields}")

        return DetachedPromptTemplate(
            name=detached_prompt_dict.get("name", self.DEFAULT_PROMPT_NAME),
            model_id=detached_prompt_dict.get(
                "model_id", self.DEFAULT_MODEL_ID),
            input_text=detached_prompt_dict.get("input_text", ""),
            input_variables=detached_prompt_dict.get("input_variables", []),
            detached_prompt_id=detached_prompt_dict.get(
                "detached_prompt_id", ""),
            detached_model_id=detached_prompt_dict.get(
                "detached_model_id", self.DEFAULT_MODEL_ID),
            detached_model_provider=detached_prompt_dict.get(
                "detached_model_provider", ""
            ),
            detached_model_name=detached_prompt_dict.get(
                "detached_model_name", ""),
            detached_model_url=detached_prompt_dict.get(
                "detached_model_url", ""),
            detached_prompt_url=detached_prompt_dict.get(
                "detached_prompt_url", self.DEFAULT_PROMPT_NAME),
            detached_prompt_additional_information=detached_prompt_dict.get(
                "detached_prompt_additional_information", None
            ),
            task_ids=detached_prompt_dict.get("task_ids", []),
        )

    def __build_base_prompt_setup(self, input_prompt_setup: dict[str, any]):
        problem_type = input_prompt_setup.get("problem_type", None)

        if not problem_type:
            raise Exception("Missing `problem_type` from the configuration")

        prompt_setup = {}
        prompt_setup["problem_type"] = problem_type

        prompt_setup["input_data_type"] = input_prompt_setup.get(
            "input_data_type", "unstructured_text"
        )
        prompt_setup["prediction_field"] = input_prompt_setup.get(
            "prediction_field", "generated_text"
        )

        # Use the default values based on the problem type
        if problem_type == TaskType.RAG.value:
            prompt_setup["question_field"] = input_prompt_setup.get(
                "question_field", "question"
            )
            prompt_setup["label_column"] = input_prompt_setup.get(
                "label_column", "answer"
            )
            prompt_setup["context_fields"] = input_prompt_setup.get(
                "context_fields")

        elif problem_type == TaskType.SUMMARIZATION.value:
            prompt_setup["label_column"] = input_prompt_setup.get(
                "label_column", "ground_truth"
            )

        elif problem_type == TaskType.QA.value:
            prompt_setup["label_column"] = input_prompt_setup.get(
                "label_column", "answers"
            )

        elif problem_type == TaskType.GENERATION.value:
            prompt_setup["label_column"] = input_prompt_setup.get(
                "label_column", "reference"
            )

        elif problem_type == TaskType.EXTRACTION.value:
            prompt_setup["label_column"] = input_prompt_setup.get(
                "label_column", "answer"
            )

        elif problem_type == TaskType.CLASSIFICATION.value:
            prompt_setup["label_column"] = input_prompt_setup.get(
                "label_column", "class_name"
            )

        else:
            raise Exception(
                f"unsupported `problem_type`: {problem_type}. Supported values: {TaskType.values()}"
            )

        return prompt_setup

    def __convert_monitor_to_dict(
        self, monitors_list: list[BaseMonitor], task_type: TaskType
    ):
        if not monitors_list:
            if task_type == TaskType.CLASSIFICATION.value:
                monitors_list = [QualityMonitor()]
            if task_type == TaskType.SUMMARIZATION.value:
                monitors_list = [GenerativeAIQualityMonitor(
                    parameters={
                        "metrics_configuration": {
                            "bleu": {},
                            "cosine_similarity": {},
                            "hap_score": {},
                            "jaccard_similarity": {},
                            "meteor": {},
                            "normalized_f1": {},
                            "normalized_precision": {},
                            "normalized_recall": {},
                            "rouge_score": {},
                            "sari": {},
                            "pii": {},
                        },
                    }
                )]
            else:
                monitors_list = [GenerativeAIQualityMonitor()]

        monitors = {}
        for monitor in monitors_list:
            monitors[monitor.monitor_name] = {}
            if monitor.thresholds:
                monitors[monitor.monitor_name]["thresholds"] = monitor.thresholds
            if monitor.parameters:
                monitors[monitor.monitor_name]["parameters"] = monitor.parameters

        return monitors

    def __get_pta_evaluator_urls(self) -> dict[str, any]:
        """Helper to get the urls for pta"""

        # Using cloud
        if self.credentials.version is None:
            url_map = WOS_URL_MAPPING.get(self.credentials.url)

            # remove 'api' netloc from dataplatform url
            parsed_dai_url = urlparse(url_map.dai_url)
            updated_netlock = parsed_dai_url.netloc.replace("api.", "", 1)
            platform_url = urlunparse(
                parsed_dai_url._replace(netloc=updated_netlock))

            return {
                "wml_url": url_map.wml_url,
                "platform_url": platform_url,
                "wos_url": url_map.wxg_url,
                "dataplatform_url": url_map.dai_url,
            }

        # using CPD
        return {
            "wml_url": self.credentials.url,
            "platform_url": self.credentials.url,
            "wos_url": self.credentials.url,
            "dataplatform_url": self.credentials.url,
        }

    def __build_pta_evaluator_config(self, config: dict[str, any]):
        input_prompt_setup = config.get("prompt_setup", {})

        base_prompt_setup = self.__build_base_prompt_setup(
            input_prompt_setup=input_prompt_setup
        )

        stages = {}

        if "development_project_id" in config.keys():
            development_prompt_setup = base_prompt_setup.copy()
            development_prompt_setup["operational_space_id"] = "development"

            development_prompt_setup["monitors"] = self.__convert_monitor_to_dict(
                monitors_list=config.get("development_monitors"),
                task_type=input_prompt_setup.get("problem_type"),
            )

            stages["development"] = {
                "prompt_setup": development_prompt_setup,
                "project_id": config.get("development_project_id"),
            }

        if "production_space_id" in config.keys():
            production_prompt_setup = base_prompt_setup.copy()
            production_prompt_setup["operational_space_id"] = "production"

            production_prompt_setup["monitors"] = self.__convert_monitor_to_dict(
                monitors_list=config.get("production_monitors"),
                task_type=input_prompt_setup.get("problem_type"),
            )

            space_deployment = config.get("space_deployment", {})

            if "serving_name" not in space_deployment.keys():
                space_deployment["serving_name"] = (
                    f"deployment_{calendar.timegm(time.gmtime())}"
                )

            base_model_id = space_deployment.get("base_model_id")

            if not base_model_id:
                if "prompt_template" in config.keys():
                    base_model_id = config.get("prompt_template", {}).get(
                        "model_id", self.DEFAULT_MODEL_ID
                    )
                else:
                    base_model_id = config.get("detached_prompt_template", {}).get(
                        "model_id", self.DEFAULT_MODEL_ID
                    )

            space_deployment["base_model_id"] = base_model_id

            if "description" not in space_deployment.keys():
                space_deployment["description"] = (
                    f"production space {calendar.timegm(time.gmtime())}"
                )

            if "name" not in space_deployment.keys():
                space_deployment["name"] = "Production Space"

            if "version_date" not in space_deployment.keys():
                space_deployment["version_date"] = "2024-12-18"

            stages["production"] = {
                "space_deployment": space_deployment,
                "prompt_setup": production_prompt_setup,
                "space_id": config.get("production_space_id"),
            }

        # Only parse model usecase details if ai_usecase_id is provided
        if "ai_usecase_id" in config.keys():
            usecase_details = {}
            for key in ["ai_usecase_id", "catalog_id", "approach_version", "approach_id"]:
                if key in config.keys():
                    usecase_details[key] = config[key]

            # Set default approach_version
            if "approach_version" not in usecase_details.keys():
                usecase_details["approach_version"] = self.DEFAULT_APPROACH_VERSION
        else:
            usecase_details = None

        config_urls = self.__get_pta_evaluator_urls()

        pta_config = {
            "common_configurations": {
                "credentials": self.__get_credentials_dict(),
                "use_cpd": self.credentials.version is not None,
                "use_ssl": not self.credentials.disable_ssl,
                "service_instance_id": (
                    self.credentials.service_instance_id
                    if self.credentials.service_instance_id
                    else "00000000-0000-0000-0000-000000000000"
                ),
                "ai_usecase": usecase_details,
                **config_urls,
            },
            **stages,
        }

        return pta_config

    def get_prompt_template_id(
        self,
        environment: EvaluationStage = EvaluationStage.DEVELOPMENT,
    ) -> str:
        return self.__pta_evaluator.get_prompt_template_id(stage=environment)
