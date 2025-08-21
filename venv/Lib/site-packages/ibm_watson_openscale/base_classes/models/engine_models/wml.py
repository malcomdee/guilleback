# coding: utf-8

# Copyright 2021 IBM All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from ibm_watson_openscale.base_classes.models.known_service_model import KnownServiceModel
from ibm_watson_openscale.supporting_classes.enums import *
from ibm_watson_openscale.utils.client_errors import *
from ibm_watson_openscale.utils.data_reader import DataReader
from ibm_watson_openscale.utils import *

from ibm_cloud_sdk_core.authenticators import IAMAuthenticator


class WatsonMachineLearningModel(KnownServiceModel):
    """
    Describes Watson Machine Learning asset.

    :param model_uid: WML model id
    :type model_uid: str
    :param deployment_uid: Deployment id of model
    :type deployment_uid: str
    :param problem_type: type of model (problem) (optional).
    :type problem_type: str
    :param input_data_type: type of input data (optional).
    :type input_data_type: str
    :param training_data_reference: reference to training data (optional).
    :type training_data_reference: StorageReference or json
    :param test_data_df: test data to run evaluation against (optional).
    :type test_data_df: pandas dataframe
    :param label_column: the column/field name containing target/label values (optional).
    :type label_column: str
    :param prediction_column: the name of column/field with predicted values (optional).
    :type prediction_column: str
    :param probability_column: the name of column/field with prediction probability (optional).
    :type probability_column: str
    :param feature_columns: names of columns which contains features (optional).
    :type feature_columns: list of str
    :param categorical_columns: names of columns which contains categorical data (optional).
    :type categorical_columns: list of str

    Example usage:

        >>> from ibm_watson_openscale.supporting_classes.enums import *
        >>>
        >>> WatsonMachineLearningModel(model_uid, deployment_uid, input_data_type=InputDataType.STRUCTURED)
    """
    service_type = ServiceTypes.WATSON_MACHINE_LEARNING
    _ai_client = None
    _binding_uid = None
    _is_icp = False
    _model_details = None
    _deployment_details = None

    def __init__(self, model_uid, deployment_uid, space_uid=None, problem_type=None, input_data_type=None,
                 training_data_reference=None, test_data_df=None, label_column=None, prediction_column=None, probability_column=None,
                 feature_columns=None, categorical_columns=None, favorable_classes=None, unfavorable_classes=None,
                 quality_config=None, fairness_config=None, drift_config=None):

        KnownServiceModel.__init__(self, self.service_type, model_uid=model_uid, deployment_uid=deployment_uid, space_uid=space_uid,
                                   problem_type=problem_type, input_data_type=input_data_type,
                                   training_data_reference=training_data_reference, test_data_df=test_data_df,
                                   label_column=label_column, prediction_column=prediction_column,
                                   probability_column=probability_column, feature_columns=feature_columns,
                                   categorical_columns=categorical_columns, favorable_classes=favorable_classes,
                                   unfavorable_classes=unfavorable_classes, quality_config=quality_config,
                                   fairness_config=fairness_config, drift_config=drift_config)
    
    def validate(self, ai_client=None, binding_uid=None, is_icp=False):
        """
        Validates the model class
        """

        self._ai_client = ai_client
        self._binding_uid = binding_uid
        self._is_icp = is_icp

        
        deployment_details = self._get_asset_deployment_details(deployment_uid=self.deployment_uid)
        
        if deployment_details is not None:
            self._deployment_details = deployment_details
            self.deployment_name = self._deployment_details['entity']['asset']['name']
            print("Existence check for deployment finished. Deployment is {}".format(self.deployment_name))
            if self._deployment_details['entity']['asset']['asset_id'] == self.model_uid:
                print("Existence check for Model finished.")
            else:
                raise MissingValue(u'model_id', "Could not find the model with id {}".format(self.model_uid))    
        else:    
            raise MissingValue(u'deployment_uid', "Could not find the deployment with id {}".format(self.deployment_uid))    

        # Infer the label column from the model details
        if self.label_column is None:
            if 'label_column' in self._deployment_details['entity']['asset_properties']:
                self.label_column = self._deployment_details['entity']['asset_properties']['label_column']

        # label_column is not found in model_details for AutoAI models
        if self.label_column is None:
            raise MissingValue(u'label_column', "label_column not supplied for AutoAI model")

        if self.test_data_df is None:
            raise MissingValue(u'test_data_df', "test_data_df not supplied for evaluation")
        else:
            validate_pandas_dataframe(self.test_data_df, "test_data_df", True)

        if self.training_data_reference is not None:
            training_data_df = DataReader.get_input_data(self.training_data_reference, is_icp=self._is_icp)
            print("Finished reading training data...")
            data_columns = training_data_df.columns.tolist()

            # Label column should be provided in the training data being supplied
            if self.label_column not in data_columns:
                raise MissingValue(u'label_column', "Supplied test data doesn't contain label column")

            # Infer the feature columns from the training data supplied
            feature_cols_df = training_data_df.drop(columns=[self.label_column])
            if self.feature_columns is None:
                self.feature_columns = feature_cols_df.columns.tolist()
            
            # Infer categorical columns
            if self.categorical_columns is None:
                self.categorical_columns = feature_cols_df.select_dtypes(include=['object']).columns.tolist()
                    
            # Infer the input data type from the training data supplied
            if self.input_data_type is None:
                numeric_features = feature_cols_df.select_dtypes(include=['int64', 'float64']).columns

                if len(numeric_features) > 0:
                    self.input_data_type = InputDataType.STRUCTURED

            # Infer the problem type from the training data supplied
            if self.problem_type is None:
                from sklearn.utils.multiclass import type_of_target
                label = training_data_df[self.label_column]
                if type_of_target(label.values) == "multiclass":
                    self.problem_type = ProblemType.MULTICLASS_CLASSIFICATION
                elif type_of_target(label.values) == "binary":
                    self.problem_type = ProblemType.BINARY_CLASSIFICATION
                else:
                    self.problem_type = ProblemType.REGRESSION

            if self.problem_type != ProblemType.REGRESSION and self.fairness_config is None:
                if self.favorable_classes is None or len(self.favorable_classes) == 0:
                    raise MissingValue(u'favorable_classes')
                elif self.unfavorable_classes is None or len(self.unfavorable_classes) == 0:
                    raise MissingValue(u'unfavorable_classes')

            scoring_url = deployment_details['entity']['scoring_endpoint']['url']
            prediction_column, probability_column = self._get_prediction_probability_columns(scoring_url, feature_cols_df)
            if self.prediction_column is None:
                self.prediction_column = prediction_column

            if self.probability_column is None:
                self.probability_column = probability_column

            print("Finished inferring model details")            

    def _get_prediction_probability_columns(self, scoring_url, feature_cols_df):

        prediction_column = None
        probability_column = None
        # Send only one record for scoring
        payload = self._get_scoring_payload(feature_cols_df.head(1), self._is_icp)
        scoring_response = self._score(scoring_url, payload)
        predictions = None
        if scoring_response is not None:
            if self._is_icp:
                if "predictions" in scoring_response:
                    predictions = scoring_response["predictions"]
            else:
                predictions = [scoring_response]

            for prediction in predictions:
                if "fields" in prediction:
                    if "predictedLabel" in prediction["fields"]:
                        prediction_column = "predictedLabel"

                    if prediction_column is None and "prediction" in prediction["fields"]:
                        prediction_column = "prediction"

                    if "probability" in prediction["fields"]:
                        probability_column = "probability"

        return prediction_column, probability_column

    def _get_asset_details(self, model_uid):

        all_asset_details = self._ai_client.data_mart.bindings.get_asset_details(binding_uid=self._binding_uid)
        for asset_details in all_asset_details:
            if "source_uid" in asset_details and asset_details["source_uid"] == model_uid:
                return asset_details

    def _get_asset_deployment_details(self, deployment_uid):

        return self._ai_client.service_providers.get_deployment_asset(data_mart_id=self._ai_client.service_instance_id,service_provider_id=self._binding_uid,deployment_id=deployment_uid,deployment_space_id=self.space_uid)

    @staticmethod
    def _get_scoring_payload(dataframe, is_icp=False):

        payload = {
            "input_data": [
                {
                    "fields": dataframe.columns.tolist(),
                    "values": dataframe.values.tolist()
                }
            ]
        }
        
        return payload

    def _score(self, scoring_url, payload):
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        requests_session = requests.Session()
        retry = Retry(connect=3, backoff_factor=0.5)
        adapter = HTTPAdapter(max_retries=retry)
        requests_session.mount('http://', adapter)
        requests_session.mount('https://', adapter)
        
        token = self._ai_client.authenticator.token_manager.get_token() if ( isinstance(self._ai_client.authenticator, IAMAuthenticator) or (isinstance(self._ai_client.authenticator, CloudPakForDataAuthenticator))) else self._ai_client.authenticator.bearer_token
        iam_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % token
        }
        scoring_url = scoring_url + "?version=2021-04-07"
        response = requests_session.post(scoring_url, json=payload, headers=iam_headers)

        try:
            predictions_response = handle_response(200, 'predictions', response, True)
        except ApiRequestFailure:
            raise ApiRequestFailure(u'Scoring against WML model failed.', response)

        return predictions_response

    def add_payload_logging_record(self, record_count, is_icp=False):

        scoring_url = self._deployment_details['entity']['scoring_endpoint']['url']
        feature_cols_df = self.test_data_df.drop(columns=[self.label_column])
        scoring_payload = self._get_scoring_payload(feature_cols_df.head(record_count), is_icp)
        self._score(scoring_url, scoring_payload)
