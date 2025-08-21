# coding: utf-8

# Copyright 2020,2021 IBM All Rights Reserved.
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


from typing import Tuple
import uuid

from ibm_cloud_sdk_core import BaseService
from ibm_watson_openscale.base_classes.tables import Table
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import Asset, AssetPropertiesRequest, \
    AssetDeploymentRequest, RiskEvaluationStatus
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import SparkStruct    
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import Subscriptions as BaseSubscriptions
from ibm_watson_openscale.supporting_classes.enums import *

from .utils import *


if TYPE_CHECKING:
    from .client import WatsonOpenScaleV2Adapter
    from ibm_watson_openscale.base_classes.watson_open_scale_v2 import DetailedResponse

_DEFAULT_LIST_LENGTH = 50


# TODO: Add parameters validation in every method
class Subscriptions(BaseSubscriptions):
    """
    Manages Subscription instance.
    """

    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter') -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        super().__init__(watson_open_scale=self._ai_client)

    def show(self, limit: Optional[int] = 10,
             data_mart_id: str = None,
            service_provider_id: str = None,
            asset_asset_id: str = None,
            deployment_deployment_id: str = None,
            deployment_deployment_type: str = None,
            integration_reference_integrated_system_id: str = None,
            integration_reference_external_id: str = None,
            risk_evaluation_status_state: str = None,
            service_provider_operational_space_id: str = None,
            pre_production_reference_id: str = None,
            **kwargs) -> None:
        """
        Show service providers. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int
        :param str data_mart_id: (optional) comma-separeted list of IDs.
        :param str service_provider_id: (optional) comma-separeted list of IDs.
        :param str asset_asset_id: (optional) comma-separeted list of IDs.
        :param str deployment_deployment_id: (optional) comma-separeted list of
               IDs.
        :param str deployment_deployment_type: (optional) comma-separeted list of
               types.
        :param str integration_reference_integrated_system_id: (optional)
               comma-separeted list of IDs.
        :param str integration_reference_external_id: (optional) comma-separeted
               list of IDs.
        :param str risk_evaluation_status_state: (optional) comma-separeted list of
               states.
        :param str service_provider_operational_space_id: (optional)
               comma-separeted list of operational space ids (property of service provider
               object).
        :param str pre_production_reference_id: (optional) comma-separeted list of
               IDs.
        :param dict headers: A `dict` containing the request headers       

        A way you might use me is:

        >>> client.subscriptions.show()
        >>> client.subscriptions.show(limit=20)
        >>> client.subscriptions.show(limit=None)
        """
        validate_type(limit, u'limit', int, False)

        response = self.list(data_mart_id = data_mart_id,
            service_provider_id = service_provider_id,
            asset_asset_id = asset_asset_id,
            deployment_deployment_id = deployment_deployment_id,
            deployment_deployment_type = deployment_deployment_type,
            integration_reference_integrated_system_id = integration_reference_integrated_system_id,
            integration_reference_external_id = integration_reference_external_id,
            risk_evaluation_status_state = risk_evaluation_status_state,
            service_provider_operational_space_id = service_provider_operational_space_id,
            pre_production_reference_id = pre_production_reference_id,
            **kwargs)

        records = [[subscription.entity.asset.asset_id,
                    subscription.entity.asset.name,
                    subscription.entity.data_mart_id,
                    subscription.entity.deployment.deployment_id,
                    subscription.entity.deployment.name,
                    subscription.entity.service_provider_id,
                    subscription.entity.status.state,
                    subscription.metadata.created_at,
                    subscription.metadata.id
                    ] for subscription in response.result.subscriptions]
        columns = ['asset_id', 'asset_name', 'data_mart_id', 'deployment_id', 'deployment_name',
                   'service_provider_id', 'status', 'created_at', 'id']

        Table(columns, records).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="Subscriptions"
        )

    def add(self,
            data_mart_id: str,
            service_provider_id: str,
            asset: 'Asset',
            deployment: 'AssetDeploymentRequest',
            asset_properties: 'AssetPropertiesRequest' = None,
            risk_evaluation_status: 'RiskEvaluationStatus' = None,
            analytics_engine: 'AnalyticsEngine' = None,
            data_sources: List['DataSource'] = None,
            training_data_stats: dict = None,
            background_mode: bool = True,
            **kwargs) -> Union['DetailedResponse', Optional[dict]]:
        """
        Add a subscription to the model deployment.

        :param str data_mart_id: ID of the data_mart (required)
        :param str service_provider_id: ID of the service_provider (required)
        :param Asset asset: an Asset object with asset's information (required)
        :param AssetDeploymentRequest deployment: an AssetDeploymentRequest object with deployment's information (required)
        :param AssetPropertiesRequest asset_properties: (optional) Additional asset
               properties (subject of discovery if not provided when creating the
               subscription).
        :param RiskEvaluationStatus risk_evaluation_status: (optional)
        :param AnalyticsEngine analytics_engine: (optional)
        :param List[DataSource] data_sources: (optional)
        :param training_data_stats: Training statistic json generated using training stats notebook (https://github.com/IBM-Watson/aios-data-distribution/blob/master/training_statistics_notebook.ipynb)
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `SubscriptionResponse` result

        A way you may use me:

        >>> from ibm_watson_openscale import *
        >>> added_subscription_info = client.subscriptions.add(
                data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                service_provider_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                asset=Asset(...),
                deployment=AssetDeploymentRequest(...),
                asset_properties=AssetPropertiesRequest(...),
             )
        """
        validate_type(data_mart_id, 'data_mart_id', str, True)
        validate_type(service_provider_id, 'service_provider_id', str, True)
        
        if self._ai_client.check_entitlements is True and self._ai_client.plan_name == constants.LITE_PLAN:
            total_subscriptions = self.list().result.subscriptions
            if len(total_subscriptions) >= 5:
                raise Exception("You are not allowed to create more than 5 subscriptions for lite plan.")
        
        if asset_properties is None and training_data_stats is None:
            raise Exception("Either asset_properties or training_data_stats has to be passed")
     
        ### If "other" data type is present in output or input schema then remove it from subscription before saving it.
        ### https://github.ibm.com/aiopenscale/tracker/issues/19160
        if asset_properties is not None:
            asset_props = asset_properties.to_dict()
            if 'input_data_schema' in asset_props:
                input_schema = asset_props['input_data_schema']
                if input_schema is not None:
                    has_other_data_type = self._has_other_datatype(input_schema['fields'])
                    if has_other_data_type is True:
                        asset_properties.input_data_schema = None    
            if 'output_data_schema' in asset_props:    
                output_schema = asset_props['output_data_schema']
                if output_schema is not None:
                    has_other_data_type = self._has_other_datatype(output_schema['fields'])
                    if has_other_data_type is True:
                        asset_properties.output_data_schema = None
            if 'training_data_schema' in asset_props:    
                training_schema = asset_props['training_data_schema']
                if training_schema is not None:
                    has_other_data_type = self._has_other_datatype(training_schema['fields'])
                    if has_other_data_type is True:
                        asset_properties.training_data_schema = None 
                        
        if training_data_stats is None:
            response = super().add(data_mart_id=data_mart_id, service_provider_id=service_provider_id, asset=asset,
                                   deployment=deployment, asset_properties=asset_properties,
                                   risk_evaluation_status=risk_evaluation_status, 
                                   analytics_engine=analytics_engine,
                                   data_sources=data_sources)
        else:
            #Create subscription using data available in training stats
            if len(training_data_stats) == 0:
                raise Exception("training_data_stats is empty. Please re-generate and use it")
            response = self.__create_subscription_from_training_stats(data_mart_id, service_provider_id, training_data_stats, kwargs,background_mode )

        subscription_id = response.result.metadata.id

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.get(subscription_id=subscription_id)
                return details.result.entity.status.state

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.get(subscription_id=subscription_id)
                state = details.result.entity.status.state

                if state in [StatusStateType.ACTIVE]:
                    return "Successfully finished adding subscription", None, details
                else:
                    return "Add subscription failed with status: {}".format(state), \
                           'Reason: {}'.format(["code: {}, message: {}".format(error.code, error.message) for error in
                                                details.result.entity.status.failure.errors]), details

            return print_synchronous_run(
                'Waiting for end of adding subscription {}'.format(subscription_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.ACTIVE]
            )

    def delete(self,
               subscription_id: str,
               force: bool = None,
               background_mode: bool = True) -> Union['DetailedResponse', Optional[dict]]:
        """
        Delete subscription.

        :param str subscription_id: Unique subscription ID.
        :param bool force: (optional) force hard delete.
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse

        A way you may use me:

        >>> client.subscriptions.delete(
                background_mode=False,
                subscription_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                force=True
             )
        """
        response = super().delete(subscription_id=subscription_id, force=force)

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.list()
                if subscription_id not in str(details.result):
                    return StatusStateType.FINISHED
                else:
                    return StatusStateType.ACTIVE

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.list()
                if subscription_id not in str(details.result):
                    state = StatusStateType.FINISHED
                else:
                    state = StatusStateType.ACTIVE

                if state in [StatusStateType.FINISHED]:
                    return "Successfully finished deleting subscription", None, response
                else:
                    return "Delete subscription failed", 'Reason: None', response  # TODO: Need to show the reason.

            return print_synchronous_run(
                'Waiting for end of deleting subscription {}'.format(subscription_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.FINISHED]
            )
            
    def _has_other_datatype(self, fields):
        for field in fields:
            type = field['type']
            if type == 'other':
                return True
        return False   
    
    #Private method to create subscription using training stats data
    def __create_subscription_from_training_stats(self, data_mart_id, service_provider_id, training_stats_info, params,background_mode):
        
        deployment_id = params.get("deployment_id")
        #Required in case of headless subscription
        deployment_name = params.get("deployment_name")
        deployment_space_id = params.get("deployment_space_id")
        model_type = training_stats_info['common_configuration']['problem_type']
        problem_type = None
        if model_type=="binary":
            problem_type = ProblemType.BINARY_CLASSIFICATION
        elif model_type=="multiclass":
            problem_type = ProblemType.MULTICLASS_CLASSIFICATION
        elif model_type=="regression":
            problem_type = ProblemType.REGRESSION    
        
        
        prediction_column = params.get("prediction_field")
        probability_columns = params.get("probability_fields")
        predicted_target_column = params.get("predicted_target_field")
        
        #validate_type(deployment_id, 'deployment_id', str, True)
        validate_type(prediction_column, 'prediction_field', str, True)
        #validate_type(predicted_target_column, 'predicted_target_field', str, True)
        
        if deployment_id is None and deployment_name is None :
            raise Exception("Please provide deployment_id if you have deployment information or else provide deployment_name in case you want to create headless subscription")
            
        model_asset_details_from_deployment = {}
        deployment_found = False
        if deployment_id is not None and deployment_space_id is not None:
            model_asset_details_from_deployment=self._ai_client.service_providers.get_deployment_asset(data_mart_id=data_mart_id,service_provider_id=service_provider_id,deployment_id=deployment_id,deployment_space_id=deployment_space_id)
            if model_asset_details_from_deployment['metadata']['guid']== deployment_id:
                deployment_found = True
            if not deployment_found :
                raise Exception("Deployment with id {} could not be found in deployment space {}. Please check again".format(deployment_id, deployment_space_id))    
        elif deployment_id is not None and deployment_space_id is None:
            #For non-WML model, pick the right deployment from list
            model_asset_details_from_deployment=self._ai_client.service_providers.list_assets(data_mart_id=data_mart_id,service_provider_id=service_provider_id).result    
            models = model_asset_details_from_deployment['resources']
            for model in models:
                if model['metadata']['guid']== deployment_id:
                    model_asset_details_from_deployment = model
                    deployment_found = True
                    break;
            if not deployment_found :
                raise Exception("Deployment with id {} could not be found. Please check again".format(deployment_id))
        elif deployment_id is None and deployment_space_id is not None:     
            raise Exception("Please provide deployment_id for space {}".format(deployment_space_id))
        else:
            print("Creating headless subscription as both deployment id and deployment space id are null")              
            
        input_data_schema = training_stats_info["common_configuration"]["input_data_schema"]
        fields = []
        label_column=training_stats_info["common_configuration"]["label_column"]
        # remove label column entry from input data schema
        for field in input_data_schema["fields"]:
            if field["name"] == label_column:
                continue
            fields.append(field)
        
        required_input_data_schema = {
            "type": "struct",
            "fields": fields
        }
        training_data_schema = None
          
        if deployment_name is not None and not deployment_found:
            model_asset_id = str(uuid.uuid4())  
            model_name = deployment_name   
            model_url = "https://dummyModelUrl"
            deployment_asset_id = str(uuid.uuid4()) 
            deployment_name = deployment_name 
            scoring_endpoint = "https://dummyScoringUrl"
        else:
            if not deployment_found:
                raise Exception("Deployment with id {} not found".format(deployment_id))    
            model_asset_id = model_asset_details_from_deployment["entity"]["asset"]["asset_id"] 
            model_name = model_asset_details_from_deployment["entity"]["asset"]["name"]   
            model_url = model_asset_details_from_deployment["entity"]["asset"]["url"]
            deployment_asset_id =  model_asset_details_from_deployment['metadata']['guid']
            deployment_name = model_asset_details_from_deployment['entity']['name']
            scoring_endpoint = model_asset_details_from_deployment['entity']['scoring_endpoint']['url']
        
        if model_asset_details_from_deployment is not None and len(model_asset_details_from_deployment)>0:     
            if "training_data_schema" in model_asset_details_from_deployment["entity"]["asset_properties"]:
                training_data_schema = SparkStruct.from_dict(model_asset_details_from_deployment["entity"]["asset_properties"]["training_data_schema"])
            
        return super().add(
                data_mart_id=data_mart_id,
                service_provider_id=service_provider_id,
                asset=Asset(
                    asset_id=model_asset_id,
                    name=model_name,
                    url=model_url,
                    asset_type=AssetTypes.MODEL,
                    input_data_type=InputDataType.STRUCTURED,
                    problem_type=problem_type
                ),
                deployment=AssetDeploymentRequest(
                    deployment_id=deployment_asset_id,
                    name=deployment_name,
                    deployment_type= DeploymentTypes.ONLINE,
                    url=scoring_endpoint
                ),
                asset_properties=AssetPropertiesRequest(
                    label_column=label_column,
                    probability_fields=probability_columns,
                    prediction_field=prediction_column,
                    predicted_target_field=predicted_target_column,
                    feature_fields = training_stats_info["common_configuration"]["feature_fields"],
                    categorical_fields = training_stats_info["common_configuration"]["categorical_fields"],
                    input_data_schema = SparkStruct.from_dict(required_input_data_schema),
                    training_data_schema=training_data_schema
                ),
                background_mode=background_mode
            )