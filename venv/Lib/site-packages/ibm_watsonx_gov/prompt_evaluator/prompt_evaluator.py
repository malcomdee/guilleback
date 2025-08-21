# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# OCO Source Materials
# 5900-A3Q, 5737-H76
# Copyright IBM Corp. 2025
# The source code for this program is not published or other-wise divested of its trade
# secrets, irrespective of what has been deposited with the U.S.Copyright Office.
# ----------------------------------------------------------------------------------------------------

from ibm_watsonx_ai.foundation_models.prompts.prompt_template import (
    DetachedPromptTemplate, PromptTemplate)

from ibm_watsonx_gov.entities.container import (BaseMonitor, ProjectContainer,
                                                SpaceContainer)
from ibm_watsonx_gov.entities.credentials import Credentials
from ibm_watsonx_gov.entities.enums import EvaluationStage
from ibm_watsonx_gov.entities.prompt_setup import PromptSetup
from ibm_watsonx_gov.prompt_evaluator.impl.prompt_evaluator_impl import \
    PromptEvaluatorImpl


class PromptEvaluator:
    """
    PromptEvaluator is a class that sets up a prompt template and evaluates the risks associated with it.

    Example
    -------
    .. code-block:: python

        # Create the prompt evaluator
        evaluator = PromptEvaluator(
            credentials=Credentials(api_key="")
        )

        # Create the prompt setup
        prompt_setup = PromptSetup(
            task_type=TaskType.RAG,
            question_field="question",
            context_fields=["context1"],
            label_column="answer",
        )

        # Create the prompt template
        prompt_template = PromptTemplate(
            name="test",
            description="description",
            input_variables=["question", "context1"],
            input_text="Answer the below question from the given context only and do not use the knowledge outside the context. Context: {context1} Question: {question} Answer:",
            model_id="google/flan-ul2",
            task_ids=[TaskType.RAG.value]
        )

        # Provide the development container details
        development_container = ProjectContainer(
            container_id="3acf420f-526a-4007-abe7-78a03435aac2",
            monitors=[
                GenerativeAIQualityMonitor(),
            ]
        )

        # Evaluate the risk based on the provided dataset
        evaluator.evaluate_risk(
            prompt_setup=prompt_setup,
            prompt_template=prompt_template,
            containers=[development_container],
            environments=[EvaluationStage.DEVELOPMENT],
            input_file_path="./rag_dataset.csv",
        )

        # Show the evaluation result
        evaluator.get_monitor_metrics(
            monitor=BaseMonitor(monitor_name="generative_ai_quality"),
            environment=EvaluationStage.DEVELOPMENT,
            show_table=True,
        )

        evaluator.get_dataset_records(
            dataset_type="gen_ai_quality_metrics",
            environment=EvaluationStage.DEVELOPMENT,
            show_table=True,
        )

    """

    def __init__(self, credentials: Credentials | None = None):
        """
        Initializes the code assistant with the provided credentials.

        Args:
            credentials (Credentials): The credentials required for authentication and authorization.
        """
        self.__evaluator = PromptEvaluatorImpl(credentials)

    def e2e_prompt_evaluation(
        self,
        config: dict[str, any],
        input_file_path: str = None,
    ):
        """
        Method to set up and evaluate the prompt template end to end with a simplified interface.

        Examples:

            .. code-block:: python

                # Create the prompt evaluator
                evaluator = PromptEvaluator(
                    credentials=Credentials(api_key="")
                )

                # detached prompt configuration example
                detached_prompt_config = {
                    "prompt_setup": {
                        "problem_type": TaskType.RAG.value,
                        "context_fields": ["context1"],
                    },
                    "development_project_id": "3acf420f-526a-4007-abe7-78a03435aac2",
                    "detached_prompt_template": {
                        "name": "detached prompt experiment",
                        "model_id": "ibm/granite-3-2-8b-instruct",
                        "input_text": "Answer the below question from the given context only and do not use the knowledge outside the context. Context: {context1} Question: {question} Answer:",
                        "input_variables": ["question", "context1"],
                        "detached_model_url": "https://us-south.ml.cloud.ibm.com/ml/v1/deployments/insurance_test_deployment/text/generation?version=2021-05-01",
                        "task_ids": [TaskType.RAG.value],
                    }

                # prompt configuration example
                prompt_config = {
                    "prompt_setup": {
                        "problem_type": TaskType.RAG.value,
                        "context_fields": ["context1"],
                    },
                    "development_project_id": "3acf420f-526a-4007-abe7-78a03435aac2",
                    "prompt_template": {
                        "name": "prompt experiment",
                        "model_id": "ibm/granite-3-2-8b-instruct",
                        "input_text": "Answer the below question from the given context only and do not use the knowledge outside the context. Context: {context1} Question: {question} Answer:",
                        "input_variables": ["question", "context1"],
                        "task_ids": [TaskType.RAG.value],
                    },
                    // optional usecase configuration
                    "ai_usecase_id": "b1504848-3cf9-4ab9-9d46-d688e34a0295",
                    "catalog_id": "7bca9a52-7c90-4fb4-b3ef-3194e25a8452", // same as inventory_id
                    "approach_id": "80b3a883-015f-498a-86f3-55ba74b5374b",
                    "approach_version": "0.0.2",
                }

                # Evaluate the risk based on the provided dataset
                evaluator.e2e_prompt_evaluation(
                    config=config,
                    input_file_path="./rag_dataset.csv",
                )

                # Show the evaluation result
                evaluator.get_monitor_metrics(
                    monitor=BaseMonitor(monitor_name="generative_ai_quality"),
                    environment=EvaluationStage.DEVELOPMENT,
                    show_table=True,
                )

                evaluator.get_dataset_records(
                    dataset_type="gen_ai_quality_metrics",
                    environment=EvaluationStage.DEVELOPMENT,
                    show_table=True,
                )
        Args:
            config (dict[str, any]): configurations dictionary
            input_file_path (str, optional): Path to the input to evaluate. This can be a local file or link to a file. The propmt template evaluation will be skipped if this argument is no set.
        """
        self.__evaluator.e2e_prompt_evaluation(config, input_file_path)

    def evaluate_risk(
        self,
        prompt_setup: PromptSetup,
        containers: list[ProjectContainer | SpaceContainer],
        input_file_path: str,
        prompt_template: PromptTemplate | DetachedPromptTemplate = None,
        prompt_template_id: str = None,
        environments: list[EvaluationStage] = [EvaluationStage.DEVELOPMENT],
    ):
        """
        Evaluate the risk of a given input file path for a list of containers. Note either prompt_template or prompt_template_id should be provided.

        Args:
            prompt_template (PromptTemplate | DetachedPromptTemplate, optional): The prompt template to use for evaluation.
            prompt_template_id (str, optional): The prompt template id to use for evaluation.
            containers (list[ProjectContainer | SpaceContainer]): The containers details.
            input_file_path (str): The path to the input file to evaluate.
            environments (list[EvaluationStage], optional): The list of evaluation stages to do the evaluation in. Defaults to [EvaluationStage.DEVELOPMENT].
        """
        self.__evaluator.evaluate_risk(
            prompt_setup=prompt_setup,
            prompt_template=prompt_template,
            prompt_template_id=prompt_template_id,
            containers=containers,
            evaluation_stages=environments,
            input_file_path=input_file_path,
        )

    def get_monitor_metrics(
            self,
            monitor: BaseMonitor,
            environment: EvaluationStage = EvaluationStage.DEVELOPMENT,
            show_table: bool = False,
    ):
        """
        Get monitors metrics for a given monitor in a specific environment.

        Args:
            monitor (BaseMonitor): monitor to get the metrics for.
            environment (EvaluationStage, optional): monitor environment. Defaults to EvaluationStage.DEVELOPMENT.
            show_table (bool, optional): Flag to print the result table. Defaults to False.

        Returns:
            dict[str, any]: Monitor metrics dictionary
        """
        return self.__evaluator.get_monitor_metrics(
            evaluation_stage=environment,
            monitor=monitor,
            show_table=show_table,
        )

    def get_dataset_records(
            self,
            dataset_type: str,
            environment: EvaluationStage = EvaluationStage.DEVELOPMENT,
            show_table: bool = False,
    ) -> dict[str, any]:
        """
        Retrieve dataset records for a given dataset type and environment.

        Args:
            dataset_type (str): The type of dataset to retrieve records for.
            environment (EvaluationStage, optional): The environment to retrieve records from. Defaults to EvaluationStage.DEVELOPMENT.
            show_table (bool, optional): Whether to display the dataset records as a table. Defaults to False.

        Returns:
            dict[str, any]: A dictionary containing the dataset records.
        """
        return self.__evaluator.get_dataset_records(
            evaluation_stage=environment,
            dataset_type=dataset_type,
            show_table=show_table,
        )

    def get_prompt_template_id(
        self,
        environment: EvaluationStage = EvaluationStage.DEVELOPMENT,
    ) -> str:
        """
        Retrieves the prompt template ID based on the specified environment.

        Args:
            environment (EvaluationStage, optional): The environment for which to retrieve the prompt template ID.
                Defaults to EvaluationStage.DEVELOPMENT.

        Returns:
            str: The prompt template ID corresponding to the specified environment.
        """
        return self.__evaluator.get_prompt_template_id(
            environment=environment
        )
