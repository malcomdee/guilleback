# coding: utf-8

# Copyright 2020 IBM All Rights Reserved.
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

from typing import Tuple, Dict

from ibm_cloud_sdk_core import BaseService

from ibm_watson_openscale.base_classes.tables import Table
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import \
    AzureCredentials, CustomCredentials, SageMakerCredentials, \
    SPSSCredentials, WMLCredentialsCP4D, WMLCredentialsCloud
from .utils import *
from .utils.client_errors import InvalidCredentialsProvided,IncorrectParameter
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import ServiceProviders as BaseServiceProviders
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import get_sdk_headers

if TYPE_CHECKING:
    from pandas import DataFrame
    from .client import WatsonOpenScaleV2Adapter

_DEFAULT_LIST_LENGTH = 50


# TODO: Add parameters validation in every method
class ServiceProviders(BaseServiceProviders):
    """
    Manages Service Provider instance.
    """

    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter') -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        super().__init__(watson_open_scale=self._ai_client)

    def show(self, limit: Optional[int] = 10, show_deleted: bool = None,
             service_type: str = None,
             instance_id: str = None,
             operational_space_id: str = None,
             deployment_space_id: str = None,
             **kwargs) -> None:
        """
        Show service providers. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int
        :param bool show_deleted: (optional) show also resources pending delete.
        :param str service_type: (optional) Type of service.
        :param str instance_id: (optional) comma-separeted list of IDs.
        :param str operational_space_id: (optional) comma-separeted list of IDs.
        :param str deployment_space_id: (optional) comma-separeted list of IDs.
        :param dict headers: A `dict` containing the request headers
        
        A way you might use me is:

        >>> client.service_providers.show()
        >>> client.service_providers.show(limit=20)
        >>> client.service_providers.show(limit=None)
        """
        validate_type(limit, u'limit', int, False)

        response = self.list(
            show_deleted=show_deleted,
            service_type=service_type,
            instance_id=instance_id,
            operational_space_id=operational_space_id,
            deployment_space_id=deployment_space_id,
            **kwargs)

        records = [[service_provider.entity.instance_id,
                    service_provider.entity.status.state,
                    service_provider.entity.name,
                    service_provider.entity.service_type,
                    service_provider.metadata.created_at,
                    service_provider.metadata.id
                    ] for service_provider in response.result.service_providers]
        columns = ['instance_id', 'status', 'name', 'service_type', 'created_at', 'id']

        Table(columns, records).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="Service Providers"
        )

    def add(self,
            name: str,
            service_type: str = None,
            description: str = None,
            credentials: 'MLCredentials' = None,
            request_headers: object = None,
            operational_space_id: str = None,
            deployment_space_id: str = None,
            group_ids: List[str] = None,
            user_ids: List[str] = None,
            background_mode: bool = True) -> 'DetailedResponse':
        """
        Add service provider.

        Assosiate external Machine Learning service instance with the OpenScale DataMart.

        :param str name: Name of the ML service instance.
        :param str service_type: (optional) machine learning service type
               (azure_machine_learning_studio is a preferred alias for
               azure_machine_learning and should be used in new service bindings).
        :param str description: (optional)
        :param MLCredentials credentials: (optional)
        :param object request_headers: (optional) map header name to header value.
        :param str operational_space_id: (optional) Reference to Operational Space.
                                         Allowed values are 'production' and 'pre-production'
        :param str deployment_space_id: (optional) Reference to V2 Space ID
        :param List[str] group_ids: (optional) Access control list of group id of
               Cloud Pak for Data (Only available for OpenScale on Cloud Pak for Data >=
               4.0.6 with ENABLE_GROUP_AUTH being true).
        :param List[str] user_ids: (optional) Access control list of user id of
               Cloud Pak for Data (Only available for OpenScale on Cloud Pak for Data >=
               4.0.6 with ENABLE_GROUP_AUTH being true).
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `ServiceProviderResponse` result

        A way you may use me when WML is located on same cluster
        
        >>> from ibm_watson_openscale import *
        >>> added_service_provider_info = client.service_providers.add(
                background_mode=False,
                name="WML instance",
                service_type=ServiceTypes.WATSON_MACHINE_LEARNING,
                deployment_space_id = <SPACE_ID>,
                operational_space_id = "production"
                credentials=WMLCredentialsCloud(
                    url='<URL>',
                    username='<USERNAME>',
                    password='<PASSWORD>'
                )
             )
        
        A way you may use me when WML is located on different CP4D cluster (Available only on CP4D 4.0 or higher)
        
        >>> from ibm_watson_openscale import *
        >>> from ibm_watson_openscale.supporting_classes.enums import *
        >>> added_service_provider_info = client.service_providers.add(
                background_mode=False,
                name="WML instance",
                service_type=ServiceTypes.WATSON_MACHINE_LEARNING,
                deployment_space_id = <SPACE_ID>,
                operational_space_id = "production"
                credentials=WMLCredentialsCloud(
                    url = '<URL>',
                    username='<USERNAME>,
                    apikey='APIKEY>',
                    wml_location = CP4DWMLLocation.CPD_REMOTE
                )
             )
             
        A way you may use me when WML is located on IBM Cloud
        
        >>> from ibm_watson_openscale import *
        >>> from ibm_watson_openscale.supporting_classes.enums import *
        >>> added_service_provider_info = client.service_providers.add(
                background_mode=False,
                name="WML instance",
                service_type=ServiceTypes.WATSON_MACHINE_LEARNING,
                deployment_space_id = <SPACE_ID>,
                operational_space_id = "production"
                credentials=WMLCredentialsCloud(
                    url = '<URL>',
                    apikey='APIKEY>',
                    wml_location = CP4DWMLLocation.CLOUD_REMOTE
                )
             )     
                  
        """
        if isinstance(service_type, str):
            validate_type(service_type, 'service_type', str, True)
        elif isinstance(credentials, WMLCredentialsCP4D) or isinstance(credentials, WMLCredentialsCloud):
            service_type = ServiceTypes.WATSON_MACHINE_LEARNING
            # Validating the credentials
            if isinstance(credentials, WMLCredentialsCloud):
                # Checking if either API key of a token is present
                if credentials.apikey is None and credentials.token is None:
                    # Both are not given
                    raise InvalidCredentialsProvided(reason="Either API key or a token must be provided.")
        elif isinstance(credentials, AzureCredentials):
            service_type = ServiceTypes.AZURE_MACHINE_LEARNING
        elif isinstance(credentials, CustomCredentials):
            service_type = ServiceTypes.CUSTOM_MACHINE_LEARNING
        elif isinstance(credentials, SageMakerCredentials):
            service_type = ServiceTypes.AMAZON_SAGEMAKER
        elif isinstance(credentials, SPSSCredentials):
            service_type = ServiceTypes.SPSS_COLLABORATION_AND_DEPLOYMENT_SERVICES
        else:
            validate_type(service_type, 'service_type', str, True)
            
        if self._ai_client.is_cp4d is not True:
            if group_ids is not None or user_ids is not None:
                raise IncorrectParameter(parameter_name= "group_ids/user_ids", reason="Parameters group_ids/user_ids are only available for OpenScale on Cloud Pak for Data >=4.0.6 ")
                         
        response = super().add(name=name, service_type=service_type, description=description,
                               credentials=credentials, request_headers=request_headers,
                               operational_space_id=operational_space_id,deployment_space_id = deployment_space_id,
                               group_ids = group_ids,user_ids = user_ids)

        service_provider_id = response.result.metadata.id

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.get(service_provider_id=service_provider_id)
                return details.result.entity.status.state

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.get(service_provider_id=service_provider_id)
                state = details.result.entity.status.state

                if state in [StatusStateType.ACTIVE]:
                    return "Successfully finished adding service provider", None, details
                else:
                    return "Add service provider failed with status: {}".format(state), \
                           'Reason: {}'.format(["code: {}, message: {}".format(error.code, error.message) for error in
                                                details.result.entity.status.failure.errors]), details

            return print_synchronous_run(
                'Waiting for end of adding service provider {}'.format(service_provider_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.ACTIVE]
            )

    def delete(self,
               service_provider_id: str,
               force: bool = None,
               background_mode: bool = True) -> 'DetailedResponse':
        """
        Delete service provider.

        Detach Machine Learning service provider.

        :param str service_provider_id: ID of the ML service provider.
        :param bool force: (optional) force hard delete.
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse

        A way you may use me:

        >>> client.service_providers.delete(
                background_mode=False,
                service_provider_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                force=True
             )
        """
        response = super().delete(service_provider_id=service_provider_id, force=force)

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.list()
                if service_provider_id not in str(details.result):
                    return StatusStateType.FINISHED
                else:
                    return StatusStateType.ACTIVE

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.list()
                if service_provider_id not in str(details.result):
                    state = StatusStateType.FINISHED
                else:
                    state = StatusStateType.ACTIVE

                if state in [StatusStateType.FINISHED]:
                    return "Successfully finished deleting service provider", None, response
                else:
                    return "Delete service provider failed", 'Reason: None', response  # TODO: Need to show the reason.

            return print_synchronous_run(
                'Waiting for end of deleting service provider {}'.format(service_provider_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.FINISHED]
            )

    def list_assets(self, data_mart_id: str, service_provider_id: str, deployment_id: str = None, deployment_space_id: str = None) -> 'Response':
        """
        Listing all deployments and assets for specific data_mart and service_provider.

        :param str data_mart_id: ID of the data_mart (required)
        :param str service_provider_id: ID of the service_provider (required)
        :param str deployment_id: ID of the deployment (optional), when used, only specific deployment is returned
        :param str deployment_space_id: (optional) Reference to V2 Space ID
        :return: Response

        A way you may use me:

        >>> response = client.service_providers.list_assets(
                data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                service_provider_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                deployment_space_id='6574djd4-00d2-4g05-ac02-287ebfc603b5'
             )
        >>> print(response.result)
         {'count': 1,
         'resources': [{'entity': {'asset': {'asset_id': '997b1474-00d2-4g05-ac02-287ebfc603b5',
                                             'asset_type': 'model',
                                             'created_at': '2020-01-13T09:15:26.586Z',
                                             'name': 'AIOS Spark Credit Risk model',
                                             'url': 'https://us-south.ml.cloud.ibm.com/v3/wml_instances/997b1474-00d2-4g05-ac02-287ebfc603b5/published_models/997b1474-00d2-4g05-ac02-287ebfc603b5'},
                                   'asset_properties': {'asset_revision': '997b1474-00d2-4g05-ac02-287ebfc603b5',
                                                        'input_data_schema': {'fields': [{'metadata': {},
                                                                                          'name': 'CheckingStatus',
                                                                                          'nullable': True,
                                                                                          'type': 'string'},
                                                                                         ...
                                                        'label_column': 'Risk',
                                                        'model_type': 'mllib-2.3',
                                                        'runtime_environment': 'spark-2.3',
                                                        'training_data_schema': {'fields': [{'metadata': {},
                                                                                             'name': 'CheckingStatus',
                                                                                             'nullable': True,
                                                                                             'type': 'string'},
                                                                                            ...
                                   'description': 'Description of deployment',
                                   'name': 'AIOS Spark Credit Risk deployment',
                                   'scoring_endpoint': {'url': 'https://us-south.ml.cloud.ibm.com/v3/wml_instances/997b1474-00d2-4g05-ac02-287ebfc603b5/deployments/997b1474-00d2-4g05-ac02-287ebfc603b5/online'},
                                   'type': 'online'},
                        'metadata': {'created_at': '2020-01-13T09:15:26.607Z',
                                     'guid': '997b1474-00d2-4g05-ac02-287ebfc603b5',
                                     'modified_at': '2020-01-13T09:15:26.848Z',
                                     'url': 'https://us-south.ml.cloud.ibm.com/v3/wml_instances/997b1474-00d2-4g05-ac02-287ebfc603b5/deployments/997b1474-00d2-4g05-ac02-287ebfc603b5'}}]}
        >>> response = client.service_providers.list_assets(
                data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                service_provider_id='997b1474-00d2-4g05-ac02-287ebfc603b5'
                deployment_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                deployment_space_id='6574djd4-00d2-4g05-ac02-287ebfc603b5'
             )
        """
        validate_type(data_mart_id, 'data_mart_id', str, True)
        validate_type(service_provider_id, 'service_provider_id', str, True)
        validate_type(deployment_id, 'deployment_id', str, False)
        validate_type(deployment_space_id, 'deployment_space_id', str, False)

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V1',
                                      operation_id='get_asset_and_deployments_details')
        headers.update(sdk_headers)
        provider_details = self.get(service_provider_id).result
        service_type = provider_details.to_dict()['entity']['service_type']
        
        if deployment_space_id is None:
            url = f'/v1/ml_instances/{service_provider_id}/deployments?datamart_id={data_mart_id}&limit=1000'
        else:    
            url = f"/openscale/{data_mart_id}/v2/ml_deployments?limit=100&service_provider_id={service_provider_id}&service_type={service_type}"
            url = url + f'&space_id={deployment_space_id}'
        
        request = self.watson_open_scale.prepare_request(method='GET',
                                                          url=url,
                                                          headers=headers)
        request['url'] = f"https://{request['url'].split('/')[2]}{url}"
        response = self.watson_open_scale.send(request)

        if deployment_id is not None and 'resources' in response.result and len(response.result['resources']) > 0:
            response.result['resources'] = [resource for resource in response.result['resources'] if resource['metadata']['guid'] == deployment_id]

        return response
    
    def get_deployment_asset(self, data_mart_id: str, service_provider_id: str, deployment_id: str, deployment_space_id: str = None ) -> 'Response':
        """
        Listing all deployments and assets for specific data_mart and service_provider.

        :param str data_mart_id: ID of the data_mart (required)
        :param str service_provider_id: ID of the service_provider (required)
        :param str deployment_id: ID of the deployment (required), when used, only specific deployment is returned
        :param str deployment_space_id: Reference to V2 Space ID (required)
        :return: Response

        A way you may use me:

        >>> response = client.service_providers.list_assets(
                data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                service_provider_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                deployment_space_id='6574djd4-00d2-4g05-ac02-287ebfc603b5'
             )
        >>> print(response.result)
         {'entity': {'asset': {'asset_id': '997b1474-00d2-4g05-ac02-287ebfc603b5',
                                             'asset_type': 'model',
                                             'created_at': '2020-01-13T09:15:26.586Z',
                                             'name': 'AIOS Spark Credit Risk model',
                                             'url': 'https://us-south.ml.cloud.ibm.com/v3/wml_instances/997b1474-00d2-4g05-ac02-287ebfc603b5/published_models/997b1474-00d2-4g05-ac02-287ebfc603b5'},
                                   'asset_properties': {'asset_revision': '997b1474-00d2-4g05-ac02-287ebfc603b5',
                                                        'input_data_schema': {'fields': [{'metadata': {},
                                                                                          'name': 'CheckingStatus',
                                                                                          'nullable': True,
                                                                                          'type': 'string'},
                                                                                         ...
                                                        'label_column': 'Risk',
                                                        'model_type': 'mllib-2.3',
                                                        'runtime_environment': 'spark-2.3',
                                                        'training_data_schema': {'fields': [{'metadata': {},
                                                                                             'name': 'CheckingStatus',
                                                                                             'nullable': True,
                                                                                             'type': 'string'},
                                                                                            ...
                                   'description': 'Description of deployment',
                                   'name': 'AIOS Spark Credit Risk deployment',
                                   'scoring_endpoint': {'url': 'https://us-south.ml.cloud.ibm.com/v3/wml_instances/997b1474-00d2-4g05-ac02-287ebfc603b5/deployments/997b1474-00d2-4g05-ac02-287ebfc603b5/online'},
                                   'type': 'online'},
                        'metadata': {'created_at': '2020-01-13T09:15:26.607Z',
                                     'guid': '997b1474-00d2-4g05-ac02-287ebfc603b5',
                                     'modified_at': '2020-01-13T09:15:26.848Z',
                                     'url': 'https://us-south.ml.cloud.ibm.com/v3/wml_instances/997b1474-00d2-4g05-ac02-287ebfc603b5/deployments/997b1474-00d2-4g05-ac02-287ebfc603b5'}}
        >>> response = client.service_providers.get_deployment_asset(
                data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                service_provider_id='997b1474-00d2-4g05-ac02-287ebfc603b5'
                deployment_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                deployment_space_id='6574djd4-00d2-4g05-ac02-287ebfc603b5'
             )
        """
        validate_type(data_mart_id, 'data_mart_id', str, True)
        validate_type(service_provider_id, 'service_provider_id', str, True)
        validate_type(deployment_id, 'deployment_id', str, True)
        validate_type(deployment_space_id, 'deployment_space_id', str, False)

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V1',
                                      operation_id='get_asset_and_deployments_details')
        headers.update(sdk_headers)
        provider_details = self.get(service_provider_id).result
        service_type = provider_details.to_dict()['entity']['service_type']
        
        
        if deployment_space_id is None:
            url = f'/v1/ml_instances/{service_provider_id}/deployments?datamart_id={data_mart_id}&limit=1000'
        else:    
            url = f"/openscale/{data_mart_id}/v2/ml_deployments/{deployment_id}?service_provider_id={service_provider_id}&service_type={service_type}&space_id={deployment_space_id}"
        
        request = self.watson_open_scale.prepare_request(method='GET',
                                                          url=url,
                                                          headers=headers)
        request['url'] = f"https://{request['url'].split('/')[2]}{url}"

        response = self.watson_open_scale.send(request)
       
        return response.result
    
