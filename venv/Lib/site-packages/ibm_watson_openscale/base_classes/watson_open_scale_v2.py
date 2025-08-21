# coding: utf-8

# (C) Copyright IBM Corp. 2022.
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

"""
Watson OpenScale API Specification
"""

from datetime import datetime
from enum import Enum
from typing import BinaryIO, Dict, List, TextIO, Union
import json

from ibm_cloud_sdk_core import BaseService, DetailedResponse
from ibm_cloud_sdk_core.authenticators.authenticator import Authenticator
from ibm_cloud_sdk_core.get_authenticator import get_authenticator_from_environment
from ibm_cloud_sdk_core.utils import convert_list, convert_model, datetime_to_string, string_to_datetime

from .common import get_sdk_headers

##############################################################################
# Service
##############################################################################

class WatsonOpenScaleV2(BaseService):
    """The Watson OpenScale V2 service."""

    DEFAULT_SERVICE_URL = None
    DEFAULT_SERVICE_NAME = 'ai_openscale'

    @classmethod
    def new_instance(cls,
                     service_name: str = DEFAULT_SERVICE_NAME,
                    ) -> 'WatsonOpenScaleV2':
        """
        Return a new client for the Watson OpenScale service using the specified
               parameters and external configuration.
        """
        authenticator = get_authenticator_from_environment(service_name)
        service = cls(
            authenticator
            )
        service.configure_service(service_name)
        return service

    def __init__(self,
                 authenticator: Authenticator = None,
                ) -> None:
        """
        Construct a new client for the Watson OpenScale service.

        :param Authenticator authenticator: The authenticator specifies the authentication mechanism.
               Get up to date information from https://github.com/IBM/python-sdk-core/blob/master/README.md
               about initializing the authenticator of your choice.
        """
        BaseService.__init__(self,
                             service_url=self.DEFAULT_SERVICE_URL,
                             authenticator=authenticator)


#########################
# Data Marts
#########################

class DataMarts:
    """
    Data Marts
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a DataMarts client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def add(self,
        *,
        name: str = None,
        description: str = None,
        service_instance_crn: str = None,
        internal_database: bool = None,
        database_configuration: 'DatabaseConfigurationRequest' = None,
        database_discovery: str = None,
        force: bool = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Create a new data mart.

        Create a new data mart with the given database connection.

        :param str name: (optional) Name of the data mart.
        :param str description: (optional) Description of the data mart.
        :param str service_instance_crn: (optional) Can be omitted if user token is
               used for authorization.
        :param bool internal_database: (optional) If `true` the internal database
               managed by AI OpenScale is provided for the user.
        :param DatabaseConfigurationRequest database_configuration: (optional)
               Database configuration ignored if internal database is requested
               (`internal_database` is `true`).
        :param str database_discovery: (optional) Indicates if the database was
               discovered automatically or manually added by user through UI.
        :param bool force: (optional) force update of metadata and db credentials
               (assumption is that the new database is already prepared and populated).
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataMartDatabaseResponse` result
        """

        if database_configuration is not None:
            database_configuration = convert_model(database_configuration)
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='data_marts_add')
        headers.update(sdk_headers)

        params = {
            'force': force
        }

        data = {
            'name': name,
            'description': description,
            'service_instance_crn': service_instance_crn,
            'internal_database': internal_database,
            'database_configuration': database_configuration,
            'database_discovery': database_discovery
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_marts'
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(DataMartDatabaseResponse, 'from_dict'):
            response.result = DataMartDatabaseResponse.from_dict(response.result)
        return response


    def list(self,
        **kwargs
    ) -> DetailedResponse:
        """
        List all data marts.

        The method returns the data mart confugrations as an object.

        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataMartDatabaseResponseCollection` result
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='data_marts_list')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_marts'
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(DataMartDatabaseResponseCollection, 'from_dict'):
            response.result = DataMartDatabaseResponseCollection.from_dict(response.result)
        return response


    def get(self,
        data_mart_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Get data mart with the given id.

        :param str data_mart_id: ID of the data mart.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataMartDatabaseResponse` result
        """

        if data_mart_id is None:
            raise ValueError('data_mart_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='data_marts_get')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_marts/{0}'.format(
            *self.watson_open_scale.encode_path_vars(data_mart_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(DataMartDatabaseResponse, 'from_dict'):
            response.result = DataMartDatabaseResponse.from_dict(response.result)
        return response


    def patch(self,
        data_mart_id: str,
        json_patch_operation: List['JsonPatchOperation'],
        **kwargs
    ) -> DetailedResponse:
        """
        Update a data mart.

        :param str data_mart_id: ID of the data mart.
        :param List[JsonPatchOperation] json_patch_operation:
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataMartDatabaseResponse` result
        """

        if data_mart_id is None:
            raise ValueError('data_mart_id must be provided')
        if json_patch_operation is None:
            raise ValueError('json_patch_operation must be provided')
        json_patch_operation = [convert_model(x) for x in json_patch_operation]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='data_marts_patch')
        headers.update(sdk_headers)

        data = json.dumps(json_patch_operation)
        headers['content-type'] = 'application/json-patch+json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_marts/{0}'.format(
            *self.watson_open_scale.encode_path_vars(data_mart_id))
        request = self.watson_open_scale.prepare_request(method='PATCH',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(DataMartDatabaseResponse, 'from_dict'):
            response.result = DataMartDatabaseResponse.from_dict(response.result)
        return response


    def delete(self,
        data_mart_id: str,
        *,
        force: bool = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Delete a data mart.

        :param str data_mart_id: ID of the data mart.
        :param bool force: (optional) force hard delete.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if data_mart_id is None:
            raise ValueError('data_mart_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='data_marts_delete')
        headers.update(sdk_headers)

        params = {
            'force': force
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/data_marts/{0}'.format(
            *self.watson_open_scale.encode_path_vars(data_mart_id))
        request = self.watson_open_scale.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        return response

#########################
# Service Providers
#########################

class ServiceProviders:
    """
    Service Providers
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a ServiceProviders client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def list(self,
        *,
        show_deleted: bool = None,
        service_type: str = None,
        instance_id: str = None,
        operational_space_id: str = None,
        deployment_space_id: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        List service providers.

        List assosiated Machine Learning service instances.

        :param bool show_deleted: (optional) show also resources pending delete.
        :param str service_type: (optional) Type of service.
        :param str instance_id: (optional) comma-separeted list of IDs.
        :param str operational_space_id: (optional) comma-separeted list of IDs.
        :param str deployment_space_id: (optional) comma-separeted list of IDs.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `ServiceProviderResponseCollection` result
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='service_providers_list')
        headers.update(sdk_headers)

        params = {
            'show_deleted': show_deleted,
            'service_type': service_type,
            'instance_id': instance_id,
            'operational_space_id': operational_space_id,
            'deployment_space_id': deployment_space_id
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/service_providers'
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(ServiceProviderResponseCollection, 'from_dict'):
            response.result = ServiceProviderResponseCollection.from_dict(response.result)
        return response


    def add(self,
        name: str,
        service_type: str,
        credentials: 'MLCredentials',
        *,
        description: str = None,
        request_headers: dict = None,
        operational_space_id: str = None,
        deployment_space_id: str = None,
        group_ids: List[str] = None,
        user_ids: List[str] = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Add service provider.

        Assosiate external Machine Learning service instance with the OpenScale DataMart.

        :param str name: Name of the ML service instance.
        :param str service_type: machine learning service type
               (azure_machine_learning_studio is a prefered alias for
               azure_machine_learning and should be used in new service bindings).
        :param MLCredentials credentials:
        :param str description: (optional)
        :param dict request_headers: (optional) map header name to header value.
        :param str operational_space_id: (optional) Reference to Operational Space.
        :param str deployment_space_id: (optional) Reference to V2 Space ID.
        :param List[str] group_ids: (optional) Access control list of group id of
               Cloud Pak for Data (Only available for OpenScale on Cloud Pak for Data >=
               4.0.6 with ENABLE_GROUP_AUTH being true).
        :param List[str] user_ids: (optional) Access control list of user id of
               Cloud Pak for Data (Only available for OpenScale on Cloud Pak for Data >=
               4.0.6 with ENABLE_GROUP_AUTH being true).
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `ServiceProviderResponse` result
        """

        if name is None:
            raise ValueError('name must be provided')
        if service_type is None:
            raise ValueError('service_type must be provided')
        if credentials is None:
            raise ValueError('credentials must be provided')
        credentials = convert_model(credentials)
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='service_providers_add')
        headers.update(sdk_headers)

        data = {
            'name': name,
            'service_type': service_type,
            'credentials': credentials,
            'description': description,
            'request_headers': request_headers,
            'operational_space_id': operational_space_id,
            'deployment_space_id': deployment_space_id,
            'group_ids': group_ids,
            'user_ids': user_ids
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/service_providers'
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(ServiceProviderResponse, 'from_dict'):
            response.result = ServiceProviderResponse.from_dict(response.result)
        return response


    def get(self,
        service_provider_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Get a specific service provider.

        Get the assosiated Machine Learning service provider details.

        :param str service_provider_id: ID of the ML service provider.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `ServiceProviderResponse` result
        """

        if service_provider_id is None:
            raise ValueError('service_provider_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='service_providers_get')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/service_providers/{0}'.format(
            *self.watson_open_scale.encode_path_vars(service_provider_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(ServiceProviderResponse, 'from_dict'):
            response.result = ServiceProviderResponse.from_dict(response.result)
        return response


    def delete(self,
        service_provider_id: str,
        *,
        force: bool = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Delete a service provider.

        Detach Machine Learning service provider.

        :param str service_provider_id: ID of the ML service provider.
        :param bool force: (optional) force hard delete.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if service_provider_id is None:
            raise ValueError('service_provider_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='service_providers_delete')
        headers.update(sdk_headers)

        params = {
            'force': force
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/service_providers/{0}'.format(
            *self.watson_open_scale.encode_path_vars(service_provider_id))
        request = self.watson_open_scale.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        return response


    def update(self,
        service_provider_id: str,
        patch_document: List['PatchDocument'],
        **kwargs
    ) -> DetailedResponse:
        """
        Update a service provider.

        Update existing service provider.

        :param str service_provider_id: ID of the ML service provider.
        :param List[PatchDocument] patch_document:
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `ServiceProviderResponse` result
        """

        if service_provider_id is None:
            raise ValueError('service_provider_id must be provided')
        if patch_document is None:
            raise ValueError('patch_document must be provided')
        patch_document = [convert_model(x) for x in patch_document]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='service_providers_update')
        headers.update(sdk_headers)

        data = json.dumps(patch_document)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/service_providers/{0}'.format(
            *self.watson_open_scale.encode_path_vars(service_provider_id))
        request = self.watson_open_scale.prepare_request(method='PATCH',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(ServiceProviderResponse, 'from_dict'):
            response.result = ServiceProviderResponse.from_dict(response.result)
        return response

#########################
# Subscriptions
#########################

class Subscriptions:
    """
    Subscriptions
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a Subscriptions client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def list(self,
        *,
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
        **kwargs
    ) -> DetailedResponse:
        """
        List subscriptions.

        List subscriptions.

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
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `SubscriptionResponseCollection` result
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='subscriptions_list')
        headers.update(sdk_headers)

        params = {
            'data_mart_id': data_mart_id,
            'service_provider_id': service_provider_id,
            'asset.asset_id': asset_asset_id,
            'deployment.deployment_id': deployment_deployment_id,
            'deployment.deployment_type': deployment_deployment_type,
            'integration_reference.integrated_system_id': integration_reference_integrated_system_id,
            'integration_reference.external_id': integration_reference_external_id,
            'risk_evaluation_status.state': risk_evaluation_status_state,
            'service_provider.operational_space_id': service_provider_operational_space_id,
            'pre_production_reference_id': pre_production_reference_id
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/subscriptions'
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(SubscriptionResponseCollection, 'from_dict'):
            response.result = SubscriptionResponseCollection.from_dict(response.result)
        return response


    def add(self,
        data_mart_id: str,
        service_provider_id: str,
        asset: 'Asset',
        deployment: 'AssetDeploymentRequest',
        *,
        asset_properties: 'AssetPropertiesRequest' = None,
        risk_evaluation_status: 'RiskEvaluationStatus' = None,
        analytics_engine: 'AnalyticsEngine' = None,
        data_sources: List['DataSource'] = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Add a new subscription.

        Add a new subscription to the model deployment.

        :param str data_mart_id:
        :param str service_provider_id:
        :param Asset asset:
        :param AssetDeploymentRequest deployment:
        :param AssetPropertiesRequest asset_properties: (optional) Additional asset
               properties (subject of discovery if not provided when creating the
               subscription).
        :param RiskEvaluationStatus risk_evaluation_status: (optional)
        :param AnalyticsEngine analytics_engine: (optional)
        :param List[DataSource] data_sources: (optional)
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `SubscriptionResponse` result
        """

        if data_mart_id is None:
            raise ValueError('data_mart_id must be provided')
        if service_provider_id is None:
            raise ValueError('service_provider_id must be provided')
        if asset is None:
            raise ValueError('asset must be provided')
        if deployment is None:
            raise ValueError('deployment must be provided')
        asset = convert_model(asset)
        deployment = convert_model(deployment)
        if asset_properties is not None:
            asset_properties = convert_model(asset_properties)
        if risk_evaluation_status is not None:
            risk_evaluation_status = convert_model(risk_evaluation_status)
        if analytics_engine is not None:
            analytics_engine = convert_model(analytics_engine)
        if data_sources is not None:
            data_sources = [convert_model(x) for x in data_sources]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='subscriptions_add')
        headers.update(sdk_headers)

        data = {
            'data_mart_id': data_mart_id,
            'service_provider_id': service_provider_id,
            'asset': asset,
            'deployment': deployment,
            'asset_properties': asset_properties,
            'risk_evaluation_status': risk_evaluation_status,
            'analytics_engine': analytics_engine,
            'data_sources': data_sources
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/subscriptions'
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(SubscriptionResponse, 'from_dict'):
            response.result = SubscriptionResponse.from_dict(response.result)
        return response


    def get(self,
        subscription_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Get a specific subscription.

        Get a specific subscription.

        :param str subscription_id: Unique subscription ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `SubscriptionResponse` result
        """

        if subscription_id is None:
            raise ValueError('subscription_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='subscriptions_get')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/subscriptions/{0}'.format(
            *self.watson_open_scale.encode_path_vars(subscription_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(SubscriptionResponse, 'from_dict'):
            response.result = SubscriptionResponse.from_dict(response.result)
        return response


    def update(self,
        subscription_id: str,
        patch_document: List['PatchDocument'],
        **kwargs
    ) -> DetailedResponse:
        """
        Update a subscription.

        Update existing asset (from ML service instance) subscription.

        :param str subscription_id: Unique subscription ID.
        :param List[PatchDocument] patch_document:
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `SubscriptionResponse` result
        """

        if subscription_id is None:
            raise ValueError('subscription_id must be provided')
        if patch_document is None:
            raise ValueError('patch_document must be provided')
        patch_document = [convert_model(x) for x in patch_document]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='subscriptions_update')
        headers.update(sdk_headers)

        data = json.dumps(patch_document)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/subscriptions/{0}'.format(
            *self.watson_open_scale.encode_path_vars(subscription_id))
        request = self.watson_open_scale.prepare_request(method='PATCH',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(SubscriptionResponse, 'from_dict'):
            response.result = SubscriptionResponse.from_dict(response.result)
        return response


    def delete(self,
        subscription_id: str,
        *,
        force: bool = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Delete a subscription.

        Delete a subscription.

        :param str subscription_id: Unique subscription ID.
        :param bool force: (optional) force hard delete.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if subscription_id is None:
            raise ValueError('subscription_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='subscriptions_delete')
        headers.update(sdk_headers)

        params = {
            'force': force
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/subscriptions/{0}'.format(
            *self.watson_open_scale.encode_path_vars(subscription_id))
        request = self.watson_open_scale.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        return response


    def schemas(self,
        subscription_id: str,
        *,
        input_data: List['ScoreData'] = None,
        training_data_reference: 'InputDataReference' = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Derive model schemas from the training data.

        Derive model schemas from the training data. Only "structured" input data type is
        supported. If the input_data_type field in the subscription (subscription ->
        entity -> asset -> input_data_type) is not "structured", an error will be
        returned.

        :param str subscription_id: Unique subscription ID.
        :param List[ScoreData] input_data: (optional) Array of score data object.
               If multiple score data objects are included, the "fields" array (if any)
               for score purposes will always be taken from the first score data object.
        :param InputDataReference training_data_reference: (optional)
               InputDataReference is the same as TrainingDataReference except that neither
               location nor connection is required. This is needed for the Schemas API and
               to avoid updating existing APIs.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `SchemaInferenceResponse` result
        """

        if subscription_id is None:
            raise ValueError('subscription_id must be provided')
        if input_data is not None:
            input_data = [convert_model(x) for x in input_data]
        if training_data_reference is not None:
            training_data_reference = convert_model(training_data_reference)
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='subscriptions_schemas')
        headers.update(sdk_headers)

        data = {
            'input_data': input_data,
            'training_data_reference': training_data_reference
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/subscriptions/{0}/schemas'.format(
            *self.watson_open_scale.encode_path_vars(subscription_id))
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(SchemaInferenceResponse, 'from_dict'):
            response.result = SchemaInferenceResponse.from_dict(response.result)
        return response


    def score(self,
        subscription_id: str,
        values: List[str],
        *,
        fields: List[str] = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Computes the bias mitigation/remediation for the specified model.

        Computes the bias mitigation/remediation for the specified model. The fairness
        monitoring debias request payload details must be valid.

        :param str subscription_id: Unique subscription ID.
        :param List[str] values: The values associated to the fields.
        :param List[str] fields: (optional) The fields to process debias scoring.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `FairnessMonitoringRemediation` result
        """

        if subscription_id is None:
            raise ValueError('subscription_id must be provided')
        if values is None:
            raise ValueError('values must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='subscriptions_score')
        headers.update(sdk_headers)

        data = {
            'values': values,
            'fields': fields
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/subscriptions/{0}/predictions'.format(
            *self.watson_open_scale.encode_path_vars(subscription_id))
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(FairnessMonitoringRemediation, 'from_dict'):
            response.result = FairnessMonitoringRemediation.from_dict(response.result)
        return response

#########################
# Data Sets
#########################

class DataSets:
    """
    Data Sets
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a DataSets client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def list(self,
        *,
        target_target_id: str = None,
        target_target_type: str = None,
        type: str = None,
        managed_by: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        List all data sets specified by the parameters.

        :param str target_target_id: (optional) ID of the data set target (e.g.
               subscription ID, business application ID).
        :param str target_target_type: (optional) type of the target.
        :param str type: (optional) type of the data set.
        :param str managed_by: (optional) ID of the managing entity (e.g. business
               application ID).
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataSetResponseCollection` result
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='data_sets_list')
        headers.update(sdk_headers)

        params = {
            'target.target_id': target_target_id,
            'target.target_type': target_target_type,
            'type': type,
            'managed_by': managed_by
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_sets'
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(DataSetResponseCollection, 'from_dict'):
            response.result = DataSetResponseCollection.from_dict(response.result)
        return response


    def add(self,
        data_mart_id: str,
        name: str,
        type: str,
        target: 'Target',
        data_schema: 'SparkStruct',
        *,
        description: str = None,
        schema_update_mode: str = None,
        location: 'LocationTableName' = None,
        managed_by: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Create a new data set.

        Create a new data set.

        :param str data_mart_id:
        :param str name:
        :param str type: type of a data set.
        :param Target target:
        :param SparkStruct data_schema:
        :param str description: (optional)
        :param str schema_update_mode: (optional)
        :param LocationTableName location: (optional)
        :param str managed_by: (optional)
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataSetResponse` result
        """

        if data_mart_id is None:
            raise ValueError('data_mart_id must be provided')
        if name is None:
            raise ValueError('name must be provided')
        if type is None:
            raise ValueError('type must be provided')
        if target is None:
            raise ValueError('target must be provided')
        if data_schema is None:
            raise ValueError('data_schema must be provided')
        target = convert_model(target)
        data_schema = convert_model(data_schema)
        if location is not None:
            location = convert_model(location)
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='data_sets_add')
        headers.update(sdk_headers)

        data = {
            'data_mart_id': data_mart_id,
            'name': name,
            'type': type,
            'target': target,
            'data_schema': data_schema,
            'description': description,
            'schema_update_mode': schema_update_mode,
            'location': location,
            'managed_by': managed_by
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_sets'
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(DataSetResponse, 'from_dict'):
            response.result = DataSetResponse.from_dict(response.result)
        return response


    def get(self,
        data_set_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Get data set with the given id.

        :param str data_set_id: ID of the data set.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataSetResponse` result
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='data_sets_get')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_sets/{0}'.format(
            *self.watson_open_scale.encode_path_vars(data_set_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(DataSetResponse, 'from_dict'):
            response.result = DataSetResponse.from_dict(response.result)
        return response


    def delete(self,
        data_set_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Delete a data set.

        :param str data_set_id: ID of the data set.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='data_sets_delete')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/data_sets/{0}'.format(
            *self.watson_open_scale.encode_path_vars(data_set_id))
        request = self.watson_open_scale.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        return response


    def update(self,
        data_set_id: str,
        patch_document: List['PatchDocument'],
        **kwargs
    ) -> DetailedResponse:
        """
        Update a data set.

        Update the data set.

        :param str data_set_id: ID of the data set.
        :param List[PatchDocument] patch_document:
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataSetResponse` result
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        if patch_document is None:
            raise ValueError('patch_document must be provided')
        patch_document = [convert_model(x) for x in patch_document]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='data_sets_update')
        headers.update(sdk_headers)

        data = json.dumps(patch_document)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_sets/{0}'.format(
            *self.watson_open_scale.encode_path_vars(data_set_id))
        request = self.watson_open_scale.prepare_request(method='PATCH',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(DataSetResponse, 'from_dict'):
            response.result = DataSetResponse.from_dict(response.result)
        return response

#########################
# Records
#########################

class Records:
    """
    Records
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a Records client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def add(self,
        data_set_id: str,
        request_body: Union[List[object], str, TextIO],
        *,
        content_type: str = None,
        header: bool = None,
        skip: int = None,
        limit: int = None,
        delimiter: str = None,
        on_error: str = None,
        csv_max_line_length: float = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Add new data set records.

        Add new data set records.

        :param str data_set_id: ID of the data set.
        :param List[object] request_body:
        :param str content_type: (optional) The type of the input. A character
               encoding can be specified by including a `charset` parameter. For example,
               'text/csv;charset=utf-8'.
        :param bool header: (optional) if not provided service will attempt to
               automatically detect header in the first line.
        :param int skip: (optional) skip number of rows from input.
        :param int limit: (optional) limit for number of processed input rows.
        :param str delimiter: (optional) delimiter character for data provided as
               csv.
        :param str on_error: (optional) expected behaviour on error.
        :param float csv_max_line_length: (optional) maximum length of single line
               in bytes (default 10MB).
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `Status` result
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        if request_body is None:
            raise ValueError('request_body must be provided')
        headers = {
            'Content-Type': content_type
        }
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='records_add')
        headers.update(sdk_headers)

        params = {
            'header': header,
            'skip': skip,
            'limit': limit,
            'delimiter': delimiter,
            'on_error': on_error,
            'csv_max_line_length': csv_max_line_length
        }

        if isinstance(request_body, list):
            data = json.dumps(request_body)
            if content_type is None:
                headers['Content-Type'] = 'application/json'
        else:
            data = request_body

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_sets/{0}/records'.format(
            *self.watson_open_scale.encode_path_vars(data_set_id))
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(Status, 'from_dict'):
            response.result = Status.from_dict(response.result)
        return response


    def list(self,
        data_set_id: str,
        *,
        start: datetime = None,
        end: datetime = None,
        limit: int = None,
        offset: int = None,
        annotations: List[str] = None,
        filter: str = None,
        include_total_count: bool = None,
        format: str = None,
        binary_format: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        List data set records.

        List data set records.

        :param str data_set_id: ID of the data set.
        :param datetime start: (optional) return records with timestamp grather
               then or equal to `start` parameter.
        :param datetime end: (optional) return records with timestamp lower then
               `end` parameter.
        :param int limit: (optional) limit for number of returned records. If the
               value is greater than 1000 than it will be truncated.
        :param int offset: (optional) offset of returned records.
        :param List[str] annotations: (optional) return record annotations with
               given names.
        :param str filter: (optional) Only return records that match given filters.
               There are two types of filters, separated by commas:
                 * normal filter (multiple are possible), {field_name}:{op}:{value} —
                     filter records directly
                 * joining filter (only a single one is possible),
               {data_set_id}.{field_name}:{op}:{value} —
                     join a data set by transaction_id (the user must ensure it's
               provided!)
                     and filter by this data set's records' field.
                     Will fail if the user hasn't provided transaction_id for both data
               sets' records. Filters of different types can be mixed. They are partly
               compatible with the ones in POST /v2/data_sets/{data_set_id}/distributions.
               Available operators:
                 | op   |  meaning                    |     example        |  code
               equivalent         |
               |:----:|:---------------------------:|:------------------:|:------------------------:|
                 | eq   |  equality                   | field:eq:value     |  field ==
               value          |
                 | gt   |  greater than               | field:gt:value     |  field >
               value           |
                 | gte  |  greater or equal           | field:gte:value    |  field >=
               value          |
                 | lt   |  less than                  | field:lt:value     |  field <
               value           |
                 | lte  |  less or equal              | field:lte:value    |  field <=
               value          |
                 | like |  matching a simple pattern* | field:like:pattern |
               pattern.match(field)    |
                 | in   |  is contained in list       | field:in:a;b;c     |
               [a,b,c].contains(field) |
               * - "%" means "one or more character", "_" means "any single character",
               other characters have their usual,
                   literal meaning (e.g. "|" means character "|").
        :param bool include_total_count: (optional) If total_count should be
               included. It can have performance impact if total_count is calculated.
        :param str format: (optional) What JSON format to use on output.
        :param str binary_format: (optional) Binary data presentation format. By
               default, the binary field value is encoded to base64 string. If _reference_
               is chosen, every binary field is moved to the _references_ section with
               value set to an uri to the particular field within the record that can be
               GET in a separate request.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `RecordsListResponse` result
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='records_list')
        headers.update(sdk_headers)

        params = {
            'start': start,
            'end': end,
            'limit': limit,
            'offset': offset,
            'annotations': convert_list(annotations),
            'filter': filter,
            'include_total_count': include_total_count,
            'format': format,
            'binary_format': binary_format
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_sets/{0}/records'.format(
            *self.watson_open_scale.encode_path_vars(data_set_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(RecordsListResponse, 'from_dict'):
            response.result = RecordsListResponse.from_dict(response.result)
        return response


    def patch(self,
        data_set_id: str,
        patch_document: List['PatchDocument'],
        **kwargs
    ) -> DetailedResponse:
        """
        Update data set records.

        Update data set records.

        :param str data_set_id: ID of the data set.
        :param List[PatchDocument] patch_document:
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `Status` result
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        if patch_document is None:
            raise ValueError('patch_document must be provided')
        patch_document = [convert_model(x) for x in patch_document]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='records_patch')
        headers.update(sdk_headers)

        data = json.dumps(patch_document)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_sets/{0}/records'.format(
            *self.watson_open_scale.encode_path_vars(data_set_id))
        request = self.watson_open_scale.prepare_request(method='PATCH',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(Status, 'from_dict'):
            response.result = Status.from_dict(response.result)
        return response


    def get(self,
        data_set_id: str,
        record_id: str,
        *,
        binary_format: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Get a specific data set record with the given id.

        Get a specific record in a data set.

        :param str data_set_id: ID of the data set.
        :param str record_id: ID of the record.
        :param str binary_format: (optional) Binary data presentation format. By
               default, the binary field value is encoded to base64 string. If _reference_
               is chosen, every binary field is moved to the _references_ section with
               value set to an uri to the particular field within the record that can be
               GET in a separate request.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataRecordResponse` result
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        if record_id is None:
            raise ValueError('record_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='records_get')
        headers.update(sdk_headers)

        params = {
            'binary_format': binary_format
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_sets/{0}/records/{1}'.format(
            *self.watson_open_scale.encode_path_vars(data_set_id, record_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(DataRecordResponse, 'from_dict'):
            response.result = DataRecordResponse.from_dict(response.result)
        return response


    def update(self,
        data_set_id: str,
        record_id: str,
        patch_document: List['PatchDocument'],
        *,
        binary_format: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Update a specific record in a data set.

        Update a specific record in a data set.

        :param str data_set_id: ID of the data set.
        :param str record_id: ID of the record.
        :param List[PatchDocument] patch_document:
        :param str binary_format: (optional) Binary data presentation format. By
               default, the binary field value is encoded to base64 string. If _reference_
               is chosen, every binary field is moved to the _references_ section with
               value set to an uri to the particular field within the record that can be
               GET in a separate request.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataRecordResponse` result
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        if record_id is None:
            raise ValueError('record_id must be provided')
        if patch_document is None:
            raise ValueError('patch_document must be provided')
        patch_document = [convert_model(x) for x in patch_document]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='records_update')
        headers.update(sdk_headers)

        params = {
            'binary_format': binary_format
        }

        data = json.dumps(patch_document)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_sets/{0}/records/{1}'.format(
            *self.watson_open_scale.encode_path_vars(data_set_id, record_id))
        request = self.watson_open_scale.prepare_request(method='PATCH',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(DataRecordResponse, 'from_dict'):
            response.result = DataRecordResponse.from_dict(response.result)
        return response


    def field(self,
        data_set_id: str,
        record_id: str,
        field_name: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Get value of a field in a given record.

        Get value of a field in a given record.

        :param str data_set_id: ID of the data set.
        :param str record_id: ID of the record.
        :param str field_name: field_name should map to db column name which value
               is to be retrieved.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        if record_id is None:
            raise ValueError('record_id must be provided')
        if field_name is None:
            raise ValueError('field_name must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='records_field')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/data_sets/{0}/records/{1}/{2}'.format(
            *self.watson_open_scale.encode_path_vars(data_set_id, record_id, field_name))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        return response


    def query(self,
        data_set_type: str,
        *,
        record_id: List[str] = None,
        transaction_id: List[str] = None,
        start: datetime = None,
        end: datetime = None,
        offset: int = None,
        limit: int = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Get data set records using record_id or transaction_id.

        Get data set records with specific record_id or transaction_id.

        :param str data_set_type: a (single) data set type.
        :param List[str] record_id: (optional) one or more record id values that
               should be matched.
        :param List[str] transaction_id: (optional) one or more transaction id
               values that should be matched.
        :param datetime start: (optional) beginning of the time range.
        :param datetime end: (optional) end of the time range.
        :param int offset: (optional) offset of returned explanations.
        :param int limit: (optional) Maximum number of elements returned.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataSetRecords` result
        """

        if data_set_type is None:
            raise ValueError('data_set_type must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='records_query')
        headers.update(sdk_headers)

        params = {
            'data_set_type': data_set_type,
            'record_id': convert_list(record_id),
            'transaction_id': convert_list(transaction_id),
            'start': start,
            'end': end,
            'offset': offset,
            'limit': limit
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_set_records'
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(DataSetRecords, 'from_dict'):
            response.result = DataSetRecords.from_dict(response.result)
        return response

#########################
# Requests
#########################

class Requests:
    """
    Requests
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a Requests client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def get(self,
        data_set_id: str,
        request_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Get status of a specific request.

        Get status of a specific request.

        :param str data_set_id: ID of the data set.
        :param str request_id: ID of the request.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `Status` result
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        if request_id is None:
            raise ValueError('request_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='requests_get')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_sets/{0}/requests/{1}'.format(
            *self.watson_open_scale.encode_path_vars(data_set_id, request_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(Status, 'from_dict'):
            response.result = Status.from_dict(response.result)
        return response

#########################
# Distributions
#########################

class Distributions:
    """
    Distributions
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a Distributions client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def add(self,
        data_set_id: str,
        start: str,
        end: str,
        dataset: str,
        group: List[str],
        *,
        limit: float = None,
        filter: str = None,
        agg: List[str] = None,
        max_bins: float = None,
        nocache: bool = None,
        **kwargs
    ) -> DetailedResponse:
        """
        add new data disbributions.

        add new data disbributions.

        :param str data_set_id: ID of the data set.
        :param str start: start datetime in ISO format.
        :param str end: end datetime in ISO format.
        :param str dataset: type of a data set.
        :param List[str] group: names of columns to be grouped.
        :param float limit: (optional) limit for number of rows, by default it is
               50,000 (max possible limit is 50,000).
        :param str filter: (optional) Filters defined by user in format:
               {field_name}:{op}:{value}. Partly compatible with filters in "filter"
               parameter of GET /v2/data_sets/{data_set_id}/records.
               Possible filter operators:
               * eq - equals (numeric, string)
               * gt - greater than (numeric)
               * gte - greater than or equal (numeric)
               * lt - lower than (numeric)
               * lte - lower than or equal (numeric)
               * in - value in a set (numeric, string)
               * field:null (a no-argument filter) - value is null (any nullable)
               * field:exists (a no-argument filter) - value is not null (any column).
        :param List[str] agg: (optional) Definition of aggregations, by default
               'count'.
               Aggregations can be one of:
               * count
               * <column_name>:sum
               * <column_name>:min
               * <column_name>:max
               * <column_name>:avg
               * <column_name>:stddev.
        :param float max_bins: (optional) max number of bins which will be
               generated for data.
        :param bool nocache: (optional) force columns data refresh.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataDistributionResponse` result
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        if start is None:
            raise ValueError('start must be provided')
        if end is None:
            raise ValueError('end must be provided')
        if dataset is None:
            raise ValueError('dataset must be provided')
        if group is None:
            raise ValueError('group must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='distributions_add')
        headers.update(sdk_headers)

        params = {
            'nocache': nocache
        }

        data = {
            'start': start,
            'end': end,
            'dataset': dataset,
            'group': group,
            'limit': limit,
            'filter': filter,
            'agg': agg,
            'max_bins': max_bins
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_sets/{0}/distributions'.format(
            *self.watson_open_scale.encode_path_vars(data_set_id))
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(DataDistributionResponse, 'from_dict'):
            response.result = DataDistributionResponse.from_dict(response.result)
        return response


    def delete(self,
        data_set_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Delete data distributions.

        Delete data distribution.

        :param str data_set_id: ID of the data set.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='distributions_delete')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/data_sets/{0}/distributions'.format(
            *self.watson_open_scale.encode_path_vars(data_set_id))
        request = self.watson_open_scale.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        return response


    def get(self,
        data_set_id: str,
        data_distribution_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Get a specific data distribution.

        Get a specific data distribution.

        :param str data_set_id: ID of the data set.
        :param str data_distribution_id: ID of the data distribution requested to
               be calculated.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataDistributionResponse` result
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        if data_distribution_id is None:
            raise ValueError('data_distribution_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='distributions_get')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/data_sets/{0}/distributions/{1}'.format(
            *self.watson_open_scale.encode_path_vars(data_set_id, data_distribution_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(DataDistributionResponse, 'from_dict'):
            response.result = DataDistributionResponse.from_dict(response.result)
        return response

#########################
# Monitors
#########################

class Monitors:
    """
    Monitors
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a Monitors client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def list(self,
        *,
        name: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        List available monitors.

        List available monitors.

        :param str name: (optional) comma-separeted list of names.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorCollections` result
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='monitors_list')
        headers.update(sdk_headers)

        params = {
            'name': name
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_definitions'
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitorCollections, 'from_dict'):
            response.result = MonitorCollections.from_dict(response.result)
        return response


    def add(self,
        name: str,
        metrics: List['MonitorMetricRequest'],
        tags: List['MonitorTagRequest'],
        *,
        description: str = None,
        applies_to: 'ApplicabilitySelection' = None,
        parameters_schema: dict = None,
        managed_by: str = None,
        schedule: 'MonitorInstanceSchedule' = None,
        schedules: 'MonitorInstanceScheduleCollection' = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Add custom monitor.

        Add custom monitor.

        :param str name: Monitor UI label (must be unique).
        :param List[MonitorMetricRequest] metrics: A list of metric definition.
        :param List[MonitorTagRequest] tags: Available tags.
        :param str description: (optional) Long monitoring description presented in
               monitoring catalog.
        :param ApplicabilitySelection applies_to: (optional)
        :param dict parameters_schema: (optional) JSON schema that will be used to
               validate monitoring parameters when enabled.
        :param str managed_by: (optional)
        :param MonitorInstanceSchedule schedule: (optional) The schedule used to
               control how frequently the target is monitored. The maximum frequency is
               once every 30 minutes.
               Defaults to once every hour if not specified.
        :param MonitorInstanceScheduleCollection schedules: (optional) A set of
               schedules used to control how frequently the target is monitored for online
               and batch deployment type.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorDisplayForm` result
        """

        if name is None:
            raise ValueError('name must be provided')
        if metrics is None:
            raise ValueError('metrics must be provided')
        if tags is None:
            raise ValueError('tags must be provided')
        metrics = [convert_model(x) for x in metrics]
        tags = [convert_model(x) for x in tags]
        if applies_to is not None:
            applies_to = convert_model(applies_to)
        if schedule is not None:
            schedule = convert_model(schedule)
        if schedules is not None:
            schedules = convert_model(schedules)
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='monitors_add')
        headers.update(sdk_headers)

        data = {
            'name': name,
            'metrics': metrics,
            'tags': tags,
            'description': description,
            'applies_to': applies_to,
            'parameters_schema': parameters_schema,
            'managed_by': managed_by,
            'schedule': schedule,
            'schedules': schedules
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_definitions'
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitorDisplayForm, 'from_dict'):
            response.result = MonitorDisplayForm.from_dict(response.result)
        return response


    def get(self,
        monitor_definition_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Get a specific monitor definition.

        Get a specific monitor definition.

        :param str monitor_definition_id: Unique monitor definition ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorDisplayForm` result
        """

        if monitor_definition_id is None:
            raise ValueError('monitor_definition_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='monitors_get')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_definitions/{0}'.format(
            *self.watson_open_scale.encode_path_vars(monitor_definition_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitorDisplayForm, 'from_dict'):
            response.result = MonitorDisplayForm.from_dict(response.result)
        return response


    def update(self,
        monitor_definition_id: str,
        name: str,
        metrics: List['MonitorMetricRequest'],
        tags: List['MonitorTagRequest'],
        *,
        description: str = None,
        applies_to: 'ApplicabilitySelection' = None,
        parameters_schema: dict = None,
        managed_by: str = None,
        schedule: 'MonitorInstanceSchedule' = None,
        schedules: 'MonitorInstanceScheduleCollection' = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Update the monitor definition.

        Update a monitor definition.

        :param str monitor_definition_id: Unique monitor definition ID.
        :param str name: Monitor UI label (must be unique).
        :param List[MonitorMetricRequest] metrics: A list of metric definition.
        :param List[MonitorTagRequest] tags: Available tags.
        :param str description: (optional) Long monitoring description presented in
               monitoring catalog.
        :param ApplicabilitySelection applies_to: (optional)
        :param dict parameters_schema: (optional) JSON schema that will be used to
               validate monitoring parameters when enabled.
        :param str managed_by: (optional)
        :param MonitorInstanceSchedule schedule: (optional) The schedule used to
               control how frequently the target is monitored. The maximum frequency is
               once every 30 minutes.
               Defaults to once every hour if not specified.
        :param MonitorInstanceScheduleCollection schedules: (optional) A set of
               schedules used to control how frequently the target is monitored for online
               and batch deployment type.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorDisplayForm` result
        """

        if monitor_definition_id is None:
            raise ValueError('monitor_definition_id must be provided')
        if name is None:
            raise ValueError('name must be provided')
        if metrics is None:
            raise ValueError('metrics must be provided')
        if tags is None:
            raise ValueError('tags must be provided')
        metrics = [convert_model(x) for x in metrics]
        tags = [convert_model(x) for x in tags]
        if applies_to is not None:
            applies_to = convert_model(applies_to)
        if schedule is not None:
            schedule = convert_model(schedule)
        if schedules is not None:
            schedules = convert_model(schedules)
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='monitors_update')
        headers.update(sdk_headers)

        data = {
            'name': name,
            'metrics': metrics,
            'tags': tags,
            'description': description,
            'applies_to': applies_to,
            'parameters_schema': parameters_schema,
            'managed_by': managed_by,
            'schedule': schedule,
            'schedules': schedules
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_definitions/{0}'.format(
            *self.watson_open_scale.encode_path_vars(monitor_definition_id))
        request = self.watson_open_scale.prepare_request(method='PUT',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitorDisplayForm, 'from_dict'):
            response.result = MonitorDisplayForm.from_dict(response.result)
        return response


    def patch(self,
        monitor_definition_id: str,
        json_patch_operation: List['JsonPatchOperation'],
        **kwargs
    ) -> DetailedResponse:
        """
        Update a monitor definition.

        Update a monitor definition.

        :param str monitor_definition_id: Unique monitor definition ID.
        :param List[JsonPatchOperation] json_patch_operation:
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorDisplayForm` result
        """

        if monitor_definition_id is None:
            raise ValueError('monitor_definition_id must be provided')
        if json_patch_operation is None:
            raise ValueError('json_patch_operation must be provided')
        json_patch_operation = [convert_model(x) for x in json_patch_operation]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='monitors_patch')
        headers.update(sdk_headers)

        data = json.dumps(json_patch_operation)
        headers['content-type'] = 'application/json-patch+json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_definitions/{0}'.format(
            *self.watson_open_scale.encode_path_vars(monitor_definition_id))
        request = self.watson_open_scale.prepare_request(method='PATCH',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitorDisplayForm, 'from_dict'):
            response.result = MonitorDisplayForm.from_dict(response.result)
        return response


    def delete(self,
        monitor_definition_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Delete a monitor definition.

        Delete a monitor definition.

        :param str monitor_definition_id: Unique monitor definition ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if monitor_definition_id is None:
            raise ValueError('monitor_definition_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='monitors_delete')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/monitor_definitions/{0}'.format(
            *self.watson_open_scale.encode_path_vars(monitor_definition_id))
        request = self.watson_open_scale.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        return response

#########################
# Instances
#########################

class Instances:
    """
    Instances
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a Instances client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def list(self,
        *,
        data_mart_id: str = None,
        monitor_definition_id: str = None,
        target_target_id: str = None,
        target_target_type: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        List monitor instances.

        List monitor instances.

        :param str data_mart_id: (optional) comma-separeted list of IDs.
        :param str monitor_definition_id: (optional) comma-separeted list of IDs.
        :param str target_target_id: (optional) comma-separeted list of IDs.
        :param str target_target_type: (optional) comma-separeted list of types.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorInstanceCollection` result
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='instances_list')
        headers.update(sdk_headers)

        params = {
            'data_mart_id': data_mart_id,
            'monitor_definition_id': monitor_definition_id,
            'target.target_id': target_target_id,
            'target.target_type': target_target_type
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_instances'
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitorInstanceCollection, 'from_dict'):
            response.result = MonitorInstanceCollection.from_dict(response.result)
        return response


    def add(self,
        data_mart_id: str,
        monitor_definition_id: str,
        target: 'Target',
        *,
        parameters: dict = None,
        thresholds: List['MetricThresholdOverride'] = None,
        schedule: 'MonitorInstanceSchedule' = None,
        schedules: 'MonitorInstanceScheduleCollection' = None,
        schedule_id: str = None,
        managed_by: str = None,
        unprocessed_records: 'RecordsCountSummary' = None,
        total_records: 'RecordsCountSummary' = None,
        skip_scheduler: bool = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Create a new monitor instance.

        Create a new monitor instance.

        :param str data_mart_id:
        :param str monitor_definition_id:
        :param Target target:
        :param dict parameters: (optional) Monitoring parameters consistent with
               the `parameters_schema` from the monitor definition.
        :param List[MetricThresholdOverride] thresholds: (optional)
        :param MonitorInstanceSchedule schedule: (optional) The schedule used to
               control how frequently the target is monitored. The maximum frequency is
               once every 30 minutes.
               Defaults to once every hour if not specified.
        :param MonitorInstanceScheduleCollection schedules: (optional) A set of
               schedules used to control how frequently the target is monitored for online
               and batch deployment type.
        :param str schedule_id: (optional)
        :param str managed_by: (optional)
        :param RecordsCountSummary unprocessed_records: (optional) Summary about
               records count.
        :param RecordsCountSummary total_records: (optional) Summary about records
               count.
        :param bool skip_scheduler: (optional) prevent schedule creation for this
               monitor instnace.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorInstanceResponse` result
        """

        if data_mart_id is None:
            raise ValueError('data_mart_id must be provided')
        if monitor_definition_id is None:
            raise ValueError('monitor_definition_id must be provided')
        if target is None:
            raise ValueError('target must be provided')
        target = convert_model(target)
        if thresholds is not None:
            thresholds = [convert_model(x) for x in thresholds]
        if schedule is not None:
            schedule = convert_model(schedule)
        if schedules is not None:
            schedules = convert_model(schedules)
        if unprocessed_records is not None:
            unprocessed_records = convert_model(unprocessed_records)
        if total_records is not None:
            total_records = convert_model(total_records)
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='instances_add')
        headers.update(sdk_headers)

        params = {
            'skip_scheduler': skip_scheduler
        }

        data = {
            'data_mart_id': data_mart_id,
            'monitor_definition_id': monitor_definition_id,
            'target': target,
            'parameters': parameters,
            'thresholds': thresholds,
            'schedule': schedule,
            'schedules': schedules,
            'schedule_id': schedule_id,
            'managed_by': managed_by,
            'unprocessed_records': unprocessed_records,
            'total_records': total_records
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_instances'
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitorInstanceResponse, 'from_dict'):
            response.result = MonitorInstanceResponse.from_dict(response.result)
        return response


    def get(self,
        monitor_instance_id: str,
        *,
        expand: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Get monitor instance details.

        Get monitor instance details.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param str expand: (optional) comma-separeted list of fields (supported
               fields are unprocessed_records and total_records).
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorInstanceResponse` result
        """

        if monitor_instance_id is None:
            raise ValueError('monitor_instance_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='instances_get')
        headers.update(sdk_headers)

        params = {
            'expand': expand
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_instances/{0}'.format(
            *self.watson_open_scale.encode_path_vars(monitor_instance_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitorInstanceResponse, 'from_dict'):
            response.result = MonitorInstanceResponse.from_dict(response.result)
        return response


    def update(self,
        monitor_instance_id: str,
        patch_document: List['PatchDocument'],
        *,
        update_metadata_only: bool = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Update a monitor instance.

        Update a monitor instance.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param List[PatchDocument] patch_document:
        :param bool update_metadata_only: (optional) Flag that allows to control if
               the underlaying actions related to the monitor reconfiguration should be
               triggered.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorInstanceResponse` result
        """

        if monitor_instance_id is None:
            raise ValueError('monitor_instance_id must be provided')
        if patch_document is None:
            raise ValueError('patch_document must be provided')
        patch_document = [convert_model(x) for x in patch_document]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='instances_update')
        headers.update(sdk_headers)

        params = {
            'update_metadata_only': update_metadata_only
        }

        data = json.dumps(patch_document)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_instances/{0}'.format(
            *self.watson_open_scale.encode_path_vars(monitor_instance_id))
        request = self.watson_open_scale.prepare_request(method='PATCH',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitorInstanceResponse, 'from_dict'):
            response.result = MonitorInstanceResponse.from_dict(response.result)
        return response


    def delete(self,
        monitor_instance_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Delete a monitor instance.

        Delete a monitor instance.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if monitor_instance_id is None:
            raise ValueError('monitor_instance_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='instances_delete')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/monitor_instances/{0}'.format(
            *self.watson_open_scale.encode_path_vars(monitor_instance_id))
        request = self.watson_open_scale.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        return response

#########################
# Runs
#########################

class Runs:
    """
    Runs
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a Runs client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def add(self,
        monitor_instance_id: str,
        *,
        triggered_by: str = None,
        parameters: dict = None,
        business_metric_context: 'MonitoringRunBusinessMetricContext' = None,
        expiration_date: datetime = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Trigger monitoring run.

        Trigger monitoring run.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param str triggered_by: (optional) An identifier representing the source
               that triggered the run request (optional). One of: event, scheduler, user,
               webhook.
        :param dict parameters: (optional) Monitoring parameters consistent with
               the `parameters_schema` from the monitor definition.
        :param MonitoringRunBusinessMetricContext business_metric_context:
               (optional) Properties defining the business metric context in the triggered
               run of AI metric calculation.
        :param datetime expiration_date: (optional) The timestamp when the
               monitoring run was created with expiry date (in the format
               YYYY-MM-DDTHH:mm:ssZ or YYYY-MM-DDTHH:mm:ss.sssZ, matching the date-time
               format as specified by RFC 3339).
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitoringRun` result
        """

        if monitor_instance_id is None:
            raise ValueError('monitor_instance_id must be provided')
        if business_metric_context is not None:
            business_metric_context = convert_model(business_metric_context)
        if expiration_date is not None:
            expiration_date = datetime_to_string(expiration_date)
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='runs_add')
        headers.update(sdk_headers)

        data = {
            'triggered_by': triggered_by,
            'parameters': parameters,
            'business_metric_context': business_metric_context,
            'expiration_date': expiration_date
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_instances/{0}/runs'.format(
            *self.watson_open_scale.encode_path_vars(monitor_instance_id))
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitoringRun, 'from_dict'):
            response.result = MonitoringRun.from_dict(response.result)
        return response


    def list(self,
        monitor_instance_id: str,
        *,
        start: str = None,
        limit: int = None,
        **kwargs
    ) -> DetailedResponse:
        """
        List monitoring runs.

        List monitoring runs.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param str start: (optional) The page token indicating where to start
               paging from.
        :param int limit: (optional) The limit of the number of items to return,
               for example limit=50. If not specified a default of 100 will be  used.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitoringRunCollection` result
        """

        if monitor_instance_id is None:
            raise ValueError('monitor_instance_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='runs_list')
        headers.update(sdk_headers)

        params = {
            'start': start,
            'limit': limit
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_instances/{0}/runs'.format(
            *self.watson_open_scale.encode_path_vars(monitor_instance_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitoringRunCollection, 'from_dict'):
            response.result = MonitoringRunCollection.from_dict(response.result)
        return response


    def get(self,
        monitor_instance_id: str,
        monitoring_run_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Get monitoring run details.

        Get monitoring run details.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param str monitoring_run_id: Unique monitoring run ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitoringRun` result
        """

        if monitor_instance_id is None:
            raise ValueError('monitor_instance_id must be provided')
        if monitoring_run_id is None:
            raise ValueError('monitoring_run_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='runs_get')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_instances/{0}/runs/{1}'.format(
            *self.watson_open_scale.encode_path_vars(monitor_instance_id, monitoring_run_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitoringRun, 'from_dict'):
            response.result = MonitoringRun.from_dict(response.result)
        return response


    def update(self,
        monitor_instance_id: str,
        monitoring_run_id: str,
        json_patch_operation: List['JsonPatchOperation'],
        **kwargs
    ) -> DetailedResponse:
        """
        Update existing monitoring run details.

        Update existing monitoring run details.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param str monitoring_run_id: Unique monitoring run ID.
        :param List[JsonPatchOperation] json_patch_operation:
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitoringRun` result
        """

        if monitor_instance_id is None:
            raise ValueError('monitor_instance_id must be provided')
        if monitoring_run_id is None:
            raise ValueError('monitoring_run_id must be provided')
        if json_patch_operation is None:
            raise ValueError('json_patch_operation must be provided')
        json_patch_operation = [convert_model(x) for x in json_patch_operation]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='runs_update')
        headers.update(sdk_headers)

        data = json.dumps(json_patch_operation)
        headers['content-type'] = 'application/json-patch+json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_instances/{0}/runs/{1}'.format(
            *self.watson_open_scale.encode_path_vars(monitor_instance_id, monitoring_run_id))
        request = self.watson_open_scale.prepare_request(method='PATCH',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitoringRun, 'from_dict'):
            response.result = MonitoringRun.from_dict(response.result)
        return response

#########################
# Measurements
#########################

class Measurements:
    """
    Measurements
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a Measurements client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def add(self,
        monitor_instance_id: str,
        monitor_measurement_request: List['MonitorMeasurementRequest'],
        **kwargs
    ) -> DetailedResponse:
        """
        Publish measurement data to OpenScale.

        Publish measurement data to OpenScale.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param List[MonitorMeasurementRequest] monitor_measurement_request:
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if monitor_instance_id is None:
            raise ValueError('monitor_instance_id must be provided')
        if monitor_measurement_request is None:
            raise ValueError('monitor_measurement_request must be provided')
        monitor_measurement_request = [convert_model(x) for x in monitor_measurement_request]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='measurements_add')
        headers.update(sdk_headers)

        data = json.dumps(monitor_measurement_request)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/monitor_instances/{0}/measurements'.format(
            *self.watson_open_scale.encode_path_vars(monitor_instance_id))
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        return response


    def list(self,
        monitor_instance_id: str,
        start: datetime,
        end: datetime,
        run_id: str,
        *,
        filter: str = None,
        limit: int = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Query measeurements from OpenScale DataMart.

        Query measeurements from OpenScale DataMart. It is required to either provide a
        `start end` or `run_id` parameter.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param datetime start: Beginning of the time range.
        :param datetime end: End of the time range.
        :param str run_id: Comma delimited list of measurement run_id.
        :param str filter: (optional) Filter expression can consist of any metric
               tag or a common column of string type followed by filter name and
               optionally a value, all delimited by colon. Supported filters are: `in`,
               `eq`, `null` and `exists`. Sample filters are:
               `filter=region:in:[us,pl],segment:eq:sales` or
               `filter=region:null,segment:exists`.
        :param int limit: (optional) Maximum number of elements returned.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorMeasurementResponseCollection` result
        """

        if monitor_instance_id is None:
            raise ValueError('monitor_instance_id must be provided')
        if start is None:
            raise ValueError('start must be provided')
        if end is None:
            raise ValueError('end must be provided')
        if run_id is None:
            raise ValueError('run_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='measurements_list')
        headers.update(sdk_headers)

        params = {
            'start': start,
            'end': end,
            'run_id': run_id,
            'filter': filter,
            'limit': limit
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_instances/{0}/measurements'.format(
            *self.watson_open_scale.encode_path_vars(monitor_instance_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitorMeasurementResponseCollection, 'from_dict'):
            response.result = MonitorMeasurementResponseCollection.from_dict(response.result)
        return response


    def get(self,
        monitor_instance_id: str,
        measurement_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Get measeurement data from OpenScale DataMart.

        Get measeurement data from OpenScale DataMart.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param str measurement_id: Uniq monitoring run ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorMeasurementResponse` result
        """

        if monitor_instance_id is None:
            raise ValueError('monitor_instance_id must be provided')
        if measurement_id is None:
            raise ValueError('measurement_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='measurements_get')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_instances/{0}/measurements/{1}'.format(
            *self.watson_open_scale.encode_path_vars(monitor_instance_id, measurement_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(MonitorMeasurementResponse, 'from_dict'):
            response.result = MonitorMeasurementResponse.from_dict(response.result)
        return response


    def query(self,
        *,
        target_id: str = None,
        target_type: str = None,
        monitor_definition_id: str = None,
        filter: str = None,
        recent_count: int = None,
        format: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Query for the recent measurement.

        Query for the recent measurement grouped by the monitoring target (subscription or
        business application).

        :param str target_id: (optional) Comma separated ID of the monitoring
               target (subscription or business application).
        :param str target_type: (optional) Type of the monitoring target
               (subscription or business application).
        :param str monitor_definition_id: (optional) Comma separated ID of the
               monitor definition.
        :param str filter: (optional) Filter expression can consist of any metric
               tag or a common column of string type followed by filter name and
               optionally a value, all delimited by colon and prepended with
               `monitor_definition_id.` string. Supported filters are: `in`, `eq`, `null`
               and `exists`. Sample filters are:
               `monitor_definition_id.filter=region:in:[us,pl],monitor_definition_id.segment:eq:sales`
               or
               `filter=monitor_definition_id.region:null,monitor_definition_id.segment:exists`.
               Every monitor_definition_id can have own set of filters.
        :param int recent_count: (optional) Number of measurements (per target) to
               be returned.
        :param str format: (optional) Format of the returned data. `full` format
               compared to `compact` is additive and contains `sources` part.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MeasurementsResponseCollection` result
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='measurements_query')
        headers.update(sdk_headers)

        params = {
            'target_id': target_id,
            'target_type': target_type,
            'monitor_definition_id': monitor_definition_id,
            'filter': filter,
            'recent_count': recent_count,
            'format': format
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/measurements'
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(MeasurementsResponseCollection, 'from_dict'):
            response.result = MeasurementsResponseCollection.from_dict(response.result)
        return response

#########################
# Metrics
#########################

class Metrics:
    """
    Metrics
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a Metrics client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def list(self,
        monitor_instance_id: str,
        start: datetime,
        end: datetime,
        agg: str,
        *,
        interval: str = None,
        filter: str = None,
        group: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Query monitor instance metrics from OpenScale DataMart.

        Query monitor instance metrics from OpenScale DataMart. See <a
        href="https://github.ibm.com/aiopenscale/aios-datamart-service-api/wiki/1.3.-Metrics-Query-Language">Metrics
        Query Language documentation</a>.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param datetime start: Calculations **inclusive**, internally floored to
               achieve full interval. If interval is vulnerable to time zone, the
               calculated value depends on a backend db engine: PostgreSQL respects time
               zone and DB2 use UTC time. Calculated value is returned in response.
        :param datetime end: Calculations **exclusive**, internally ceiled to
               achieve full interval. If interval is vulnerable to time zone, the
               calculated value depends on a backend db engine: PostgreSQL respects time
               zone and DB2 use UTC time. Calculated value is returned in response.
        :param str agg: Comma delimited function list constructed from metric name
               and function, e.g. `agg=metric_name:count,:last` that defines aggregations.
        :param str interval: (optional) Time unit in which metrics are grouped and
               aggregated, interval by interval.
        :param str filter: (optional) Filter expression can consist of any metric
               tag or a common column of string type followed by filter name and
               optionally a value, all delimited by colon. Supported filters are: `in`,
               `eq`, `null` and `exists`. Sample filters are:
               `filter=region:in:[us,pl],segment:eq:sales` or
               `filter=region:null,segment:exists`.
        :param str group: (optional) Comma delimited list constructed from metric
               tags, e.g. `group=region,segment` to group metrics before aggregations.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataMartGetMonitorInstanceMetrics` result
        """

        if monitor_instance_id is None:
            raise ValueError('monitor_instance_id must be provided')
        if start is None:
            raise ValueError('start must be provided')
        if end is None:
            raise ValueError('end must be provided')
        if agg is None:
            raise ValueError('agg must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='metrics_list')
        headers.update(sdk_headers)

        params = {
            'start': start,
            'end': end,
            'agg': agg,
            'interval': interval,
            'filter': filter,
            'group': group
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/monitor_instances/{0}/metrics'.format(
            *self.watson_open_scale.encode_path_vars(monitor_instance_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(DataMartGetMonitorInstanceMetrics, 'from_dict'):
            response.result = DataMartGetMonitorInstanceMetrics.from_dict(response.result)
        return response

#########################
# Integrated Systems
#########################

class IntegratedSystems:
    """
    Integrated Systems
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a IntegratedSystems client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def list(self,
        **kwargs
    ) -> DetailedResponse:
        """
        List integrated systems.

        List integrated systems.

        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `IntegratedSystemCollection` result
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='integrated_systems_list')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/integrated_systems'
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(IntegratedSystemCollection, 'from_dict'):
            response.result = IntegratedSystemCollection.from_dict(response.result)
        return response


    def add(self,
        name: str,
        type: str,
        description: str,
        credentials: dict,
        *,
        connection: object = None,
        group_ids: List[str] = None,
        user_ids: List[str] = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Create a new integrated system.

        Create a new integrated system.

        :param str name: The name of the Integrated System.
        :param str type:
        :param str description: The description of the Integrated System.
        :param dict credentials: The credentials for the Integrated System.
        :param object connection: (optional) The additional connection information
               for the Integrated System.
        :param List[str] group_ids: (optional) Access control list of group id of
               Cloud Pak for Data (Only available for open_pages type and OpenScale on
               Cloud Pak for Data >= 4.0.6 with ENABLE_GROUP_AUTH being true).
        :param List[str] user_ids: (optional) Access control list of user id of
               Cloud Pak for Data (Only available for open_pages type and OpenScale on
               Cloud Pak for Data >= 4.0.6 with ENABLE_GROUP_AUTH being true).
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `IntegratedSystemResponse` result
        """

        if name is None:
            raise ValueError('name must be provided')
        if type is None:
            raise ValueError('type must be provided')
        if description is None:
            raise ValueError('description must be provided')
        if credentials is None:
            raise ValueError('credentials must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='integrated_systems_add')
        headers.update(sdk_headers)

        data = {
            'name': name,
            'type': type,
            'description': description,
            'credentials': credentials,
            'connection': connection,
            'group_ids': group_ids,
            'user_ids': user_ids
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/integrated_systems'
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(IntegratedSystemResponse, 'from_dict'):
            response.result = IntegratedSystemResponse.from_dict(response.result)
        return response


    def get(self,
        integrated_system_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Get a specific integrated system.

        Get a specific integrated system.

        :param str integrated_system_id: Unique integrated system ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `IntegratedSystemResponse` result
        """

        if integrated_system_id is None:
            raise ValueError('integrated_system_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='integrated_systems_get')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/integrated_systems/{0}'.format(
            *self.watson_open_scale.encode_path_vars(integrated_system_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(IntegratedSystemResponse, 'from_dict'):
            response.result = IntegratedSystemResponse.from_dict(response.result)
        return response


    def update(self,
        integrated_system_id: str,
        json_patch_operation: List['JsonPatchOperation'],
        **kwargs
    ) -> DetailedResponse:
        """
        Update an integrated system.

        Update an integrated system.

        :param str integrated_system_id: Unique integrated system ID.
        :param List[JsonPatchOperation] json_patch_operation:
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `IntegratedSystemResponse` result
        """

        if integrated_system_id is None:
            raise ValueError('integrated_system_id must be provided')
        if json_patch_operation is None:
            raise ValueError('json_patch_operation must be provided')
        json_patch_operation = [convert_model(x) for x in json_patch_operation]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='integrated_systems_update')
        headers.update(sdk_headers)

        data = json.dumps(json_patch_operation)
        headers['content-type'] = 'application/json-patch+json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/integrated_systems/{0}'.format(
            *self.watson_open_scale.encode_path_vars(integrated_system_id))
        request = self.watson_open_scale.prepare_request(method='PATCH',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(IntegratedSystemResponse, 'from_dict'):
            response.result = IntegratedSystemResponse.from_dict(response.result)
        return response


    def delete(self,
        integrated_system_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Delete an integrated system.

        Delete an integrated system.

        :param str integrated_system_id: Unique integrated system ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if integrated_system_id is None:
            raise ValueError('integrated_system_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='integrated_systems_delete')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/integrated_systems/{0}'.format(
            *self.watson_open_scale.encode_path_vars(integrated_system_id))
        request = self.watson_open_scale.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        return response

#########################
# Operational Spaces
#########################

class OperationalSpaces:
    """
    Operational Spaces
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a OperationalSpaces client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def list(self,
        **kwargs
    ) -> DetailedResponse:
        """
        List Operational Spaces.

        List Operational Spaces.

        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `OperationalSpaceCollection` result
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='operational_spaces_list')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/operational_spaces'
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(OperationalSpaceCollection, 'from_dict'):
            response.result = OperationalSpaceCollection.from_dict(response.result)
        return response


    def add(self,
        name: str,
        *,
        description: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Create an operational space.

        Create an operational space.

        :param str name: The name of the Operational Space.
        :param str description: (optional) The description of the Operational
               Space.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `OperationalSpaceResponse` result
        """

        if name is None:
            raise ValueError('name must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='operational_spaces_add')
        headers.update(sdk_headers)

        data = {
            'name': name,
            'description': description
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/operational_spaces'
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(OperationalSpaceResponse, 'from_dict'):
            response.result = OperationalSpaceResponse.from_dict(response.result)
        return response


    def get(self,
        operational_space_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Get an operational space.

        Get an operational space.

        :param str operational_space_id: Unique Operational Space ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `OperationalSpaceResponse` result
        """

        if operational_space_id is None:
            raise ValueError('operational_space_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='operational_spaces_get')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/operational_spaces/{0}'.format(
            *self.watson_open_scale.encode_path_vars(operational_space_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(OperationalSpaceResponse, 'from_dict'):
            response.result = OperationalSpaceResponse.from_dict(response.result)
        return response


    def update(self,
        operational_space_id: str,
        json_patch_operation: List['JsonPatchOperation'],
        **kwargs
    ) -> DetailedResponse:
        """
        Update an operational space.

        Update an operational space.

        :param str operational_space_id: Unique Operational Space ID.
        :param List[JsonPatchOperation] json_patch_operation:
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `OperationalSpaceResponse` result
        """

        if operational_space_id is None:
            raise ValueError('operational_space_id must be provided')
        if json_patch_operation is None:
            raise ValueError('json_patch_operation must be provided')
        json_patch_operation = [convert_model(x) for x in json_patch_operation]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='operational_spaces_update')
        headers.update(sdk_headers)

        data = json.dumps(json_patch_operation)
        headers['content-type'] = 'application/json-patch+json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/operational_spaces/{0}'.format(
            *self.watson_open_scale.encode_path_vars(operational_space_id))
        request = self.watson_open_scale.prepare_request(method='PATCH',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(OperationalSpaceResponse, 'from_dict'):
            response.result = OperationalSpaceResponse.from_dict(response.result)
        return response


    def delete(self,
        operational_space_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Delete an operational space.

        Delete an operational space.

        :param str operational_space_id: Unique Operational Space ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if operational_space_id is None:
            raise ValueError('operational_space_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='operational_spaces_delete')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/operational_spaces/{0}'.format(
            *self.watson_open_scale.encode_path_vars(operational_space_id))
        request = self.watson_open_scale.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        return response

#########################
# User Preferences
#########################

class UserPreferences:
    """
    User Preferences
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a UserPreferences client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def list(self,
        **kwargs
    ) -> DetailedResponse:
        """
        Get User Preferences.

        Get User Preferences.

        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='user_preferences_list')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/user_preferences'
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        return response


    def patch(self,
        json_patch_operation: List['JsonPatchOperation'],
        **kwargs
    ) -> DetailedResponse:
        """
        Update User Preferences.

        Update User Preferences.

        :param List[JsonPatchOperation] json_patch_operation:
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if json_patch_operation is None:
            raise ValueError('json_patch_operation must be provided')
        json_patch_operation = [convert_model(x) for x in json_patch_operation]
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='user_preferences_patch')
        headers.update(sdk_headers)

        data = json.dumps(json_patch_operation)
        headers['content-type'] = 'application/json-patch+json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/user_preferences'
        request = self.watson_open_scale.prepare_request(method='PATCH',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        return response


    def get(self,
        user_preference_key: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Get a specific user prefrence.

        Get a specific user preference.

        :param str user_preference_key: key in user preferences.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `UserPreferencesGetResponse` result
        """

        if user_preference_key is None:
            raise ValueError('user_preference_key must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='user_preferences_get')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/user_preferences/{0}'.format(
            *self.watson_open_scale.encode_path_vars(user_preference_key))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        if hasattr(UserPreferencesGetResponse, 'from_dict'):
            response.result = UserPreferencesGetResponse.from_dict(response.result)
        return response


    def update(self,
        user_preference_key: str,
        user_preferences_update_request: 'UserPreferencesUpdateRequest',
        **kwargs
    ) -> DetailedResponse:
        """
        Update the user preference.

        Update the user preference.

        :param str user_preference_key: key in user preferences.
        :param UserPreferencesUpdateRequest user_preferences_update_request:
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if user_preference_key is None:
            raise ValueError('user_preference_key must be provided')
        if user_preferences_update_request is None:
            raise ValueError('user_preferences_update_request must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='user_preferences_update')
        headers.update(sdk_headers)

        data = json.dumps(user_preferences_update_request)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/user_preferences/{0}'.format(
            *self.watson_open_scale.encode_path_vars(user_preference_key))
        request = self.watson_open_scale.prepare_request(method='PUT',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        return response


    def delete(self,
        user_preference_key: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Delete the user preference.

        Delete the user preference.

        :param str user_preference_key: key in user preferences.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if user_preference_key is None:
            raise ValueError('user_preference_key must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='user_preferences_delete')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/user_preferences/{0}'.format(
            *self.watson_open_scale.encode_path_vars(user_preference_key))
        request = self.watson_open_scale.prepare_request(method='DELETE',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        return response

#########################
# Explanation Tasks
#########################

class ExplanationTasks:
    """
    Explanation Tasks
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a ExplanationTasks client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def add(self,
        *,
        scoring_ids: List[str] = None,
        input_rows: List[dict] = None,
        explanation_types: List[str] = None,
        subscription_id: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Compute explanations.

        Submit tasks for computing explanation of predictions.

        :param List[str] scoring_ids: (optional) IDs of the scoring transaction.
        :param List[dict] input_rows: (optional) List of scoring transactions.
        :param List[str] explanation_types: (optional) Types of explanations to
               generate.
        :param str subscription_id: (optional) Unique subscription ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `PostExplanationTaskResponse` result
        """

        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='explanation_tasks_add')
        headers.update(sdk_headers)

        data = {
            'scoring_ids': scoring_ids,
            'input_rows': input_rows,
            'explanation_types': explanation_types,
            'subscription_id': subscription_id
        }
        data = {k: v for (k, v) in data.items() if v is not None}
        data = json.dumps(data)
        headers['content-type'] = 'application/json'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/explanation_tasks'
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       data=data)

        response = self.watson_open_scale.send(request)
        if hasattr(PostExplanationTaskResponse, 'from_dict'):
            response.result = PostExplanationTaskResponse.from_dict(response.result)
        return response


    def list(self,
        subscription_id: str,
        *,
        offset: int = None,
        limit: int = None,
        scoring_id: str = None,
        status: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        List all explanations.

        List of all the computed explanations.

        :param str subscription_id: Unique subscription ID.
        :param int offset: (optional) offset of the explanations to return.
        :param int limit: (optional) Maximum number of explanations to return.
        :param str scoring_id: (optional) ID of the scoring transaction.
        :param str status: (optional) Status of the explanation task.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `GetExplanationTasksResponse` result
        """

        if subscription_id is None:
            raise ValueError('subscription_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='explanation_tasks_list')
        headers.update(sdk_headers)

        params = {
            'subscription_id': subscription_id,
            'offset': offset,
            'limit': limit,
            'scoring_id': scoring_id,
            'status': status
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/explanation_tasks'
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(GetExplanationTasksResponse, 'from_dict'):
            response.result = GetExplanationTasksResponse.from_dict(response.result)
        return response


    def get(self,
        explanation_task_id: str,
        *,
        subscription_id: str = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Get explanation.

        Get explanation for the given explanation task id.

        :param str explanation_task_id: ID of the explanation task.
        :param str subscription_id: (optional) Unique subscription ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `GetExplanationTaskResponse` result
        """

        if explanation_task_id is None:
            raise ValueError('explanation_task_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='explanation_tasks_get')
        headers.update(sdk_headers)

        params = {
            'subscription_id': subscription_id
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/json'

        url = '/v2/explanation_tasks/{0}'.format(
            *self.watson_open_scale.encode_path_vars(explanation_task_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        if hasattr(GetExplanationTaskResponse, 'from_dict'):
            response.result = GetExplanationTaskResponse.from_dict(response.result)
        return response

#########################
# Drift Service
#########################

class DriftService:
    """
    Drift Service
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a DriftService client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def drift_archive_head(self,
        monitor_instance_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Retrieves the Drift archive metadata.

        API to retrieve the Drift archive metadata.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if monitor_instance_id is None:
            raise ValueError('monitor_instance_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='drift_archive_head')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/monitoring_services/drift/monitor_instances/{0}/archives'.format(
            *self.watson_open_scale.encode_path_vars(monitor_instance_id))
        request = self.watson_open_scale.prepare_request(method='HEAD',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        return response


    def drift_archive_post(self,
        data_mart_id: str,
        subscription_id: str,
        body: BinaryIO,
        *,
        archive_name: str = None,
        enable_data_drift: bool = None,
        enable_model_drift: bool = None,
        **kwargs
    ) -> DetailedResponse:
        """
        Upload Drift archives.

        API to upload drift archive such as the Drift Detection Model.

        :param str data_mart_id: ID of the data mart.
        :param str subscription_id: Unique subscription ID.
        :param BinaryIO body:
        :param str archive_name: (optional) The name of the archive being uploaded.
        :param bool enable_data_drift: (optional) Flag to enable/disable data
               drift.
        :param bool enable_model_drift: (optional) Flag to enable/disable model
               drift.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if data_mart_id is None:
            raise ValueError('data_mart_id must be provided')
        if subscription_id is None:
            raise ValueError('subscription_id must be provided')
        if body is None:
            raise ValueError('body must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='drift_archive_post')
        headers.update(sdk_headers)

        params = {
            'archive_name': archive_name,
            'enable_data_drift': enable_data_drift,
            'enable_model_drift': enable_model_drift
        }

        data = body
        headers['content-type'] = 'application/octet-stream'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/monitoring_services/drift/data_marts/{0}/subscriptions/{1}/archives'.format(
            *self.watson_open_scale.encode_path_vars(data_mart_id, subscription_id))
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.watson_open_scale.send(request)
        return response


    def drift_archive_get(self,
        monitor_instance_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Retrieves the Drift archives.

        API to retrieve the Drift archives.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if monitor_instance_id is None:
            raise ValueError('monitor_instance_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='drift_archive_get')
        headers.update(sdk_headers)

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/octet-stream'

        url = '/v2/monitoring_services/drift/monitor_instances/{0}/archives'.format(
            *self.watson_open_scale.encode_path_vars(monitor_instance_id))
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers)

        response = self.watson_open_scale.send(request)
        return response

#########################
# explainabilityService
#########################

class ExplainabilityService:
    """
    explainabilityService
    """

    def __init__(self, watson_open_scale: WatsonOpenScaleV2) -> None:
        """
        Construct a ExplainabilityService client for the Watson OpenScale service.

        :param WatsonOpenScaleV2 watson_open_scale: client for the Watson OpenScale service.
        """
        self.watson_open_scale = watson_open_scale


    def explainability_archive_post(self,
        subscription_id: str,
        body: BinaryIO,
        **kwargs
    ) -> DetailedResponse:
        """
        Upload explainability archives.

        API to upload explainability archives such as the Perturbations scoring response
        archive. The api can also be used to update the archive.

        :param str subscription_id: Unique subscription ID.
        :param BinaryIO body:
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if subscription_id is None:
            raise ValueError('subscription_id must be provided')
        if body is None:
            raise ValueError('body must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='explainability_archive_post')
        headers.update(sdk_headers)

        params = {
            'subscription_id': subscription_id
        }

        data = body
        headers['content-type'] = 'application/octet-stream'

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))

        url = '/v2/monitoring_services/explainability/archives'
        request = self.watson_open_scale.prepare_request(method='POST',
                                       url=url,
                                       headers=headers,
                                       params=params,
                                       data=data)

        response = self.watson_open_scale.send(request)
        return response


    def explainability_archive_get(self,
        subscription_id: str,
        **kwargs
    ) -> DetailedResponse:
        """
        Retrieves the Explainability archives.

        API to retrieve the Explainability archives.

        :param str subscription_id: Unique subscription ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """

        if subscription_id is None:
            raise ValueError('subscription_id must be provided')
        headers = {}
        sdk_headers = get_sdk_headers(service_name=self.watson_open_scale.DEFAULT_SERVICE_NAME,
                                      service_version='V2',
                                      operation_id='explainability_archive_get')
        headers.update(sdk_headers)

        params = {
            'subscription_id': subscription_id
        }

        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        headers['Accept'] = 'application/octet-stream'

        url = '/v2/monitoring_services/explainability/archives'
        request = self.watson_open_scale.prepare_request(method='GET',
                                       url=url,
                                       headers=headers,
                                       params=params)

        response = self.watson_open_scale.send(request)
        return response


class DataSetsListEnums:
    """
    Enums for data_sets_list parameters.
    """

    class TargetTargetType(str, Enum):
        """
        type of the target.
        """
        SUBSCRIPTION = 'subscription'
        BUSINESS_APPLICATION = 'business_application'
        INSTANCE = 'instance'
        DATA_MART = 'data_mart'
    class Type(str, Enum):
        """
        type of the data set.
        """
        MANUAL_LABELING = 'manual_labeling'
        PAYLOAD_LOGGING = 'payload_logging'
        FEEDBACK = 'feedback'
        BUSINESS_PAYLOAD = 'business_payload'
        EXPLANATIONS = 'explanations'
        EXPLANATIONS_WHATIF = 'explanations_whatif'
        TRAINING = 'training'
        PAYLOAD_LOGGING_ERROR = 'payload_logging_error'
        CUSTOM = 'custom'


class RecordsAddEnums:
    """
    Enums for records_add parameters.
    """

    class ContentType(str, Enum):
        """
        The type of the input. A character encoding can be specified by including a
        `charset` parameter. For example, 'text/csv;charset=utf-8'.
        """
        APPLICATION_JSON = 'application/json'
        TEXT_CSV = 'text/csv'
    class OnError(str, Enum):
        """
        expected behaviour on error.
        """
        STOP = 'stop'
        CONTINUE = 'continue'


class RecordsListEnums:
    """
    Enums for records_list parameters.
    """

    class Format(str, Enum):
        """
        What JSON format to use on output.
        """
        DICT = 'dict'
        LIST = 'list'
    class BinaryFormat(str, Enum):
        """
        Binary data presentation format. By default, the binary field value is encoded to
        base64 string. If _reference_ is chosen, every binary field is moved to the
        _references_ section with value set to an uri to the particular field within the
        record that can be GET in a separate request.
        """
        REFERENCE = 'reference'


class RecordsGetEnums:
    """
    Enums for records_get parameters.
    """

    class BinaryFormat(str, Enum):
        """
        Binary data presentation format. By default, the binary field value is encoded to
        base64 string. If _reference_ is chosen, every binary field is moved to the
        _references_ section with value set to an uri to the particular field within the
        record that can be GET in a separate request.
        """
        REFERENCE = 'reference'


class RecordsUpdateEnums:
    """
    Enums for records_update parameters.
    """

    class BinaryFormat(str, Enum):
        """
        Binary data presentation format. By default, the binary field value is encoded to
        base64 string. If _reference_ is chosen, every binary field is moved to the
        _references_ section with value set to an uri to the particular field within the
        record that can be GET in a separate request.
        """
        REFERENCE = 'reference'


class RecordsQueryEnums:
    """
    Enums for records_query parameters.
    """

    class DataSetType(str, Enum):
        """
        a (single) data set type.
        """
        MANUAL_LABELING = 'manual_labeling'
        PAYLOAD_LOGGING = 'payload_logging'
        FEEDBACK = 'feedback'
        BUSINESS_PAYLOAD = 'business_payload'
        EXPLANATIONS = 'explanations'
        EXPLANATIONS_WHATIF = 'explanations_whatif'
        TRAINING = 'training'
        PAYLOAD_LOGGING_ERROR = 'payload_logging_error'
        CUSTOM = 'custom'


class MeasurementsQueryEnums:
    """
    Enums for measurements_query parameters.
    """

    class TargetType(str, Enum):
        """
        Type of the monitoring target (subscription or business application).
        """
        SUBSCRIPTION = 'subscription'
        BUSINESS_APPLICATION = 'business_application'
        INSTANCE = 'instance'
        DATA_MART = 'data_mart'
    class Format(str, Enum):
        """
        Format of the returned data. `full` format compared to `compact` is additive and
        contains `sources` part.
        """
        COMPACT = 'compact'
        FULL = 'full'


class MetricsListEnums:
    """
    Enums for metrics_list parameters.
    """

    class Agg(str, Enum):
        """
        Comma delimited function list constructed from metric name and function, e.g.
        `agg=metric_name:count,:last` that defines aggregations.
        """
        LAST = 'last'
        FIRST = 'first'
        MAX = 'max'
        MIN = 'min'
        SUM = 'sum'
        AVG = 'avg'
        COUNT = 'count'
        STDDEV = 'stddev'
    class Interval(str, Enum):
        """
        Time unit in which metrics are grouped and aggregated, interval by interval.
        """
        MINUTE = 'minute'
        HOUR = 'hour'
        DAY = 'day'
        WEEK = 'week'
        MONTH = 'month'
        YEAR = 'year'


class ExplanationTasksListEnums:
    """
    Enums for explanation_tasks_list parameters.
    """

    class Status(str, Enum):
        """
        Status of the explanation task.
        """
        IN_PROGRESS = 'in_progress'
        FINISHED = 'finished'
        ERROR = 'error'


##############################################################################
# Models
##############################################################################


class AnalyticsEngine():
    """
    AnalyticsEngine.

    :attr str type: (optional) Type of analytics engine. e.g. spark.
    :attr str integrated_system_id: (optional) id of the Integrated System.
    :attr object credentials: (optional) Credentials to override credentials in
          integration_reference.
    :attr object parameters: (optional) Additional parameters (e.g.
          max_num_executors, min_num_executors, executor_cores, executor_memory,
          driver_cores, driver_memory).
    """

    def __init__(self,
                 *,
                 type: str = None,
                 integrated_system_id: str = None,
                 credentials: object = None,
                 parameters: object = None) -> None:
        """
        Initialize a AnalyticsEngine object.

        :param str type: (optional) Type of analytics engine. e.g. spark.
        :param str integrated_system_id: (optional) id of the Integrated System.
        :param object credentials: (optional) Credentials to override credentials
               in integration_reference.
        :param object parameters: (optional) Additional parameters (e.g.
               max_num_executors, min_num_executors, executor_cores, executor_memory,
               driver_cores, driver_memory).
        """
        self.type = type
        self.integrated_system_id = integrated_system_id
        self.credentials = credentials
        self.parameters = parameters

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AnalyticsEngine':
        """Initialize a AnalyticsEngine object from a json dictionary."""
        args = {}
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        if 'integrated_system_id' in _dict:
            args['integrated_system_id'] = _dict.get('integrated_system_id')
        if 'credentials' in _dict:
            args['credentials'] = _dict.get('credentials')
        if 'parameters' in _dict:
            args['parameters'] = _dict.get('parameters')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AnalyticsEngine object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'integrated_system_id') and self.integrated_system_id is not None:
            _dict['integrated_system_id'] = self.integrated_system_id
        if hasattr(self, 'credentials') and self.credentials is not None:
            _dict['credentials'] = self.credentials
        if hasattr(self, 'parameters') and self.parameters is not None:
            _dict['parameters'] = self.parameters
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AnalyticsEngine object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AnalyticsEngine') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AnalyticsEngine') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class ApplicabilitySelection():
    """
    ApplicabilitySelection.

    :attr List[str] input_data_type: (optional)
    :attr List[str] problem_type: (optional)
    :attr List[str] target_type: (optional)
    """

    def __init__(self,
                 *,
                 input_data_type: List[str] = None,
                 problem_type: List[str] = None,
                 target_type: List[str] = None) -> None:
        """
        Initialize a ApplicabilitySelection object.

        :param List[str] input_data_type: (optional)
        :param List[str] problem_type: (optional)
        :param List[str] target_type: (optional)
        """
        self.input_data_type = input_data_type
        self.problem_type = problem_type
        self.target_type = target_type

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ApplicabilitySelection':
        """Initialize a ApplicabilitySelection object from a json dictionary."""
        args = {}
        if 'input_data_type' in _dict:
            args['input_data_type'] = _dict.get('input_data_type')
        if 'problem_type' in _dict:
            args['problem_type'] = _dict.get('problem_type')
        if 'target_type' in _dict:
            args['target_type'] = _dict.get('target_type')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ApplicabilitySelection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'input_data_type') and self.input_data_type is not None:
            _dict['input_data_type'] = self.input_data_type
        if hasattr(self, 'problem_type') and self.problem_type is not None:
            _dict['problem_type'] = self.problem_type
        if hasattr(self, 'target_type') and self.target_type is not None:
            _dict['target_type'] = self.target_type
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ApplicabilitySelection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ApplicabilitySelection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ApplicabilitySelection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class InputDataTypeEnum(str, Enum):
        """
        input_data_type.
        """
        STRUCTURED = 'structured'
        UNSTRUCTURED_IMAGE = 'unstructured_image'
        UNSTRUCTURED_TEXT = 'unstructured_text'
        UNSTRUCTURED_VIDEO = 'unstructured_video'
        UNSTRUCTURED_AUDIO = 'unstructured_audio'


    class ProblemTypeEnum(str, Enum):
        """
        problem_type.
        """
        BINARY = 'binary'
        REGRESSION = 'regression'
        MULTICLASS = 'multiclass'


    class TargetTypeEnum(str, Enum):
        """
        Type of the target (e.g. subscription, business application, ...).
        """
        SUBSCRIPTION = 'subscription'
        BUSINESS_APPLICATION = 'business_application'
        INSTANCE = 'instance'
        DATA_MART = 'data_mart'


class Asset():
    """
    Asset.

    :attr str asset_id:
    :attr str url: (optional)
    :attr str name: (optional)
    :attr str asset_type:
    :attr str asset_rn: (optional) Asset Resource Name (used for integration with
          3rd party ML engines).
    :attr str created_at: (optional)
    :attr str problem_type: (optional)
    :attr str model_type: (optional)
    :attr str runtime_environment: (optional)
    :attr str input_data_type: (optional)
    """

    def __init__(self,
                 asset_id: str,
                 asset_type: str,
                 *,
                 url: str = None,
                 name: str = None,
                 asset_rn: str = None,
                 created_at: str = None,
                 problem_type: str = None,
                 model_type: str = None,
                 runtime_environment: str = None,
                 input_data_type: str = None) -> None:
        """
        Initialize a Asset object.

        :param str asset_id:
        :param str asset_type:
        :param str url: (optional)
        :param str name: (optional)
        :param str asset_rn: (optional) Asset Resource Name (used for integration
               with 3rd party ML engines).
        :param str created_at: (optional)
        :param str problem_type: (optional)
        :param str model_type: (optional)
        :param str runtime_environment: (optional)
        :param str input_data_type: (optional)
        """
        self.asset_id = asset_id
        self.url = url
        self.name = name
        self.asset_type = asset_type
        self.asset_rn = asset_rn
        self.created_at = created_at
        self.problem_type = problem_type
        self.model_type = model_type
        self.runtime_environment = runtime_environment
        self.input_data_type = input_data_type

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Asset':
        """Initialize a Asset object from a json dictionary."""
        args = {}
        if 'asset_id' in _dict:
            args['asset_id'] = _dict.get('asset_id')
        else:
            raise ValueError('Required property \'asset_id\' not present in Asset JSON')
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        if 'asset_type' in _dict:
            args['asset_type'] = _dict.get('asset_type')
        else:
            raise ValueError('Required property \'asset_type\' not present in Asset JSON')
        if 'asset_rn' in _dict:
            args['asset_rn'] = _dict.get('asset_rn')
        if 'created_at' in _dict:
            args['created_at'] = _dict.get('created_at')
        if 'problem_type' in _dict:
            args['problem_type'] = _dict.get('problem_type')
        if 'model_type' in _dict:
            args['model_type'] = _dict.get('model_type')
        if 'runtime_environment' in _dict:
            args['runtime_environment'] = _dict.get('runtime_environment')
        if 'input_data_type' in _dict:
            args['input_data_type'] = _dict.get('input_data_type')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Asset object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'asset_id') and self.asset_id is not None:
            _dict['asset_id'] = self.asset_id
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'asset_type') and self.asset_type is not None:
            _dict['asset_type'] = self.asset_type
        if hasattr(self, 'asset_rn') and self.asset_rn is not None:
            _dict['asset_rn'] = self.asset_rn
        if hasattr(self, 'created_at') and self.created_at is not None:
            _dict['created_at'] = self.created_at
        if hasattr(self, 'problem_type') and self.problem_type is not None:
            _dict['problem_type'] = self.problem_type
        if hasattr(self, 'model_type') and self.model_type is not None:
            _dict['model_type'] = self.model_type
        if hasattr(self, 'runtime_environment') and self.runtime_environment is not None:
            _dict['runtime_environment'] = self.runtime_environment
        if hasattr(self, 'input_data_type') and self.input_data_type is not None:
            _dict['input_data_type'] = self.input_data_type
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Asset object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Asset') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Asset') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class AssetTypeEnum(str, Enum):
        """
        asset_type.
        """
        MODEL = 'model'
        FUNCTION = 'function'


    class ProblemTypeEnum(str, Enum):
        """
        problem_type.
        """
        BINARY = 'binary'
        REGRESSION = 'regression'
        MULTICLASS = 'multiclass'


    class InputDataTypeEnum(str, Enum):
        """
        input_data_type.
        """
        STRUCTURED = 'structured'
        UNSTRUCTURED_IMAGE = 'unstructured_image'
        UNSTRUCTURED_TEXT = 'unstructured_text'
        UNSTRUCTURED_VIDEO = 'unstructured_video'
        UNSTRUCTURED_AUDIO = 'unstructured_audio'


class AssetDeployment():
    """
    AssetDeployment.

    :attr str deployment_id: (optional)
    :attr str deployment_rn: (optional) Deployment Resource Name (used for
          integration with 3rd party ML engines).
    :attr str url: (optional)
    :attr str name: (optional)
    :attr str description: (optional)
    :attr str deployment_type: (optional) Deployment type, e.g. online, batch.
    :attr str created_at: (optional)
    :attr ScoringEndpoint scoring_endpoint: (optional) Definition of scoring
          endpoint in custom_machine_learning.
    """

    def __init__(self,
                 *,
                 deployment_id: str = None,
                 deployment_rn: str = None,
                 url: str = None,
                 name: str = None,
                 description: str = None,
                 deployment_type: str = None,
                 created_at: str = None,
                 scoring_endpoint: 'ScoringEndpoint' = None) -> None:
        """
        Initialize a AssetDeployment object.

        :param str deployment_id: (optional)
        :param str deployment_rn: (optional) Deployment Resource Name (used for
               integration with 3rd party ML engines).
        :param str url: (optional)
        :param str name: (optional)
        :param str description: (optional)
        :param str deployment_type: (optional) Deployment type, e.g. online, batch.
        :param str created_at: (optional)
        :param ScoringEndpoint scoring_endpoint: (optional) Definition of scoring
               endpoint in custom_machine_learning.
        """
        self.deployment_id = deployment_id
        self.deployment_rn = deployment_rn
        self.url = url
        self.name = name
        self.description = description
        self.deployment_type = deployment_type
        self.created_at = created_at
        self.scoring_endpoint = scoring_endpoint

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AssetDeployment':
        """Initialize a AssetDeployment object from a json dictionary."""
        args = {}
        if 'deployment_id' in _dict:
            args['deployment_id'] = _dict.get('deployment_id')
        if 'deployment_rn' in _dict:
            args['deployment_rn'] = _dict.get('deployment_rn')
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'deployment_type' in _dict:
            args['deployment_type'] = _dict.get('deployment_type')
        if 'created_at' in _dict:
            args['created_at'] = _dict.get('created_at')
        if 'scoring_endpoint' in _dict:
            args['scoring_endpoint'] = ScoringEndpoint.from_dict(_dict.get('scoring_endpoint'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AssetDeployment object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'deployment_id') and self.deployment_id is not None:
            _dict['deployment_id'] = self.deployment_id
        if hasattr(self, 'deployment_rn') and self.deployment_rn is not None:
            _dict['deployment_rn'] = self.deployment_rn
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'deployment_type') and self.deployment_type is not None:
            _dict['deployment_type'] = self.deployment_type
        if hasattr(self, 'created_at') and self.created_at is not None:
            _dict['created_at'] = self.created_at
        if hasattr(self, 'scoring_endpoint') and self.scoring_endpoint is not None:
            _dict['scoring_endpoint'] = self.scoring_endpoint.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AssetDeployment object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AssetDeployment') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AssetDeployment') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class AssetDeploymentRequest():
    """
    AssetDeploymentRequest.

    :attr str deployment_id:
    :attr str deployment_rn: (optional) Deployment Resource Name (used for
          integration with 3rd party ML engines).
    :attr str url: (optional)
    :attr str name:
    :attr str description: (optional)
    :attr str deployment_type: Deployment type, e.g. online, batch.
    :attr str created_at: (optional)
    :attr ScoringEndpointRequest scoring_endpoint: (optional) Definition of scoring
          endpoint in custom_machine_learning.
    """

    def __init__(self,
                 deployment_id: str,
                 name: str,
                 deployment_type: str,
                 *,
                 deployment_rn: str = None,
                 url: str = None,
                 description: str = None,
                 created_at: str = None,
                 scoring_endpoint: 'ScoringEndpointRequest' = None) -> None:
        """
        Initialize a AssetDeploymentRequest object.

        :param str deployment_id:
        :param str name:
        :param str deployment_type: Deployment type, e.g. online, batch.
        :param str deployment_rn: (optional) Deployment Resource Name (used for
               integration with 3rd party ML engines).
        :param str url: (optional)
        :param str description: (optional)
        :param str created_at: (optional)
        :param ScoringEndpointRequest scoring_endpoint: (optional) Definition of
               scoring endpoint in custom_machine_learning.
        """
        self.deployment_id = deployment_id
        self.deployment_rn = deployment_rn
        self.url = url
        self.name = name
        self.description = description
        self.deployment_type = deployment_type
        self.created_at = created_at
        self.scoring_endpoint = scoring_endpoint

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AssetDeploymentRequest':
        """Initialize a AssetDeploymentRequest object from a json dictionary."""
        args = {}
        if 'deployment_id' in _dict:
            args['deployment_id'] = _dict.get('deployment_id')
        else:
            raise ValueError('Required property \'deployment_id\' not present in AssetDeploymentRequest JSON')
        if 'deployment_rn' in _dict:
            args['deployment_rn'] = _dict.get('deployment_rn')
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        else:
            raise ValueError('Required property \'name\' not present in AssetDeploymentRequest JSON')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'deployment_type' in _dict:
            args['deployment_type'] = _dict.get('deployment_type')
        else:
            raise ValueError('Required property \'deployment_type\' not present in AssetDeploymentRequest JSON')
        if 'created_at' in _dict:
            args['created_at'] = _dict.get('created_at')
        if 'scoring_endpoint' in _dict:
            args['scoring_endpoint'] = ScoringEndpointRequest.from_dict(_dict.get('scoring_endpoint'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AssetDeploymentRequest object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'deployment_id') and self.deployment_id is not None:
            _dict['deployment_id'] = self.deployment_id
        if hasattr(self, 'deployment_rn') and self.deployment_rn is not None:
            _dict['deployment_rn'] = self.deployment_rn
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'deployment_type') and self.deployment_type is not None:
            _dict['deployment_type'] = self.deployment_type
        if hasattr(self, 'created_at') and self.created_at is not None:
            _dict['created_at'] = self.created_at
        if hasattr(self, 'scoring_endpoint') and self.scoring_endpoint is not None:
            _dict['scoring_endpoint'] = self.scoring_endpoint.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AssetDeploymentRequest object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AssetDeploymentRequest') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AssetDeploymentRequest') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class AssetProperties():
    """
    Additional asset properties (subject of discovery if not provided when creating the
    subscription).

    :attr str problem_type: (optional)
    :attr str model_type: (optional)
    :attr str runtime_environment: (optional)
    :attr SecretCleaned training_data_reference: (optional)
    :attr SparkStruct training_data_schema: (optional)
    :attr SparkStruct input_data_schema: (optional)
    :attr SparkStruct output_data_schema: (optional)
    :attr str label_column: (optional)
    :attr str predicted_target_field: (optional) Field with this name will be given
          modeling_role `decoded-target`.
    :attr str prediction_field: (optional) Field with this name will be given
          modeling_role `prediction`.
    :attr str transaction_id_field: (optional) Field with this name will have
          `transaction_id_key` metadata set to true.
    :attr str input_data_type: (optional)
    :attr dict dashboard_configuration: (optional)
    :attr List[str] feature_fields: (optional) Fields to be given modeling_role
          feature.
    :attr List[str] categorical_fields: (optional) Fields to be given metadata
          `measure` of value `discrete`.
    :attr List[str] probability_fields: (optional) Fields to be given modeling_role
          `class_probability` (for columns of double data type) or `probability` (for
          column of array data type).
    """

    def __init__(self,
                 *,
                 problem_type: str = None,
                 model_type: str = None,
                 runtime_environment: str = None,
                 training_data_reference: 'SecretCleaned' = None,
                 training_data_schema: 'SparkStruct' = None,
                 input_data_schema: 'SparkStruct' = None,
                 output_data_schema: 'SparkStruct' = None,
                 label_column: str = None,
                 predicted_target_field: str = None,
                 prediction_field: str = None,
                 transaction_id_field: str = None,
                 input_data_type: str = None,
                 dashboard_configuration: dict = None,
                 feature_fields: List[str] = None,
                 categorical_fields: List[str] = None,
                 probability_fields: List[str] = None) -> None:
        """
        Initialize a AssetProperties object.

        :param str problem_type: (optional)
        :param str model_type: (optional)
        :param str runtime_environment: (optional)
        :param SecretCleaned training_data_reference: (optional)
        :param SparkStruct training_data_schema: (optional)
        :param SparkStruct input_data_schema: (optional)
        :param SparkStruct output_data_schema: (optional)
        :param str label_column: (optional)
        :param str predicted_target_field: (optional) Field with this name will be
               given modeling_role `decoded-target`.
        :param str prediction_field: (optional) Field with this name will be given
               modeling_role `prediction`.
        :param str transaction_id_field: (optional) Field with this name will have
               `transaction_id_key` metadata set to true.
        :param str input_data_type: (optional)
        :param dict dashboard_configuration: (optional)
        :param List[str] feature_fields: (optional) Fields to be given
               modeling_role feature.
        :param List[str] categorical_fields: (optional) Fields to be given metadata
               `measure` of value `discrete`.
        :param List[str] probability_fields: (optional) Fields to be given
               modeling_role `class_probability` (for columns of double data type) or
               `probability` (for column of array data type).
        """
        self.problem_type = problem_type
        self.model_type = model_type
        self.runtime_environment = runtime_environment
        self.training_data_reference = training_data_reference
        self.training_data_schema = training_data_schema
        self.input_data_schema = input_data_schema
        self.output_data_schema = output_data_schema
        self.label_column = label_column
        self.predicted_target_field = predicted_target_field
        self.prediction_field = prediction_field
        self.transaction_id_field = transaction_id_field
        self.input_data_type = input_data_type
        self.dashboard_configuration = dashboard_configuration
        self.feature_fields = feature_fields
        self.categorical_fields = categorical_fields
        self.probability_fields = probability_fields

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AssetProperties':
        """Initialize a AssetProperties object from a json dictionary."""
        args = {}
        if 'problem_type' in _dict:
            args['problem_type'] = _dict.get('problem_type')
        if 'model_type' in _dict:
            args['model_type'] = _dict.get('model_type')
        if 'runtime_environment' in _dict:
            args['runtime_environment'] = _dict.get('runtime_environment')
        if 'training_data_reference' in _dict:
            args['training_data_reference'] = SecretCleaned.from_dict(_dict.get('training_data_reference'))
        if 'training_data_schema' in _dict:
            args['training_data_schema'] = SparkStruct.from_dict(_dict.get('training_data_schema'))
        if 'input_data_schema' in _dict:
            args['input_data_schema'] = SparkStruct.from_dict(_dict.get('input_data_schema'))
        if 'output_data_schema' in _dict:
            args['output_data_schema'] = SparkStruct.from_dict(_dict.get('output_data_schema'))
        if 'label_column' in _dict:
            args['label_column'] = _dict.get('label_column')
        if 'predicted_target_field' in _dict:
            args['predicted_target_field'] = _dict.get('predicted_target_field')
        if 'prediction_field' in _dict:
            args['prediction_field'] = _dict.get('prediction_field')
        if 'transaction_id_field' in _dict:
            args['transaction_id_field'] = _dict.get('transaction_id_field')
        if 'input_data_type' in _dict:
            args['input_data_type'] = _dict.get('input_data_type')
        if 'dashboard_configuration' in _dict:
            args['dashboard_configuration'] = _dict.get('dashboard_configuration')
        if 'feature_fields' in _dict:
            args['feature_fields'] = _dict.get('feature_fields')
        if 'categorical_fields' in _dict:
            args['categorical_fields'] = _dict.get('categorical_fields')
        if 'probability_fields' in _dict:
            args['probability_fields'] = _dict.get('probability_fields')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AssetProperties object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'problem_type') and self.problem_type is not None:
            _dict['problem_type'] = self.problem_type
        if hasattr(self, 'model_type') and self.model_type is not None:
            _dict['model_type'] = self.model_type
        if hasattr(self, 'runtime_environment') and self.runtime_environment is not None:
            _dict['runtime_environment'] = self.runtime_environment
        if hasattr(self, 'training_data_reference') and self.training_data_reference is not None:
            _dict['training_data_reference'] = self.training_data_reference.to_dict()
        if hasattr(self, 'training_data_schema') and self.training_data_schema is not None:
            _dict['training_data_schema'] = self.training_data_schema.to_dict()
        if hasattr(self, 'input_data_schema') and self.input_data_schema is not None:
            _dict['input_data_schema'] = self.input_data_schema.to_dict()
        if hasattr(self, 'output_data_schema') and self.output_data_schema is not None:
            _dict['output_data_schema'] = self.output_data_schema.to_dict()
        if hasattr(self, 'label_column') and self.label_column is not None:
            _dict['label_column'] = self.label_column
        if hasattr(self, 'predicted_target_field') and self.predicted_target_field is not None:
            _dict['predicted_target_field'] = self.predicted_target_field
        if hasattr(self, 'prediction_field') and self.prediction_field is not None:
            _dict['prediction_field'] = self.prediction_field
        if hasattr(self, 'transaction_id_field') and self.transaction_id_field is not None:
            _dict['transaction_id_field'] = self.transaction_id_field
        if hasattr(self, 'input_data_type') and self.input_data_type is not None:
            _dict['input_data_type'] = self.input_data_type
        if hasattr(self, 'dashboard_configuration') and self.dashboard_configuration is not None:
            _dict['dashboard_configuration'] = self.dashboard_configuration
        if hasattr(self, 'feature_fields') and self.feature_fields is not None:
            _dict['feature_fields'] = self.feature_fields
        if hasattr(self, 'categorical_fields') and self.categorical_fields is not None:
            _dict['categorical_fields'] = self.categorical_fields
        if hasattr(self, 'probability_fields') and self.probability_fields is not None:
            _dict['probability_fields'] = self.probability_fields
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AssetProperties object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AssetProperties') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AssetProperties') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class ProblemTypeEnum(str, Enum):
        """
        problem_type.
        """
        BINARY = 'binary'
        REGRESSION = 'regression'
        MULTICLASS = 'multiclass'


    class InputDataTypeEnum(str, Enum):
        """
        input_data_type.
        """
        STRUCTURED = 'structured'
        UNSTRUCTURED_IMAGE = 'unstructured_image'
        UNSTRUCTURED_TEXT = 'unstructured_text'
        UNSTRUCTURED_VIDEO = 'unstructured_video'
        UNSTRUCTURED_AUDIO = 'unstructured_audio'


class AssetPropertiesRequest():
    """
    Additional asset properties (subject of discovery if not provided when creating the
    subscription).

    :attr TrainingDataReference training_data_reference: (optional)
    :attr SparkStruct training_data_schema: (optional)
    :attr SparkStruct input_data_schema: (optional)
    :attr SparkStruct output_data_schema: (optional)
    :attr str label_column: (optional)
    :attr List[str] labels: (optional)
    :attr str predicted_target_field: (optional) Field with this name will be given
          modeling_role `decoded-target`.
    :attr str prediction_field: (optional) Field with this name will be given
          modeling_role `prediction`.
    :attr str transaction_id_field: (optional) Field with this name will have
          `transaction_id_key` metadata set to true.
    :attr dict dashboard_configuration: (optional)
    :attr List[str] feature_fields: (optional) Fields to be given modeling_role
          feature.
    :attr List[str] categorical_fields: (optional) Fields to be given metadata
          `measure` of value `discrete`.
    :attr List[str] probability_fields: (optional) Fields to be given modeling_role
          `class_probability` (for columns of double data type) or `probability` (for
          column of array data type).
    """

    def __init__(self,
                 *,
                 training_data_reference: 'TrainingDataReference' = None,
                 training_data_schema: 'SparkStruct' = None,
                 input_data_schema: 'SparkStruct' = None,
                 output_data_schema: 'SparkStruct' = None,
                 label_column: str = None,
                 labels: List[str] = None,
                 predicted_target_field: str = None,
                 prediction_field: str = None,
                 transaction_id_field: str = None,
                 dashboard_configuration: dict = None,
                 feature_fields: List[str] = None,
                 categorical_fields: List[str] = None,
                 probability_fields: List[str] = None) -> None:
        """
        Initialize a AssetPropertiesRequest object.

        :param TrainingDataReference training_data_reference: (optional)
        :param SparkStruct training_data_schema: (optional)
        :param SparkStruct input_data_schema: (optional)
        :param SparkStruct output_data_schema: (optional)
        :param str label_column: (optional)
        :param List[str] labels: (optional)
        :param str predicted_target_field: (optional) Field with this name will be
               given modeling_role `decoded-target`.
        :param str prediction_field: (optional) Field with this name will be given
               modeling_role `prediction`.
        :param str transaction_id_field: (optional) Field with this name will have
               `transaction_id_key` metadata set to true.
        :param dict dashboard_configuration: (optional)
        :param List[str] feature_fields: (optional) Fields to be given
               modeling_role feature.
        :param List[str] categorical_fields: (optional) Fields to be given metadata
               `measure` of value `discrete`.
        :param List[str] probability_fields: (optional) Fields to be given
               modeling_role `class_probability` (for columns of double data type) or
               `probability` (for column of array data type).
        """
        self.training_data_reference = training_data_reference
        self.training_data_schema = training_data_schema
        self.input_data_schema = input_data_schema
        self.output_data_schema = output_data_schema
        self.label_column = label_column
        self.labels = labels
        self.predicted_target_field = predicted_target_field
        self.prediction_field = prediction_field
        self.transaction_id_field = transaction_id_field
        self.dashboard_configuration = dashboard_configuration
        self.feature_fields = feature_fields
        self.categorical_fields = categorical_fields
        self.probability_fields = probability_fields

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AssetPropertiesRequest':
        """Initialize a AssetPropertiesRequest object from a json dictionary."""
        args = {}
        if 'training_data_reference' in _dict:
            args['training_data_reference'] = TrainingDataReference.from_dict(_dict.get('training_data_reference'))
        if 'training_data_schema' in _dict:
            args['training_data_schema'] = SparkStruct.from_dict(_dict.get('training_data_schema'))
        if 'input_data_schema' in _dict:
            args['input_data_schema'] = SparkStruct.from_dict(_dict.get('input_data_schema'))
        if 'output_data_schema' in _dict:
            args['output_data_schema'] = SparkStruct.from_dict(_dict.get('output_data_schema'))
        if 'label_column' in _dict:
            args['label_column'] = _dict.get('label_column')
        if 'labels' in _dict:
            args['labels'] = _dict.get('labels')
        if 'predicted_target_field' in _dict:
            args['predicted_target_field'] = _dict.get('predicted_target_field')
        if 'prediction_field' in _dict:
            args['prediction_field'] = _dict.get('prediction_field')
        if 'transaction_id_field' in _dict:
            args['transaction_id_field'] = _dict.get('transaction_id_field')
        if 'dashboard_configuration' in _dict:
            args['dashboard_configuration'] = _dict.get('dashboard_configuration')
        if 'feature_fields' in _dict:
            args['feature_fields'] = _dict.get('feature_fields')
        if 'categorical_fields' in _dict:
            args['categorical_fields'] = _dict.get('categorical_fields')
        if 'probability_fields' in _dict:
            args['probability_fields'] = _dict.get('probability_fields')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AssetPropertiesRequest object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'training_data_reference') and self.training_data_reference is not None:
            _dict['training_data_reference'] = self.training_data_reference.to_dict()
        if hasattr(self, 'training_data_schema') and self.training_data_schema is not None:
            _dict['training_data_schema'] = self.training_data_schema.to_dict()
        if hasattr(self, 'input_data_schema') and self.input_data_schema is not None:
            _dict['input_data_schema'] = self.input_data_schema.to_dict()
        if hasattr(self, 'output_data_schema') and self.output_data_schema is not None:
            _dict['output_data_schema'] = self.output_data_schema.to_dict()
        if hasattr(self, 'label_column') and self.label_column is not None:
            _dict['label_column'] = self.label_column
        if hasattr(self, 'labels') and self.labels is not None:
            _dict['labels'] = self.labels
        if hasattr(self, 'predicted_target_field') and self.predicted_target_field is not None:
            _dict['predicted_target_field'] = self.predicted_target_field
        if hasattr(self, 'prediction_field') and self.prediction_field is not None:
            _dict['prediction_field'] = self.prediction_field
        if hasattr(self, 'transaction_id_field') and self.transaction_id_field is not None:
            _dict['transaction_id_field'] = self.transaction_id_field
        if hasattr(self, 'dashboard_configuration') and self.dashboard_configuration is not None:
            _dict['dashboard_configuration'] = self.dashboard_configuration
        if hasattr(self, 'feature_fields') and self.feature_fields is not None:
            _dict['feature_fields'] = self.feature_fields
        if hasattr(self, 'categorical_fields') and self.categorical_fields is not None:
            _dict['categorical_fields'] = self.categorical_fields
        if hasattr(self, 'probability_fields') and self.probability_fields is not None:
            _dict['probability_fields'] = self.probability_fields
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AssetPropertiesRequest object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AssetPropertiesRequest') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AssetPropertiesRequest') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class AzureWorkspaceCredentials():
    """
    AzureWorkspaceCredentials.

    :attr str workspace_id:
    :attr str token:
    """

    def __init__(self,
                 workspace_id: str,
                 token: str) -> None:
        """
        Initialize a AzureWorkspaceCredentials object.

        :param str workspace_id:
        :param str token:
        """
        self.workspace_id = workspace_id
        self.token = token

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AzureWorkspaceCredentials':
        """Initialize a AzureWorkspaceCredentials object from a json dictionary."""
        args = {}
        if 'workspace_id' in _dict:
            args['workspace_id'] = _dict.get('workspace_id')
        else:
            raise ValueError('Required property \'workspace_id\' not present in AzureWorkspaceCredentials JSON')
        if 'token' in _dict:
            args['token'] = _dict.get('token')
        else:
            raise ValueError('Required property \'token\' not present in AzureWorkspaceCredentials JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AzureWorkspaceCredentials object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'workspace_id') and self.workspace_id is not None:
            _dict['workspace_id'] = self.workspace_id
        if hasattr(self, 'token') and self.token is not None:
            _dict['token'] = self.token
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AzureWorkspaceCredentials object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AzureWorkspaceCredentials') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AzureWorkspaceCredentials') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class CollectionUrlModel():
    """
    CollectionUrlModel.

    :attr str url: URI of a resource.
    """

    def __init__(self,
                 url: str) -> None:
        """
        Initialize a CollectionUrlModel object.

        :param str url: URI of a resource.
        """
        self.url = url

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'CollectionUrlModel':
        """Initialize a CollectionUrlModel object from a json dictionary."""
        args = {}
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        else:
            raise ValueError('Required property \'url\' not present in CollectionUrlModel JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a CollectionUrlModel object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this CollectionUrlModel object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'CollectionUrlModel') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'CollectionUrlModel') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataDistributionResponse():
    """
    Data distribution details response.

    :attr Metadata metadata:
    :attr DataDistributionResponseEntity entity: The computed data distribution
          against specified data set.
    """

    def __init__(self,
                 metadata: 'Metadata',
                 entity: 'DataDistributionResponseEntity') -> None:
        """
        Initialize a DataDistributionResponse object.

        :param Metadata metadata:
        :param DataDistributionResponseEntity entity: The computed data
               distribution against specified data set.
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataDistributionResponse':
        """Initialize a DataDistributionResponse object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in DataDistributionResponse JSON')
        if 'entity' in _dict:
            args['entity'] = DataDistributionResponseEntity.from_dict(_dict.get('entity'))
        else:
            raise ValueError('Required property \'entity\' not present in DataDistributionResponse JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataDistributionResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataDistributionResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataDistributionResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataDistributionResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataDistributionResponseEntity():
    """
    The computed data distribution against specified data set.

    :attr str start: start datetime in ISO format.
    :attr str end: end datetime in ISO format.
    :attr str dataset: type of a data set.
    :attr float limit: (optional) limit for number of rows, by default it is 50,000
          (max possible limit is 50,000).
    :attr List[str] group: names of columns to be grouped.
    :attr str filter: (optional) Filters defined by user in format:
          {field_name}:{op}:{value}. Partly compatible with filters in "filter" parameter
          of GET /v2/data_sets/{data_set_id}/records.
          Possible filter operators:
          * eq - equals (numeric, string)
          * gt - greater than (numeric)
          * gte - greater than or equal (numeric)
          * lt - lower than (numeric)
          * lte - lower than or equal (numeric)
          * in - value in a set (numeric, string)
          * field:null (a no-argument filter) - value is null (any nullable)
          * field:exists (a no-argument filter) - value is not null (any column).
    :attr List[str] agg: (optional) Definition of aggregations, by default 'count'.
          Aggregations can be one of:
          * count
          * <column_name>:sum
          * <column_name>:min
          * <column_name>:max
          * <column_name>:avg
          * <column_name>:stddev.
    :attr float max_bins: (optional) max number of bins which will be generated for
          data.
    :attr MonitoringRunStatus status: (optional) The status information for the
          monitoring run.
    :attr float processed_records: (optional) number of processed records.
    :attr bool limited_data: (optional) was the limit used on data.
    :attr DataDistributionResponseEntityDistribution distribution: (optional)
    """

    def __init__(self,
                 start: str,
                 end: str,
                 dataset: str,
                 group: List[str],
                 *,
                 limit: float = None,
                 filter: str = None,
                 agg: List[str] = None,
                 max_bins: float = None,
                 status: 'MonitoringRunStatus' = None,
                 processed_records: float = None,
                 limited_data: bool = None,
                 distribution: 'DataDistributionResponseEntityDistribution' = None) -> None:
        """
        Initialize a DataDistributionResponseEntity object.

        :param str start: start datetime in ISO format.
        :param str end: end datetime in ISO format.
        :param str dataset: type of a data set.
        :param List[str] group: names of columns to be grouped.
        :param float limit: (optional) limit for number of rows, by default it is
               50,000 (max possible limit is 50,000).
        :param str filter: (optional) Filters defined by user in format:
               {field_name}:{op}:{value}. Partly compatible with filters in "filter"
               parameter of GET /v2/data_sets/{data_set_id}/records.
               Possible filter operators:
               * eq - equals (numeric, string)
               * gt - greater than (numeric)
               * gte - greater than or equal (numeric)
               * lt - lower than (numeric)
               * lte - lower than or equal (numeric)
               * in - value in a set (numeric, string)
               * field:null (a no-argument filter) - value is null (any nullable)
               * field:exists (a no-argument filter) - value is not null (any column).
        :param List[str] agg: (optional) Definition of aggregations, by default
               'count'.
               Aggregations can be one of:
               * count
               * <column_name>:sum
               * <column_name>:min
               * <column_name>:max
               * <column_name>:avg
               * <column_name>:stddev.
        :param float max_bins: (optional) max number of bins which will be
               generated for data.
        :param MonitoringRunStatus status: (optional) The status information for
               the monitoring run.
        :param float processed_records: (optional) number of processed records.
        :param bool limited_data: (optional) was the limit used on data.
        :param DataDistributionResponseEntityDistribution distribution: (optional)
        """
        self.start = start
        self.end = end
        self.dataset = dataset
        self.limit = limit
        self.group = group
        self.filter = filter
        self.agg = agg
        self.max_bins = max_bins
        self.status = status
        self.processed_records = processed_records
        self.limited_data = limited_data
        self.distribution = distribution

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataDistributionResponseEntity':
        """Initialize a DataDistributionResponseEntity object from a json dictionary."""
        args = {}
        if 'start' in _dict:
            args['start'] = _dict.get('start')
        else:
            raise ValueError('Required property \'start\' not present in DataDistributionResponseEntity JSON')
        if 'end' in _dict:
            args['end'] = _dict.get('end')
        else:
            raise ValueError('Required property \'end\' not present in DataDistributionResponseEntity JSON')
        if 'dataset' in _dict:
            args['dataset'] = _dict.get('dataset')
        else:
            raise ValueError('Required property \'dataset\' not present in DataDistributionResponseEntity JSON')
        if 'limit' in _dict:
            args['limit'] = _dict.get('limit')
        if 'group' in _dict:
            args['group'] = _dict.get('group')
        else:
            raise ValueError('Required property \'group\' not present in DataDistributionResponseEntity JSON')
        if 'filter' in _dict:
            args['filter'] = _dict.get('filter')
        if 'agg' in _dict:
            args['agg'] = _dict.get('agg')
        if 'max_bins' in _dict:
            args['max_bins'] = _dict.get('max_bins')
        if 'status' in _dict:
            args['status'] = MonitoringRunStatus.from_dict(_dict.get('status'))
        if 'processed_records' in _dict:
            args['processed_records'] = _dict.get('processed_records')
        if 'limited_data' in _dict:
            args['limited_data'] = _dict.get('limited_data')
        if 'distribution' in _dict:
            args['distribution'] = DataDistributionResponseEntityDistribution.from_dict(_dict.get('distribution'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataDistributionResponseEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'start') and self.start is not None:
            _dict['start'] = self.start
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = self.end
        if hasattr(self, 'dataset') and self.dataset is not None:
            _dict['dataset'] = self.dataset
        if hasattr(self, 'limit') and self.limit is not None:
            _dict['limit'] = self.limit
        if hasattr(self, 'group') and self.group is not None:
            _dict['group'] = self.group
        if hasattr(self, 'filter') and self.filter is not None:
            _dict['filter'] = self.filter
        if hasattr(self, 'agg') and self.agg is not None:
            _dict['agg'] = self.agg
        if hasattr(self, 'max_bins') and self.max_bins is not None:
            _dict['max_bins'] = self.max_bins
        if hasattr(self, 'status') and self.status is not None:
            _dict['status'] = self.status.to_dict()
        if hasattr(self, 'processed_records') and self.processed_records is not None:
            _dict['processed_records'] = self.processed_records
        if hasattr(self, 'limited_data') and self.limited_data is not None:
            _dict['limited_data'] = self.limited_data
        if hasattr(self, 'distribution') and self.distribution is not None:
            _dict['distribution'] = self.distribution.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataDistributionResponseEntity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataDistributionResponseEntity') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataDistributionResponseEntity') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class DatasetEnum(str, Enum):
        """
        type of a data set.
        """
        MANUAL_LABELING = 'manual_labeling'
        PAYLOAD_LOGGING = 'payload_logging'
        FEEDBACK = 'feedback'
        BUSINESS_PAYLOAD = 'business_payload'
        EXPLANATIONS = 'explanations'
        EXPLANATIONS_WHATIF = 'explanations_whatif'
        TRAINING = 'training'
        PAYLOAD_LOGGING_ERROR = 'payload_logging_error'
        CUSTOM = 'custom'


class DataDistributionResponseEntityDistribution():
    """
    DataDistributionResponseEntityDistribution.

    :attr List[str] fields: names of the data distribution fields.
    :attr List[object] values: data distribution rows.
    """

    def __init__(self,
                 fields: List[str],
                 values: List[object]) -> None:
        """
        Initialize a DataDistributionResponseEntityDistribution object.

        :param List[str] fields: names of the data distribution fields.
        :param List[object] values: data distribution rows.
        """
        self.fields = fields
        self.values = values

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataDistributionResponseEntityDistribution':
        """Initialize a DataDistributionResponseEntityDistribution object from a json dictionary."""
        args = {}
        if 'fields' in _dict:
            args['fields'] = _dict.get('fields')
        else:
            raise ValueError('Required property \'fields\' not present in DataDistributionResponseEntityDistribution JSON')
        if 'values' in _dict:
            args['values'] = _dict.get('values')
        else:
            raise ValueError('Required property \'values\' not present in DataDistributionResponseEntityDistribution JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataDistributionResponseEntityDistribution object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'fields') and self.fields is not None:
            _dict['fields'] = self.fields
        if hasattr(self, 'values') and self.values is not None:
            _dict['values'] = self.values
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataDistributionResponseEntityDistribution object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataDistributionResponseEntityDistribution') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataDistributionResponseEntityDistribution') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataMartDatabaseResponse():
    """
    DataMartDatabaseResponse.

    :attr Metadata metadata:
    :attr DataMartDatabaseResponseEntity entity:
    """

    def __init__(self,
                 metadata: 'Metadata',
                 entity: 'DataMartDatabaseResponseEntity') -> None:
        """
        Initialize a DataMartDatabaseResponse object.

        :param Metadata metadata:
        :param DataMartDatabaseResponseEntity entity:
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataMartDatabaseResponse':
        """Initialize a DataMartDatabaseResponse object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in DataMartDatabaseResponse JSON')
        if 'entity' in _dict:
            args['entity'] = DataMartDatabaseResponseEntity.from_dict(_dict.get('entity'))
        else:
            raise ValueError('Required property \'entity\' not present in DataMartDatabaseResponse JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataMartDatabaseResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataMartDatabaseResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataMartDatabaseResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataMartDatabaseResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataMartDatabaseResponseCollection():
    """
    DataMartDatabaseResponseCollection.

    :attr List[DataMartDatabaseResponse] data_marts:
    """

    def __init__(self,
                 data_marts: List['DataMartDatabaseResponse']) -> None:
        """
        Initialize a DataMartDatabaseResponseCollection object.

        :param List[DataMartDatabaseResponse] data_marts:
        """
        self.data_marts = data_marts

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataMartDatabaseResponseCollection':
        """Initialize a DataMartDatabaseResponseCollection object from a json dictionary."""
        args = {}
        if 'data_marts' in _dict:
            args['data_marts'] = [DataMartDatabaseResponse.from_dict(x) for x in _dict.get('data_marts')]
        else:
            raise ValueError('Required property \'data_marts\' not present in DataMartDatabaseResponseCollection JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataMartDatabaseResponseCollection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'data_marts') and self.data_marts is not None:
            _dict['data_marts'] = [x.to_dict() for x in self.data_marts]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataMartDatabaseResponseCollection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataMartDatabaseResponseCollection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataMartDatabaseResponseCollection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataMartDatabaseResponseEntity():
    """
    DataMartDatabaseResponseEntity.

    :attr str name: (optional)
    :attr str description: (optional)
    :attr str service_instance_crn: (optional)
    :attr bool internal_database: (optional) If `true` the internal database managed
          by AI OpenScale is provided for the user.
    :attr DatabaseConfiguration database_configuration: (optional) Database
          configuration ignored if internal database is requested (`internal_database` is
          `true`).
    :attr str database_discovery: (optional) Used by UI to check if database
          discovery was automatic or manual.
    :attr Status status: (optional)
    """

    def __init__(self,
                 *,
                 name: str = None,
                 description: str = None,
                 service_instance_crn: str = None,
                 internal_database: bool = None,
                 database_configuration: 'DatabaseConfiguration' = None,
                 database_discovery: str = None,
                 status: 'Status' = None) -> None:
        """
        Initialize a DataMartDatabaseResponseEntity object.

        :param str name: (optional)
        :param str description: (optional)
        :param str service_instance_crn: (optional)
        :param bool internal_database: (optional) If `true` the internal database
               managed by AI OpenScale is provided for the user.
        :param DatabaseConfiguration database_configuration: (optional) Database
               configuration ignored if internal database is requested
               (`internal_database` is `true`).
        :param str database_discovery: (optional) Used by UI to check if database
               discovery was automatic or manual.
        :param Status status: (optional)
        """
        self.name = name
        self.description = description
        self.service_instance_crn = service_instance_crn
        self.internal_database = internal_database
        self.database_configuration = database_configuration
        self.database_discovery = database_discovery
        self.status = status

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataMartDatabaseResponseEntity':
        """Initialize a DataMartDatabaseResponseEntity object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'service_instance_crn' in _dict:
            args['service_instance_crn'] = _dict.get('service_instance_crn')
        if 'internal_database' in _dict:
            args['internal_database'] = _dict.get('internal_database')
        if 'database_configuration' in _dict:
            args['database_configuration'] = DatabaseConfiguration.from_dict(_dict.get('database_configuration'))
        if 'database_discovery' in _dict:
            args['database_discovery'] = _dict.get('database_discovery')
        if 'status' in _dict:
            args['status'] = Status.from_dict(_dict.get('status'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataMartDatabaseResponseEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'service_instance_crn') and self.service_instance_crn is not None:
            _dict['service_instance_crn'] = self.service_instance_crn
        if hasattr(self, 'internal_database') and self.internal_database is not None:
            _dict['internal_database'] = self.internal_database
        if hasattr(self, 'database_configuration') and self.database_configuration is not None:
            _dict['database_configuration'] = self.database_configuration.to_dict()
        if hasattr(self, 'database_discovery') and self.database_discovery is not None:
            _dict['database_discovery'] = self.database_discovery
        if hasattr(self, 'status') and self.status is not None:
            _dict['status'] = self.status.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataMartDatabaseResponseEntity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataMartDatabaseResponseEntity') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataMartDatabaseResponseEntity') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class DatabaseDiscoveryEnum(str, Enum):
        """
        Used by UI to check if database discovery was automatic or manual.
        """
        AUTOMATIC = 'automatic'
        MANUAL = 'manual'


class DataMartGetMonitorInstanceMetrics():
    """
    DataMartGetMonitorInstanceMetrics.

    :attr datetime start: (optional) Floored to full interval.
    :attr datetime end: (optional) Ceiled to full interval.
    :attr str interval: (optional)
    :attr str monitor_definition_id: (optional)
    :attr List[DataMartGetMonitorInstanceMetricsGroupsItem] groups: (optional)
    """

    def __init__(self,
                 *,
                 start: datetime = None,
                 end: datetime = None,
                 interval: str = None,
                 monitor_definition_id: str = None,
                 groups: List['DataMartGetMonitorInstanceMetricsGroupsItem'] = None) -> None:
        """
        Initialize a DataMartGetMonitorInstanceMetrics object.

        :param datetime start: (optional) Floored to full interval.
        :param datetime end: (optional) Ceiled to full interval.
        :param str interval: (optional)
        :param str monitor_definition_id: (optional)
        :param List[DataMartGetMonitorInstanceMetricsGroupsItem] groups: (optional)
        """
        self.start = start
        self.end = end
        self.interval = interval
        self.monitor_definition_id = monitor_definition_id
        self.groups = groups

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataMartGetMonitorInstanceMetrics':
        """Initialize a DataMartGetMonitorInstanceMetrics object from a json dictionary."""
        args = {}
        if 'start' in _dict:
            args['start'] = string_to_datetime(_dict.get('start'))
        if 'end' in _dict:
            args['end'] = string_to_datetime(_dict.get('end'))
        if 'interval' in _dict:
            args['interval'] = _dict.get('interval')
        if 'monitor_definition_id' in _dict:
            args['monitor_definition_id'] = _dict.get('monitor_definition_id')
        if 'groups' in _dict:
            args['groups'] = [DataMartGetMonitorInstanceMetricsGroupsItem.from_dict(x) for x in _dict.get('groups')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataMartGetMonitorInstanceMetrics object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'start') and self.start is not None:
            _dict['start'] = datetime_to_string(self.start)
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = datetime_to_string(self.end)
        if hasattr(self, 'interval') and self.interval is not None:
            _dict['interval'] = self.interval
        if hasattr(self, 'monitor_definition_id') and self.monitor_definition_id is not None:
            _dict['monitor_definition_id'] = self.monitor_definition_id
        if hasattr(self, 'groups') and self.groups is not None:
            _dict['groups'] = [x.to_dict() for x in self.groups]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataMartGetMonitorInstanceMetrics object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataMartGetMonitorInstanceMetrics') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataMartGetMonitorInstanceMetrics') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataMartGetMonitorInstanceMetricsGroupsItem():
    """
    DataMartGetMonitorInstanceMetricsGroupsItem.

    :attr List[DataMartGetMonitorInstanceMetricsGroupsItemTagsItem] tags: (optional)
    :attr List[DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem] metrics:
          (optional)
    """

    def __init__(self,
                 *,
                 tags: List['DataMartGetMonitorInstanceMetricsGroupsItemTagsItem'] = None,
                 metrics: List['DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem'] = None) -> None:
        """
        Initialize a DataMartGetMonitorInstanceMetricsGroupsItem object.

        :param List[DataMartGetMonitorInstanceMetricsGroupsItemTagsItem] tags:
               (optional)
        :param List[DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem]
               metrics: (optional)
        """
        self.tags = tags
        self.metrics = metrics

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataMartGetMonitorInstanceMetricsGroupsItem':
        """Initialize a DataMartGetMonitorInstanceMetricsGroupsItem object from a json dictionary."""
        args = {}
        if 'tags' in _dict:
            args['tags'] = [DataMartGetMonitorInstanceMetricsGroupsItemTagsItem.from_dict(x) for x in _dict.get('tags')]
        if 'metrics' in _dict:
            args['metrics'] = [DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem.from_dict(x) for x in _dict.get('metrics')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataMartGetMonitorInstanceMetricsGroupsItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'tags') and self.tags is not None:
            _dict['tags'] = [x.to_dict() for x in self.tags]
        if hasattr(self, 'metrics') and self.metrics is not None:
            _dict['metrics'] = [x.to_dict() for x in self.metrics]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataMartGetMonitorInstanceMetricsGroupsItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataMartGetMonitorInstanceMetricsGroupsItem') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataMartGetMonitorInstanceMetricsGroupsItem') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem():
    """
    DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem.

    :attr str id:
    :attr float lower_limit: (optional)
    :attr float upper_limit: (optional)
    :attr DataMartGetMonitorInstanceMetricsGroupsItemMetricsItemLast last:
          (optional)
    """

    def __init__(self,
                 id: str,
                 *,
                 lower_limit: float = None,
                 upper_limit: float = None,
                 last: 'DataMartGetMonitorInstanceMetricsGroupsItemMetricsItemLast' = None) -> None:
        """
        Initialize a DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem object.

        :param str id:
        :param float lower_limit: (optional)
        :param float upper_limit: (optional)
        :param DataMartGetMonitorInstanceMetricsGroupsItemMetricsItemLast last:
               (optional)
        """
        self.id = id
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit
        self.last = last

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem':
        """Initialize a DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        else:
            raise ValueError('Required property \'id\' not present in DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem JSON')
        if 'lower_limit' in _dict:
            args['lower_limit'] = _dict.get('lower_limit')
        if 'upper_limit' in _dict:
            args['upper_limit'] = _dict.get('upper_limit')
        if 'last' in _dict:
            args['last'] = DataMartGetMonitorInstanceMetricsGroupsItemMetricsItemLast.from_dict(_dict.get('last'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'lower_limit') and self.lower_limit is not None:
            _dict['lower_limit'] = self.lower_limit
        if hasattr(self, 'upper_limit') and self.upper_limit is not None:
            _dict['upper_limit'] = self.upper_limit
        if hasattr(self, 'last') and self.last is not None:
            _dict['last'] = self.last.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataMartGetMonitorInstanceMetricsGroupsItemMetricsItem') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataMartGetMonitorInstanceMetricsGroupsItemMetricsItemLast():
    """
    DataMartGetMonitorInstanceMetricsGroupsItemMetricsItemLast.

    :attr List[float] value: (optional)
    :attr List[str] measurement_id: (optional)
    """

    def __init__(self,
                 *,
                 value: List[float] = None,
                 measurement_id: List[str] = None) -> None:
        """
        Initialize a DataMartGetMonitorInstanceMetricsGroupsItemMetricsItemLast object.

        :param List[float] value: (optional)
        :param List[str] measurement_id: (optional)
        """
        self.value = value
        self.measurement_id = measurement_id

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataMartGetMonitorInstanceMetricsGroupsItemMetricsItemLast':
        """Initialize a DataMartGetMonitorInstanceMetricsGroupsItemMetricsItemLast object from a json dictionary."""
        args = {}
        if 'value' in _dict:
            args['value'] = _dict.get('value')
        if 'measurement_id' in _dict:
            args['measurement_id'] = _dict.get('measurement_id')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataMartGetMonitorInstanceMetricsGroupsItemMetricsItemLast object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        if hasattr(self, 'measurement_id') and self.measurement_id is not None:
            _dict['measurement_id'] = self.measurement_id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataMartGetMonitorInstanceMetricsGroupsItemMetricsItemLast object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataMartGetMonitorInstanceMetricsGroupsItemMetricsItemLast') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataMartGetMonitorInstanceMetricsGroupsItemMetricsItemLast') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataMartGetMonitorInstanceMetricsGroupsItemTagsItem():
    """
    DataMartGetMonitorInstanceMetricsGroupsItemTagsItem.

    :attr str id:
    :attr str value:
    """

    def __init__(self,
                 id: str,
                 value: str) -> None:
        """
        Initialize a DataMartGetMonitorInstanceMetricsGroupsItemTagsItem object.

        :param str id:
        :param str value:
        """
        self.id = id
        self.value = value

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataMartGetMonitorInstanceMetricsGroupsItemTagsItem':
        """Initialize a DataMartGetMonitorInstanceMetricsGroupsItemTagsItem object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        else:
            raise ValueError('Required property \'id\' not present in DataMartGetMonitorInstanceMetricsGroupsItemTagsItem JSON')
        if 'value' in _dict:
            args['value'] = _dict.get('value')
        else:
            raise ValueError('Required property \'value\' not present in DataMartGetMonitorInstanceMetricsGroupsItemTagsItem JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataMartGetMonitorInstanceMetricsGroupsItemTagsItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataMartGetMonitorInstanceMetricsGroupsItemTagsItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataMartGetMonitorInstanceMetricsGroupsItemTagsItem') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataMartGetMonitorInstanceMetricsGroupsItemTagsItem') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataRecord():
    """
    DataRecord.

    :attr object values: Fields and values of the entity matches JSON object's
          fields and values.
    :attr dict annotations: (optional) Any JSON object representing annotations.
    """

    def __init__(self,
                 values: object,
                 *,
                 annotations: dict = None) -> None:
        """
        Initialize a DataRecord object.

        :param object values: Fields and values of the entity matches JSON object's
               fields and values.
        :param dict annotations: (optional) Any JSON object representing
               annotations.
        """
        self.values = values
        self.annotations = annotations

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataRecord':
        """Initialize a DataRecord object from a json dictionary."""
        args = {}
        if 'values' in _dict:
            args['values'] = _dict.get('values')
        else:
            raise ValueError('Required property \'values\' not present in DataRecord JSON')
        if 'annotations' in _dict:
            args['annotations'] = _dict.get('annotations')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataRecord object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'values') and self.values is not None:
            _dict['values'] = self.values
        if hasattr(self, 'annotations') and self.annotations is not None:
            _dict['annotations'] = self.annotations
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataRecord object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataRecord') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataRecord') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataRecordResponse():
    """
    DataRecordResponse.

    :attr Metadata metadata:
    :attr DataRecord entity:
    """

    def __init__(self,
                 metadata: 'Metadata',
                 entity: 'DataRecord') -> None:
        """
        Initialize a DataRecordResponse object.

        :param Metadata metadata:
        :param DataRecord entity:
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataRecordResponse':
        """Initialize a DataRecordResponse object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in DataRecordResponse JSON')
        if 'entity' in _dict:
            args['entity'] = DataRecord.from_dict(_dict.get('entity'))
        else:
            raise ValueError('Required property \'entity\' not present in DataRecordResponse JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataRecordResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataRecordResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataRecordResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataRecordResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataRecordResponseList():
    """
    DataRecordResponseList.

    :attr List[str] fields: Fields' names are listed in order in 'fields'.
    :attr List[List[object]] values: Rows organized per fields as described in
          'fields'.
    :attr List[dict] annotations: (optional) List of annotations objects.
    """

    def __init__(self,
                 fields: List[str],
                 values: List[List[object]],
                 *,
                 annotations: List[dict] = None) -> None:
        """
        Initialize a DataRecordResponseList object.

        :param List[str] fields: Fields' names are listed in order in 'fields'.
        :param List[List[object]] values: Rows organized per fields as described in
               'fields'.
        :param List[dict] annotations: (optional) List of annotations objects.
        """
        self.fields = fields
        self.values = values
        self.annotations = annotations

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataRecordResponseList':
        """Initialize a DataRecordResponseList object from a json dictionary."""
        args = {}
        if 'fields' in _dict:
            args['fields'] = _dict.get('fields')
        else:
            raise ValueError('Required property \'fields\' not present in DataRecordResponseList JSON')
        if 'values' in _dict:
            args['values'] = _dict.get('values')
        else:
            raise ValueError('Required property \'values\' not present in DataRecordResponseList JSON')
        if 'annotations' in _dict:
            args['annotations'] = _dict.get('annotations')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataRecordResponseList object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'fields') and self.fields is not None:
            _dict['fields'] = self.fields
        if hasattr(self, 'values') and self.values is not None:
            _dict['values'] = self.values
        if hasattr(self, 'annotations') and self.annotations is not None:
            _dict['annotations'] = self.annotations
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataRecordResponseList object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataRecordResponseList') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataRecordResponseList') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataSetObject():
    """
    DataSetObject.

    :attr str data_mart_id:
    :attr str name:
    :attr str description: (optional)
    :attr str type: type of a data set.
    :attr Target target:
    :attr str schema_update_mode: (optional)
    :attr SparkStruct data_schema:
    :attr LocationTableName location: (optional)
    :attr str managed_by: (optional)
    :attr Status status:
    """

    def __init__(self,
                 data_mart_id: str,
                 name: str,
                 type: str,
                 target: 'Target',
                 data_schema: 'SparkStruct',
                 status: 'Status',
                 *,
                 description: str = None,
                 schema_update_mode: str = None,
                 location: 'LocationTableName' = None,
                 managed_by: str = None) -> None:
        """
        Initialize a DataSetObject object.

        :param str data_mart_id:
        :param str name:
        :param str type: type of a data set.
        :param Target target:
        :param SparkStruct data_schema:
        :param Status status:
        :param str description: (optional)
        :param str schema_update_mode: (optional)
        :param LocationTableName location: (optional)
        :param str managed_by: (optional)
        """
        self.data_mart_id = data_mart_id
        self.name = name
        self.description = description
        self.type = type
        self.target = target
        self.schema_update_mode = schema_update_mode
        self.data_schema = data_schema
        self.location = location
        self.managed_by = managed_by
        self.status = status

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataSetObject':
        """Initialize a DataSetObject object from a json dictionary."""
        args = {}
        if 'data_mart_id' in _dict:
            args['data_mart_id'] = _dict.get('data_mart_id')
        else:
            raise ValueError('Required property \'data_mart_id\' not present in DataSetObject JSON')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        else:
            raise ValueError('Required property \'name\' not present in DataSetObject JSON')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in DataSetObject JSON')
        if 'target' in _dict:
            args['target'] = Target.from_dict(_dict.get('target'))
        else:
            raise ValueError('Required property \'target\' not present in DataSetObject JSON')
        if 'schema_update_mode' in _dict:
            args['schema_update_mode'] = _dict.get('schema_update_mode')
        if 'data_schema' in _dict:
            args['data_schema'] = SparkStruct.from_dict(_dict.get('data_schema'))
        else:
            raise ValueError('Required property \'data_schema\' not present in DataSetObject JSON')
        if 'location' in _dict:
            args['location'] = LocationTableName.from_dict(_dict.get('location'))
        if 'managed_by' in _dict:
            args['managed_by'] = _dict.get('managed_by')
        if 'status' in _dict:
            args['status'] = Status.from_dict(_dict.get('status'))
        else:
            raise ValueError('Required property \'status\' not present in DataSetObject JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataSetObject object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'data_mart_id') and self.data_mart_id is not None:
            _dict['data_mart_id'] = self.data_mart_id
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'target') and self.target is not None:
            _dict['target'] = self.target.to_dict()
        if hasattr(self, 'schema_update_mode') and self.schema_update_mode is not None:
            _dict['schema_update_mode'] = self.schema_update_mode
        if hasattr(self, 'data_schema') and self.data_schema is not None:
            _dict['data_schema'] = self.data_schema.to_dict()
        if hasattr(self, 'location') and self.location is not None:
            _dict['location'] = self.location.to_dict()
        if hasattr(self, 'managed_by') and self.managed_by is not None:
            _dict['managed_by'] = self.managed_by
        if hasattr(self, 'status') and self.status is not None:
            _dict['status'] = self.status.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataSetObject object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataSetObject') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataSetObject') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class TypeEnum(str, Enum):
        """
        type of a data set.
        """
        MANUAL_LABELING = 'manual_labeling'
        PAYLOAD_LOGGING = 'payload_logging'
        FEEDBACK = 'feedback'
        BUSINESS_PAYLOAD = 'business_payload'
        EXPLANATIONS = 'explanations'
        EXPLANATIONS_WHATIF = 'explanations_whatif'
        TRAINING = 'training'
        PAYLOAD_LOGGING_ERROR = 'payload_logging_error'
        CUSTOM = 'custom'


    class SchemaUpdateModeEnum(str, Enum):
        """
        schema_update_mode.
        """
        NONE = 'none'
        AUTO = 'auto'


class DataSetRecords():
    """
    DataSetRecords.

    :attr List[DataSetRecordsDataSetRecordsItem] data_set_records:
    """

    def __init__(self,
                 data_set_records: List['DataSetRecordsDataSetRecordsItem']) -> None:
        """
        Initialize a DataSetRecords object.

        :param List[DataSetRecordsDataSetRecordsItem] data_set_records:
        """
        self.data_set_records = data_set_records

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataSetRecords':
        """Initialize a DataSetRecords object from a json dictionary."""
        args = {}
        if 'data_set_records' in _dict:
            args['data_set_records'] = [DataSetRecordsDataSetRecordsItem.from_dict(x) for x in _dict.get('data_set_records')]
        else:
            raise ValueError('Required property \'data_set_records\' not present in DataSetRecords JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataSetRecords object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'data_set_records') and self.data_set_records is not None:
            _dict['data_set_records'] = [x.to_dict() for x in self.data_set_records]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataSetRecords object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataSetRecords') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataSetRecords') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataSetRecordsDataSetRecordsItem():
    """
    DataSetRecordsDataSetRecordsItem.

    :attr DataSetRecordsDataSetRecordsItemDataSet data_set:
    :attr DataSetRecordsDataSetRecordsItemRecords records:
    """

    def __init__(self,
                 data_set: 'DataSetRecordsDataSetRecordsItemDataSet',
                 records: 'DataSetRecordsDataSetRecordsItemRecords') -> None:
        """
        Initialize a DataSetRecordsDataSetRecordsItem object.

        :param DataSetRecordsDataSetRecordsItemDataSet data_set:
        :param DataSetRecordsDataSetRecordsItemRecords records:
        """
        self.data_set = data_set
        self.records = records

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataSetRecordsDataSetRecordsItem':
        """Initialize a DataSetRecordsDataSetRecordsItem object from a json dictionary."""
        args = {}
        if 'data_set' in _dict:
            args['data_set'] = DataSetRecordsDataSetRecordsItemDataSet.from_dict(_dict.get('data_set'))
        else:
            raise ValueError('Required property \'data_set\' not present in DataSetRecordsDataSetRecordsItem JSON')
        if 'records' in _dict:
            args['records'] = DataSetRecordsDataSetRecordsItemRecords.from_dict(_dict.get('records'))
        else:
            raise ValueError('Required property \'records\' not present in DataSetRecordsDataSetRecordsItem JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataSetRecordsDataSetRecordsItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'data_set') and self.data_set is not None:
            _dict['data_set'] = self.data_set.to_dict()
        if hasattr(self, 'records') and self.records is not None:
            _dict['records'] = self.records.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataSetRecordsDataSetRecordsItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataSetRecordsDataSetRecordsItem') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataSetRecordsDataSetRecordsItem') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataSetRecordsDataSetRecordsItemDataSet():
    """
    DataSetRecordsDataSetRecordsItemDataSet.

    :attr str data_mart_id:
    :attr str type: type of a data set.
    :attr Target target:
    :attr SparkStruct data_schema:
    """

    def __init__(self,
                 data_mart_id: str,
                 type: str,
                 target: 'Target',
                 data_schema: 'SparkStruct') -> None:
        """
        Initialize a DataSetRecordsDataSetRecordsItemDataSet object.

        :param str data_mart_id:
        :param str type: type of a data set.
        :param Target target:
        :param SparkStruct data_schema:
        """
        self.data_mart_id = data_mart_id
        self.type = type
        self.target = target
        self.data_schema = data_schema

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataSetRecordsDataSetRecordsItemDataSet':
        """Initialize a DataSetRecordsDataSetRecordsItemDataSet object from a json dictionary."""
        args = {}
        if 'data_mart_id' in _dict:
            args['data_mart_id'] = _dict.get('data_mart_id')
        else:
            raise ValueError('Required property \'data_mart_id\' not present in DataSetRecordsDataSetRecordsItemDataSet JSON')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in DataSetRecordsDataSetRecordsItemDataSet JSON')
        if 'target' in _dict:
            args['target'] = Target.from_dict(_dict.get('target'))
        else:
            raise ValueError('Required property \'target\' not present in DataSetRecordsDataSetRecordsItemDataSet JSON')
        if 'data_schema' in _dict:
            args['data_schema'] = SparkStruct.from_dict(_dict.get('data_schema'))
        else:
            raise ValueError('Required property \'data_schema\' not present in DataSetRecordsDataSetRecordsItemDataSet JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataSetRecordsDataSetRecordsItemDataSet object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'data_mart_id') and self.data_mart_id is not None:
            _dict['data_mart_id'] = self.data_mart_id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'target') and self.target is not None:
            _dict['target'] = self.target.to_dict()
        if hasattr(self, 'data_schema') and self.data_schema is not None:
            _dict['data_schema'] = self.data_schema.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataSetRecordsDataSetRecordsItemDataSet object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataSetRecordsDataSetRecordsItemDataSet') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataSetRecordsDataSetRecordsItemDataSet') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class TypeEnum(str, Enum):
        """
        type of a data set.
        """
        MANUAL_LABELING = 'manual_labeling'
        PAYLOAD_LOGGING = 'payload_logging'
        FEEDBACK = 'feedback'
        BUSINESS_PAYLOAD = 'business_payload'
        EXPLANATIONS = 'explanations'
        EXPLANATIONS_WHATIF = 'explanations_whatif'
        TRAINING = 'training'
        PAYLOAD_LOGGING_ERROR = 'payload_logging_error'
        CUSTOM = 'custom'


class DataSetRecordsDataSetRecordsItemRecords():
    """
    DataSetRecordsDataSetRecordsItemRecords.

    :attr Metadata metadata:
    :attr DataSetRecordsDataSetRecordsItemRecordsEntity entity:
    """

    def __init__(self,
                 metadata: 'Metadata',
                 entity: 'DataSetRecordsDataSetRecordsItemRecordsEntity') -> None:
        """
        Initialize a DataSetRecordsDataSetRecordsItemRecords object.

        :param Metadata metadata:
        :param DataSetRecordsDataSetRecordsItemRecordsEntity entity:
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataSetRecordsDataSetRecordsItemRecords':
        """Initialize a DataSetRecordsDataSetRecordsItemRecords object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in DataSetRecordsDataSetRecordsItemRecords JSON')
        if 'entity' in _dict:
            args['entity'] = DataSetRecordsDataSetRecordsItemRecordsEntity.from_dict(_dict.get('entity'))
        else:
            raise ValueError('Required property \'entity\' not present in DataSetRecordsDataSetRecordsItemRecords JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataSetRecordsDataSetRecordsItemRecords object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataSetRecordsDataSetRecordsItemRecords object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataSetRecordsDataSetRecordsItemRecords') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataSetRecordsDataSetRecordsItemRecords') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataSetRecordsDataSetRecordsItemRecordsEntity():
    """
    DataSetRecordsDataSetRecordsItemRecordsEntity.

    :attr object values: Fields and values of the entity matches JSON object's
          fields and values.
    """

    def __init__(self,
                 values: object) -> None:
        """
        Initialize a DataSetRecordsDataSetRecordsItemRecordsEntity object.

        :param object values: Fields and values of the entity matches JSON object's
               fields and values.
        """
        self.values = values

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataSetRecordsDataSetRecordsItemRecordsEntity':
        """Initialize a DataSetRecordsDataSetRecordsItemRecordsEntity object from a json dictionary."""
        args = {}
        if 'values' in _dict:
            args['values'] = _dict.get('values')
        else:
            raise ValueError('Required property \'values\' not present in DataSetRecordsDataSetRecordsItemRecordsEntity JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataSetRecordsDataSetRecordsItemRecordsEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'values') and self.values is not None:
            _dict['values'] = self.values
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataSetRecordsDataSetRecordsItemRecordsEntity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataSetRecordsDataSetRecordsItemRecordsEntity') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataSetRecordsDataSetRecordsItemRecordsEntity') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataSetResponse():
    """
    DataSetResponse.

    :attr Metadata metadata:
    :attr DataSetObject entity:
    """

    def __init__(self,
                 metadata: 'Metadata',
                 entity: 'DataSetObject') -> None:
        """
        Initialize a DataSetResponse object.

        :param Metadata metadata:
        :param DataSetObject entity:
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataSetResponse':
        """Initialize a DataSetResponse object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in DataSetResponse JSON')
        if 'entity' in _dict:
            args['entity'] = DataSetObject.from_dict(_dict.get('entity'))
        else:
            raise ValueError('Required property \'entity\' not present in DataSetResponse JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataSetResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataSetResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataSetResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataSetResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataSetResponseCollection():
    """
    DataSetResponseCollection.

    :attr List[DataSetResponse] data_sets:
    """

    def __init__(self,
                 data_sets: List['DataSetResponse']) -> None:
        """
        Initialize a DataSetResponseCollection object.

        :param List[DataSetResponse] data_sets:
        """
        self.data_sets = data_sets

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataSetResponseCollection':
        """Initialize a DataSetResponseCollection object from a json dictionary."""
        args = {}
        if 'data_sets' in _dict:
            args['data_sets'] = [DataSetResponse.from_dict(x) for x in _dict.get('data_sets')]
        else:
            raise ValueError('Required property \'data_sets\' not present in DataSetResponseCollection JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataSetResponseCollection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'data_sets') and self.data_sets is not None:
            _dict['data_sets'] = [x.to_dict() for x in self.data_sets]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataSetResponseCollection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataSetResponseCollection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataSetResponseCollection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataSource():
    """
    DataSource.

    :attr str type: (optional) Type of data source. e.g. payload, feedback,
          drift,explain.
    :attr DataSourceConnection connection: (optional)
    :attr str database_name: (optional) database name.
    :attr str schema_name: (optional) schema name.
    :attr str table_name: (optional) table name.
    :attr DataSourceEndpoint endpoint: (optional)
    :attr object parameters: (optional) Additional parameters.
    """

    def __init__(self,
                 *,
                 type: str = None,
                 connection: 'DataSourceConnection' = None,
                 database_name: str = None,
                 schema_name: str = None,
                 table_name: str = None,
                 endpoint: 'DataSourceEndpoint' = None,
                 parameters: object = None) -> None:
        """
        Initialize a DataSource object.

        :param str type: (optional) Type of data source. e.g. payload, feedback,
               drift,explain.
        :param DataSourceConnection connection: (optional)
        :param str database_name: (optional) database name.
        :param str schema_name: (optional) schema name.
        :param str table_name: (optional) table name.
        :param DataSourceEndpoint endpoint: (optional)
        :param object parameters: (optional) Additional parameters.
        """
        self.type = type
        self.connection = connection
        self.database_name = database_name
        self.schema_name = schema_name
        self.table_name = table_name
        self.endpoint = endpoint
        self.parameters = parameters

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataSource':
        """Initialize a DataSource object from a json dictionary."""
        args = {}
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        if 'connection' in _dict:
            args['connection'] = DataSourceConnection.from_dict(_dict.get('connection'))
        if 'database_name' in _dict:
            args['database_name'] = _dict.get('database_name')
        if 'schema_name' in _dict:
            args['schema_name'] = _dict.get('schema_name')
        if 'table_name' in _dict:
            args['table_name'] = _dict.get('table_name')
        if 'endpoint' in _dict:
            args['endpoint'] = DataSourceEndpoint.from_dict(_dict.get('endpoint'))
        if 'parameters' in _dict:
            args['parameters'] = _dict.get('parameters')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataSource object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'connection') and self.connection is not None:
            _dict['connection'] = self.connection.to_dict()
        if hasattr(self, 'database_name') and self.database_name is not None:
            _dict['database_name'] = self.database_name
        if hasattr(self, 'schema_name') and self.schema_name is not None:
            _dict['schema_name'] = self.schema_name
        if hasattr(self, 'table_name') and self.table_name is not None:
            _dict['table_name'] = self.table_name
        if hasattr(self, 'endpoint') and self.endpoint is not None:
            _dict['endpoint'] = self.endpoint.to_dict()
        if hasattr(self, 'parameters') and self.parameters is not None:
            _dict['parameters'] = self.parameters
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataSource object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataSource') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataSource') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataSourceConnection():
    """
    DataSourceConnection.

    :attr str type: (optional) Type of integrated system, e.g. hive, jdbc.
    :attr str integrated_system_id: (optional) id of the integrated system.
    :attr object parameters: (optional) Additional parameters.
    """

    def __init__(self,
                 *,
                 type: str = None,
                 integrated_system_id: str = None,
                 parameters: object = None) -> None:
        """
        Initialize a DataSourceConnection object.

        :param str type: (optional) Type of integrated system, e.g. hive, jdbc.
        :param str integrated_system_id: (optional) id of the integrated system.
        :param object parameters: (optional) Additional parameters.
        """
        self.type = type
        self.integrated_system_id = integrated_system_id
        self.parameters = parameters

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataSourceConnection':
        """Initialize a DataSourceConnection object from a json dictionary."""
        args = {}
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        if 'integrated_system_id' in _dict:
            args['integrated_system_id'] = _dict.get('integrated_system_id')
        if 'parameters' in _dict:
            args['parameters'] = _dict.get('parameters')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataSourceConnection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'integrated_system_id') and self.integrated_system_id is not None:
            _dict['integrated_system_id'] = self.integrated_system_id
        if hasattr(self, 'parameters') and self.parameters is not None:
            _dict['parameters'] = self.parameters
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataSourceConnection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataSourceConnection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataSourceConnection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DataSourceEndpoint():
    """
    DataSourceEndpoint.

    :attr str url: Url of the endpoint.
    :attr object credentials: (optional) Credentials for the endpoint.
    """

    def __init__(self,
                 url: str,
                 *,
                 credentials: object = None) -> None:
        """
        Initialize a DataSourceEndpoint object.

        :param str url: Url of the endpoint.
        :param object credentials: (optional) Credentials for the endpoint.
        """
        self.url = url
        self.credentials = credentials

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DataSourceEndpoint':
        """Initialize a DataSourceEndpoint object from a json dictionary."""
        args = {}
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        else:
            raise ValueError('Required property \'url\' not present in DataSourceEndpoint JSON')
        if 'credentials' in _dict:
            args['credentials'] = _dict.get('credentials')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DataSourceEndpoint object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        if hasattr(self, 'credentials') and self.credentials is not None:
            _dict['credentials'] = self.credentials
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DataSourceEndpoint object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DataSourceEndpoint') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DataSourceEndpoint') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DatabaseConfiguration():
    """
    Database configuration ignored if internal database is requested (`internal_database`
    is `true`).

    :attr str database_type:
    :attr str instance_id: (optional)
    :attr str name: (optional)
    :attr SecretCleaned credentials:
    :attr LocationSchemaName location: (optional)
    """

    def __init__(self,
                 database_type: str,
                 credentials: 'SecretCleaned',
                 *,
                 instance_id: str = None,
                 name: str = None,
                 location: 'LocationSchemaName' = None) -> None:
        """
        Initialize a DatabaseConfiguration object.

        :param str database_type:
        :param SecretCleaned credentials:
        :param str instance_id: (optional)
        :param str name: (optional)
        :param LocationSchemaName location: (optional)
        """
        self.database_type = database_type
        self.instance_id = instance_id
        self.name = name
        self.credentials = credentials
        self.location = location

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DatabaseConfiguration':
        """Initialize a DatabaseConfiguration object from a json dictionary."""
        args = {}
        if 'database_type' in _dict:
            args['database_type'] = _dict.get('database_type')
        else:
            raise ValueError('Required property \'database_type\' not present in DatabaseConfiguration JSON')
        if 'instance_id' in _dict:
            args['instance_id'] = _dict.get('instance_id')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        if 'credentials' in _dict:
            args['credentials'] = SecretCleaned.from_dict(_dict.get('credentials'))
        else:
            raise ValueError('Required property \'credentials\' not present in DatabaseConfiguration JSON')
        if 'location' in _dict:
            args['location'] = LocationSchemaName.from_dict(_dict.get('location'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DatabaseConfiguration object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'database_type') and self.database_type is not None:
            _dict['database_type'] = self.database_type
        if hasattr(self, 'instance_id') and self.instance_id is not None:
            _dict['instance_id'] = self.instance_id
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'credentials') and self.credentials is not None:
            _dict['credentials'] = self.credentials.to_dict()
        if hasattr(self, 'location') and self.location is not None:
            _dict['location'] = self.location.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DatabaseConfiguration object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DatabaseConfiguration') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DatabaseConfiguration') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class DatabaseTypeEnum(str, Enum):
        """
        database_type.
        """
        POSTGRESQL = 'postgresql'
        DB2 = 'db2'


class DatabaseConfigurationRequest():
    """
    Database configuration ignored if internal database is requested (`internal_database`
    is `true`).

    :attr str database_type:
    :attr str name: (optional)
    :attr str instance_id: (optional)
    :attr PrimaryStorageCredentials credentials:
    :attr LocationSchemaName location: (optional)
    """

    def __init__(self,
                 database_type: str,
                 credentials: 'PrimaryStorageCredentials',
                 *,
                 name: str = None,
                 instance_id: str = None,
                 location: 'LocationSchemaName' = None) -> None:
        """
        Initialize a DatabaseConfigurationRequest object.

        :param str database_type:
        :param PrimaryStorageCredentials credentials:
        :param str name: (optional)
        :param str instance_id: (optional)
        :param LocationSchemaName location: (optional)
        """
        self.database_type = database_type
        self.name = name
        self.instance_id = instance_id
        self.credentials = credentials
        self.location = location

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DatabaseConfigurationRequest':
        """Initialize a DatabaseConfigurationRequest object from a json dictionary."""
        args = {}
        if 'database_type' in _dict:
            args['database_type'] = _dict.get('database_type')
        else:
            raise ValueError('Required property \'database_type\' not present in DatabaseConfigurationRequest JSON')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        if 'instance_id' in _dict:
            args['instance_id'] = _dict.get('instance_id')
        if 'credentials' in _dict:
            args['credentials'] = _dict.get('credentials')
        else:
            raise ValueError('Required property \'credentials\' not present in DatabaseConfigurationRequest JSON')
        if 'location' in _dict:
            args['location'] = LocationSchemaName.from_dict(_dict.get('location'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DatabaseConfigurationRequest object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'database_type') and self.database_type is not None:
            _dict['database_type'] = self.database_type
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'instance_id') and self.instance_id is not None:
            _dict['instance_id'] = self.instance_id
        if hasattr(self, 'credentials') and self.credentials is not None:
            if isinstance(self.credentials, dict):
                _dict['credentials'] = self.credentials
            else:
                _dict['credentials'] = self.credentials.to_dict()
        if hasattr(self, 'location') and self.location is not None:
            _dict['location'] = self.location.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DatabaseConfigurationRequest object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DatabaseConfigurationRequest') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DatabaseConfigurationRequest') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class DatabaseTypeEnum(str, Enum):
        """
        database_type.
        """
        POSTGRESQL = 'postgresql'
        DB2 = 'db2'


class ExplanationError():
    """
    Explanation error details.

    :attr str explanation_type: (optional) Type of explanation.
    :attr ExplanationErrorError error: (optional) The error message details.
    :attr str trace_id: (optional) ID used to track the explanation task via logs.
    """

    def __init__(self,
                 *,
                 explanation_type: str = None,
                 error: 'ExplanationErrorError' = None,
                 trace_id: str = None) -> None:
        """
        Initialize a ExplanationError object.

        :param str explanation_type: (optional) Type of explanation.
        :param ExplanationErrorError error: (optional) The error message details.
        :param str trace_id: (optional) ID used to track the explanation task via
               logs.
        """
        self.explanation_type = explanation_type
        self.error = error
        self.trace_id = trace_id

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ExplanationError':
        """Initialize a ExplanationError object from a json dictionary."""
        args = {}
        if 'explanation_type' in _dict:
            args['explanation_type'] = _dict.get('explanation_type')
        if 'error' in _dict:
            args['error'] = ExplanationErrorError.from_dict(_dict.get('error'))
        if 'trace_id' in _dict:
            args['trace_id'] = _dict.get('trace_id')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ExplanationError object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'explanation_type') and self.explanation_type is not None:
            _dict['explanation_type'] = self.explanation_type
        if hasattr(self, 'error') and self.error is not None:
            _dict['error'] = self.error.to_dict()
        if hasattr(self, 'trace_id') and self.trace_id is not None:
            _dict['trace_id'] = self.trace_id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ExplanationError object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ExplanationError') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ExplanationError') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class ExplanationErrorError():
    """
    The error message details.

    :attr str code: (optional) Error code.
    :attr str message: (optional) Error message.
    """

    def __init__(self,
                 *,
                 code: str = None,
                 message: str = None) -> None:
        """
        Initialize a ExplanationErrorError object.

        :param str code: (optional) Error code.
        :param str message: (optional) Error message.
        """
        self.code = code
        self.message = message

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ExplanationErrorError':
        """Initialize a ExplanationErrorError object from a json dictionary."""
        args = {}
        if 'code' in _dict:
            args['code'] = _dict.get('code')
        if 'message' in _dict:
            args['message'] = _dict.get('message')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ExplanationErrorError object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'code') and self.code is not None:
            _dict['code'] = self.code
        if hasattr(self, 'message') and self.message is not None:
            _dict['message'] = self.message
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ExplanationErrorError object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ExplanationErrorError') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ExplanationErrorError') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class ExplanationTaskResponseEntityAsset():
    """
    Asset details in get explanation task response.

    :attr str id: (optional) Identifier for the asset.
    :attr str name: (optional) Name of the asset.
    :attr str input_data_type: (optional) Type of the input data.
    :attr str problem_type: (optional) Problem type.
    :attr ExplanationTaskResponseEntityAssetDeployment deployment: (optional) Asset
          deployment details.
    """

    def __init__(self,
                 *,
                 id: str = None,
                 name: str = None,
                 input_data_type: str = None,
                 problem_type: str = None,
                 deployment: 'ExplanationTaskResponseEntityAssetDeployment' = None) -> None:
        """
        Initialize a ExplanationTaskResponseEntityAsset object.

        :param str id: (optional) Identifier for the asset.
        :param str name: (optional) Name of the asset.
        :param str input_data_type: (optional) Type of the input data.
        :param str problem_type: (optional) Problem type.
        :param ExplanationTaskResponseEntityAssetDeployment deployment: (optional)
               Asset deployment details.
        """
        self.id = id
        self.name = name
        self.input_data_type = input_data_type
        self.problem_type = problem_type
        self.deployment = deployment

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ExplanationTaskResponseEntityAsset':
        """Initialize a ExplanationTaskResponseEntityAsset object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        if 'input_data_type' in _dict:
            args['input_data_type'] = _dict.get('input_data_type')
        if 'problem_type' in _dict:
            args['problem_type'] = _dict.get('problem_type')
        if 'deployment' in _dict:
            args['deployment'] = ExplanationTaskResponseEntityAssetDeployment.from_dict(_dict.get('deployment'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ExplanationTaskResponseEntityAsset object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'input_data_type') and self.input_data_type is not None:
            _dict['input_data_type'] = self.input_data_type
        if hasattr(self, 'problem_type') and self.problem_type is not None:
            _dict['problem_type'] = self.problem_type
        if hasattr(self, 'deployment') and self.deployment is not None:
            _dict['deployment'] = self.deployment.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ExplanationTaskResponseEntityAsset object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ExplanationTaskResponseEntityAsset') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ExplanationTaskResponseEntityAsset') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class InputDataTypeEnum(str, Enum):
        """
        Type of the input data.
        """
        STRUCTURED = 'structured'
        UNSTRUCTURED_IMAGE = 'unstructured_image'
        UNSTRUCTURED_TEXT = 'unstructured_text'


    class ProblemTypeEnum(str, Enum):
        """
        Problem type.
        """
        BINARY = 'binary'
        REGRESSION = 'regression'
        MULTICLASS = 'multiclass'


class ExplanationTaskResponseEntityAssetDeployment():
    """
    Asset deployment details.

    :attr str id: (optional) Identifier for the asset deployment.
    :attr str name: (optional) Name of the asset deployment.
    """

    def __init__(self,
                 *,
                 id: str = None,
                 name: str = None) -> None:
        """
        Initialize a ExplanationTaskResponseEntityAssetDeployment object.

        :param str id: (optional) Identifier for the asset deployment.
        :param str name: (optional) Name of the asset deployment.
        """
        self.id = id
        self.name = name

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ExplanationTaskResponseEntityAssetDeployment':
        """Initialize a ExplanationTaskResponseEntityAssetDeployment object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ExplanationTaskResponseEntityAssetDeployment object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ExplanationTaskResponseEntityAssetDeployment object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ExplanationTaskResponseEntityAssetDeployment') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ExplanationTaskResponseEntityAssetDeployment') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class ExplanationTaskResponseEntityInputFeature():
    """
    Input feature details in get explanation task response.

    :attr str name: (optional) Name of the feature column.
    :attr str value: (optional) Value of the feature column.
    :attr str feature_type: (optional) Identifies the type of feature column.
    """

    def __init__(self,
                 *,
                 name: str = None,
                 value: str = None,
                 feature_type: str = None) -> None:
        """
        Initialize a ExplanationTaskResponseEntityInputFeature object.

        :param str name: (optional) Name of the feature column.
        :param str value: (optional) Value of the feature column.
        :param str feature_type: (optional) Identifies the type of feature column.
        """
        self.name = name
        self.value = value
        self.feature_type = feature_type

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ExplanationTaskResponseEntityInputFeature':
        """Initialize a ExplanationTaskResponseEntityInputFeature object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        if 'value' in _dict:
            args['value'] = _dict.get('value')
        if 'feature_type' in _dict:
            args['feature_type'] = _dict.get('feature_type')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ExplanationTaskResponseEntityInputFeature object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        if hasattr(self, 'feature_type') and self.feature_type is not None:
            _dict['feature_type'] = self.feature_type
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ExplanationTaskResponseEntityInputFeature object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ExplanationTaskResponseEntityInputFeature') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ExplanationTaskResponseEntityInputFeature') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class FeatureTypeEnum(str, Enum):
        """
        Identifies the type of feature column.
        """
        NUMERICAL = 'numerical'
        CATEGORICAL = 'categorical'


class FairnessMonitoringRemediation():
    """
    FairnessMonitoringRemediation.

    :attr List[str] fields: The fields of the model processed debias scoring.
    :attr List[object] values: The values associated to the fields.
    """

    def __init__(self,
                 fields: List[str],
                 values: List[object]) -> None:
        """
        Initialize a FairnessMonitoringRemediation object.

        :param List[str] fields: The fields of the model processed debias scoring.
        :param List[object] values: The values associated to the fields.
        """
        self.fields = fields
        self.values = values

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'FairnessMonitoringRemediation':
        """Initialize a FairnessMonitoringRemediation object from a json dictionary."""
        args = {}
        if 'fields' in _dict:
            args['fields'] = _dict.get('fields')
        else:
            raise ValueError('Required property \'fields\' not present in FairnessMonitoringRemediation JSON')
        if 'values' in _dict:
            args['values'] = _dict.get('values')
        else:
            raise ValueError('Required property \'values\' not present in FairnessMonitoringRemediation JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a FairnessMonitoringRemediation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'fields') and self.fields is not None:
            _dict['fields'] = self.fields
        if hasattr(self, 'values') and self.values is not None:
            _dict['values'] = self.values
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this FairnessMonitoringRemediation object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'FairnessMonitoringRemediation') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'FairnessMonitoringRemediation') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class FileAssetMetadata():
    """
    File data asset metadata.

    :attr str project_id: (optional) Project id.
    :attr str project_name: (optional) Project name.
    :attr str asset_id: (optional) File data asset id.
    :attr str asset_name: (optional) File data asset name.
    :attr str asset_href: File data asset reference.
    :attr FileTrainingDataReferenceOptions meta: (optional) additional options for
          different types of training data references.
    """

    def __init__(self,
                 asset_href: str,
                 *,
                 project_id: str = None,
                 project_name: str = None,
                 asset_id: str = None,
                 asset_name: str = None,
                 meta: 'FileTrainingDataReferenceOptions' = None) -> None:
        """
        Initialize a FileAssetMetadata object.

        :param str asset_href: File data asset reference.
        :param str project_id: (optional) Project id.
        :param str project_name: (optional) Project name.
        :param str asset_id: (optional) File data asset id.
        :param str asset_name: (optional) File data asset name.
        :param FileTrainingDataReferenceOptions meta: (optional) additional options
               for different types of training data references.
        """
        self.project_id = project_id
        self.project_name = project_name
        self.asset_id = asset_id
        self.asset_name = asset_name
        self.asset_href = asset_href
        self.meta = meta

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'FileAssetMetadata':
        """Initialize a FileAssetMetadata object from a json dictionary."""
        args = {}
        if 'project_id' in _dict:
            args['project_id'] = _dict.get('project_id')
        if 'project_name' in _dict:
            args['project_name'] = _dict.get('project_name')
        if 'asset_id' in _dict:
            args['asset_id'] = _dict.get('asset_id')
        if 'asset_name' in _dict:
            args['asset_name'] = _dict.get('asset_name')
        if 'asset_href' in _dict:
            args['asset_href'] = _dict.get('asset_href')
        else:
            raise ValueError('Required property \'asset_href\' not present in FileAssetMetadata JSON')
        if 'meta' in _dict:
            args['meta'] = FileTrainingDataReferenceOptions.from_dict(_dict.get('meta'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a FileAssetMetadata object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'project_id') and self.project_id is not None:
            _dict['project_id'] = self.project_id
        if hasattr(self, 'project_name') and self.project_name is not None:
            _dict['project_name'] = self.project_name
        if hasattr(self, 'asset_id') and self.asset_id is not None:
            _dict['asset_id'] = self.asset_id
        if hasattr(self, 'asset_name') and self.asset_name is not None:
            _dict['asset_name'] = self.asset_name
        if hasattr(self, 'asset_href') and self.asset_href is not None:
            _dict['asset_href'] = self.asset_href
        if hasattr(self, 'meta') and self.meta is not None:
            _dict['meta'] = self.meta.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this FileAssetMetadata object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'FileAssetMetadata') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'FileAssetMetadata') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class FileTrainingDataReferenceOptions():
    """
    additional options for different types of training data references.

    :attr str file_name: (optional) file name.
    :attr str file_format: (optional) File format.
    :attr bool first_line_is_header: (optional) if not provided service will attempt
          to automatically detect header in the first line (for data provided as csv).
    :attr str delimiter: (optional) delimiter character for data provided as csv.
    :attr float csv_max_line_length: (optional) maximum length of single line in
          bytes (default 10000000).
    :attr str on_error: (optional) Expected behaviour on error while reading a csv
          file. Default behaviour is "stop".
    """

    def __init__(self,
                 *,
                 file_name: str = None,
                 file_format: str = None,
                 first_line_is_header: bool = None,
                 delimiter: str = None,
                 csv_max_line_length: float = None,
                 on_error: str = None) -> None:
        """
        Initialize a FileTrainingDataReferenceOptions object.

        :param str file_name: (optional) file name.
        :param str file_format: (optional) File format.
        :param bool first_line_is_header: (optional) if not provided service will
               attempt to automatically detect header in the first line (for data provided
               as csv).
        :param str delimiter: (optional) delimiter character for data provided as
               csv.
        :param float csv_max_line_length: (optional) maximum length of single line
               in bytes (default 10000000).
        :param str on_error: (optional) Expected behaviour on error while reading a
               csv file. Default behaviour is "stop".
        """
        self.file_name = file_name
        self.file_format = file_format
        self.first_line_is_header = first_line_is_header
        self.delimiter = delimiter
        self.csv_max_line_length = csv_max_line_length
        self.on_error = on_error

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'FileTrainingDataReferenceOptions':
        """Initialize a FileTrainingDataReferenceOptions object from a json dictionary."""
        args = {}
        if 'file_name' in _dict:
            args['file_name'] = _dict.get('file_name')
        if 'file_format' in _dict:
            args['file_format'] = _dict.get('file_format')
        if 'first_line_is_header' in _dict:
            args['first_line_is_header'] = _dict.get('first_line_is_header')
        if 'delimiter' in _dict:
            args['delimiter'] = _dict.get('delimiter')
        if 'csv_max_line_length' in _dict:
            args['csv_max_line_length'] = _dict.get('csv_max_line_length')
        if 'on_error' in _dict:
            args['on_error'] = _dict.get('on_error')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a FileTrainingDataReferenceOptions object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'file_name') and self.file_name is not None:
            _dict['file_name'] = self.file_name
        if hasattr(self, 'file_format') and self.file_format is not None:
            _dict['file_format'] = self.file_format
        if hasattr(self, 'first_line_is_header') and self.first_line_is_header is not None:
            _dict['first_line_is_header'] = self.first_line_is_header
        if hasattr(self, 'delimiter') and self.delimiter is not None:
            _dict['delimiter'] = self.delimiter
        if hasattr(self, 'csv_max_line_length') and self.csv_max_line_length is not None:
            _dict['csv_max_line_length'] = self.csv_max_line_length
        if hasattr(self, 'on_error') and self.on_error is not None:
            _dict['on_error'] = self.on_error
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this FileTrainingDataReferenceOptions object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'FileTrainingDataReferenceOptions') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'FileTrainingDataReferenceOptions') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class OnErrorEnum(str, Enum):
        """
        Expected behaviour on error while reading a csv file. Default behaviour is "stop".
        """
        STOP = 'stop'
        CONTINUE = 'continue'


class GenericErrorResponse():
    """
    GenericErrorResponse.

    :attr str trace: ID of the original request.
    :attr List[GenericErrorResponseErrorsItem] errors:
    """

    def __init__(self,
                 trace: str,
                 errors: List['GenericErrorResponseErrorsItem']) -> None:
        """
        Initialize a GenericErrorResponse object.

        :param str trace: ID of the original request.
        :param List[GenericErrorResponseErrorsItem] errors:
        """
        self.trace = trace
        self.errors = errors

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'GenericErrorResponse':
        """Initialize a GenericErrorResponse object from a json dictionary."""
        args = {}
        if 'trace' in _dict:
            args['trace'] = _dict.get('trace')
        else:
            raise ValueError('Required property \'trace\' not present in GenericErrorResponse JSON')
        if 'errors' in _dict:
            args['errors'] = [GenericErrorResponseErrorsItem.from_dict(x) for x in _dict.get('errors')]
        else:
            raise ValueError('Required property \'errors\' not present in GenericErrorResponse JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a GenericErrorResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'trace') and self.trace is not None:
            _dict['trace'] = self.trace
        if hasattr(self, 'errors') and self.errors is not None:
            _dict['errors'] = [x.to_dict() for x in self.errors]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this GenericErrorResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'GenericErrorResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'GenericErrorResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class GenericErrorResponseErrorsItem():
    """
    GenericErrorResponseErrorsItem.

    :attr str code: Error code.
    :attr str message: Error message.
    :attr List[str] parameters: (optional) Error message parameters.
    """

    def __init__(self,
                 code: str,
                 message: str,
                 *,
                 parameters: List[str] = None) -> None:
        """
        Initialize a GenericErrorResponseErrorsItem object.

        :param str code: Error code.
        :param str message: Error message.
        :param List[str] parameters: (optional) Error message parameters.
        """
        self.code = code
        self.message = message
        self.parameters = parameters

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'GenericErrorResponseErrorsItem':
        """Initialize a GenericErrorResponseErrorsItem object from a json dictionary."""
        args = {}
        if 'code' in _dict:
            args['code'] = _dict.get('code')
        else:
            raise ValueError('Required property \'code\' not present in GenericErrorResponseErrorsItem JSON')
        if 'message' in _dict:
            args['message'] = _dict.get('message')
        else:
            raise ValueError('Required property \'message\' not present in GenericErrorResponseErrorsItem JSON')
        if 'parameters' in _dict:
            args['parameters'] = _dict.get('parameters')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a GenericErrorResponseErrorsItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'code') and self.code is not None:
            _dict['code'] = self.code
        if hasattr(self, 'message') and self.message is not None:
            _dict['message'] = self.message
        if hasattr(self, 'parameters') and self.parameters is not None:
            _dict['parameters'] = self.parameters
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this GenericErrorResponseErrorsItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'GenericErrorResponseErrorsItem') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'GenericErrorResponseErrorsItem') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class GetExplanationTaskResponse():
    """
    Get explanation task response.

    :attr GetExplanationTaskResponseMetadata metadata: Metadata of get explanation
          task response.
    :attr GetExplanationTaskResponseEntity entity: Entity of get explanation task
          response.
    """

    def __init__(self,
                 metadata: 'GetExplanationTaskResponseMetadata',
                 entity: 'GetExplanationTaskResponseEntity') -> None:
        """
        Initialize a GetExplanationTaskResponse object.

        :param GetExplanationTaskResponseMetadata metadata: Metadata of get
               explanation task response.
        :param GetExplanationTaskResponseEntity entity: Entity of get explanation
               task response.
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'GetExplanationTaskResponse':
        """Initialize a GetExplanationTaskResponse object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = GetExplanationTaskResponseMetadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in GetExplanationTaskResponse JSON')
        if 'entity' in _dict:
            args['entity'] = GetExplanationTaskResponseEntity.from_dict(_dict.get('entity'))
        else:
            raise ValueError('Required property \'entity\' not present in GetExplanationTaskResponse JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a GetExplanationTaskResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this GetExplanationTaskResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'GetExplanationTaskResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'GetExplanationTaskResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class GetExplanationTaskResponseEntity():
    """
    Entity of get explanation task response.

    :attr GetExplanationTaskResponseEntityStatus status: Status of the explanation
          task.
    :attr ExplanationTaskResponseEntityAsset asset: (optional) Asset details in get
          explanation task response.
    :attr List[ExplanationTaskResponseEntityInputFeature] input_features: (optional)
          List of input features.
    :attr str perturbed: (optional) Indicate whether the transaction is perturbed or
          not.
    :attr List[object] explanations: (optional) List of generated explanations.
    :attr List[ExplanationError] errors: (optional) List of errors occurred while
          generating explanations.
    :attr str scoring_id: (optional) ID of the scoring transaction.
    """

    def __init__(self,
                 status: 'GetExplanationTaskResponseEntityStatus',
                 *,
                 asset: 'ExplanationTaskResponseEntityAsset' = None,
                 input_features: List['ExplanationTaskResponseEntityInputFeature'] = None,
                 perturbed: str = None,
                 explanations: List[object] = None,
                 errors: List['ExplanationError'] = None,
                 scoring_id: str = None) -> None:
        """
        Initialize a GetExplanationTaskResponseEntity object.

        :param GetExplanationTaskResponseEntityStatus status: Status of the
               explanation task.
        :param ExplanationTaskResponseEntityAsset asset: (optional) Asset details
               in get explanation task response.
        :param List[ExplanationTaskResponseEntityInputFeature] input_features:
               (optional) List of input features.
        :param str perturbed: (optional) Indicate whether the transaction is
               perturbed or not.
        :param List[object] explanations: (optional) List of generated
               explanations.
        :param List[ExplanationError] errors: (optional) List of errors occurred
               while generating explanations.
        :param str scoring_id: (optional) ID of the scoring transaction.
        """
        self.status = status
        self.asset = asset
        self.input_features = input_features
        self.perturbed = perturbed
        self.explanations = explanations
        self.errors = errors
        self.scoring_id = scoring_id

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'GetExplanationTaskResponseEntity':
        """Initialize a GetExplanationTaskResponseEntity object from a json dictionary."""
        args = {}
        if 'status' in _dict:
            args['status'] = GetExplanationTaskResponseEntityStatus.from_dict(_dict.get('status'))
        else:
            raise ValueError('Required property \'status\' not present in GetExplanationTaskResponseEntity JSON')
        if 'asset' in _dict:
            args['asset'] = ExplanationTaskResponseEntityAsset.from_dict(_dict.get('asset'))
        if 'input_features' in _dict:
            args['input_features'] = [ExplanationTaskResponseEntityInputFeature.from_dict(x) for x in _dict.get('input_features')]
        if 'perturbed' in _dict:
            args['perturbed'] = _dict.get('perturbed')
        if 'explanations' in _dict:
            args['explanations'] = _dict.get('explanations')
        if 'errors' in _dict:
            args['errors'] = [ExplanationError.from_dict(x) for x in _dict.get('errors')]
        if 'scoring_id' in _dict:
            args['scoring_id'] = _dict.get('scoring_id')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a GetExplanationTaskResponseEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'status') and self.status is not None:
            _dict['status'] = self.status.to_dict()
        if hasattr(self, 'asset') and self.asset is not None:
            _dict['asset'] = self.asset.to_dict()
        if hasattr(self, 'input_features') and self.input_features is not None:
            _dict['input_features'] = [x.to_dict() for x in self.input_features]
        if hasattr(self, 'perturbed') and self.perturbed is not None:
            _dict['perturbed'] = self.perturbed
        if hasattr(self, 'explanations') and self.explanations is not None:
            _dict['explanations'] = self.explanations
        if hasattr(self, 'errors') and self.errors is not None:
            _dict['errors'] = [x.to_dict() for x in self.errors]
        if hasattr(self, 'scoring_id') and self.scoring_id is not None:
            _dict['scoring_id'] = self.scoring_id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this GetExplanationTaskResponseEntity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'GetExplanationTaskResponseEntity') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'GetExplanationTaskResponseEntity') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class PerturbedEnum(str, Enum):
        """
        Indicate whether the transaction is perturbed or not.
        """
        TRUE = 'true'
        FALSE = 'false'


class GetExplanationTaskResponseEntityStatus():
    """
    Status of the explanation task.

    :attr str state: (optional) Overall status of the explanation task.
    """

    def __init__(self,
                 *,
                 state: str = None) -> None:
        """
        Initialize a GetExplanationTaskResponseEntityStatus object.

        :param str state: (optional) Overall status of the explanation task.
        """
        self.state = state

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'GetExplanationTaskResponseEntityStatus':
        """Initialize a GetExplanationTaskResponseEntityStatus object from a json dictionary."""
        args = {}
        if 'state' in _dict:
            args['state'] = _dict.get('state')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a GetExplanationTaskResponseEntityStatus object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'state') and self.state is not None:
            _dict['state'] = self.state
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this GetExplanationTaskResponseEntityStatus object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'GetExplanationTaskResponseEntityStatus') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'GetExplanationTaskResponseEntityStatus') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class StateEnum(str, Enum):
        """
        Overall status of the explanation task.
        """
        IN_PROGRESS = 'in_progress'
        FINISHED = 'finished'
        ERROR = 'error'


class GetExplanationTaskResponseMetadata():
    """
    Metadata of get explanation task response.

    :attr str explanation_task_id: Identifier for tracking explanation task.
    :attr str created_by: ID of the user creating explanation task.
    :attr str created_at: Time when the explanation task was initiated.
    :attr str updated_at: (optional) Time when the explanation task was last
          updated.
    """

    def __init__(self,
                 explanation_task_id: str,
                 created_by: str,
                 created_at: str,
                 *,
                 updated_at: str = None) -> None:
        """
        Initialize a GetExplanationTaskResponseMetadata object.

        :param str explanation_task_id: Identifier for tracking explanation task.
        :param str created_by: ID of the user creating explanation task.
        :param str created_at: Time when the explanation task was initiated.
        :param str updated_at: (optional) Time when the explanation task was last
               updated.
        """
        self.explanation_task_id = explanation_task_id
        self.created_by = created_by
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'GetExplanationTaskResponseMetadata':
        """Initialize a GetExplanationTaskResponseMetadata object from a json dictionary."""
        args = {}
        if 'explanation_task_id' in _dict:
            args['explanation_task_id'] = _dict.get('explanation_task_id')
        else:
            raise ValueError('Required property \'explanation_task_id\' not present in GetExplanationTaskResponseMetadata JSON')
        if 'created_by' in _dict:
            args['created_by'] = _dict.get('created_by')
        else:
            raise ValueError('Required property \'created_by\' not present in GetExplanationTaskResponseMetadata JSON')
        if 'created_at' in _dict:
            args['created_at'] = _dict.get('created_at')
        else:
            raise ValueError('Required property \'created_at\' not present in GetExplanationTaskResponseMetadata JSON')
        if 'updated_at' in _dict:
            args['updated_at'] = _dict.get('updated_at')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a GetExplanationTaskResponseMetadata object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'explanation_task_id') and self.explanation_task_id is not None:
            _dict['explanation_task_id'] = self.explanation_task_id
        if hasattr(self, 'created_by') and self.created_by is not None:
            _dict['created_by'] = self.created_by
        if hasattr(self, 'created_at') and self.created_at is not None:
            _dict['created_at'] = self.created_at
        if hasattr(self, 'updated_at') and self.updated_at is not None:
            _dict['updated_at'] = self.updated_at
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this GetExplanationTaskResponseMetadata object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'GetExplanationTaskResponseMetadata') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'GetExplanationTaskResponseMetadata') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class GetExplanationTasksResponse():
    """
    List all explanations response.

    :attr int total_count: Total number of computed explanations.
    :attr int limit: Maximum number of returned explanations.
    :attr int offset: Offset of returned explanations.
    :attr List[str] explanation_fields: The list of explanation fields.
    :attr List[str] explanation_values: (optional) The list of explanation values.
    """

    def __init__(self,
                 total_count: int,
                 limit: int,
                 offset: int,
                 explanation_fields: List[str],
                 *,
                 explanation_values: List[str] = None) -> None:
        """
        Initialize a GetExplanationTasksResponse object.

        :param int total_count: Total number of computed explanations.
        :param int limit: Maximum number of returned explanations.
        :param int offset: Offset of returned explanations.
        :param List[str] explanation_fields: The list of explanation fields.
        :param List[str] explanation_values: (optional) The list of explanation
               values.
        """
        self.total_count = total_count
        self.limit = limit
        self.offset = offset
        self.explanation_fields = explanation_fields
        self.explanation_values = explanation_values

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'GetExplanationTasksResponse':
        """Initialize a GetExplanationTasksResponse object from a json dictionary."""
        args = {}
        if 'total_count' in _dict:
            args['total_count'] = _dict.get('total_count')
        else:
            raise ValueError('Required property \'total_count\' not present in GetExplanationTasksResponse JSON')
        if 'limit' in _dict:
            args['limit'] = _dict.get('limit')
        else:
            raise ValueError('Required property \'limit\' not present in GetExplanationTasksResponse JSON')
        if 'offset' in _dict:
            args['offset'] = _dict.get('offset')
        else:
            raise ValueError('Required property \'offset\' not present in GetExplanationTasksResponse JSON')
        if 'explanation_fields' in _dict:
            args['explanation_fields'] = _dict.get('explanation_fields')
        else:
            raise ValueError('Required property \'explanation_fields\' not present in GetExplanationTasksResponse JSON')
        if 'explanation_values' in _dict:
            args['explanation_values'] = _dict.get('explanation_values')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a GetExplanationTasksResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'total_count') and self.total_count is not None:
            _dict['total_count'] = self.total_count
        if hasattr(self, 'limit') and self.limit is not None:
            _dict['limit'] = self.limit
        if hasattr(self, 'offset') and self.offset is not None:
            _dict['offset'] = self.offset
        if hasattr(self, 'explanation_fields') and self.explanation_fields is not None:
            _dict['explanation_fields'] = self.explanation_fields
        if hasattr(self, 'explanation_values') and self.explanation_values is not None:
            _dict['explanation_values'] = self.explanation_values
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this GetExplanationTasksResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'GetExplanationTasksResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'GetExplanationTasksResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class InputDataReference():
    """
    InputDataReference is the same as TrainingDataReference except that neither location
    nor connection is required. This is needed for the Schemas API and to avoid updating
    existing APIs.

    :attr str type: Type of the storage.
    :attr TrainingDataReferenceLocation location: (optional) training data set
          location.
    :attr TrainingDataReferenceConnection connection: (optional) training data set
          connection credentials.
    :attr str name: (optional)
    """

    def __init__(self,
                 type: str,
                 *,
                 location: 'TrainingDataReferenceLocation' = None,
                 connection: 'TrainingDataReferenceConnection' = None,
                 name: str = None) -> None:
        """
        Initialize a InputDataReference object.

        :param str type: Type of the storage.
        :param TrainingDataReferenceLocation location: (optional) training data set
               location.
        :param TrainingDataReferenceConnection connection: (optional) training data
               set connection credentials.
        :param str name: (optional)
        """
        self.type = type
        self.location = location
        self.connection = connection
        self.name = name

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'InputDataReference':
        """Initialize a InputDataReference object from a json dictionary."""
        args = {}
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in InputDataReference JSON')
        if 'location' in _dict:
            args['location'] = _dict.get('location')
        if 'connection' in _dict:
            args['connection'] = _dict.get('connection')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a InputDataReference object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'location') and self.location is not None:
            if isinstance(self.location, dict):
                _dict['location'] = self.location
            else:
                _dict['location'] = self.location.to_dict()
        if hasattr(self, 'connection') and self.connection is not None:
            if isinstance(self.connection, dict):
                _dict['connection'] = self.connection
            else:
                _dict['connection'] = self.connection.to_dict()
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this InputDataReference object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'InputDataReference') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'InputDataReference') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class TypeEnum(str, Enum):
        """
        Type of the storage.
        """
        DB2 = 'db2'
        COS = 'cos'
        DATASET = 'dataset'
        FILE_ASSET = 'file_asset'


class IntegratedSystem():
    """
    Integrated System definition.

    :attr str name: The name of the Integrated System.
    :attr str type:
    :attr str description: The description of the Integrated System.
    :attr dict credentials: The credentials for the Integrated System.
    :attr object connection: (optional) The additional connection information for
          the Integrated System.
    :attr List[str] group_ids: (optional) Access control list of group id of Cloud
          Pak for Data (Only available for open_pages type and OpenScale on Cloud Pak for
          Data >= 4.0.6 with ENABLE_GROUP_AUTH being true).
    :attr List[str] user_ids: (optional) Access control list of user id of Cloud Pak
          for Data (Only available for open_pages type and OpenScale on Cloud Pak for Data
          >= 4.0.6 with ENABLE_GROUP_AUTH being true).
    """

    def __init__(self,
                 name: str,
                 type: str,
                 description: str,
                 credentials: dict,
                 *,
                 connection: object = None,
                 group_ids: List[str] = None,
                 user_ids: List[str] = None) -> None:
        """
        Initialize a IntegratedSystem object.

        :param str name: The name of the Integrated System.
        :param str type:
        :param str description: The description of the Integrated System.
        :param dict credentials: The credentials for the Integrated System.
        :param object connection: (optional) The additional connection information
               for the Integrated System.
        :param List[str] group_ids: (optional) Access control list of group id of
               Cloud Pak for Data (Only available for open_pages type and OpenScale on
               Cloud Pak for Data >= 4.0.6 with ENABLE_GROUP_AUTH being true).
        :param List[str] user_ids: (optional) Access control list of user id of
               Cloud Pak for Data (Only available for open_pages type and OpenScale on
               Cloud Pak for Data >= 4.0.6 with ENABLE_GROUP_AUTH being true).
        """
        self.name = name
        self.type = type
        self.description = description
        self.credentials = credentials
        self.connection = connection
        self.group_ids = group_ids
        self.user_ids = user_ids

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'IntegratedSystem':
        """Initialize a IntegratedSystem object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        else:
            raise ValueError('Required property \'name\' not present in IntegratedSystem JSON')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in IntegratedSystem JSON')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        else:
            raise ValueError('Required property \'description\' not present in IntegratedSystem JSON')
        if 'credentials' in _dict:
            args['credentials'] = _dict.get('credentials')
        else:
            raise ValueError('Required property \'credentials\' not present in IntegratedSystem JSON')
        if 'connection' in _dict:
            args['connection'] = _dict.get('connection')
        if 'group_ids' in _dict:
            args['group_ids'] = _dict.get('group_ids')
        if 'user_ids' in _dict:
            args['user_ids'] = _dict.get('user_ids')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a IntegratedSystem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'credentials') and self.credentials is not None:
            _dict['credentials'] = self.credentials
        if hasattr(self, 'connection') and self.connection is not None:
            _dict['connection'] = self.connection
        if hasattr(self, 'group_ids') and self.group_ids is not None:
            _dict['group_ids'] = self.group_ids
        if hasattr(self, 'user_ids') and self.user_ids is not None:
            _dict['user_ids'] = self.user_ids
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this IntegratedSystem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'IntegratedSystem') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'IntegratedSystem') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class TypeEnum(str, Enum):
        """
        type.
        """
        OPEN_PAGES = 'open_pages'
        SLACK = 'slack'
        HIVE = 'hive'
        SPARK = 'spark'
        JDBC = 'jdbc'
        CUSTOM_METRICS_PROVIDER = 'custom_metrics_provider'
        WATSON_KNOWLEDGE_CATALOG = 'watson_knowledge_catalog'


class IntegratedSystemCollection():
    """
    IntegratedSystemCollection.

    :attr List[IntegratedSystemResponse] integrated_systems:
    """

    def __init__(self,
                 integrated_systems: List['IntegratedSystemResponse']) -> None:
        """
        Initialize a IntegratedSystemCollection object.

        :param List[IntegratedSystemResponse] integrated_systems:
        """
        self.integrated_systems = integrated_systems

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'IntegratedSystemCollection':
        """Initialize a IntegratedSystemCollection object from a json dictionary."""
        args = {}
        if 'integrated_systems' in _dict:
            args['integrated_systems'] = [IntegratedSystemResponse.from_dict(x) for x in _dict.get('integrated_systems')]
        else:
            raise ValueError('Required property \'integrated_systems\' not present in IntegratedSystemCollection JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a IntegratedSystemCollection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'integrated_systems') and self.integrated_systems is not None:
            _dict['integrated_systems'] = [x.to_dict() for x in self.integrated_systems]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this IntegratedSystemCollection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'IntegratedSystemCollection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'IntegratedSystemCollection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class IntegratedSystemReference():
    """
    Integrated System reference.

    :attr str integrated_system_id: id of the Integrated System.
    :attr str external_id: id of the resource in the Integrated System.
    :attr object parameters: (optional) Additional parameters.
    """

    def __init__(self,
                 integrated_system_id: str,
                 external_id: str,
                 *,
                 parameters: object = None) -> None:
        """
        Initialize a IntegratedSystemReference object.

        :param str integrated_system_id: id of the Integrated System.
        :param str external_id: id of the resource in the Integrated System.
        :param object parameters: (optional) Additional parameters.
        """
        self.integrated_system_id = integrated_system_id
        self.external_id = external_id
        self.parameters = parameters

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'IntegratedSystemReference':
        """Initialize a IntegratedSystemReference object from a json dictionary."""
        args = {}
        if 'integrated_system_id' in _dict:
            args['integrated_system_id'] = _dict.get('integrated_system_id')
        else:
            raise ValueError('Required property \'integrated_system_id\' not present in IntegratedSystemReference JSON')
        if 'external_id' in _dict:
            args['external_id'] = _dict.get('external_id')
        else:
            raise ValueError('Required property \'external_id\' not present in IntegratedSystemReference JSON')
        if 'parameters' in _dict:
            args['parameters'] = _dict.get('parameters')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a IntegratedSystemReference object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'integrated_system_id') and self.integrated_system_id is not None:
            _dict['integrated_system_id'] = self.integrated_system_id
        if hasattr(self, 'external_id') and self.external_id is not None:
            _dict['external_id'] = self.external_id
        if hasattr(self, 'parameters') and self.parameters is not None:
            _dict['parameters'] = self.parameters
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this IntegratedSystemReference object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'IntegratedSystemReference') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'IntegratedSystemReference') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class IntegratedSystemResponse():
    """
    IntegratedSystemResponse.

    :attr Metadata metadata: (optional)
    :attr IntegratedSystem entity: (optional) Integrated System definition.
    """

    def __init__(self,
                 *,
                 metadata: 'Metadata' = None,
                 entity: 'IntegratedSystem' = None) -> None:
        """
        Initialize a IntegratedSystemResponse object.

        :param Metadata metadata: (optional)
        :param IntegratedSystem entity: (optional) Integrated System definition.
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'IntegratedSystemResponse':
        """Initialize a IntegratedSystemResponse object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        if 'entity' in _dict:
            args['entity'] = IntegratedSystem.from_dict(_dict.get('entity'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a IntegratedSystemResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this IntegratedSystemResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'IntegratedSystemResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'IntegratedSystemResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class JsonPatchOperation():
    """
    This model represents an individual patch operation to be performed on a JSON
    document, as defined by RFC 6902.

    :attr str op: The operation to be performed.
    :attr str path: The JSON Pointer that identifies the field that is the target of
          the operation.
    :attr str from_: (optional) The JSON Pointer that identifies the field that is
          the source of the operation.
    :attr object value: (optional) The value to be used within the operation.
    """

    def __init__(self,
                 op: str,
                 path: str,
                 *,
                 from_: str = None,
                 value: object = None) -> None:
        """
        Initialize a JsonPatchOperation object.

        :param str op: The operation to be performed.
        :param str path: The JSON Pointer that identifies the field that is the
               target of the operation.
        :param str from_: (optional) The JSON Pointer that identifies the field
               that is the source of the operation.
        :param object value: (optional) The value to be used within the operation.
        """
        self.op = op
        self.path = path
        self.from_ = from_
        self.value = value

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'JsonPatchOperation':
        """Initialize a JsonPatchOperation object from a json dictionary."""
        args = {}
        if 'op' in _dict:
            args['op'] = _dict.get('op')
        else:
            raise ValueError('Required property \'op\' not present in JsonPatchOperation JSON')
        if 'path' in _dict:
            args['path'] = _dict.get('path')
        else:
            raise ValueError('Required property \'path\' not present in JsonPatchOperation JSON')
        if 'from' in _dict:
            args['from_'] = _dict.get('from')
        if 'value' in _dict:
            args['value'] = _dict.get('value')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a JsonPatchOperation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'op') and self.op is not None:
            _dict['op'] = self.op
        if hasattr(self, 'path') and self.path is not None:
            _dict['path'] = self.path
        if hasattr(self, 'from_') and self.from_ is not None:
            _dict['from'] = self.from_
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this JsonPatchOperation object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'JsonPatchOperation') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'JsonPatchOperation') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class OpEnum(str, Enum):
        """
        The operation to be performed.
        """
        ADD = 'add'
        REMOVE = 'remove'
        REPLACE = 'replace'
        MOVE = 'move'
        COPY = 'copy'
        TEST = 'test'


class LocationSchemaName():
    """
    LocationSchemaName.

    :attr str schema_name: (optional) Database schema name (for PostgreSQL default
          is a public schema).
    """

    def __init__(self,
                 *,
                 schema_name: str = None) -> None:
        """
        Initialize a LocationSchemaName object.

        :param str schema_name: (optional) Database schema name (for PostgreSQL
               default is a public schema).
        """
        self.schema_name = schema_name

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'LocationSchemaName':
        """Initialize a LocationSchemaName object from a json dictionary."""
        args = {}
        if 'schema_name' in _dict:
            args['schema_name'] = _dict.get('schema_name')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a LocationSchemaName object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'schema_name') and self.schema_name is not None:
            _dict['schema_name'] = self.schema_name
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this LocationSchemaName object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'LocationSchemaName') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'LocationSchemaName') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class LocationTableName():
    """
    LocationTableName.

    :attr str table_name: (optional) Database table name.
    """

    def __init__(self,
                 *,
                 table_name: str = None) -> None:
        """
        Initialize a LocationTableName object.

        :param str table_name: (optional) Database table name.
        """
        self.table_name = table_name

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'LocationTableName':
        """Initialize a LocationTableName object from a json dictionary."""
        args = {}
        if 'table_name' in _dict:
            args['table_name'] = _dict.get('table_name')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a LocationTableName object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'table_name') and self.table_name is not None:
            _dict['table_name'] = self.table_name
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this LocationTableName object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'LocationTableName') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'LocationTableName') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MLCredentials():
    """
    MLCredentials.

    """

    def __init__(self,
                 **kwargs) -> None:
        """
        Initialize a MLCredentials object.

        :param **kwargs: (optional) Any additional properties.
        """
        msg = "Cannot instantiate base class. Instead, instantiate one of the defined subclasses: {0}".format(
                  ", ".join(['SageMakerCredentials', 'AzureCredentials', 'CustomCredentials', 'WMLCredentialsCloud', 'WMLCredentialsCP4D', 'SPSSCredentials', 'UnknownCredentials']))
        raise Exception(msg)

class MeasurementEntity():
    """
    MeasurementEntity.

    :attr datetime timestamp:
    :attr str run_id: (optional) ID of the monitoring run which produced the
          measurement.
    :attr List[MonitorMeasurementValue] values: Metrics grouped for a single
          measurement.
    :attr int issue_count: Number of the metrics with issues, which exceeded limits.
    :attr str asset_revision: (optional) Revision number of the ML model or function
          used by the monitor.
    :attr Target target: (optional)
    :attr str monitor_instance_id: (optional)
    :attr str monitor_definition_id: (optional)
    """

    def __init__(self,
                 timestamp: datetime,
                 values: List['MonitorMeasurementValue'],
                 issue_count: int,
                 *,
                 run_id: str = None,
                 asset_revision: str = None,
                 target: 'Target' = None,
                 monitor_instance_id: str = None,
                 monitor_definition_id: str = None) -> None:
        """
        Initialize a MeasurementEntity object.

        :param datetime timestamp:
        :param List[MonitorMeasurementValue] values: Metrics grouped for a single
               measurement.
        :param int issue_count: Number of the metrics with issues, which exceeded
               limits.
        :param str run_id: (optional) ID of the monitoring run which produced the
               measurement.
        :param str asset_revision: (optional) Revision number of the ML model or
               function used by the monitor.
        :param Target target: (optional)
        :param str monitor_instance_id: (optional)
        :param str monitor_definition_id: (optional)
        """
        self.timestamp = timestamp
        self.run_id = run_id
        self.values = values
        self.issue_count = issue_count
        self.asset_revision = asset_revision
        self.target = target
        self.monitor_instance_id = monitor_instance_id
        self.monitor_definition_id = monitor_definition_id

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MeasurementEntity':
        """Initialize a MeasurementEntity object from a json dictionary."""
        args = {}
        if 'timestamp' in _dict:
            args['timestamp'] = string_to_datetime(_dict.get('timestamp'))
        else:
            raise ValueError('Required property \'timestamp\' not present in MeasurementEntity JSON')
        if 'run_id' in _dict:
            args['run_id'] = _dict.get('run_id')
        if 'values' in _dict:
            args['values'] = [MonitorMeasurementValue.from_dict(x) for x in _dict.get('values')]
        else:
            raise ValueError('Required property \'values\' not present in MeasurementEntity JSON')
        if 'issue_count' in _dict:
            args['issue_count'] = _dict.get('issue_count')
        else:
            raise ValueError('Required property \'issue_count\' not present in MeasurementEntity JSON')
        if 'asset_revision' in _dict:
            args['asset_revision'] = _dict.get('asset_revision')
        if 'target' in _dict:
            args['target'] = Target.from_dict(_dict.get('target'))
        if 'monitor_instance_id' in _dict:
            args['monitor_instance_id'] = _dict.get('monitor_instance_id')
        if 'monitor_definition_id' in _dict:
            args['monitor_definition_id'] = _dict.get('monitor_definition_id')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MeasurementEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'timestamp') and self.timestamp is not None:
            _dict['timestamp'] = datetime_to_string(self.timestamp)
        if hasattr(self, 'run_id') and self.run_id is not None:
            _dict['run_id'] = self.run_id
        if hasattr(self, 'values') and self.values is not None:
            _dict['values'] = [x.to_dict() for x in self.values]
        if hasattr(self, 'issue_count') and self.issue_count is not None:
            _dict['issue_count'] = self.issue_count
        if hasattr(self, 'asset_revision') and self.asset_revision is not None:
            _dict['asset_revision'] = self.asset_revision
        if hasattr(self, 'target') and self.target is not None:
            _dict['target'] = self.target.to_dict()
        if hasattr(self, 'monitor_instance_id') and self.monitor_instance_id is not None:
            _dict['monitor_instance_id'] = self.monitor_instance_id
        if hasattr(self, 'monitor_definition_id') and self.monitor_definition_id is not None:
            _dict['monitor_definition_id'] = self.monitor_definition_id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MeasurementEntity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MeasurementEntity') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MeasurementEntity') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MeasurementsResponseCollection():
    """
    MeasurementsResponseCollection.

    :attr List[MeasurementsResponseCollectionMeasurementsItem] measurements:
    """

    def __init__(self,
                 measurements: List['MeasurementsResponseCollectionMeasurementsItem']) -> None:
        """
        Initialize a MeasurementsResponseCollection object.

        :param List[MeasurementsResponseCollectionMeasurementsItem] measurements:
        """
        self.measurements = measurements

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MeasurementsResponseCollection':
        """Initialize a MeasurementsResponseCollection object from a json dictionary."""
        args = {}
        if 'measurements' in _dict:
            args['measurements'] = [MeasurementsResponseCollectionMeasurementsItem.from_dict(x) for x in _dict.get('measurements')]
        else:
            raise ValueError('Required property \'measurements\' not present in MeasurementsResponseCollection JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MeasurementsResponseCollection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'measurements') and self.measurements is not None:
            _dict['measurements'] = [x.to_dict() for x in self.measurements]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MeasurementsResponseCollection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MeasurementsResponseCollection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MeasurementsResponseCollection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MeasurementsResponseCollectionMeasurementsItem():
    """
    MeasurementsResponseCollectionMeasurementsItem.

    :attr Metadata metadata:
    :attr MeasurementEntity entity:
    """

    def __init__(self,
                 metadata: 'Metadata',
                 entity: 'MeasurementEntity') -> None:
        """
        Initialize a MeasurementsResponseCollectionMeasurementsItem object.

        :param Metadata metadata:
        :param MeasurementEntity entity:
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MeasurementsResponseCollectionMeasurementsItem':
        """Initialize a MeasurementsResponseCollectionMeasurementsItem object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in MeasurementsResponseCollectionMeasurementsItem JSON')
        if 'entity' in _dict:
            args['entity'] = MeasurementEntity.from_dict(_dict.get('entity'))
        else:
            raise ValueError('Required property \'entity\' not present in MeasurementsResponseCollectionMeasurementsItem JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MeasurementsResponseCollectionMeasurementsItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MeasurementsResponseCollectionMeasurementsItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MeasurementsResponseCollectionMeasurementsItem') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MeasurementsResponseCollectionMeasurementsItem') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class Metadata():
    """
    Metadata.

    :attr str id: The ID (typically a GUID) which uniquely identifies the resource.
    :attr str crn: (optional) Cloud Resource Name (CRN) uniquely identify IBM Cloud
          resource (https://console.bluemix.net/docs/overview/crn.html).
    :attr str url: The URL which can be used to uniquely refer to the resource
          Typically a GET on this url would return details of the resource, a DELETE would
          delete it and a PUT/PATCH would update it.
    :attr datetime created_at: (optional) The timestamp when the resource was first
          created In format YYYY-MM-DDTHH:mm:ssZ or YYYY-MM-DDTHH:mm:ss.sssZ, matching the
          date-time format as specified by RFC 3339.
    :attr str created_by: (optional) The IAM ID of the user who created the
          resource.
    :attr datetime modified_at: (optional) The timestamp when the resource was first
          created In format YYYY-MM-DDTHH:mm:ssZ or YYYY-MM-DDTHH:mm:ss.sssZ, matching the
          date-time format as specified by RFC 3339.
    :attr str modified_by: (optional) The IAM ID of the user who last modified the
          resource.
    """

    def __init__(self,
                 id: str,
                 url: str,
                 *,
                 crn: str = None,
                 created_at: datetime = None,
                 created_by: str = None,
                 modified_at: datetime = None,
                 modified_by: str = None) -> None:
        """
        Initialize a Metadata object.

        :param str id: The ID (typically a GUID) which uniquely identifies the
               resource.
        :param str url: The URL which can be used to uniquely refer to the resource
               Typically a GET on this url would return details of the resource, a DELETE
               would delete it and a PUT/PATCH would update it.
        :param str crn: (optional) Cloud Resource Name (CRN) uniquely identify IBM
               Cloud resource (https://console.bluemix.net/docs/overview/crn.html).
        :param datetime created_at: (optional) The timestamp when the resource was
               first created In format YYYY-MM-DDTHH:mm:ssZ or YYYY-MM-DDTHH:mm:ss.sssZ,
               matching the date-time format as specified by RFC 3339.
        :param str created_by: (optional) The IAM ID of the user who created the
               resource.
        :param datetime modified_at: (optional) The timestamp when the resource was
               first created In format YYYY-MM-DDTHH:mm:ssZ or YYYY-MM-DDTHH:mm:ss.sssZ,
               matching the date-time format as specified by RFC 3339.
        :param str modified_by: (optional) The IAM ID of the user who last modified
               the resource.
        """
        self.id = id
        self.crn = crn
        self.url = url
        self.created_at = created_at
        self.created_by = created_by
        self.modified_at = modified_at
        self.modified_by = modified_by

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Metadata':
        """Initialize a Metadata object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        else:
            raise ValueError('Required property \'id\' not present in Metadata JSON')
        if 'crn' in _dict:
            args['crn'] = _dict.get('crn')
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        else:
            raise ValueError('Required property \'url\' not present in Metadata JSON')
        if 'created_at' in _dict:
            args['created_at'] = string_to_datetime(_dict.get('created_at'))
        if 'created_by' in _dict:
            args['created_by'] = _dict.get('created_by')
        if 'modified_at' in _dict:
            args['modified_at'] = string_to_datetime(_dict.get('modified_at'))
        if 'modified_by' in _dict:
            args['modified_by'] = _dict.get('modified_by')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Metadata object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'crn') and self.crn is not None:
            _dict['crn'] = self.crn
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        if hasattr(self, 'created_at') and self.created_at is not None:
            _dict['created_at'] = datetime_to_string(self.created_at)
        if hasattr(self, 'created_by') and self.created_by is not None:
            _dict['created_by'] = self.created_by
        if hasattr(self, 'modified_at') and self.modified_at is not None:
            _dict['modified_at'] = datetime_to_string(self.modified_at)
        if hasattr(self, 'modified_by') and self.modified_by is not None:
            _dict['modified_by'] = self.modified_by
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Metadata object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Metadata') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Metadata') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MetricSpecificThresholdObject():
    """
    MetricSpecificThresholdObject.

    :attr str id:
    :attr float default: default value of threshold.
    :attr str recommendation: (optional)
    :attr List[ThresholdConditionObject] applies_to:
    """

    def __init__(self,
                 id: str,
                 default: float,
                 applies_to: List['ThresholdConditionObject'],
                 *,
                 recommendation: str = None) -> None:
        """
        Initialize a MetricSpecificThresholdObject object.

        :param str id:
        :param float default: default value of threshold.
        :param List[ThresholdConditionObject] applies_to:
        :param str recommendation: (optional)
        """
        self.id = id
        self.default = default
        self.recommendation = recommendation
        self.applies_to = applies_to

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MetricSpecificThresholdObject':
        """Initialize a MetricSpecificThresholdObject object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        else:
            raise ValueError('Required property \'id\' not present in MetricSpecificThresholdObject JSON')
        if 'default' in _dict:
            args['default'] = _dict.get('default')
        else:
            raise ValueError('Required property \'default\' not present in MetricSpecificThresholdObject JSON')
        if 'recommendation' in _dict:
            args['recommendation'] = _dict.get('recommendation')
        if 'applies_to' in _dict:
            args['applies_to'] = [ThresholdConditionObject.from_dict(x) for x in _dict.get('applies_to')]
        else:
            raise ValueError('Required property \'applies_to\' not present in MetricSpecificThresholdObject JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MetricSpecificThresholdObject object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'default') and self.default is not None:
            _dict['default'] = self.default
        if hasattr(self, 'recommendation') and self.recommendation is not None:
            _dict['recommendation'] = self.recommendation
        if hasattr(self, 'applies_to') and self.applies_to is not None:
            _dict['applies_to'] = [x.to_dict() for x in self.applies_to]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MetricSpecificThresholdObject object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MetricSpecificThresholdObject') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MetricSpecificThresholdObject') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MetricSpecificThresholdShortObject():
    """
    MetricSpecificThresholdShortObject.

    :attr float value: value of threshold.
    :attr List[ThresholdConditionObject] applies_to:
    """

    def __init__(self,
                 value: float,
                 applies_to: List['ThresholdConditionObject']) -> None:
        """
        Initialize a MetricSpecificThresholdShortObject object.

        :param float value: value of threshold.
        :param List[ThresholdConditionObject] applies_to:
        """
        self.value = value
        self.applies_to = applies_to

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MetricSpecificThresholdShortObject':
        """Initialize a MetricSpecificThresholdShortObject object from a json dictionary."""
        args = {}
        if 'value' in _dict:
            args['value'] = _dict.get('value')
        else:
            raise ValueError('Required property \'value\' not present in MetricSpecificThresholdShortObject JSON')
        if 'applies_to' in _dict:
            args['applies_to'] = [ThresholdConditionObject.from_dict(x) for x in _dict.get('applies_to')]
        else:
            raise ValueError('Required property \'applies_to\' not present in MetricSpecificThresholdShortObject JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MetricSpecificThresholdShortObject object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        if hasattr(self, 'applies_to') and self.applies_to is not None:
            _dict['applies_to'] = [x.to_dict() for x in self.applies_to]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MetricSpecificThresholdShortObject object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MetricSpecificThresholdShortObject') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MetricSpecificThresholdShortObject') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MetricThreshold():
    """
    MetricThreshold.

    :attr str type:
    :attr float default: (optional) default value of threshold.
    :attr str default_recommendation: (optional)
    :attr List[MetricSpecificThresholdObject] specific_values: (optional)
    """

    def __init__(self,
                 type: str,
                 *,
                 default: float = None,
                 default_recommendation: str = None,
                 specific_values: List['MetricSpecificThresholdObject'] = None) -> None:
        """
        Initialize a MetricThreshold object.

        :param str type:
        :param float default: (optional) default value of threshold.
        :param str default_recommendation: (optional)
        :param List[MetricSpecificThresholdObject] specific_values: (optional)
        """
        self.type = type
        self.default = default
        self.default_recommendation = default_recommendation
        self.specific_values = specific_values

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MetricThreshold':
        """Initialize a MetricThreshold object from a json dictionary."""
        args = {}
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in MetricThreshold JSON')
        if 'default' in _dict:
            args['default'] = _dict.get('default')
        if 'default_recommendation' in _dict:
            args['default_recommendation'] = _dict.get('default_recommendation')
        if 'specific_values' in _dict:
            args['specific_values'] = [MetricSpecificThresholdObject.from_dict(x) for x in _dict.get('specific_values')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MetricThreshold object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'default') and self.default is not None:
            _dict['default'] = self.default
        if hasattr(self, 'default_recommendation') and self.default_recommendation is not None:
            _dict['default_recommendation'] = self.default_recommendation
        if hasattr(self, 'specific_values') and self.specific_values is not None:
            _dict['specific_values'] = [x.to_dict() for x in self.specific_values]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MetricThreshold object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MetricThreshold') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MetricThreshold') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class TypeEnum(str, Enum):
        """
        type.
        """
        LOWER_LIMIT = 'lower_limit'
        UPPER_LIMIT = 'upper_limit'


class MetricThresholdOverride():
    """
    MetricThresholdOverride.

    :attr str metric_id:
    :attr str type:
    :attr float value: (optional) value of the threshold.
    :attr List[MetricSpecificThresholdShortObject] specific_values: (optional)
    """

    def __init__(self,
                 metric_id: str,
                 type: str,
                 *,
                 value: float = None,
                 specific_values: List['MetricSpecificThresholdShortObject'] = None) -> None:
        """
        Initialize a MetricThresholdOverride object.

        :param str metric_id:
        :param str type:
        :param float value: (optional) value of the threshold.
        :param List[MetricSpecificThresholdShortObject] specific_values: (optional)
        """
        self.metric_id = metric_id
        self.type = type
        self.value = value
        self.specific_values = specific_values

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MetricThresholdOverride':
        """Initialize a MetricThresholdOverride object from a json dictionary."""
        args = {}
        if 'metric_id' in _dict:
            args['metric_id'] = _dict.get('metric_id')
        else:
            raise ValueError('Required property \'metric_id\' not present in MetricThresholdOverride JSON')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in MetricThresholdOverride JSON')
        if 'value' in _dict:
            args['value'] = _dict.get('value')
        if 'specific_values' in _dict:
            args['specific_values'] = [MetricSpecificThresholdShortObject.from_dict(x) for x in _dict.get('specific_values')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MetricThresholdOverride object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metric_id') and self.metric_id is not None:
            _dict['metric_id'] = self.metric_id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        if hasattr(self, 'specific_values') and self.specific_values is not None:
            _dict['specific_values'] = [x.to_dict() for x in self.specific_values]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MetricThresholdOverride object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MetricThresholdOverride') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MetricThresholdOverride') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class TypeEnum(str, Enum):
        """
        type.
        """
        LOWER_LIMIT = 'lower_limit'
        UPPER_LIMIT = 'upper_limit'


class Monitor():
    """
    Monitor.

    :attr str name: Monitor UI label (must be unique).
    :attr str description: (optional) Long monitoring description presented in
          monitoring catalog.
    :attr List[MonitorMetric] metrics: A list of metric definition.
    :attr List[MonitorTag] tags: Available tags.
    :attr dict parameters_schema: (optional) JSON schema that will be used to
          validate monitoring parameters when enabled.
    :attr dict dictionary: (optional) translated resources.
    :attr ApplicabilitySelection applies_to: (optional)
    :attr str managed_by: (optional)
    :attr MonitorInstanceSchedule schedule: (optional) The schedule used to control
          how frequently the target is monitored. The maximum frequency is once every 30
          minutes.
          Defaults to once every hour if not specified.
    :attr MonitorInstanceScheduleCollection schedules: (optional) A set of schedules
          used to control how frequently the target is monitored for online and batch
          deployment type.
    :attr MonitorRuntime monitor_runtime: (optional)
    """

    def __init__(self,
                 name: str,
                 metrics: List['MonitorMetric'],
                 tags: List['MonitorTag'],
                 *,
                 description: str = None,
                 parameters_schema: dict = None,
                 dictionary: dict = None,
                 applies_to: 'ApplicabilitySelection' = None,
                 managed_by: str = None,
                 schedule: 'MonitorInstanceSchedule' = None,
                 schedules: 'MonitorInstanceScheduleCollection' = None,
                 monitor_runtime: 'MonitorRuntime' = None) -> None:
        """
        Initialize a Monitor object.

        :param str name: Monitor UI label (must be unique).
        :param List[MonitorMetric] metrics: A list of metric definition.
        :param List[MonitorTag] tags: Available tags.
        :param str description: (optional) Long monitoring description presented in
               monitoring catalog.
        :param dict parameters_schema: (optional) JSON schema that will be used to
               validate monitoring parameters when enabled.
        :param dict dictionary: (optional) translated resources.
        :param ApplicabilitySelection applies_to: (optional)
        :param str managed_by: (optional)
        :param MonitorInstanceSchedule schedule: (optional) The schedule used to
               control how frequently the target is monitored. The maximum frequency is
               once every 30 minutes.
               Defaults to once every hour if not specified.
        :param MonitorInstanceScheduleCollection schedules: (optional) A set of
               schedules used to control how frequently the target is monitored for online
               and batch deployment type.
        :param MonitorRuntime monitor_runtime: (optional)
        """
        self.name = name
        self.description = description
        self.metrics = metrics
        self.tags = tags
        self.parameters_schema = parameters_schema
        self.dictionary = dictionary
        self.applies_to = applies_to
        self.managed_by = managed_by
        self.schedule = schedule
        self.schedules = schedules
        self.monitor_runtime = monitor_runtime

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Monitor':
        """Initialize a Monitor object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        else:
            raise ValueError('Required property \'name\' not present in Monitor JSON')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'metrics' in _dict:
            args['metrics'] = [MonitorMetric.from_dict(x) for x in _dict.get('metrics')]
        else:
            raise ValueError('Required property \'metrics\' not present in Monitor JSON')
        if 'tags' in _dict:
            args['tags'] = [MonitorTag.from_dict(x) for x in _dict.get('tags')]
        else:
            raise ValueError('Required property \'tags\' not present in Monitor JSON')
        if 'parameters_schema' in _dict:
            args['parameters_schema'] = _dict.get('parameters_schema')
        if 'dictionary' in _dict:
            args['dictionary'] = _dict.get('dictionary')
        if 'applies_to' in _dict:
            args['applies_to'] = ApplicabilitySelection.from_dict(_dict.get('applies_to'))
        if 'managed_by' in _dict:
            args['managed_by'] = _dict.get('managed_by')
        if 'schedule' in _dict:
            args['schedule'] = MonitorInstanceSchedule.from_dict(_dict.get('schedule'))
        if 'schedules' in _dict:
            args['schedules'] = MonitorInstanceScheduleCollection.from_dict(_dict.get('schedules'))
        if 'monitor_runtime' in _dict:
            args['monitor_runtime'] = MonitorRuntime.from_dict(_dict.get('monitor_runtime'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Monitor object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'metrics') and self.metrics is not None:
            _dict['metrics'] = [x.to_dict() for x in self.metrics]
        if hasattr(self, 'tags') and self.tags is not None:
            _dict['tags'] = [x.to_dict() for x in self.tags]
        if hasattr(self, 'parameters_schema') and self.parameters_schema is not None:
            _dict['parameters_schema'] = self.parameters_schema
        if hasattr(self, 'dictionary') and self.dictionary is not None:
            _dict['dictionary'] = self.dictionary
        if hasattr(self, 'applies_to') and self.applies_to is not None:
            _dict['applies_to'] = self.applies_to.to_dict()
        if hasattr(self, 'managed_by') and self.managed_by is not None:
            _dict['managed_by'] = self.managed_by
        if hasattr(self, 'schedule') and self.schedule is not None:
            _dict['schedule'] = self.schedule.to_dict()
        if hasattr(self, 'schedules') and self.schedules is not None:
            _dict['schedules'] = self.schedules.to_dict()
        if hasattr(self, 'monitor_runtime') and self.monitor_runtime is not None:
            _dict['monitor_runtime'] = self.monitor_runtime.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Monitor object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Monitor') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Monitor') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorCollections():
    """
    MonitorCollections.

    :attr List[MonitorDisplayForm] monitor_definitions:
    """

    def __init__(self,
                 monitor_definitions: List['MonitorDisplayForm']) -> None:
        """
        Initialize a MonitorCollections object.

        :param List[MonitorDisplayForm] monitor_definitions:
        """
        self.monitor_definitions = monitor_definitions

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorCollections':
        """Initialize a MonitorCollections object from a json dictionary."""
        args = {}
        if 'monitor_definitions' in _dict:
            args['monitor_definitions'] = [MonitorDisplayForm.from_dict(x) for x in _dict.get('monitor_definitions')]
        else:
            raise ValueError('Required property \'monitor_definitions\' not present in MonitorCollections JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorCollections object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'monitor_definitions') and self.monitor_definitions is not None:
            _dict['monitor_definitions'] = [x.to_dict() for x in self.monitor_definitions]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorCollections object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorCollections') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorCollections') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorDisplayForm():
    """
    MonitorDisplayForm.

    :attr Metadata metadata:
    :attr Monitor entity:
    """

    def __init__(self,
                 metadata: 'Metadata',
                 entity: 'Monitor') -> None:
        """
        Initialize a MonitorDisplayForm object.

        :param Metadata metadata:
        :param Monitor entity:
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorDisplayForm':
        """Initialize a MonitorDisplayForm object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in MonitorDisplayForm JSON')
        if 'entity' in _dict:
            args['entity'] = Monitor.from_dict(_dict.get('entity'))
        else:
            raise ValueError('Required property \'entity\' not present in MonitorDisplayForm JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorDisplayForm object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorDisplayForm object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorDisplayForm') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorDisplayForm') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorInstanceCollection():
    """
    MonitorInstanceCollection.

    :attr List[MonitorInstanceResponse] monitor_instances:
    """

    def __init__(self,
                 monitor_instances: List['MonitorInstanceResponse']) -> None:
        """
        Initialize a MonitorInstanceCollection object.

        :param List[MonitorInstanceResponse] monitor_instances:
        """
        self.monitor_instances = monitor_instances

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorInstanceCollection':
        """Initialize a MonitorInstanceCollection object from a json dictionary."""
        args = {}
        if 'monitor_instances' in _dict:
            args['monitor_instances'] = [MonitorInstanceResponse.from_dict(x) for x in _dict.get('monitor_instances')]
        else:
            raise ValueError('Required property \'monitor_instances\' not present in MonitorInstanceCollection JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorInstanceCollection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'monitor_instances') and self.monitor_instances is not None:
            _dict['monitor_instances'] = [x.to_dict() for x in self.monitor_instances]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorInstanceCollection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorInstanceCollection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorInstanceCollection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorInstanceResponse():
    """
    MonitorInstanceResponse.

    :attr Metadata metadata: (optional)
    :attr MonitorInstanceResponseEntity entity: (optional)
    """

    def __init__(self,
                 *,
                 metadata: 'Metadata' = None,
                 entity: 'MonitorInstanceResponseEntity' = None) -> None:
        """
        Initialize a MonitorInstanceResponse object.

        :param Metadata metadata: (optional)
        :param MonitorInstanceResponseEntity entity: (optional)
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorInstanceResponse':
        """Initialize a MonitorInstanceResponse object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        if 'entity' in _dict:
            args['entity'] = MonitorInstanceResponseEntity.from_dict(_dict.get('entity'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorInstanceResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorInstanceResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorInstanceResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorInstanceResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorInstanceResponseEntity():
    """
    MonitorInstanceResponseEntity.

    :attr str data_mart_id:
    :attr str monitor_definition_id:
    :attr Target target:
    :attr dict parameters: (optional) Monitoring parameters consistent with the
          `parameters_schema` from the monitor definition.
    :attr List[MetricThresholdOverride] thresholds: (optional)
    :attr MonitorInstanceSchedule schedule: (optional) The schedule used to control
          how frequently the target is monitored. The maximum frequency is once every 30
          minutes.
          Defaults to once every hour if not specified.
    :attr MonitorInstanceScheduleCollection schedules: (optional) A set of schedules
          used to control how frequently the target is monitored for online and batch
          deployment type.
    :attr str schedule_id: (optional)
    :attr str managed_by: (optional)
    :attr RecordsCountSummary unprocessed_records: (optional) Summary about records
          count.
    :attr RecordsCountSummary total_records: (optional) Summary about records count.
    :attr MonitorInstanceResponseEntityStatus status:
    """

    def __init__(self,
                 data_mart_id: str,
                 monitor_definition_id: str,
                 target: 'Target',
                 status: 'MonitorInstanceResponseEntityStatus',
                 *,
                 parameters: dict = None,
                 thresholds: List['MetricThresholdOverride'] = None,
                 schedule: 'MonitorInstanceSchedule' = None,
                 schedules: 'MonitorInstanceScheduleCollection' = None,
                 schedule_id: str = None,
                 managed_by: str = None,
                 unprocessed_records: 'RecordsCountSummary' = None,
                 total_records: 'RecordsCountSummary' = None) -> None:
        """
        Initialize a MonitorInstanceResponseEntity object.

        :param str data_mart_id:
        :param str monitor_definition_id:
        :param Target target:
        :param MonitorInstanceResponseEntityStatus status:
        :param dict parameters: (optional) Monitoring parameters consistent with
               the `parameters_schema` from the monitor definition.
        :param List[MetricThresholdOverride] thresholds: (optional)
        :param MonitorInstanceSchedule schedule: (optional) The schedule used to
               control how frequently the target is monitored. The maximum frequency is
               once every 30 minutes.
               Defaults to once every hour if not specified.
        :param MonitorInstanceScheduleCollection schedules: (optional) A set of
               schedules used to control how frequently the target is monitored for online
               and batch deployment type.
        :param str schedule_id: (optional)
        :param str managed_by: (optional)
        :param RecordsCountSummary unprocessed_records: (optional) Summary about
               records count.
        :param RecordsCountSummary total_records: (optional) Summary about records
               count.
        """
        self.data_mart_id = data_mart_id
        self.monitor_definition_id = monitor_definition_id
        self.target = target
        self.parameters = parameters
        self.thresholds = thresholds
        self.schedule = schedule
        self.schedules = schedules
        self.schedule_id = schedule_id
        self.managed_by = managed_by
        self.unprocessed_records = unprocessed_records
        self.total_records = total_records
        self.status = status

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorInstanceResponseEntity':
        """Initialize a MonitorInstanceResponseEntity object from a json dictionary."""
        args = {}
        if 'data_mart_id' in _dict:
            args['data_mart_id'] = _dict.get('data_mart_id')
        else:
            raise ValueError('Required property \'data_mart_id\' not present in MonitorInstanceResponseEntity JSON')
        if 'monitor_definition_id' in _dict:
            args['monitor_definition_id'] = _dict.get('monitor_definition_id')
        else:
            raise ValueError('Required property \'monitor_definition_id\' not present in MonitorInstanceResponseEntity JSON')
        if 'target' in _dict:
            args['target'] = Target.from_dict(_dict.get('target'))
        else:
            raise ValueError('Required property \'target\' not present in MonitorInstanceResponseEntity JSON')
        if 'parameters' in _dict:
            args['parameters'] = _dict.get('parameters')
        if 'thresholds' in _dict:
            args['thresholds'] = [MetricThresholdOverride.from_dict(x) for x in _dict.get('thresholds')]
        if 'schedule' in _dict:
            args['schedule'] = MonitorInstanceSchedule.from_dict(_dict.get('schedule'))
        if 'schedules' in _dict:
            args['schedules'] = MonitorInstanceScheduleCollection.from_dict(_dict.get('schedules'))
        if 'schedule_id' in _dict:
            args['schedule_id'] = _dict.get('schedule_id')
        if 'managed_by' in _dict:
            args['managed_by'] = _dict.get('managed_by')
        if 'unprocessed_records' in _dict:
            args['unprocessed_records'] = RecordsCountSummary.from_dict(_dict.get('unprocessed_records'))
        if 'total_records' in _dict:
            args['total_records'] = RecordsCountSummary.from_dict(_dict.get('total_records'))
        if 'status' in _dict:
            args['status'] = MonitorInstanceResponseEntityStatus.from_dict(_dict.get('status'))
        else:
            raise ValueError('Required property \'status\' not present in MonitorInstanceResponseEntity JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorInstanceResponseEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'data_mart_id') and self.data_mart_id is not None:
            _dict['data_mart_id'] = self.data_mart_id
        if hasattr(self, 'monitor_definition_id') and self.monitor_definition_id is not None:
            _dict['monitor_definition_id'] = self.monitor_definition_id
        if hasattr(self, 'target') and self.target is not None:
            _dict['target'] = self.target.to_dict()
        if hasattr(self, 'parameters') and self.parameters is not None:
            _dict['parameters'] = self.parameters
        if hasattr(self, 'thresholds') and self.thresholds is not None:
            _dict['thresholds'] = [x.to_dict() for x in self.thresholds]
        if hasattr(self, 'schedule') and self.schedule is not None:
            _dict['schedule'] = self.schedule.to_dict()
        if hasattr(self, 'schedules') and self.schedules is not None:
            _dict['schedules'] = self.schedules.to_dict()
        if hasattr(self, 'schedule_id') and self.schedule_id is not None:
            _dict['schedule_id'] = self.schedule_id
        if hasattr(self, 'managed_by') and self.managed_by is not None:
            _dict['managed_by'] = self.managed_by
        if hasattr(self, 'unprocessed_records') and self.unprocessed_records is not None:
            _dict['unprocessed_records'] = self.unprocessed_records.to_dict()
        if hasattr(self, 'total_records') and self.total_records is not None:
            _dict['total_records'] = self.total_records.to_dict()
        if hasattr(self, 'status') and self.status is not None:
            _dict['status'] = self.status.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorInstanceResponseEntity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorInstanceResponseEntity') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorInstanceResponseEntity') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorInstanceResponseEntityStatus():
    """
    MonitorInstanceResponseEntityStatus.

    :attr str state:
    :attr GenericErrorResponse failure: (optional)
    :attr MonitorInstanceResponseEntityStatusActivityStatus activity_status:
          (optional)
    """

    def __init__(self,
                 state: str,
                 *,
                 failure: 'GenericErrorResponse' = None,
                 activity_status: 'MonitorInstanceResponseEntityStatusActivityStatus' = None) -> None:
        """
        Initialize a MonitorInstanceResponseEntityStatus object.

        :param str state:
        :param GenericErrorResponse failure: (optional)
        :param MonitorInstanceResponseEntityStatusActivityStatus activity_status:
               (optional)
        """
        self.state = state
        self.failure = failure
        self.activity_status = activity_status

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorInstanceResponseEntityStatus':
        """Initialize a MonitorInstanceResponseEntityStatus object from a json dictionary."""
        args = {}
        if 'state' in _dict:
            args['state'] = _dict.get('state')
        else:
            raise ValueError('Required property \'state\' not present in MonitorInstanceResponseEntityStatus JSON')
        if 'failure' in _dict:
            args['failure'] = GenericErrorResponse.from_dict(_dict.get('failure'))
        if 'activity_status' in _dict:
            args['activity_status'] = MonitorInstanceResponseEntityStatusActivityStatus.from_dict(_dict.get('activity_status'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorInstanceResponseEntityStatus object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'state') and self.state is not None:
            _dict['state'] = self.state
        if hasattr(self, 'failure') and self.failure is not None:
            _dict['failure'] = self.failure.to_dict()
        if hasattr(self, 'activity_status') and self.activity_status is not None:
            _dict['activity_status'] = self.activity_status.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorInstanceResponseEntityStatus object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorInstanceResponseEntityStatus') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorInstanceResponseEntityStatus') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class StateEnum(str, Enum):
        """
        state.
        """
        PREPARING = 'preparing'
        ACTIVE = 'active'
        FAILED = 'failed'
        DELETING = 'deleting'
        PENDING_DELETE = 'pending_delete'


class MonitorInstanceResponseEntityStatusActivityStatus():
    """
    MonitorInstanceResponseEntityStatusActivityStatus.

    :attr str id: (optional)
    :attr str url: (optional)
    """

    def __init__(self,
                 *,
                 id: str = None,
                 url: str = None) -> None:
        """
        Initialize a MonitorInstanceResponseEntityStatusActivityStatus object.

        :param str id: (optional)
        :param str url: (optional)
        """
        self.id = id
        self.url = url

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorInstanceResponseEntityStatusActivityStatus':
        """Initialize a MonitorInstanceResponseEntityStatusActivityStatus object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorInstanceResponseEntityStatusActivityStatus object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorInstanceResponseEntityStatusActivityStatus object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorInstanceResponseEntityStatusActivityStatus') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorInstanceResponseEntityStatusActivityStatus') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorInstanceSchedule():
    """
    The schedule used to control how frequently the target is monitored. The maximum
    frequency is once every 30 minutes. Defaults to once every hour if not specified.

    :attr int repeat_interval: The interval to monitor the target.
    :attr str repeat_unit: The type of interval to monitor the target.
    :attr ScheduleStartTime start_time: (optional) Defintion of first run time for
          scheduled activity; either absolute or relative the the moment of activation.
    :attr str repeat_type: (optional) The type of interval to monitor the target.
    """

    def __init__(self,
                 repeat_interval: int,
                 repeat_unit: str,
                 *,
                 start_time: 'ScheduleStartTime' = None,
                 repeat_type: str = None) -> None:
        """
        Initialize a MonitorInstanceSchedule object.

        :param int repeat_interval: The interval to monitor the target.
        :param str repeat_unit: The type of interval to monitor the target.
        :param ScheduleStartTime start_time: (optional) Defintion of first run time
               for scheduled activity; either absolute or relative the the moment of
               activation.
        :param str repeat_type: (optional) The type of interval to monitor the
               target.
        """
        self.repeat_interval = repeat_interval
        self.repeat_unit = repeat_unit
        self.start_time = start_time
        self.repeat_type = repeat_type

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorInstanceSchedule':
        """Initialize a MonitorInstanceSchedule object from a json dictionary."""
        args = {}
        if 'repeat_interval' in _dict:
            args['repeat_interval'] = _dict.get('repeat_interval')
        else:
            raise ValueError('Required property \'repeat_interval\' not present in MonitorInstanceSchedule JSON')
        if 'repeat_unit' in _dict:
            args['repeat_unit'] = _dict.get('repeat_unit')
        else:
            raise ValueError('Required property \'repeat_unit\' not present in MonitorInstanceSchedule JSON')
        if 'start_time' in _dict:
            args['start_time'] = ScheduleStartTime.from_dict(_dict.get('start_time'))
        if 'repeat_type' in _dict:
            args['repeat_type'] = _dict.get('repeat_type')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorInstanceSchedule object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'repeat_interval') and self.repeat_interval is not None:
            _dict['repeat_interval'] = self.repeat_interval
        if hasattr(self, 'repeat_unit') and self.repeat_unit is not None:
            _dict['repeat_unit'] = self.repeat_unit
        if hasattr(self, 'start_time') and self.start_time is not None:
            _dict['start_time'] = self.start_time.to_dict()
        if hasattr(self, 'repeat_type') and self.repeat_type is not None:
            _dict['repeat_type'] = self.repeat_type
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorInstanceSchedule object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorInstanceSchedule') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorInstanceSchedule') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class RepeatUnitEnum(str, Enum):
        """
        The type of interval to monitor the target.
        """
        MINUTE = 'minute'
        HOUR = 'hour'
        DAY = 'day'
        WEEK = 'week'
        MONTH = 'month'
        YEAR = 'year'


class MonitorInstanceScheduleCollection():
    """
    A set of schedules used to control how frequently the target is monitored for online
    and batch deployment type.

    :attr MonitorInstanceSchedule online: (optional) The schedule used to control
          how frequently the target is monitored. The maximum frequency is once every 30
          minutes.
          Defaults to once every hour if not specified.
    :attr MonitorInstanceSchedule batch: (optional) The schedule used to control how
          frequently the target is monitored. The maximum frequency is once every 30
          minutes.
          Defaults to once every hour if not specified.
    """

    def __init__(self,
                 *,
                 online: 'MonitorInstanceSchedule' = None,
                 batch: 'MonitorInstanceSchedule' = None) -> None:
        """
        Initialize a MonitorInstanceScheduleCollection object.

        :param MonitorInstanceSchedule online: (optional) The schedule used to
               control how frequently the target is monitored. The maximum frequency is
               once every 30 minutes.
               Defaults to once every hour if not specified.
        :param MonitorInstanceSchedule batch: (optional) The schedule used to
               control how frequently the target is monitored. The maximum frequency is
               once every 30 minutes.
               Defaults to once every hour if not specified.
        """
        self.online = online
        self.batch = batch

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorInstanceScheduleCollection':
        """Initialize a MonitorInstanceScheduleCollection object from a json dictionary."""
        args = {}
        if 'online' in _dict:
            args['online'] = MonitorInstanceSchedule.from_dict(_dict.get('online'))
        if 'batch' in _dict:
            args['batch'] = MonitorInstanceSchedule.from_dict(_dict.get('batch'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorInstanceScheduleCollection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'online') and self.online is not None:
            _dict['online'] = self.online.to_dict()
        if hasattr(self, 'batch') and self.batch is not None:
            _dict['batch'] = self.batch.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorInstanceScheduleCollection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorInstanceScheduleCollection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorInstanceScheduleCollection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorMeasurementMetric():
    """
    Value and limits for the metrics.

    :attr str id:
    :attr float value:
    :attr float lower_limit: (optional)
    :attr float upper_limit: (optional)
    """

    def __init__(self,
                 id: str,
                 value: float,
                 *,
                 lower_limit: float = None,
                 upper_limit: float = None) -> None:
        """
        Initialize a MonitorMeasurementMetric object.

        :param str id:
        :param float value:
        :param float lower_limit: (optional)
        :param float upper_limit: (optional)
        """
        self.id = id
        self.value = value
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorMeasurementMetric':
        """Initialize a MonitorMeasurementMetric object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        else:
            raise ValueError('Required property \'id\' not present in MonitorMeasurementMetric JSON')
        if 'value' in _dict:
            args['value'] = _dict.get('value')
        else:
            raise ValueError('Required property \'value\' not present in MonitorMeasurementMetric JSON')
        if 'lower_limit' in _dict:
            args['lower_limit'] = _dict.get('lower_limit')
        if 'upper_limit' in _dict:
            args['upper_limit'] = _dict.get('upper_limit')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorMeasurementMetric object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        if hasattr(self, 'lower_limit') and self.lower_limit is not None:
            _dict['lower_limit'] = self.lower_limit
        if hasattr(self, 'upper_limit') and self.upper_limit is not None:
            _dict['upper_limit'] = self.upper_limit
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorMeasurementMetric object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorMeasurementMetric') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorMeasurementMetric') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorMeasurementRequest():
    """
    MonitorMeasurementRequest.

    :attr datetime timestamp:
    :attr str run_id: (optional) ID of the monitoring run which produced the
          measurement.
    :attr List[dict] metrics: Metrics grouped for a single measurement.
    :attr List[Source] sources: (optional) The sources of the metric.
    :attr str asset_revision: (optional) Revision number of the ML model or function
          used by the monitor.
    """

    def __init__(self,
                 timestamp: datetime,
                 metrics: List[dict],
                 *,
                 run_id: str = None,
                 sources: List['Source'] = None,
                 asset_revision: str = None) -> None:
        """
        Initialize a MonitorMeasurementRequest object.

        :param datetime timestamp:
        :param List[dict] metrics: Metrics grouped for a single measurement.
        :param str run_id: (optional) ID of the monitoring run which produced the
               measurement.
        :param List[Source] sources: (optional) The sources of the metric.
        :param str asset_revision: (optional) Revision number of the ML model or
               function used by the monitor.
        """
        self.timestamp = timestamp
        self.run_id = run_id
        self.metrics = metrics
        self.sources = sources
        self.asset_revision = asset_revision

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorMeasurementRequest':
        """Initialize a MonitorMeasurementRequest object from a json dictionary."""
        args = {}
        if 'timestamp' in _dict:
            args['timestamp'] = string_to_datetime(_dict.get('timestamp'))
        else:
            raise ValueError('Required property \'timestamp\' not present in MonitorMeasurementRequest JSON')
        if 'run_id' in _dict:
            args['run_id'] = _dict.get('run_id')
        if 'metrics' in _dict:
            args['metrics'] = _dict.get('metrics')
        else:
            raise ValueError('Required property \'metrics\' not present in MonitorMeasurementRequest JSON')
        if 'sources' in _dict:
            args['sources'] = [Source.from_dict(x) for x in _dict.get('sources')]
        if 'asset_revision' in _dict:
            args['asset_revision'] = _dict.get('asset_revision')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorMeasurementRequest object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'timestamp') and self.timestamp is not None:
            _dict['timestamp'] = datetime_to_string(self.timestamp)
        if hasattr(self, 'run_id') and self.run_id is not None:
            _dict['run_id'] = self.run_id
        if hasattr(self, 'metrics') and self.metrics is not None:
            _dict['metrics'] = self.metrics
        if hasattr(self, 'sources') and self.sources is not None:
            _dict['sources'] = [x.to_dict() for x in self.sources]
        if hasattr(self, 'asset_revision') and self.asset_revision is not None:
            _dict['asset_revision'] = self.asset_revision
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorMeasurementRequest object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorMeasurementRequest') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorMeasurementRequest') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorMeasurementResponse():
    """
    MonitorMeasurementResponse.

    :attr Metadata metadata:
    :attr MonitorMeasurementResponseEntity entity:
    """

    def __init__(self,
                 metadata: 'Metadata',
                 entity: 'MonitorMeasurementResponseEntity') -> None:
        """
        Initialize a MonitorMeasurementResponse object.

        :param Metadata metadata:
        :param MonitorMeasurementResponseEntity entity:
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorMeasurementResponse':
        """Initialize a MonitorMeasurementResponse object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in MonitorMeasurementResponse JSON')
        if 'entity' in _dict:
            args['entity'] = MonitorMeasurementResponseEntity.from_dict(_dict.get('entity'))
        else:
            raise ValueError('Required property \'entity\' not present in MonitorMeasurementResponse JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorMeasurementResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorMeasurementResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorMeasurementResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorMeasurementResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorMeasurementResponseCollection():
    """
    MonitorMeasurementResponseCollection.

    :attr datetime start: (optional) Beginning of the time range.
    :attr datetime end: (optional) End of the time range.
    :attr List[MonitorMeasurementResponseCollectionMeasurementsItem] measurements:
    """

    def __init__(self,
                 measurements: List['MonitorMeasurementResponseCollectionMeasurementsItem'],
                 *,
                 start: datetime = None,
                 end: datetime = None) -> None:
        """
        Initialize a MonitorMeasurementResponseCollection object.

        :param List[MonitorMeasurementResponseCollectionMeasurementsItem]
               measurements:
        :param datetime start: (optional) Beginning of the time range.
        :param datetime end: (optional) End of the time range.
        """
        self.start = start
        self.end = end
        self.measurements = measurements

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorMeasurementResponseCollection':
        """Initialize a MonitorMeasurementResponseCollection object from a json dictionary."""
        args = {}
        if 'start' in _dict:
            args['start'] = string_to_datetime(_dict.get('start'))
        if 'end' in _dict:
            args['end'] = string_to_datetime(_dict.get('end'))
        if 'measurements' in _dict:
            args['measurements'] = [MonitorMeasurementResponseCollectionMeasurementsItem.from_dict(x) for x in _dict.get('measurements')]
        else:
            raise ValueError('Required property \'measurements\' not present in MonitorMeasurementResponseCollection JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorMeasurementResponseCollection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'start') and self.start is not None:
            _dict['start'] = datetime_to_string(self.start)
        if hasattr(self, 'end') and self.end is not None:
            _dict['end'] = datetime_to_string(self.end)
        if hasattr(self, 'measurements') and self.measurements is not None:
            _dict['measurements'] = [x.to_dict() for x in self.measurements]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorMeasurementResponseCollection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorMeasurementResponseCollection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorMeasurementResponseCollection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorMeasurementResponseCollectionMeasurementsItem():
    """
    MonitorMeasurementResponseCollectionMeasurementsItem.

    :attr Metadata metadata:
    :attr MeasurementEntity entity:
    """

    def __init__(self,
                 metadata: 'Metadata',
                 entity: 'MeasurementEntity') -> None:
        """
        Initialize a MonitorMeasurementResponseCollectionMeasurementsItem object.

        :param Metadata metadata:
        :param MeasurementEntity entity:
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorMeasurementResponseCollectionMeasurementsItem':
        """Initialize a MonitorMeasurementResponseCollectionMeasurementsItem object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in MonitorMeasurementResponseCollectionMeasurementsItem JSON')
        if 'entity' in _dict:
            args['entity'] = MeasurementEntity.from_dict(_dict.get('entity'))
        else:
            raise ValueError('Required property \'entity\' not present in MonitorMeasurementResponseCollectionMeasurementsItem JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorMeasurementResponseCollectionMeasurementsItem object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorMeasurementResponseCollectionMeasurementsItem object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorMeasurementResponseCollectionMeasurementsItem') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorMeasurementResponseCollectionMeasurementsItem') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorMeasurementResponseEntity():
    """
    MonitorMeasurementResponseEntity.

    :attr datetime timestamp:
    :attr str run_id: (optional) ID of the monitoring run which produced the
          measurement.
    :attr List[MonitorMeasurementValue] values: Metrics grouped for a single
          measurement.
    :attr int issue_count: Number of the metrics with issues, which exceeded limits.
    :attr str asset_revision: (optional) Revision number of the ML model or function
          used by the monitor.
    :attr Target target: (optional)
    :attr str monitor_instance_id: (optional)
    :attr str monitor_definition_id: (optional)
    :attr List[Source] sources: (optional) The sources of the metric.
    """

    def __init__(self,
                 timestamp: datetime,
                 values: List['MonitorMeasurementValue'],
                 issue_count: int,
                 *,
                 run_id: str = None,
                 asset_revision: str = None,
                 target: 'Target' = None,
                 monitor_instance_id: str = None,
                 monitor_definition_id: str = None,
                 sources: List['Source'] = None) -> None:
        """
        Initialize a MonitorMeasurementResponseEntity object.

        :param datetime timestamp:
        :param List[MonitorMeasurementValue] values: Metrics grouped for a single
               measurement.
        :param int issue_count: Number of the metrics with issues, which exceeded
               limits.
        :param str run_id: (optional) ID of the monitoring run which produced the
               measurement.
        :param str asset_revision: (optional) Revision number of the ML model or
               function used by the monitor.
        :param Target target: (optional)
        :param str monitor_instance_id: (optional)
        :param str monitor_definition_id: (optional)
        :param List[Source] sources: (optional) The sources of the metric.
        """
        self.timestamp = timestamp
        self.run_id = run_id
        self.values = values
        self.issue_count = issue_count
        self.asset_revision = asset_revision
        self.target = target
        self.monitor_instance_id = monitor_instance_id
        self.monitor_definition_id = monitor_definition_id
        self.sources = sources

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorMeasurementResponseEntity':
        """Initialize a MonitorMeasurementResponseEntity object from a json dictionary."""
        args = {}
        if 'timestamp' in _dict:
            args['timestamp'] = string_to_datetime(_dict.get('timestamp'))
        else:
            raise ValueError('Required property \'timestamp\' not present in MonitorMeasurementResponseEntity JSON')
        if 'run_id' in _dict:
            args['run_id'] = _dict.get('run_id')
        if 'values' in _dict:
            args['values'] = [MonitorMeasurementValue.from_dict(x) for x in _dict.get('values')]
        else:
            raise ValueError('Required property \'values\' not present in MonitorMeasurementResponseEntity JSON')
        if 'issue_count' in _dict:
            args['issue_count'] = _dict.get('issue_count')
        else:
            raise ValueError('Required property \'issue_count\' not present in MonitorMeasurementResponseEntity JSON')
        if 'asset_revision' in _dict:
            args['asset_revision'] = _dict.get('asset_revision')
        if 'target' in _dict:
            args['target'] = Target.from_dict(_dict.get('target'))
        if 'monitor_instance_id' in _dict:
            args['monitor_instance_id'] = _dict.get('monitor_instance_id')
        if 'monitor_definition_id' in _dict:
            args['monitor_definition_id'] = _dict.get('monitor_definition_id')
        if 'sources' in _dict:
            args['sources'] = [Source.from_dict(x) for x in _dict.get('sources')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorMeasurementResponseEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'timestamp') and self.timestamp is not None:
            _dict['timestamp'] = datetime_to_string(self.timestamp)
        if hasattr(self, 'run_id') and self.run_id is not None:
            _dict['run_id'] = self.run_id
        if hasattr(self, 'values') and self.values is not None:
            _dict['values'] = [x.to_dict() for x in self.values]
        if hasattr(self, 'issue_count') and self.issue_count is not None:
            _dict['issue_count'] = self.issue_count
        if hasattr(self, 'asset_revision') and self.asset_revision is not None:
            _dict['asset_revision'] = self.asset_revision
        if hasattr(self, 'target') and self.target is not None:
            _dict['target'] = self.target.to_dict()
        if hasattr(self, 'monitor_instance_id') and self.monitor_instance_id is not None:
            _dict['monitor_instance_id'] = self.monitor_instance_id
        if hasattr(self, 'monitor_definition_id') and self.monitor_definition_id is not None:
            _dict['monitor_definition_id'] = self.monitor_definition_id
        if hasattr(self, 'sources') and self.sources is not None:
            _dict['sources'] = [x.to_dict() for x in self.sources]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorMeasurementResponseEntity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorMeasurementResponseEntity') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorMeasurementResponseEntity') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorMeasurementTag():
    """
    Tag related to the metrics.

    :attr str id:
    :attr str value:
    """

    def __init__(self,
                 id: str,
                 value: str) -> None:
        """
        Initialize a MonitorMeasurementTag object.

        :param str id:
        :param str value:
        """
        self.id = id
        self.value = value

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorMeasurementTag':
        """Initialize a MonitorMeasurementTag object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        else:
            raise ValueError('Required property \'id\' not present in MonitorMeasurementTag JSON')
        if 'value' in _dict:
            args['value'] = _dict.get('value')
        else:
            raise ValueError('Required property \'value\' not present in MonitorMeasurementTag JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorMeasurementTag object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorMeasurementTag object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorMeasurementTag') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorMeasurementTag') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorMeasurementValue():
    """
    Measurment metrics and tags.

    :attr List[MonitorMeasurementMetric] metrics: Metrics related to the
          measurement.
    :attr List[MonitorMeasurementTag] tags: Tags related to the measurement.
    """

    def __init__(self,
                 metrics: List['MonitorMeasurementMetric'],
                 tags: List['MonitorMeasurementTag']) -> None:
        """
        Initialize a MonitorMeasurementValue object.

        :param List[MonitorMeasurementMetric] metrics: Metrics related to the
               measurement.
        :param List[MonitorMeasurementTag] tags: Tags related to the measurement.
        """
        self.metrics = metrics
        self.tags = tags

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorMeasurementValue':
        """Initialize a MonitorMeasurementValue object from a json dictionary."""
        args = {}
        if 'metrics' in _dict:
            args['metrics'] = [MonitorMeasurementMetric.from_dict(x) for x in _dict.get('metrics')]
        else:
            raise ValueError('Required property \'metrics\' not present in MonitorMeasurementValue JSON')
        if 'tags' in _dict:
            args['tags'] = [MonitorMeasurementTag.from_dict(x) for x in _dict.get('tags')]
        else:
            raise ValueError('Required property \'tags\' not present in MonitorMeasurementValue JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorMeasurementValue object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metrics') and self.metrics is not None:
            _dict['metrics'] = [x.to_dict() for x in self.metrics]
        if hasattr(self, 'tags') and self.tags is not None:
            _dict['tags'] = [x.to_dict() for x in self.tags]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorMeasurementValue object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorMeasurementValue') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorMeasurementValue') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorMetric():
    """
    MonitorMetric.

    :attr str name: unique name used by UI instead of id (must be unique in scope of
          the monitor defition across both metrics and tags).
    :attr str description: (optional) Description of the metrics.
    :attr List[MetricThreshold] thresholds: (optional)
    :attr bool required: (optional)
    :attr ApplicabilitySelection applies_to: (optional)
    :attr str expected_direction: (optional) the indicator specifying the expected
          direction of the monotonic metric values.
    :attr str default_aggregation: (optional)
    :attr str id:
    """

    def __init__(self,
                 name: str,
                 id: str,
                 *,
                 description: str = None,
                 thresholds: List['MetricThreshold'] = None,
                 required: bool = None,
                 applies_to: 'ApplicabilitySelection' = None,
                 expected_direction: str = None,
                 default_aggregation: str = None) -> None:
        """
        Initialize a MonitorMetric object.

        :param str name: unique name used by UI instead of id (must be unique in
               scope of the monitor defition across both metrics and tags).
        :param str id:
        :param str description: (optional) Description of the metrics.
        :param List[MetricThreshold] thresholds: (optional)
        :param bool required: (optional)
        :param ApplicabilitySelection applies_to: (optional)
        :param str expected_direction: (optional) the indicator specifying the
               expected direction of the monotonic metric values.
        :param str default_aggregation: (optional)
        """
        self.name = name
        self.description = description
        self.thresholds = thresholds
        self.required = required
        self.applies_to = applies_to
        self.expected_direction = expected_direction
        self.default_aggregation = default_aggregation
        self.id = id

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorMetric':
        """Initialize a MonitorMetric object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        else:
            raise ValueError('Required property \'name\' not present in MonitorMetric JSON')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'thresholds' in _dict:
            args['thresholds'] = [MetricThreshold.from_dict(x) for x in _dict.get('thresholds')]
        if 'required' in _dict:
            args['required'] = _dict.get('required')
        if 'applies_to' in _dict:
            args['applies_to'] = ApplicabilitySelection.from_dict(_dict.get('applies_to'))
        if 'expected_direction' in _dict:
            args['expected_direction'] = _dict.get('expected_direction')
        if 'default_aggregation' in _dict:
            args['default_aggregation'] = _dict.get('default_aggregation')
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        else:
            raise ValueError('Required property \'id\' not present in MonitorMetric JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorMetric object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'thresholds') and self.thresholds is not None:
            _dict['thresholds'] = [x.to_dict() for x in self.thresholds]
        if hasattr(self, 'required') and self.required is not None:
            _dict['required'] = self.required
        if hasattr(self, 'applies_to') and self.applies_to is not None:
            _dict['applies_to'] = self.applies_to.to_dict()
        if hasattr(self, 'expected_direction') and self.expected_direction is not None:
            _dict['expected_direction'] = self.expected_direction
        if hasattr(self, 'default_aggregation') and self.default_aggregation is not None:
            _dict['default_aggregation'] = self.default_aggregation
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorMetric object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorMetric') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorMetric') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class ExpectedDirectionEnum(str, Enum):
        """
        the indicator specifying the expected direction of the monotonic metric values.
        """
        INCREASING = 'increasing'
        DECREASING = 'decreasing'
        UNKNOWN = 'unknown'


class MonitorMetricRequest():
    """
    MonitorMetricRequest.

    :attr str name: unique name used by UI instead of id (must be unique in scope of
          the monitor defition across both metrics and tags).
    :attr str description: (optional) Description of the metrics.
    :attr List[MetricThreshold] thresholds: (optional)
    :attr bool required: (optional)
    :attr ApplicabilitySelection applies_to: (optional)
    :attr str expected_direction: (optional) the indicator specifying the expected
          direction of the monotonic metric values.
    :attr str default_aggregation: (optional)
    """

    def __init__(self,
                 name: str,
                 *,
                 description: str = None,
                 thresholds: List['MetricThreshold'] = None,
                 required: bool = None,
                 applies_to: 'ApplicabilitySelection' = None,
                 expected_direction: str = None,
                 default_aggregation: str = None) -> None:
        """
        Initialize a MonitorMetricRequest object.

        :param str name: unique name used by UI instead of id (must be unique in
               scope of the monitor defition across both metrics and tags).
        :param str description: (optional) Description of the metrics.
        :param List[MetricThreshold] thresholds: (optional)
        :param bool required: (optional)
        :param ApplicabilitySelection applies_to: (optional)
        :param str expected_direction: (optional) the indicator specifying the
               expected direction of the monotonic metric values.
        :param str default_aggregation: (optional)
        """
        self.name = name
        self.description = description
        self.thresholds = thresholds
        self.required = required
        self.applies_to = applies_to
        self.expected_direction = expected_direction
        self.default_aggregation = default_aggregation

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorMetricRequest':
        """Initialize a MonitorMetricRequest object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        else:
            raise ValueError('Required property \'name\' not present in MonitorMetricRequest JSON')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'thresholds' in _dict:
            args['thresholds'] = [MetricThreshold.from_dict(x) for x in _dict.get('thresholds')]
        if 'required' in _dict:
            args['required'] = _dict.get('required')
        if 'applies_to' in _dict:
            args['applies_to'] = ApplicabilitySelection.from_dict(_dict.get('applies_to'))
        if 'expected_direction' in _dict:
            args['expected_direction'] = _dict.get('expected_direction')
        if 'default_aggregation' in _dict:
            args['default_aggregation'] = _dict.get('default_aggregation')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorMetricRequest object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'thresholds') and self.thresholds is not None:
            _dict['thresholds'] = [x.to_dict() for x in self.thresholds]
        if hasattr(self, 'required') and self.required is not None:
            _dict['required'] = self.required
        if hasattr(self, 'applies_to') and self.applies_to is not None:
            _dict['applies_to'] = self.applies_to.to_dict()
        if hasattr(self, 'expected_direction') and self.expected_direction is not None:
            _dict['expected_direction'] = self.expected_direction
        if hasattr(self, 'default_aggregation') and self.default_aggregation is not None:
            _dict['default_aggregation'] = self.default_aggregation
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorMetricRequest object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorMetricRequest') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorMetricRequest') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class ExpectedDirectionEnum(str, Enum):
        """
        the indicator specifying the expected direction of the monotonic metric values.
        """
        INCREASING = 'increasing'
        DECREASING = 'decreasing'
        UNKNOWN = 'unknown'


class MonitorRuntime():
    """
    MonitorRuntime.

    :attr str type:
    """

    def __init__(self,
                 type: str) -> None:
        """
        Initialize a MonitorRuntime object.

        :param str type:
        """
        self.type = type

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorRuntime':
        """Initialize a MonitorRuntime object from a json dictionary."""
        args = {}
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in MonitorRuntime JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorRuntime object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorRuntime object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorRuntime') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorRuntime') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class TypeEnum(str, Enum):
        """
        type.
        """
        SERVICE = 'service'
        NONE = 'none'


class MonitorTag():
    """
    MonitorTag.

    :attr str name: unique name used by UI instead of id (must be unique in scope of
          the monitor defition across both metrics and tags).
    :attr str description: (optional) Description of the tag.
    :attr bool required: (optional)
    :attr str id:
    """

    def __init__(self,
                 name: str,
                 id: str,
                 *,
                 description: str = None,
                 required: bool = None) -> None:
        """
        Initialize a MonitorTag object.

        :param str name: unique name used by UI instead of id (must be unique in
               scope of the monitor defition across both metrics and tags).
        :param str id:
        :param str description: (optional) Description of the tag.
        :param bool required: (optional)
        """
        self.name = name
        self.description = description
        self.required = required
        self.id = id

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorTag':
        """Initialize a MonitorTag object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        else:
            raise ValueError('Required property \'name\' not present in MonitorTag JSON')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'required' in _dict:
            args['required'] = _dict.get('required')
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        else:
            raise ValueError('Required property \'id\' not present in MonitorTag JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorTag object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'required') and self.required is not None:
            _dict['required'] = self.required
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorTag object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorTag') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorTag') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitorTagRequest():
    """
    MonitorTagRequest.

    :attr str name: unique name used by UI instead of id (must be unique in scope of
          the monitor defition across both metrics and tags).
    :attr str description: (optional) Description of the tag.
    :attr bool required: (optional)
    """

    def __init__(self,
                 name: str,
                 *,
                 description: str = None,
                 required: bool = None) -> None:
        """
        Initialize a MonitorTagRequest object.

        :param str name: unique name used by UI instead of id (must be unique in
               scope of the monitor defition across both metrics and tags).
        :param str description: (optional) Description of the tag.
        :param bool required: (optional)
        """
        self.name = name
        self.description = description
        self.required = required

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitorTagRequest':
        """Initialize a MonitorTagRequest object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        else:
            raise ValueError('Required property \'name\' not present in MonitorTagRequest JSON')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        if 'required' in _dict:
            args['required'] = _dict.get('required')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitorTagRequest object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        if hasattr(self, 'required') and self.required is not None:
            _dict['required'] = self.required
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitorTagRequest object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitorTagRequest') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitorTagRequest') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitoringRun():
    """
    MonitoringRun.

    :attr Metadata metadata:
    :attr MonitoringRunEntity entity:
    """

    def __init__(self,
                 metadata: 'Metadata',
                 entity: 'MonitoringRunEntity') -> None:
        """
        Initialize a MonitoringRun object.

        :param Metadata metadata:
        :param MonitoringRunEntity entity:
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitoringRun':
        """Initialize a MonitoringRun object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in MonitoringRun JSON')
        if 'entity' in _dict:
            args['entity'] = MonitoringRunEntity.from_dict(_dict.get('entity'))
        else:
            raise ValueError('Required property \'entity\' not present in MonitoringRun JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitoringRun object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitoringRun object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitoringRun') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitoringRun') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitoringRunBusinessMetricContext():
    """
    Properties defining the business metric context in the triggered run of AI metric
    calculation.

    :attr str business_application_id: Unique identifier of the business
          application, which models are monitored by OpenScale.
    :attr str metric_id:
    :attr str transaction_data_set_id: Unique identifier of the data set (like
          scoring, feedback or business payload).
    :attr str transaction_batch_id:
    """

    def __init__(self,
                 business_application_id: str,
                 metric_id: str,
                 transaction_data_set_id: str,
                 transaction_batch_id: str) -> None:
        """
        Initialize a MonitoringRunBusinessMetricContext object.

        :param str business_application_id: Unique identifier of the business
               application, which models are monitored by OpenScale.
        :param str metric_id:
        :param str transaction_data_set_id: Unique identifier of the data set (like
               scoring, feedback or business payload).
        :param str transaction_batch_id:
        """
        self.business_application_id = business_application_id
        self.metric_id = metric_id
        self.transaction_data_set_id = transaction_data_set_id
        self.transaction_batch_id = transaction_batch_id

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitoringRunBusinessMetricContext':
        """Initialize a MonitoringRunBusinessMetricContext object from a json dictionary."""
        args = {}
        if 'business_application_id' in _dict:
            args['business_application_id'] = _dict.get('business_application_id')
        else:
            raise ValueError('Required property \'business_application_id\' not present in MonitoringRunBusinessMetricContext JSON')
        if 'metric_id' in _dict:
            args['metric_id'] = _dict.get('metric_id')
        else:
            raise ValueError('Required property \'metric_id\' not present in MonitoringRunBusinessMetricContext JSON')
        if 'transaction_data_set_id' in _dict:
            args['transaction_data_set_id'] = _dict.get('transaction_data_set_id')
        else:
            raise ValueError('Required property \'transaction_data_set_id\' not present in MonitoringRunBusinessMetricContext JSON')
        if 'transaction_batch_id' in _dict:
            args['transaction_batch_id'] = _dict.get('transaction_batch_id')
        else:
            raise ValueError('Required property \'transaction_batch_id\' not present in MonitoringRunBusinessMetricContext JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitoringRunBusinessMetricContext object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'business_application_id') and self.business_application_id is not None:
            _dict['business_application_id'] = self.business_application_id
        if hasattr(self, 'metric_id') and self.metric_id is not None:
            _dict['metric_id'] = self.metric_id
        if hasattr(self, 'transaction_data_set_id') and self.transaction_data_set_id is not None:
            _dict['transaction_data_set_id'] = self.transaction_data_set_id
        if hasattr(self, 'transaction_batch_id') and self.transaction_batch_id is not None:
            _dict['transaction_batch_id'] = self.transaction_batch_id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitoringRunBusinessMetricContext object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitoringRunBusinessMetricContext') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitoringRunBusinessMetricContext') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitoringRunCollection():
    """
    A page from a collection of monitoring runs.

    :attr List[MonitoringRun] runs: A page from a collection of monitoring runs.
    :attr CollectionUrlModel first: (optional)
    :attr CollectionUrlModel prev: (optional)
    :attr CollectionUrlModel next: (optional)
    :attr CollectionUrlModel last: (optional)
    :attr int limit: (optional) The number of monitoring runs requested to be
          returned.
    :attr int total_count: (optional) The total number of monitoring runs available.
    """

    def __init__(self,
                 runs: List['MonitoringRun'],
                 *,
                 first: 'CollectionUrlModel' = None,
                 prev: 'CollectionUrlModel' = None,
                 next: 'CollectionUrlModel' = None,
                 last: 'CollectionUrlModel' = None,
                 limit: int = None,
                 total_count: int = None) -> None:
        """
        Initialize a MonitoringRunCollection object.

        :param List[MonitoringRun] runs: A page from a collection of monitoring
               runs.
        :param CollectionUrlModel first: (optional)
        :param CollectionUrlModel prev: (optional)
        :param CollectionUrlModel next: (optional)
        :param CollectionUrlModel last: (optional)
        :param int limit: (optional) The number of monitoring runs requested to be
               returned.
        :param int total_count: (optional) The total number of monitoring runs
               available.
        """
        self.runs = runs
        self.first = first
        self.prev = prev
        self.next = next
        self.last = last
        self.limit = limit
        self.total_count = total_count

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitoringRunCollection':
        """Initialize a MonitoringRunCollection object from a json dictionary."""
        args = {}
        if 'runs' in _dict:
            args['runs'] = [MonitoringRun.from_dict(x) for x in _dict.get('runs')]
        else:
            raise ValueError('Required property \'runs\' not present in MonitoringRunCollection JSON')
        if 'first' in _dict:
            args['first'] = CollectionUrlModel.from_dict(_dict.get('first'))
        if 'prev' in _dict:
            args['prev'] = CollectionUrlModel.from_dict(_dict.get('prev'))
        if 'next' in _dict:
            args['next'] = CollectionUrlModel.from_dict(_dict.get('next'))
        if 'last' in _dict:
            args['last'] = CollectionUrlModel.from_dict(_dict.get('last'))
        if 'limit' in _dict:
            args['limit'] = _dict.get('limit')
        if 'total_count' in _dict:
            args['total_count'] = _dict.get('total_count')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitoringRunCollection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'runs') and self.runs is not None:
            _dict['runs'] = [x.to_dict() for x in self.runs]
        if hasattr(self, 'first') and self.first is not None:
            _dict['first'] = self.first.to_dict()
        if hasattr(self, 'prev') and self.prev is not None:
            _dict['prev'] = self.prev.to_dict()
        if hasattr(self, 'next') and self.next is not None:
            _dict['next'] = self.next.to_dict()
        if hasattr(self, 'last') and self.last is not None:
            _dict['last'] = self.last.to_dict()
        if hasattr(self, 'limit') and self.limit is not None:
            _dict['limit'] = self.limit
        if hasattr(self, 'total_count') and self.total_count is not None:
            _dict['total_count'] = self.total_count
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitoringRunCollection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitoringRunCollection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitoringRunCollection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitoringRunEntity():
    """
    MonitoringRunEntity.

    :attr str triggered_by: (optional) An identifier representing the source that
          triggered the run request (optional). One of: event, scheduler, user, webhook.
    :attr dict parameters: (optional) Monitoring parameters consistent with the
          `parameters_schema` from the monitor definition.
    :attr MonitoringRunStatus status: The status information for the monitoring run.
    """

    def __init__(self,
                 status: 'MonitoringRunStatus',
                 *,
                 triggered_by: str = None,
                 parameters: dict = None) -> None:
        """
        Initialize a MonitoringRunEntity object.

        :param MonitoringRunStatus status: The status information for the
               monitoring run.
        :param str triggered_by: (optional) An identifier representing the source
               that triggered the run request (optional). One of: event, scheduler, user,
               webhook.
        :param dict parameters: (optional) Monitoring parameters consistent with
               the `parameters_schema` from the monitor definition.
        """
        self.triggered_by = triggered_by
        self.parameters = parameters
        self.status = status

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitoringRunEntity':
        """Initialize a MonitoringRunEntity object from a json dictionary."""
        args = {}
        if 'triggered_by' in _dict:
            args['triggered_by'] = _dict.get('triggered_by')
        if 'parameters' in _dict:
            args['parameters'] = _dict.get('parameters')
        if 'status' in _dict:
            args['status'] = MonitoringRunStatus.from_dict(_dict.get('status'))
        else:
            raise ValueError('Required property \'status\' not present in MonitoringRunEntity JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitoringRunEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'triggered_by') and self.triggered_by is not None:
            _dict['triggered_by'] = self.triggered_by
        if hasattr(self, 'parameters') and self.parameters is not None:
            _dict['parameters'] = self.parameters
        if hasattr(self, 'status') and self.status is not None:
            _dict['status'] = self.status.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitoringRunEntity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitoringRunEntity') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitoringRunEntity') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class TriggeredByEnum(str, Enum):
        """
        An identifier representing the source that triggered the run request (optional).
        One of: event, scheduler, user, webhook.
        """
        EVENT = 'event'
        SCHEDULER = 'scheduler'
        USER = 'user'
        WEBHOOK = 'webhook'
        BKPI_MANAGER = 'bkpi_manager'


class MonitoringRunOperator():
    """
    MonitoringRunOperator.

    :attr str id: (optional)
    :attr MonitoringRunOperatorStatus status: (optional)
    :attr dict result: (optional) Result produced by the operator, if any.
    """

    def __init__(self,
                 *,
                 id: str = None,
                 status: 'MonitoringRunOperatorStatus' = None,
                 result: dict = None) -> None:
        """
        Initialize a MonitoringRunOperator object.

        :param str id: (optional)
        :param MonitoringRunOperatorStatus status: (optional)
        :param dict result: (optional) Result produced by the operator, if any.
        """
        self.id = id
        self.status = status
        self.result = result

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitoringRunOperator':
        """Initialize a MonitoringRunOperator object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        if 'status' in _dict:
            args['status'] = MonitoringRunOperatorStatus.from_dict(_dict.get('status'))
        if 'result' in _dict:
            args['result'] = _dict.get('result')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitoringRunOperator object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'status') and self.status is not None:
            _dict['status'] = self.status.to_dict()
        if hasattr(self, 'result') and self.result is not None:
            _dict['result'] = self.result
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitoringRunOperator object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitoringRunOperator') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitoringRunOperator') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class MonitoringRunOperatorStatus():
    """
    MonitoringRunOperatorStatus.

    :attr str state: (optional)
    :attr datetime started_at: (optional)
    :attr datetime completed_at: (optional)
    :attr GenericErrorResponse failure: (optional)
    """

    def __init__(self,
                 *,
                 state: str = None,
                 started_at: datetime = None,
                 completed_at: datetime = None,
                 failure: 'GenericErrorResponse' = None) -> None:
        """
        Initialize a MonitoringRunOperatorStatus object.

        :param str state: (optional)
        :param datetime started_at: (optional)
        :param datetime completed_at: (optional)
        :param GenericErrorResponse failure: (optional)
        """
        self.state = state
        self.started_at = started_at
        self.completed_at = completed_at
        self.failure = failure

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitoringRunOperatorStatus':
        """Initialize a MonitoringRunOperatorStatus object from a json dictionary."""
        args = {}
        if 'state' in _dict:
            args['state'] = _dict.get('state')
        if 'started_at' in _dict:
            args['started_at'] = string_to_datetime(_dict.get('started_at'))
        if 'completed_at' in _dict:
            args['completed_at'] = string_to_datetime(_dict.get('completed_at'))
        if 'failure' in _dict:
            args['failure'] = GenericErrorResponse.from_dict(_dict.get('failure'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitoringRunOperatorStatus object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'state') and self.state is not None:
            _dict['state'] = self.state
        if hasattr(self, 'started_at') and self.started_at is not None:
            _dict['started_at'] = datetime_to_string(self.started_at)
        if hasattr(self, 'completed_at') and self.completed_at is not None:
            _dict['completed_at'] = datetime_to_string(self.completed_at)
        if hasattr(self, 'failure') and self.failure is not None:
            _dict['failure'] = self.failure.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitoringRunOperatorStatus object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitoringRunOperatorStatus') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitoringRunOperatorStatus') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class StateEnum(str, Enum):
        """
        state.
        """
        QUEUED = 'queued'
        RUNNING = 'running'
        FINISHED = 'finished'
        ERROR = 'error'


class MonitoringRunStatus():
    """
    The status information for the monitoring run.

    :attr str state: (optional)
    :attr datetime queued_at: (optional) The timestamp when the monitoring run was
          queued to be run (in the format YYYY-MM-DDTHH:mm:ssZ or
          YYYY-MM-DDTHH:mm:ss.sssZ, matching the date-time format as specified by RFC
          3339).
    :attr datetime started_at: (optional) The timestamp when the monitoring run was
          started running (in the format YYYY-MM-DDTHH:mm:ssZ or YYYY-MM-DDTHH:mm:ss.sssZ,
          matching the date-time format as specified by RFC 3339).
    :attr datetime updated_at: (optional) The timestamp when the monitoring run was
          last updated (in the format YYYY-MM-DDTHH:mm:ssZ or YYYY-MM-DDTHH:mm:ss.sssZ,
          matching the date-time format as specified by RFC 3339).
    :attr datetime completed_at: (optional) The timestamp when the monitoring run
          finished running (in the format YYYY-MM-DDTHH:mm:ssZ or
          YYYY-MM-DDTHH:mm:ss.sssZ, matching the date-time format as specified by RFC
          3339).
    :attr str message: (optional) Any message associated with the monitoring run.
    :attr GenericErrorResponse failure: (optional)
    :attr List[MonitoringRunOperator] operators: (optional)
    """

    def __init__(self,
                 *,
                 state: str = None,
                 queued_at: datetime = None,
                 started_at: datetime = None,
                 updated_at: datetime = None,
                 completed_at: datetime = None,
                 message: str = None,
                 failure: 'GenericErrorResponse' = None,
                 operators: List['MonitoringRunOperator'] = None) -> None:
        """
        Initialize a MonitoringRunStatus object.

        :param str state: (optional)
        :param datetime queued_at: (optional) The timestamp when the monitoring run
               was queued to be run (in the format YYYY-MM-DDTHH:mm:ssZ or
               YYYY-MM-DDTHH:mm:ss.sssZ, matching the date-time format as specified by RFC
               3339).
        :param datetime started_at: (optional) The timestamp when the monitoring
               run was started running (in the format YYYY-MM-DDTHH:mm:ssZ or
               YYYY-MM-DDTHH:mm:ss.sssZ, matching the date-time format as specified by RFC
               3339).
        :param datetime updated_at: (optional) The timestamp when the monitoring
               run was last updated (in the format YYYY-MM-DDTHH:mm:ssZ or
               YYYY-MM-DDTHH:mm:ss.sssZ, matching the date-time format as specified by RFC
               3339).
        :param datetime completed_at: (optional) The timestamp when the monitoring
               run finished running (in the format YYYY-MM-DDTHH:mm:ssZ or
               YYYY-MM-DDTHH:mm:ss.sssZ, matching the date-time format as specified by RFC
               3339).
        :param str message: (optional) Any message associated with the monitoring
               run.
        :param GenericErrorResponse failure: (optional)
        :param List[MonitoringRunOperator] operators: (optional)
        """
        self.state = state
        self.queued_at = queued_at
        self.started_at = started_at
        self.updated_at = updated_at
        self.completed_at = completed_at
        self.message = message
        self.failure = failure
        self.operators = operators

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'MonitoringRunStatus':
        """Initialize a MonitoringRunStatus object from a json dictionary."""
        args = {}
        if 'state' in _dict:
            args['state'] = _dict.get('state')
        if 'queued_at' in _dict:
            args['queued_at'] = string_to_datetime(_dict.get('queued_at'))
        if 'started_at' in _dict:
            args['started_at'] = string_to_datetime(_dict.get('started_at'))
        if 'updated_at' in _dict:
            args['updated_at'] = string_to_datetime(_dict.get('updated_at'))
        if 'completed_at' in _dict:
            args['completed_at'] = string_to_datetime(_dict.get('completed_at'))
        if 'message' in _dict:
            args['message'] = _dict.get('message')
        if 'failure' in _dict:
            args['failure'] = GenericErrorResponse.from_dict(_dict.get('failure'))
        if 'operators' in _dict:
            args['operators'] = [MonitoringRunOperator.from_dict(x) for x in _dict.get('operators')]
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a MonitoringRunStatus object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'state') and self.state is not None:
            _dict['state'] = self.state
        if hasattr(self, 'queued_at') and self.queued_at is not None:
            _dict['queued_at'] = datetime_to_string(self.queued_at)
        if hasattr(self, 'started_at') and self.started_at is not None:
            _dict['started_at'] = datetime_to_string(self.started_at)
        if hasattr(self, 'updated_at') and self.updated_at is not None:
            _dict['updated_at'] = datetime_to_string(self.updated_at)
        if hasattr(self, 'completed_at') and self.completed_at is not None:
            _dict['completed_at'] = datetime_to_string(self.completed_at)
        if hasattr(self, 'message') and self.message is not None:
            _dict['message'] = self.message
        if hasattr(self, 'failure') and self.failure is not None:
            _dict['failure'] = self.failure.to_dict()
        if hasattr(self, 'operators') and self.operators is not None:
            _dict['operators'] = [x.to_dict() for x in self.operators]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this MonitoringRunStatus object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'MonitoringRunStatus') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'MonitoringRunStatus') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class StateEnum(str, Enum):
        """
        state.
        """
        QUEUED = 'queued'
        RUNNING = 'running'
        FINISHED = 'finished'
        ERROR = 'error'


class OperationalSpace():
    """
    Operational Space definition.

    :attr str name: The name of the Operational Space.
    :attr str description: (optional) The description of the Operational Space.
    """

    def __init__(self,
                 name: str,
                 *,
                 description: str = None) -> None:
        """
        Initialize a OperationalSpace object.

        :param str name: The name of the Operational Space.
        :param str description: (optional) The description of the Operational
               Space.
        """
        self.name = name
        self.description = description

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'OperationalSpace':
        """Initialize a OperationalSpace object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        else:
            raise ValueError('Required property \'name\' not present in OperationalSpace JSON')
        if 'description' in _dict:
            args['description'] = _dict.get('description')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a OperationalSpace object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'description') and self.description is not None:
            _dict['description'] = self.description
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this OperationalSpace object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'OperationalSpace') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'OperationalSpace') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class OperationalSpaceCollection():
    """
    OperationalSpaceCollection.

    :attr List[OperationalSpace] operational_spaces:
    """

    def __init__(self,
                 operational_spaces: List['OperationalSpace']) -> None:
        """
        Initialize a OperationalSpaceCollection object.

        :param List[OperationalSpace] operational_spaces:
        """
        self.operational_spaces = operational_spaces

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'OperationalSpaceCollection':
        """Initialize a OperationalSpaceCollection object from a json dictionary."""
        args = {}
        if 'operational_spaces' in _dict:
            args['operational_spaces'] = [OperationalSpace.from_dict(x) for x in _dict.get('operational_spaces')]
        else:
            raise ValueError('Required property \'operational_spaces\' not present in OperationalSpaceCollection JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a OperationalSpaceCollection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'operational_spaces') and self.operational_spaces is not None:
            _dict['operational_spaces'] = [x.to_dict() for x in self.operational_spaces]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this OperationalSpaceCollection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'OperationalSpaceCollection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'OperationalSpaceCollection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class OperationalSpaceResponse():
    """
    OperationalSpaceResponse.

    :attr Metadata metadata: (optional)
    :attr OperationalSpace entity: (optional) Operational Space definition.
    """

    def __init__(self,
                 *,
                 metadata: 'Metadata' = None,
                 entity: 'OperationalSpace' = None) -> None:
        """
        Initialize a OperationalSpaceResponse object.

        :param Metadata metadata: (optional)
        :param OperationalSpace entity: (optional) Operational Space definition.
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'OperationalSpaceResponse':
        """Initialize a OperationalSpaceResponse object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        if 'entity' in _dict:
            args['entity'] = OperationalSpace.from_dict(_dict.get('entity'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a OperationalSpaceResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this OperationalSpaceResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'OperationalSpaceResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'OperationalSpaceResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class PatchDocument():
    """
    A JSONPatch document as defined by RFC 6902.

    :attr str op: The operation to be performed.
    :attr str path: A JSON-Pointer.
    :attr object value: (optional) The value to be used within the operations.
    :attr str from_: (optional) A string containing a JSON Pointer value.
    """

    def __init__(self,
                 op: str,
                 path: str,
                 *,
                 value: object = None,
                 from_: str = None) -> None:
        """
        Initialize a PatchDocument object.

        :param str op: The operation to be performed.
        :param str path: A JSON-Pointer.
        :param object value: (optional) The value to be used within the operations.
        :param str from_: (optional) A string containing a JSON Pointer value.
        """
        self.op = op
        self.path = path
        self.value = value
        self.from_ = from_

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'PatchDocument':
        """Initialize a PatchDocument object from a json dictionary."""
        args = {}
        if 'op' in _dict:
            args['op'] = _dict.get('op')
        else:
            raise ValueError('Required property \'op\' not present in PatchDocument JSON')
        if 'path' in _dict:
            args['path'] = _dict.get('path')
        else:
            raise ValueError('Required property \'path\' not present in PatchDocument JSON')
        if 'value' in _dict:
            args['value'] = _dict.get('value')
        if 'from' in _dict:
            args['from_'] = _dict.get('from')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a PatchDocument object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'op') and self.op is not None:
            _dict['op'] = self.op
        if hasattr(self, 'path') and self.path is not None:
            _dict['path'] = self.path
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        if hasattr(self, 'from_') and self.from_ is not None:
            _dict['from'] = self.from_
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this PatchDocument object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'PatchDocument') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'PatchDocument') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class OpEnum(str, Enum):
        """
        The operation to be performed.
        """
        ADD = 'add'
        REMOVE = 'remove'
        REPLACE = 'replace'
        MOVE = 'move'
        COPY = 'copy'
        TEST = 'test'


class PostExplanationTaskResponse():
    """
    Post explanation tasks response.

    :attr PostExplanationTaskResponseMetadata metadata: Metadata of post explanation
          tasks response.
    """

    def __init__(self,
                 metadata: 'PostExplanationTaskResponseMetadata') -> None:
        """
        Initialize a PostExplanationTaskResponse object.

        :param PostExplanationTaskResponseMetadata metadata: Metadata of post
               explanation tasks response.
        """
        self.metadata = metadata

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'PostExplanationTaskResponse':
        """Initialize a PostExplanationTaskResponse object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = PostExplanationTaskResponseMetadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in PostExplanationTaskResponse JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a PostExplanationTaskResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this PostExplanationTaskResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'PostExplanationTaskResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'PostExplanationTaskResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class PostExplanationTaskResponseMetadata():
    """
    Metadata of post explanation tasks response.

    :attr List[str] explanation_task_ids: List of identifiers for tracking
          explanation tasks.
    :attr str created_by: ID of the user creating explanation task.
    :attr str created_at: Time when the explanation task was initiated.
    """

    def __init__(self,
                 explanation_task_ids: List[str],
                 created_by: str,
                 created_at: str) -> None:
        """
        Initialize a PostExplanationTaskResponseMetadata object.

        :param List[str] explanation_task_ids: List of identifiers for tracking
               explanation tasks.
        :param str created_by: ID of the user creating explanation task.
        :param str created_at: Time when the explanation task was initiated.
        """
        self.explanation_task_ids = explanation_task_ids
        self.created_by = created_by
        self.created_at = created_at

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'PostExplanationTaskResponseMetadata':
        """Initialize a PostExplanationTaskResponseMetadata object from a json dictionary."""
        args = {}
        if 'explanation_task_ids' in _dict:
            args['explanation_task_ids'] = _dict.get('explanation_task_ids')
        else:
            raise ValueError('Required property \'explanation_task_ids\' not present in PostExplanationTaskResponseMetadata JSON')
        if 'created_by' in _dict:
            args['created_by'] = _dict.get('created_by')
        else:
            raise ValueError('Required property \'created_by\' not present in PostExplanationTaskResponseMetadata JSON')
        if 'created_at' in _dict:
            args['created_at'] = _dict.get('created_at')
        else:
            raise ValueError('Required property \'created_at\' not present in PostExplanationTaskResponseMetadata JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a PostExplanationTaskResponseMetadata object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'explanation_task_ids') and self.explanation_task_ids is not None:
            _dict['explanation_task_ids'] = self.explanation_task_ids
        if hasattr(self, 'created_by') and self.created_by is not None:
            _dict['created_by'] = self.created_by
        if hasattr(self, 'created_at') and self.created_at is not None:
            _dict['created_at'] = self.created_at
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this PostExplanationTaskResponseMetadata object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'PostExplanationTaskResponseMetadata') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'PostExplanationTaskResponseMetadata') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class PrimaryStorageCredentials():
    """
    PrimaryStorageCredentials.

    """

    def __init__(self) -> None:
        """
        Initialize a PrimaryStorageCredentials object.

        """
        msg = "Cannot instantiate base class. Instead, instantiate one of the defined subclasses: {0}".format(
                  ", ".join(['PrimaryStorageCredentialsShort', 'PrimaryStorageCredentialsLong']))
        raise Exception(msg)

class RecordsCountSummary():
    """
    Summary about records count.

    :attr int count:
    :attr str type: The type of records time.
    :attr datetime timestamp: (optional) timestamp of last consumed record (only for
          unprocessed_records).
    :attr GenericErrorResponse failure: (optional)
    """

    def __init__(self,
                 count: int,
                 type: str,
                 *,
                 timestamp: datetime = None,
                 failure: 'GenericErrorResponse' = None) -> None:
        """
        Initialize a RecordsCountSummary object.

        :param int count:
        :param str type: The type of records time.
        :param datetime timestamp: (optional) timestamp of last consumed record
               (only for unprocessed_records).
        :param GenericErrorResponse failure: (optional)
        """
        self.count = count
        self.type = type
        self.timestamp = timestamp
        self.failure = failure

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'RecordsCountSummary':
        """Initialize a RecordsCountSummary object from a json dictionary."""
        args = {}
        if 'count' in _dict:
            args['count'] = _dict.get('count')
        else:
            raise ValueError('Required property \'count\' not present in RecordsCountSummary JSON')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in RecordsCountSummary JSON')
        if 'timestamp' in _dict:
            args['timestamp'] = string_to_datetime(_dict.get('timestamp'))
        if 'failure' in _dict:
            args['failure'] = GenericErrorResponse.from_dict(_dict.get('failure'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a RecordsCountSummary object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'count') and self.count is not None:
            _dict['count'] = self.count
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'timestamp') and self.timestamp is not None:
            _dict['timestamp'] = datetime_to_string(self.timestamp)
        if hasattr(self, 'failure') and self.failure is not None:
            _dict['failure'] = self.failure.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this RecordsCountSummary object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'RecordsCountSummary') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'RecordsCountSummary') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class TypeEnum(str, Enum):
        """
        The type of records time.
        """
        PAYLOAD_LOGGING = 'payload_logging'
        FEEDBACK = 'feedback'


class RecordsListResponse():
    """
    RecordsListResponse.

    """

    def __init__(self) -> None:
        """
        Initialize a RecordsListResponse object.

        """
        msg = "Cannot instantiate base class. Instead, instantiate one of the defined subclasses: {0}".format(
                  ", ".join(['RecordsListResponseDataRecordsResponseCollectionDict', 'RecordsListResponseDataRecordsResponseCollectionList']))
        raise Exception(msg)

class RiskEvaluationStatus():
    """
    RiskEvaluationStatus.

    :attr str state:
    :attr str comment: (optional) Optional comment to the evaluation.
    :attr str evaluated_by: (optional) Author of the evaluation.
    :attr str evaluated_at: (optional) Time of the evaluation.
    """

    def __init__(self,
                 state: str,
                 *,
                 comment: str = None,
                 evaluated_by: str = None,
                 evaluated_at: str = None) -> None:
        """
        Initialize a RiskEvaluationStatus object.

        :param str state:
        :param str comment: (optional) Optional comment to the evaluation.
        :param str evaluated_by: (optional) Author of the evaluation.
        :param str evaluated_at: (optional) Time of the evaluation.
        """
        self.state = state
        self.comment = comment
        self.evaluated_by = evaluated_by
        self.evaluated_at = evaluated_at

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'RiskEvaluationStatus':
        """Initialize a RiskEvaluationStatus object from a json dictionary."""
        args = {}
        if 'state' in _dict:
            args['state'] = _dict.get('state')
        else:
            raise ValueError('Required property \'state\' not present in RiskEvaluationStatus JSON')
        if 'comment' in _dict:
            args['comment'] = _dict.get('comment')
        if 'evaluated_by' in _dict:
            args['evaluated_by'] = _dict.get('evaluated_by')
        if 'evaluated_at' in _dict:
            args['evaluated_at'] = _dict.get('evaluated_at')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a RiskEvaluationStatus object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'state') and self.state is not None:
            _dict['state'] = self.state
        if hasattr(self, 'comment') and self.comment is not None:
            _dict['comment'] = self.comment
        if hasattr(self, 'evaluated_by') and self.evaluated_by is not None:
            _dict['evaluated_by'] = self.evaluated_by
        if hasattr(self, 'evaluated_at') and self.evaluated_at is not None:
            _dict['evaluated_at'] = self.evaluated_at
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this RiskEvaluationStatus object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'RiskEvaluationStatus') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'RiskEvaluationStatus') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class StateEnum(str, Enum):
        """
        state.
        """
        PENDING_EVALUATION = 'pending_evaluation'
        APPROVED = 'approved'
        REJECTED = 'rejected'


class ScheduleStartTime():
    """
    Defintion of first run time for scheduled activity; either absolute or relative the
    the moment of activation.

    :attr str type: The type of start time.
    :attr str delay_unit: (optional) must be set if type is `relative`.
    :attr int delay: (optional) must be set if type is `relative`.
    :attr datetime timestamp: (optional) must be set if type is `absolute`.
    """

    def __init__(self,
                 type: str,
                 *,
                 delay_unit: str = None,
                 delay: int = None,
                 timestamp: datetime = None) -> None:
        """
        Initialize a ScheduleStartTime object.

        :param str type: The type of start time.
        :param str delay_unit: (optional) must be set if type is `relative`.
        :param int delay: (optional) must be set if type is `relative`.
        :param datetime timestamp: (optional) must be set if type is `absolute`.
        """
        self.type = type
        self.delay_unit = delay_unit
        self.delay = delay
        self.timestamp = timestamp

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ScheduleStartTime':
        """Initialize a ScheduleStartTime object from a json dictionary."""
        args = {}
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in ScheduleStartTime JSON')
        if 'delay_unit' in _dict:
            args['delay_unit'] = _dict.get('delay_unit')
        if 'delay' in _dict:
            args['delay'] = _dict.get('delay')
        if 'timestamp' in _dict:
            args['timestamp'] = string_to_datetime(_dict.get('timestamp'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ScheduleStartTime object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'delay_unit') and self.delay_unit is not None:
            _dict['delay_unit'] = self.delay_unit
        if hasattr(self, 'delay') and self.delay is not None:
            _dict['delay'] = self.delay
        if hasattr(self, 'timestamp') and self.timestamp is not None:
            _dict['timestamp'] = datetime_to_string(self.timestamp)
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ScheduleStartTime object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ScheduleStartTime') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ScheduleStartTime') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class TypeEnum(str, Enum):
        """
        The type of start time.
        """
        RELATIVE = 'relative'
        ABSOLUTE = 'absolute'


    class DelayUnitEnum(str, Enum):
        """
        must be set if type is `relative`.
        """
        MINUTE = 'minute'
        HOUR = 'hour'
        DAY = 'day'
        WEEK = 'week'
        MONTH = 'month'
        YEAR = 'year'


class SchemaInferenceResponse():
    """
    Schema inference response.

    :attr FileAssetMetadata file_asset_metadata: (optional) File data asset
          metadata.
    :attr SubscriptionResponse subscription:
    """

    def __init__(self,
                 subscription: 'SubscriptionResponse',
                 *,
                 file_asset_metadata: 'FileAssetMetadata' = None) -> None:
        """
        Initialize a SchemaInferenceResponse object.

        :param SubscriptionResponse subscription:
        :param FileAssetMetadata file_asset_metadata: (optional) File data asset
               metadata.
        """
        self.file_asset_metadata = file_asset_metadata
        self.subscription = subscription

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'SchemaInferenceResponse':
        """Initialize a SchemaInferenceResponse object from a json dictionary."""
        args = {}
        if 'file_asset_metadata' in _dict:
            args['file_asset_metadata'] = FileAssetMetadata.from_dict(_dict.get('file_asset_metadata'))
        if 'subscription' in _dict:
            args['subscription'] = SubscriptionResponse.from_dict(_dict.get('subscription'))
        else:
            raise ValueError('Required property \'subscription\' not present in SchemaInferenceResponse JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SchemaInferenceResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'file_asset_metadata') and self.file_asset_metadata is not None:
            _dict['file_asset_metadata'] = self.file_asset_metadata.to_dict()
        if hasattr(self, 'subscription') and self.subscription is not None:
            _dict['subscription'] = self.subscription.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this SchemaInferenceResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'SchemaInferenceResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'SchemaInferenceResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class ScoreData():
    """
    Score data object.

    :attr List[object] values: Score value records.
    :attr List[str] fields: (optional) Score fields.
    :attr str id: (optional) Discriminates the data for multi input data situation.
          For example in cases where multiple tensors are expected.
    """

    def __init__(self,
                 values: List[object],
                 *,
                 fields: List[str] = None,
                 id: str = None) -> None:
        """
        Initialize a ScoreData object.

        :param List[object] values: Score value records.
        :param List[str] fields: (optional) Score fields.
        :param str id: (optional) Discriminates the data for multi input data
               situation. For example in cases where multiple tensors are expected.
        """
        self.values = values
        self.fields = fields
        self.id = id

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ScoreData':
        """Initialize a ScoreData object from a json dictionary."""
        args = {}
        if 'values' in _dict:
            args['values'] = _dict.get('values')
        else:
            raise ValueError('Required property \'values\' not present in ScoreData JSON')
        if 'fields' in _dict:
            args['fields'] = _dict.get('fields')
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ScoreData object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'values') and self.values is not None:
            _dict['values'] = self.values
        if hasattr(self, 'fields') and self.fields is not None:
            _dict['fields'] = self.fields
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ScoreData object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ScoreData') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ScoreData') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class ScoringEndpoint():
    """
    Definition of scoring endpoint in custom_machine_learning.

    :attr str url: (optional)
    :attr SecretCleaned credentials: (optional)
    :attr dict request_headers: (optional) map header name to header value.
    """

    def __init__(self,
                 *,
                 url: str = None,
                 credentials: 'SecretCleaned' = None,
                 request_headers: dict = None) -> None:
        """
        Initialize a ScoringEndpoint object.

        :param str url: (optional)
        :param SecretCleaned credentials: (optional)
        :param dict request_headers: (optional) map header name to header value.
        """
        self.url = url
        self.credentials = credentials
        self.request_headers = request_headers

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ScoringEndpoint':
        """Initialize a ScoringEndpoint object from a json dictionary."""
        args = {}
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        if 'credentials' in _dict:
            args['credentials'] = SecretCleaned.from_dict(_dict.get('credentials'))
        if 'request_headers' in _dict:
            args['request_headers'] = _dict.get('request_headers')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ScoringEndpoint object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        if hasattr(self, 'credentials') and self.credentials is not None:
            _dict['credentials'] = self.credentials.to_dict()
        if hasattr(self, 'request_headers') and self.request_headers is not None:
            _dict['request_headers'] = self.request_headers
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ScoringEndpoint object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ScoringEndpoint') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ScoringEndpoint') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class ScoringEndpointCredentials():
    """
    ScoringEndpointCredentials.

    """

    def __init__(self,
                 **kwargs) -> None:
        """
        Initialize a ScoringEndpointCredentials object.

        :param **kwargs: (optional) Any additional properties.
        """
        msg = "Cannot instantiate base class. Instead, instantiate one of the defined subclasses: {0}".format(
                  ", ".join(['ScoringEndpointCredentialsAzureScoringEndpointCredentials']))
        raise Exception(msg)

class ScoringEndpointRequest():
    """
    Definition of scoring endpoint in custom_machine_learning.

    :attr str url: (optional)
    :attr ScoringEndpointCredentials credentials: (optional)
    :attr dict request_headers: (optional) map header name to header value.
    """

    def __init__(self,
                 *,
                 url: str = None,
                 credentials: 'ScoringEndpointCredentials' = None,
                 request_headers: dict = None) -> None:
        """
        Initialize a ScoringEndpointRequest object.

        :param str url: (optional)
        :param ScoringEndpointCredentials credentials: (optional)
        :param dict request_headers: (optional) map header name to header value.
        """
        self.url = url
        self.credentials = credentials
        self.request_headers = request_headers

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ScoringEndpointRequest':
        """Initialize a ScoringEndpointRequest object from a json dictionary."""
        args = {}
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        if 'credentials' in _dict:
            args['credentials'] = _dict.get('credentials')
        if 'request_headers' in _dict:
            args['request_headers'] = _dict.get('request_headers')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ScoringEndpointRequest object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        if hasattr(self, 'credentials') and self.credentials is not None:
            if isinstance(self.credentials, dict):
                _dict['credentials'] = self.credentials
            else:
                _dict['credentials'] = self.credentials.to_dict()
        if hasattr(self, 'request_headers') and self.request_headers is not None:
            _dict['request_headers'] = self.request_headers
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ScoringEndpointRequest object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ScoringEndpointRequest') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ScoringEndpointRequest') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class SecretCleaned():
    """
    SecretCleaned.

    :attr str secret_id: Generated id which identifies credentials.
    """

    def __init__(self,
                 secret_id: str) -> None:
        """
        Initialize a SecretCleaned object.

        :param str secret_id: Generated id which identifies credentials.
        """
        self.secret_id = secret_id

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'SecretCleaned':
        """Initialize a SecretCleaned object from a json dictionary."""
        args = {}
        if 'secret_id' in _dict:
            args['secret_id'] = _dict.get('secret_id')
        else:
            raise ValueError('Required property \'secret_id\' not present in SecretCleaned JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SecretCleaned object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'secret_id') and self.secret_id is not None:
            _dict['secret_id'] = self.secret_id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this SecretCleaned object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'SecretCleaned') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'SecretCleaned') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class ServiceProviderResponse():
    """
    ServiceProviderResponse.

    :attr Metadata metadata:
    :attr ServiceProviderResponseEntity entity:
    """

    def __init__(self,
                 metadata: 'Metadata',
                 entity: 'ServiceProviderResponseEntity') -> None:
        """
        Initialize a ServiceProviderResponse object.

        :param Metadata metadata:
        :param ServiceProviderResponseEntity entity:
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ServiceProviderResponse':
        """Initialize a ServiceProviderResponse object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in ServiceProviderResponse JSON')
        if 'entity' in _dict:
            args['entity'] = ServiceProviderResponseEntity.from_dict(_dict.get('entity'))
        else:
            raise ValueError('Required property \'entity\' not present in ServiceProviderResponse JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ServiceProviderResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ServiceProviderResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ServiceProviderResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ServiceProviderResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class ServiceProviderResponseCollection():
    """
    ServiceProviderResponseCollection.

    :attr List[ServiceProviderResponse] service_providers:
    """

    def __init__(self,
                 service_providers: List['ServiceProviderResponse']) -> None:
        """
        Initialize a ServiceProviderResponseCollection object.

        :param List[ServiceProviderResponse] service_providers:
        """
        self.service_providers = service_providers

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ServiceProviderResponseCollection':
        """Initialize a ServiceProviderResponseCollection object from a json dictionary."""
        args = {}
        if 'service_providers' in _dict:
            args['service_providers'] = [ServiceProviderResponse.from_dict(x) for x in _dict.get('service_providers')]
        else:
            raise ValueError('Required property \'service_providers\' not present in ServiceProviderResponseCollection JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ServiceProviderResponseCollection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'service_providers') and self.service_providers is not None:
            _dict['service_providers'] = [x.to_dict() for x in self.service_providers]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ServiceProviderResponseCollection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ServiceProviderResponseCollection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ServiceProviderResponseCollection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class ServiceProviderResponseEntity():
    """
    ServiceProviderResponseEntity.

    :attr str name: Name of the ML service instance.
    :attr str service_type:
    :attr str instance_id: (optional) ID of the ML service instance (required for
          Watson Machine Learning).
    :attr SecretCleaned credentials: (optional)
    :attr dict request_headers: (optional) Additional headers passed to the ML
          engine API (for example when scoring).
    :attr str operational_space_id: (optional) Reference to Operational Space.
    :attr str deployment_space_id: (optional) Reference to V2 Space ID.
    :attr List[str] group_ids: (optional) Access control list of group id of Cloud
          Pak for Data (Only available for OpenScale on Cloud Pak for Data >= 4.0.6 with
          ENABLE_GROUP_AUTH being true).
    :attr List[str] user_ids: (optional) Access control list of user id of Cloud Pak
          for Data (Only available for OpenScale on Cloud Pak for Data >= 4.0.6 with
          ENABLE_GROUP_AUTH being true).
    :attr Status status: (optional)
    """

    def __init__(self,
                 name: str,
                 service_type: str,
                 *,
                 instance_id: str = None,
                 credentials: 'SecretCleaned' = None,
                 request_headers: dict = None,
                 operational_space_id: str = None,
                 deployment_space_id: str = None,
                 group_ids: List[str] = None,
                 user_ids: List[str] = None,
                 status: 'Status' = None) -> None:
        """
        Initialize a ServiceProviderResponseEntity object.

        :param str name: Name of the ML service instance.
        :param str service_type:
        :param str instance_id: (optional) ID of the ML service instance (required
               for Watson Machine Learning).
        :param SecretCleaned credentials: (optional)
        :param dict request_headers: (optional) Additional headers passed to the ML
               engine API (for example when scoring).
        :param str operational_space_id: (optional) Reference to Operational Space.
        :param str deployment_space_id: (optional) Reference to V2 Space ID.
        :param List[str] group_ids: (optional) Access control list of group id of
               Cloud Pak for Data (Only available for OpenScale on Cloud Pak for Data >=
               4.0.6 with ENABLE_GROUP_AUTH being true).
        :param List[str] user_ids: (optional) Access control list of user id of
               Cloud Pak for Data (Only available for OpenScale on Cloud Pak for Data >=
               4.0.6 with ENABLE_GROUP_AUTH being true).
        :param Status status: (optional)
        """
        self.name = name
        self.service_type = service_type
        self.instance_id = instance_id
        self.credentials = credentials
        self.request_headers = request_headers
        self.operational_space_id = operational_space_id
        self.deployment_space_id = deployment_space_id
        self.group_ids = group_ids
        self.user_ids = user_ids
        self.status = status

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ServiceProviderResponseEntity':
        """Initialize a ServiceProviderResponseEntity object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        else:
            raise ValueError('Required property \'name\' not present in ServiceProviderResponseEntity JSON')
        if 'service_type' in _dict:
            args['service_type'] = _dict.get('service_type')
        else:
            raise ValueError('Required property \'service_type\' not present in ServiceProviderResponseEntity JSON')
        if 'instance_id' in _dict:
            args['instance_id'] = _dict.get('instance_id')
        if 'credentials' in _dict:
            args['credentials'] = SecretCleaned.from_dict(_dict.get('credentials'))
        if 'request_headers' in _dict:
            args['request_headers'] = _dict.get('request_headers')
        if 'operational_space_id' in _dict:
            args['operational_space_id'] = _dict.get('operational_space_id')
        if 'deployment_space_id' in _dict:
            args['deployment_space_id'] = _dict.get('deployment_space_id')
        if 'group_ids' in _dict:
            args['group_ids'] = _dict.get('group_ids')
        if 'user_ids' in _dict:
            args['user_ids'] = _dict.get('user_ids')
        if 'status' in _dict:
            args['status'] = Status.from_dict(_dict.get('status'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ServiceProviderResponseEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'service_type') and self.service_type is not None:
            _dict['service_type'] = self.service_type
        if hasattr(self, 'instance_id') and self.instance_id is not None:
            _dict['instance_id'] = self.instance_id
        if hasattr(self, 'credentials') and self.credentials is not None:
            _dict['credentials'] = self.credentials.to_dict()
        if hasattr(self, 'request_headers') and self.request_headers is not None:
            _dict['request_headers'] = self.request_headers
        if hasattr(self, 'operational_space_id') and self.operational_space_id is not None:
            _dict['operational_space_id'] = self.operational_space_id
        if hasattr(self, 'deployment_space_id') and self.deployment_space_id is not None:
            _dict['deployment_space_id'] = self.deployment_space_id
        if hasattr(self, 'group_ids') and self.group_ids is not None:
            _dict['group_ids'] = self.group_ids
        if hasattr(self, 'user_ids') and self.user_ids is not None:
            _dict['user_ids'] = self.user_ids
        if hasattr(self, 'status') and self.status is not None:
            _dict['status'] = self.status.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ServiceProviderResponseEntity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ServiceProviderResponseEntity') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ServiceProviderResponseEntity') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class ServiceTypeEnum(str, Enum):
        """
        service_type.
        """
        WATSON_MACHINE_LEARNING = 'watson_machine_learning'
        AMAZON_SAGEMAKER = 'amazon_sagemaker'
        AZURE_MACHINE_LEARNING = 'azure_machine_learning'
        CUSTOM_MACHINE_LEARNING = 'custom_machine_learning'
        SPSS_COLLABORATION_AND_DEPLOYMENT_SERVICES = 'spss_collaboration_and_deployment_services'


class Source():
    """
    Source.

    :attr str id: id of the source.
    :attr str type: type of the source.
    :attr List[str] metric_ids: (optional) a selection of metrics that the source
          applies to (if not provided the source applies to all metrics).
    :attr object data: Data representing the source. It can be any value - object,
          string, number, boolean or array.
    """

    def __init__(self,
                 id: str,
                 type: str,
                 data: object,
                 *,
                 metric_ids: List[str] = None) -> None:
        """
        Initialize a Source object.

        :param str id: id of the source.
        :param str type: type of the source.
        :param object data: Data representing the source. It can be any value -
               object, string, number, boolean or array.
        :param List[str] metric_ids: (optional) a selection of metrics that the
               source applies to (if not provided the source applies to all metrics).
        """
        self.id = id
        self.type = type
        self.metric_ids = metric_ids
        self.data = data

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Source':
        """Initialize a Source object from a json dictionary."""
        args = {}
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        else:
            raise ValueError('Required property \'id\' not present in Source JSON')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in Source JSON')
        if 'metric_ids' in _dict:
            args['metric_ids'] = _dict.get('metric_ids')
        if 'data' in _dict:
            args['data'] = _dict.get('data')
        else:
            raise ValueError('Required property \'data\' not present in Source JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Source object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'metric_ids') and self.metric_ids is not None:
            _dict['metric_ids'] = self.metric_ids
        if hasattr(self, 'data') and self.data is not None:
            _dict['data'] = self.data
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Source object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Source') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Source') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class SparkStruct():
    """
    SparkStruct.

    :attr str type:
    :attr List[SparkStructField] fields:
    :attr str id: (optional)
    :attr str name: (optional)
    """

    def __init__(self,
                 type: str,
                 fields: List['SparkStructField'],
                 *,
                 id: str = None,
                 name: str = None) -> None:
        """
        Initialize a SparkStruct object.

        :param str type:
        :param List[SparkStructField] fields:
        :param str id: (optional)
        :param str name: (optional)
        """
        self.type = type
        self.fields = fields
        self.id = id
        self.name = name

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'SparkStruct':
        """Initialize a SparkStruct object from a json dictionary."""
        args = {}
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in SparkStruct JSON')
        if 'fields' in _dict:
            args['fields'] = _dict.get('fields')
        else:
            raise ValueError('Required property \'fields\' not present in SparkStruct JSON')
        if 'id' in _dict:
            args['id'] = _dict.get('id')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SparkStruct object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'fields') and self.fields is not None:
            fields_list = []
            for x in self.fields:
                if isinstance(x, dict):
                    fields_list.append(x)
                else:
                    fields_list.append(x.to_dict())
            _dict['fields'] = fields_list
        if hasattr(self, 'id') and self.id is not None:
            _dict['id'] = self.id
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this SparkStruct object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'SparkStruct') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'SparkStruct') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class SparkStructField():
    """
    Spark struct field.

    """

    def __init__(self) -> None:
        """
        Initialize a SparkStructField object.

        """
        msg = "Cannot instantiate base class. Instead, instantiate one of the defined subclasses: {0}".format(
                  ", ".join(['SparkStructFieldPrimitive', 'SparkStructFieldObject']))
        raise Exception(msg)

class Status():
    """
    Status.

    :attr str state:
    :attr str deleted_at: (optional)
    :attr GenericErrorResponse failure: (optional)
    """

    def __init__(self,
                 state: str,
                 *,
                 deleted_at: str = None,
                 failure: 'GenericErrorResponse' = None) -> None:
        """
        Initialize a Status object.

        :param str state:
        :param str deleted_at: (optional)
        :param GenericErrorResponse failure: (optional)
        """
        self.state = state
        self.deleted_at = deleted_at
        self.failure = failure

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Status':
        """Initialize a Status object from a json dictionary."""
        args = {}
        if 'state' in _dict:
            args['state'] = _dict.get('state')
        else:
            raise ValueError('Required property \'state\' not present in Status JSON')
        if 'deleted_at' in _dict:
            args['deleted_at'] = _dict.get('deleted_at')
        if 'failure' in _dict:
            args['failure'] = GenericErrorResponse.from_dict(_dict.get('failure'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Status object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'state') and self.state is not None:
            _dict['state'] = self.state
        if hasattr(self, 'deleted_at') and self.deleted_at is not None:
            _dict['deleted_at'] = self.deleted_at
        if hasattr(self, 'failure') and self.failure is not None:
            _dict['failure'] = self.failure.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Status object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Status') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Status') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class StateEnum(str, Enum):
        """
        state.
        """
        PREPARING = 'preparing'
        ACTIVE = 'active'
        DELETING = 'deleting'
        PENDING_DELETE = 'pending_delete'
        DISABLED = 'disabled'
        ERROR = 'error'


class SubscriptionResponse():
    """
    SubscriptionResponse.

    :attr Metadata metadata:
    :attr SubscriptionResponseEntity entity:
    """

    def __init__(self,
                 metadata: 'Metadata',
                 entity: 'SubscriptionResponseEntity') -> None:
        """
        Initialize a SubscriptionResponse object.

        :param Metadata metadata:
        :param SubscriptionResponseEntity entity:
        """
        self.metadata = metadata
        self.entity = entity

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'SubscriptionResponse':
        """Initialize a SubscriptionResponse object from a json dictionary."""
        args = {}
        if 'metadata' in _dict:
            args['metadata'] = Metadata.from_dict(_dict.get('metadata'))
        else:
            raise ValueError('Required property \'metadata\' not present in SubscriptionResponse JSON')
        if 'entity' in _dict:
            args['entity'] = SubscriptionResponseEntity.from_dict(_dict.get('entity'))
        else:
            raise ValueError('Required property \'entity\' not present in SubscriptionResponse JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SubscriptionResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata.to_dict()
        if hasattr(self, 'entity') and self.entity is not None:
            _dict['entity'] = self.entity.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this SubscriptionResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'SubscriptionResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'SubscriptionResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class SubscriptionResponseCollection():
    """
    SubscriptionResponseCollection.

    :attr List[SubscriptionResponse] subscriptions:
    """

    def __init__(self,
                 subscriptions: List['SubscriptionResponse']) -> None:
        """
        Initialize a SubscriptionResponseCollection object.

        :param List[SubscriptionResponse] subscriptions:
        """
        self.subscriptions = subscriptions

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'SubscriptionResponseCollection':
        """Initialize a SubscriptionResponseCollection object from a json dictionary."""
        args = {}
        if 'subscriptions' in _dict:
            args['subscriptions'] = [SubscriptionResponse.from_dict(x) for x in _dict.get('subscriptions')]
        else:
            raise ValueError('Required property \'subscriptions\' not present in SubscriptionResponseCollection JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SubscriptionResponseCollection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'subscriptions') and self.subscriptions is not None:
            _dict['subscriptions'] = [x.to_dict() for x in self.subscriptions]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this SubscriptionResponseCollection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'SubscriptionResponseCollection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'SubscriptionResponseCollection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class SubscriptionResponseEntity():
    """
    SubscriptionResponseEntity.

    :attr str data_mart_id:
    :attr str service_provider_id:
    :attr Asset asset:
    :attr AssetProperties asset_properties: (optional) Additional asset properties
          (subject of discovery if not provided when creating the subscription).
    :attr AssetDeployment deployment:
    :attr IntegratedSystemReference integration_reference: (optional) Integrated
          System reference.
    :attr RiskEvaluationStatus risk_evaluation_status: (optional)
    :attr AnalyticsEngine analytics_engine: (optional)
    :attr List[DataSource] data_sources: (optional)
    :attr Status status: (optional)
    """

    def __init__(self,
                 data_mart_id: str,
                 service_provider_id: str,
                 asset: 'Asset',
                 deployment: 'AssetDeployment',
                 *,
                 asset_properties: 'AssetProperties' = None,
                 integration_reference: 'IntegratedSystemReference' = None,
                 risk_evaluation_status: 'RiskEvaluationStatus' = None,
                 analytics_engine: 'AnalyticsEngine' = None,
                 data_sources: List['DataSource'] = None,
                 status: 'Status' = None) -> None:
        """
        Initialize a SubscriptionResponseEntity object.

        :param str data_mart_id:
        :param str service_provider_id:
        :param Asset asset:
        :param AssetDeployment deployment:
        :param AssetProperties asset_properties: (optional) Additional asset
               properties (subject of discovery if not provided when creating the
               subscription).
        :param IntegratedSystemReference integration_reference: (optional)
               Integrated System reference.
        :param RiskEvaluationStatus risk_evaluation_status: (optional)
        :param AnalyticsEngine analytics_engine: (optional)
        :param List[DataSource] data_sources: (optional)
        :param Status status: (optional)
        """
        self.data_mart_id = data_mart_id
        self.service_provider_id = service_provider_id
        self.asset = asset
        self.asset_properties = asset_properties
        self.deployment = deployment
        self.integration_reference = integration_reference
        self.risk_evaluation_status = risk_evaluation_status
        self.analytics_engine = analytics_engine
        self.data_sources = data_sources
        self.status = status

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'SubscriptionResponseEntity':
        """Initialize a SubscriptionResponseEntity object from a json dictionary."""
        args = {}
        if 'data_mart_id' in _dict:
            args['data_mart_id'] = _dict.get('data_mart_id')
        else:
            raise ValueError('Required property \'data_mart_id\' not present in SubscriptionResponseEntity JSON')
        if 'service_provider_id' in _dict:
            args['service_provider_id'] = _dict.get('service_provider_id')
        else:
            raise ValueError('Required property \'service_provider_id\' not present in SubscriptionResponseEntity JSON')
        if 'asset' in _dict:
            args['asset'] = Asset.from_dict(_dict.get('asset'))
        else:
            raise ValueError('Required property \'asset\' not present in SubscriptionResponseEntity JSON')
        if 'asset_properties' in _dict:
            args['asset_properties'] = AssetProperties.from_dict(_dict.get('asset_properties'))
        if 'deployment' in _dict:
            args['deployment'] = AssetDeployment.from_dict(_dict.get('deployment'))
        else:
            raise ValueError('Required property \'deployment\' not present in SubscriptionResponseEntity JSON')
        if 'integration_reference' in _dict:
            args['integration_reference'] = IntegratedSystemReference.from_dict(_dict.get('integration_reference'))
        if 'risk_evaluation_status' in _dict:
            args['risk_evaluation_status'] = RiskEvaluationStatus.from_dict(_dict.get('risk_evaluation_status'))
        if 'analytics_engine' in _dict:
            args['analytics_engine'] = AnalyticsEngine.from_dict(_dict.get('analytics_engine'))
        if 'data_sources' in _dict:
            args['data_sources'] = [DataSource.from_dict(x) for x in _dict.get('data_sources')]
        if 'status' in _dict:
            args['status'] = Status.from_dict(_dict.get('status'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SubscriptionResponseEntity object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'data_mart_id') and self.data_mart_id is not None:
            _dict['data_mart_id'] = self.data_mart_id
        if hasattr(self, 'service_provider_id') and self.service_provider_id is not None:
            _dict['service_provider_id'] = self.service_provider_id
        if hasattr(self, 'asset') and self.asset is not None:
            _dict['asset'] = self.asset.to_dict()
        if hasattr(self, 'asset_properties') and self.asset_properties is not None:
            _dict['asset_properties'] = self.asset_properties.to_dict()
        if hasattr(self, 'deployment') and self.deployment is not None:
            _dict['deployment'] = self.deployment.to_dict()
        if hasattr(self, 'integration_reference') and self.integration_reference is not None:
            _dict['integration_reference'] = self.integration_reference.to_dict()
        if hasattr(self, 'risk_evaluation_status') and self.risk_evaluation_status is not None:
            _dict['risk_evaluation_status'] = self.risk_evaluation_status.to_dict()
        if hasattr(self, 'analytics_engine') and self.analytics_engine is not None:
            _dict['analytics_engine'] = self.analytics_engine.to_dict()
        if hasattr(self, 'data_sources') and self.data_sources is not None:
            _dict['data_sources'] = [x.to_dict() for x in self.data_sources]
        if hasattr(self, 'status') and self.status is not None:
            _dict['status'] = self.status.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this SubscriptionResponseEntity object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'SubscriptionResponseEntity') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'SubscriptionResponseEntity') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class Target():
    """
    Target.

    :attr str target_type: Type of the target (e.g. subscription, business
          application, ...).
    :attr str target_id: ID of the data set target (e.g. subscription ID, business
          application ID, ...).
    """

    def __init__(self,
                 target_type: str,
                 target_id: str) -> None:
        """
        Initialize a Target object.

        :param str target_type: Type of the target (e.g. subscription, business
               application, ...).
        :param str target_id: ID of the data set target (e.g. subscription ID,
               business application ID, ...).
        """
        self.target_type = target_type
        self.target_id = target_id

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'Target':
        """Initialize a Target object from a json dictionary."""
        args = {}
        if 'target_type' in _dict:
            args['target_type'] = _dict.get('target_type')
        else:
            raise ValueError('Required property \'target_type\' not present in Target JSON')
        if 'target_id' in _dict:
            args['target_id'] = _dict.get('target_id')
        else:
            raise ValueError('Required property \'target_id\' not present in Target JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a Target object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'target_type') and self.target_type is not None:
            _dict['target_type'] = self.target_type
        if hasattr(self, 'target_id') and self.target_id is not None:
            _dict['target_id'] = self.target_id
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this Target object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'Target') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'Target') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class TargetTypeEnum(str, Enum):
        """
        Type of the target (e.g. subscription, business application, ...).
        """
        SUBSCRIPTION = 'subscription'
        BUSINESS_APPLICATION = 'business_application'
        INSTANCE = 'instance'
        DATA_MART = 'data_mart'


class ThresholdConditionObject():
    """
    ThresholdConditionObject.

    :attr str type:
    :attr str key:
    :attr str value:
    """

    def __init__(self,
                 type: str,
                 key: str,
                 value: str) -> None:
        """
        Initialize a ThresholdConditionObject object.

        :param str type:
        :param str key:
        :param str value:
        """
        self.type = type
        self.key = key
        self.value = value

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ThresholdConditionObject':
        """Initialize a ThresholdConditionObject object from a json dictionary."""
        args = {}
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in ThresholdConditionObject JSON')
        if 'key' in _dict:
            args['key'] = _dict.get('key')
        else:
            raise ValueError('Required property \'key\' not present in ThresholdConditionObject JSON')
        if 'value' in _dict:
            args['value'] = _dict.get('value')
        else:
            raise ValueError('Required property \'value\' not present in ThresholdConditionObject JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ThresholdConditionObject object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'key') and self.key is not None:
            _dict['key'] = self.key
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ThresholdConditionObject object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ThresholdConditionObject') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ThresholdConditionObject') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class TypeEnum(str, Enum):
        """
        type.
        """
        TAG = 'tag'


class TrainingDataReference():
    """
    TrainingDataReference.

    :attr str type: Type of the storage.
    :attr TrainingDataReferenceLocation location: training data set location.
    :attr TrainingDataReferenceConnection connection: training data set connection
          credentials.
    :attr str name: (optional)
    """

    def __init__(self,
                 type: str,
                 location: 'TrainingDataReferenceLocation',
                 connection: 'TrainingDataReferenceConnection',
                 *,
                 name: str = None) -> None:
        """
        Initialize a TrainingDataReference object.

        :param str type: Type of the storage.
        :param TrainingDataReferenceLocation location: training data set location.
        :param TrainingDataReferenceConnection connection: training data set
               connection credentials.
        :param str name: (optional)
        """
        self.type = type
        self.location = location
        self.connection = connection
        self.name = name

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'TrainingDataReference':
        """Initialize a TrainingDataReference object from a json dictionary."""
        args = {}
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in TrainingDataReference JSON')
        if 'location' in _dict:
            args['location'] = _dict.get('location')
        else:
            raise ValueError('Required property \'location\' not present in TrainingDataReference JSON')
        if 'connection' in _dict:
            args['connection'] = _dict.get('connection')
        else:
            raise ValueError('Required property \'connection\' not present in TrainingDataReference JSON')
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a TrainingDataReference object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'location') and self.location is not None:
            if isinstance(self.location, dict):
                _dict['location'] = self.location
            else:
                _dict['location'] = self.location.to_dict()
        if hasattr(self, 'connection') and self.connection is not None:
            if isinstance(self.connection, dict):
                _dict['connection'] = self.connection
            else:
                _dict['connection'] = self.connection.to_dict()
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this TrainingDataReference object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'TrainingDataReference') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'TrainingDataReference') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class TypeEnum(str, Enum):
        """
        Type of the storage.
        """
        DB2 = 'db2'
        COS = 'cos'
        DATASET = 'dataset'
        FILE_ASSET = 'file_asset'


class TrainingDataReferenceConnection():
    """
    training data set connection credentials.

    """

    def __init__(self) -> None:
        """
        Initialize a TrainingDataReferenceConnection object.

        """
        msg = "Cannot instantiate base class. Instead, instantiate one of the defined subclasses: {0}".format(
                  ", ".join(['DB2TrainingDataReferenceConnection', 'COSTrainingDataReferenceConnection']))
        raise Exception(msg)

class TrainingDataReferenceLocation():
    """
    training data set location.

    """

    def __init__(self) -> None:
        """
        Initialize a TrainingDataReferenceLocation object.

        """
        msg = "Cannot instantiate base class. Instead, instantiate one of the defined subclasses: {0}".format(
                  ", ".join(['DB2TrainingDataReferenceLocation', 'COSTrainingDataReferenceLocation', 'DatasetTrainingDataReferenceLocation', 'FileAssetTrainingDataReferenceLocation']))
        raise Exception(msg)

class UserPreferencesGetResponse():
    """
    UserPreferencesGetResponse.

    """

    def __init__(self) -> None:
        """
        Initialize a UserPreferencesGetResponse object.

        """
        msg = "Cannot instantiate base class. Instead, instantiate one of the defined subclasses: {0}".format(
                  ", ".join(['UserPreferencesGetResponseUserPreferenceValueObject', 'UserPreferencesGetResponseUserPreferenceValueString']))
        raise Exception(msg)

class UserPreferencesPatchResponse():
    """
    UserPreferencesPatchResponse.

    """

    def __init__(self) -> None:
        """
        Initialize a UserPreferencesPatchResponse object.

        """

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'UserPreferencesPatchResponse':
        """Initialize a UserPreferencesPatchResponse object from a json dictionary."""
        return cls(**_dict)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a UserPreferencesPatchResponse object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        return vars(self)

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this UserPreferencesPatchResponse object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'UserPreferencesPatchResponse') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'UserPreferencesPatchResponse') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class UserPreferencesUpdateRequest():
    """
    UserPreferencesUpdateRequest.

    """

    def __init__(self) -> None:
        """
        Initialize a UserPreferencesUpdateRequest object.

        """
        msg = "Cannot instantiate base class. Instead, instantiate one of the defined subclasses: {0}".format(
                  ", ".join(['UserPreferencesUpdateRequestUserPreferenceValueObject', 'UserPreferencesUpdateRequestUserPreferenceValueString']))
        raise Exception(msg)

class AzureCredentials(MLCredentials):
    """
    AzureCredentials.

    :attr str token: (optional)
    :attr str username: (optional)
    :attr str password: (optional)
    :attr str subscription_id: (optional)
    :attr str client_id: (optional)
    :attr str client_secret: (optional)
    :attr str tenant: (optional)
    :attr List[AzureWorkspaceCredentials] workspaces: (optional)
    """

    # The set of defined properties for the class
    _properties = frozenset(['token', 'username', 'password', 'subscription_id', 'client_id', 'client_secret', 'tenant', 'workspaces'])

    def __init__(self,
                 *,
                 token: str = None,
                 username: str = None,
                 password: str = None,
                 subscription_id: str = None,
                 client_id: str = None,
                 client_secret: str = None,
                 tenant: str = None,
                 workspaces: List['AzureWorkspaceCredentials'] = None,
                 **kwargs) -> None:
        """
        Initialize a AzureCredentials object.

        :param str token: (optional)
        :param str username: (optional)
        :param str password: (optional)
        :param str subscription_id: (optional)
        :param str client_id: (optional)
        :param str client_secret: (optional)
        :param str tenant: (optional)
        :param List[AzureWorkspaceCredentials] workspaces: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        # pylint: disable=super-init-not-called
        self.token = token
        self.username = username
        self.password = password
        self.subscription_id = subscription_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant = tenant
        self.workspaces = workspaces
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'AzureCredentials':
        """Initialize a AzureCredentials object from a json dictionary."""
        args = {}
        if 'token' in _dict:
            args['token'] = _dict.get('token')
        if 'username' in _dict:
            args['username'] = _dict.get('username')
        if 'password' in _dict:
            args['password'] = _dict.get('password')
        if 'subscription_id' in _dict:
            args['subscription_id'] = _dict.get('subscription_id')
        if 'client_id' in _dict:
            args['client_id'] = _dict.get('client_id')
        if 'client_secret' in _dict:
            args['client_secret'] = _dict.get('client_secret')
        if 'tenant' in _dict:
            args['tenant'] = _dict.get('tenant')
        if 'workspaces' in _dict:
            args['workspaces'] = [AzureWorkspaceCredentials.from_dict(x) for x in _dict.get('workspaces')]
        args.update({k:v for (k, v) in _dict.items() if k not in cls._properties})
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a AzureCredentials object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'token') and self.token is not None:
            _dict['token'] = self.token
        if hasattr(self, 'username') and self.username is not None:
            _dict['username'] = self.username
        if hasattr(self, 'password') and self.password is not None:
            _dict['password'] = self.password
        if hasattr(self, 'subscription_id') and self.subscription_id is not None:
            _dict['subscription_id'] = self.subscription_id
        if hasattr(self, 'client_id') and self.client_id is not None:
            _dict['client_id'] = self.client_id
        if hasattr(self, 'client_secret') and self.client_secret is not None:
            _dict['client_secret'] = self.client_secret
        if hasattr(self, 'tenant') and self.tenant is not None:
            _dict['tenant'] = self.tenant
        if hasattr(self, 'workspaces') and self.workspaces is not None:
            _dict['workspaces'] = [x.to_dict() for x in self.workspaces]
        for _key in [k for k in vars(self).keys() if k not in AzureCredentials._properties]:
            if getattr(self, _key, None) is not None:
                _dict[_key] = getattr(self, _key)
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this AzureCredentials object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'AzureCredentials') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'AzureCredentials') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class COSTrainingDataReferenceConnection(TrainingDataReferenceConnection):
    """
    COSTrainingDataReferenceConnection.

    :attr str resource_instance_id:
    :attr str url:
    :attr str api_key:
    :attr str iam_url: (optional)
    """

    def __init__(self,
                 resource_instance_id: str,
                 url: str,
                 api_key: str,
                 *,
                 iam_url: str = None) -> None:
        """
        Initialize a COSTrainingDataReferenceConnection object.

        :param str resource_instance_id:
        :param str url:
        :param str api_key:
        :param str iam_url: (optional)
        """
        # pylint: disable=super-init-not-called
        self.resource_instance_id = resource_instance_id
        self.url = url
        self.api_key = api_key
        self.iam_url = iam_url

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'COSTrainingDataReferenceConnection':
        """Initialize a COSTrainingDataReferenceConnection object from a json dictionary."""
        args = {}
        if 'resource_instance_id' in _dict:
            args['resource_instance_id'] = _dict.get('resource_instance_id')
        else:
            raise ValueError('Required property \'resource_instance_id\' not present in COSTrainingDataReferenceConnection JSON')
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        else:
            raise ValueError('Required property \'url\' not present in COSTrainingDataReferenceConnection JSON')
        if 'api_key' in _dict:
            args['api_key'] = _dict.get('api_key')
        else:
            raise ValueError('Required property \'api_key\' not present in COSTrainingDataReferenceConnection JSON')
        if 'iam_url' in _dict:
            args['iam_url'] = _dict.get('iam_url')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a COSTrainingDataReferenceConnection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'resource_instance_id') and self.resource_instance_id is not None:
            _dict['resource_instance_id'] = self.resource_instance_id
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        if hasattr(self, 'api_key') and self.api_key is not None:
            _dict['api_key'] = self.api_key
        if hasattr(self, 'iam_url') and self.iam_url is not None:
            _dict['iam_url'] = self.iam_url
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this COSTrainingDataReferenceConnection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'COSTrainingDataReferenceConnection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'COSTrainingDataReferenceConnection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class COSTrainingDataReferenceLocation(TrainingDataReferenceLocation):
    """
    COS file location.

    :attr str bucket:
    :attr str file_name:
    :attr bool firstlineheader: (optional)
    :attr str infer_schema: (optional)
    :attr str file_format: (optional)
    """

    def __init__(self,
                 bucket: str,
                 file_name: str,
                 *,
                 firstlineheader: bool = None,
                 infer_schema: str = None,
                 file_format: str = None) -> None:
        """
        Initialize a COSTrainingDataReferenceLocation object.

        :param str bucket:
        :param str file_name:
        :param bool firstlineheader: (optional)
        :param str infer_schema: (optional)
        :param str file_format: (optional)
        """
        # pylint: disable=super-init-not-called
        self.bucket = bucket
        self.file_name = file_name
        self.firstlineheader = firstlineheader
        self.infer_schema = infer_schema
        self.file_format = file_format

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'COSTrainingDataReferenceLocation':
        """Initialize a COSTrainingDataReferenceLocation object from a json dictionary."""
        args = {}
        if 'bucket' in _dict:
            args['bucket'] = _dict.get('bucket')
        else:
            raise ValueError('Required property \'bucket\' not present in COSTrainingDataReferenceLocation JSON')
        if 'file_name' in _dict:
            args['file_name'] = _dict.get('file_name')
        else:
            raise ValueError('Required property \'file_name\' not present in COSTrainingDataReferenceLocation JSON')
        if 'firstlineheader' in _dict:
            args['firstlineheader'] = _dict.get('firstlineheader')
        if 'infer_schema' in _dict:
            args['infer_schema'] = _dict.get('infer_schema')
        if 'file_format' in _dict:
            args['file_format'] = _dict.get('file_format')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a COSTrainingDataReferenceLocation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'bucket') and self.bucket is not None:
            _dict['bucket'] = self.bucket
        if hasattr(self, 'file_name') and self.file_name is not None:
            _dict['file_name'] = self.file_name
        if hasattr(self, 'firstlineheader') and self.firstlineheader is not None:
            _dict['firstlineheader'] = self.firstlineheader
        if hasattr(self, 'infer_schema') and self.infer_schema is not None:
            _dict['infer_schema'] = self.infer_schema
        if hasattr(self, 'file_format') and self.file_format is not None:
            _dict['file_format'] = self.file_format
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this COSTrainingDataReferenceLocation object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'COSTrainingDataReferenceLocation') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'COSTrainingDataReferenceLocation') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class FileFormatEnum(str, Enum):
        """
        file_format.
        """
        CSV = 'csv'


class CustomCredentials(MLCredentials):
    """
    CustomCredentials.

    :attr str url: (optional)
    :attr str username: (optional)
    :attr str password: (optional)
    :attr str apikey: (optional)
    :attr str auth_url: (optional)
    :attr str auth_type: (optional)
    :attr str auth_provider: (optional)
    """

    # The set of defined properties for the class
    _properties = frozenset(['url', 'username', 'password', 'apikey', 'auth_url', 'auth_type', 'auth_provider'])

    def __init__(self,
                 *,
                 url: str = None,
                 username: str = None,
                 password: str = None,
                 apikey: str = None,
                 auth_url: str = None,
                 auth_type: str = None,
                 auth_provider: str = None,
                 **kwargs) -> None:
        """
        Initialize a CustomCredentials object.

        :param str url: (optional)
        :param str username: (optional)
        :param str password: (optional)
        :param str apikey: (optional)
        :param str auth_url: (optional)
        :param str auth_type: (optional)
        :param str auth_provider: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        # pylint: disable=super-init-not-called
        self.url = url
        self.username = username
        self.password = password
        self.apikey = apikey
        self.auth_url = auth_url
        self.auth_type = auth_type
        self.auth_provider = auth_provider
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'CustomCredentials':
        """Initialize a CustomCredentials object from a json dictionary."""
        args = {}
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        if 'username' in _dict:
            args['username'] = _dict.get('username')
        if 'password' in _dict:
            args['password'] = _dict.get('password')
        if 'apikey' in _dict:
            args['apikey'] = _dict.get('apikey')
        if 'auth_url' in _dict:
            args['auth_url'] = _dict.get('auth_url')
        if 'auth_type' in _dict:
            args['auth_type'] = _dict.get('auth_type')
        if 'auth_provider' in _dict:
            args['auth_provider'] = _dict.get('auth_provider')
        args.update({k:v for (k, v) in _dict.items() if k not in cls._properties})
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a CustomCredentials object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        if hasattr(self, 'username') and self.username is not None:
            _dict['username'] = self.username
        if hasattr(self, 'password') and self.password is not None:
            _dict['password'] = self.password
        if hasattr(self, 'apikey') and self.apikey is not None:
            _dict['apikey'] = self.apikey
        if hasattr(self, 'auth_url') and self.auth_url is not None:
            _dict['auth_url'] = self.auth_url
        if hasattr(self, 'auth_type') and self.auth_type is not None:
            _dict['auth_type'] = self.auth_type
        if hasattr(self, 'auth_provider') and self.auth_provider is not None:
            _dict['auth_provider'] = self.auth_provider
        for _key in [k for k in vars(self).keys() if k not in CustomCredentials._properties]:
            if getattr(self, _key, None) is not None:
                _dict[_key] = getattr(self, _key)
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this CustomCredentials object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'CustomCredentials') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'CustomCredentials') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class AuthTypeEnum(str, Enum):
        """
        auth_type.
        """
        BASIC = 'basic'
        API_KEY = 'api_key'


    class AuthProviderEnum(str, Enum):
        """
        auth_provider.
        """
        CLOUD = 'cloud'
        CPD = 'cpd'


class DB2TrainingDataReferenceConnection(TrainingDataReferenceConnection):
    """
    DB2TrainingDataReferenceConnection.

    :attr str hostname:
    :attr str username:
    :attr str password:
    :attr str database_name:
    :attr int port: (optional)
    :attr bool ssl: (optional)
    :attr str certificate_base64: (optional) DER-encoded certificate in Base64
          encoding. The decoded content must be bound at the beginning by -----BEGIN
          CERTIFICATE----- and at the end by -----END CERTIFICATE-----.
    :attr str connection_string: (optional)
    """

    def __init__(self,
                 hostname: str,
                 username: str,
                 password: str,
                 database_name: str,
                 *,
                 port: int = None,
                 ssl: bool = None,
                 certificate_base64: str = None,
                 connection_string: str = None) -> None:
        """
        Initialize a DB2TrainingDataReferenceConnection object.

        :param str hostname:
        :param str username:
        :param str password:
        :param str database_name:
        :param int port: (optional)
        :param bool ssl: (optional)
        :param str certificate_base64: (optional) DER-encoded certificate in Base64
               encoding. The decoded content must be bound at the beginning by -----BEGIN
               CERTIFICATE----- and at the end by -----END CERTIFICATE-----.
        :param str connection_string: (optional)
        """
        # pylint: disable=super-init-not-called
        self.hostname = hostname
        self.username = username
        self.password = password
        self.database_name = database_name
        self.port = port
        self.ssl = ssl
        self.certificate_base64 = certificate_base64
        self.connection_string = connection_string

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DB2TrainingDataReferenceConnection':
        """Initialize a DB2TrainingDataReferenceConnection object from a json dictionary."""
        args = {}
        if 'hostname' in _dict:
            args['hostname'] = _dict.get('hostname')
        else:
            raise ValueError('Required property \'hostname\' not present in DB2TrainingDataReferenceConnection JSON')
        if 'username' in _dict:
            args['username'] = _dict.get('username')
        else:
            raise ValueError('Required property \'username\' not present in DB2TrainingDataReferenceConnection JSON')
        if 'password' in _dict:
            args['password'] = _dict.get('password')
        else:
            raise ValueError('Required property \'password\' not present in DB2TrainingDataReferenceConnection JSON')
        if 'database_name' in _dict:
            args['database_name'] = _dict.get('database_name')
        else:
            raise ValueError('Required property \'database_name\' not present in DB2TrainingDataReferenceConnection JSON')
        if 'port' in _dict:
            args['port'] = _dict.get('port')
        if 'ssl' in _dict:
            args['ssl'] = _dict.get('ssl')
        if 'certificate_base64' in _dict:
            args['certificate_base64'] = _dict.get('certificate_base64')
        if 'connection_string' in _dict:
            args['connection_string'] = _dict.get('connection_string')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DB2TrainingDataReferenceConnection object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'hostname') and self.hostname is not None:
            _dict['hostname'] = self.hostname
        if hasattr(self, 'username') and self.username is not None:
            _dict['username'] = self.username
        if hasattr(self, 'password') and self.password is not None:
            _dict['password'] = self.password
        if hasattr(self, 'database_name') and self.database_name is not None:
            _dict['database_name'] = self.database_name
        if hasattr(self, 'port') and self.port is not None:
            _dict['port'] = self.port
        if hasattr(self, 'ssl') and self.ssl is not None:
            _dict['ssl'] = self.ssl
        if hasattr(self, 'certificate_base64') and self.certificate_base64 is not None:
            _dict['certificate_base64'] = self.certificate_base64
        if hasattr(self, 'connection_string') and self.connection_string is not None:
            _dict['connection_string'] = self.connection_string
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DB2TrainingDataReferenceConnection object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DB2TrainingDataReferenceConnection') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DB2TrainingDataReferenceConnection') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DB2TrainingDataReferenceLocation(TrainingDataReferenceLocation):
    """
    DB2 table name.

    :attr str table_name: name of the table.
    :attr str schema_name: (optional) name of the schema.
    """

    def __init__(self,
                 table_name: str,
                 *,
                 schema_name: str = None) -> None:
        """
        Initialize a DB2TrainingDataReferenceLocation object.

        :param str table_name: name of the table.
        :param str schema_name: (optional) name of the schema.
        """
        # pylint: disable=super-init-not-called
        self.table_name = table_name
        self.schema_name = schema_name

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DB2TrainingDataReferenceLocation':
        """Initialize a DB2TrainingDataReferenceLocation object from a json dictionary."""
        args = {}
        if 'table_name' in _dict:
            args['table_name'] = _dict.get('table_name')
        else:
            raise ValueError('Required property \'table_name\' not present in DB2TrainingDataReferenceLocation JSON')
        if 'schema_name' in _dict:
            args['schema_name'] = _dict.get('schema_name')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DB2TrainingDataReferenceLocation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'table_name') and self.table_name is not None:
            _dict['table_name'] = self.table_name
        if hasattr(self, 'schema_name') and self.schema_name is not None:
            _dict['schema_name'] = self.schema_name
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DB2TrainingDataReferenceLocation object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DB2TrainingDataReferenceLocation') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DB2TrainingDataReferenceLocation') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class DatasetTrainingDataReferenceLocation(TrainingDataReferenceLocation):
    """
    WOS dataset id.

    :attr str dataset_id: Dataset id.
    :attr FileTrainingDataReferenceOptions meta: (optional) additional options for
          different types of training data references.
    """

    def __init__(self,
                 dataset_id: str,
                 *,
                 meta: 'FileTrainingDataReferenceOptions' = None) -> None:
        """
        Initialize a DatasetTrainingDataReferenceLocation object.

        :param str dataset_id: Dataset id.
        :param FileTrainingDataReferenceOptions meta: (optional) additional options
               for different types of training data references.
        """
        # pylint: disable=super-init-not-called
        self.dataset_id = dataset_id
        self.meta = meta

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'DatasetTrainingDataReferenceLocation':
        """Initialize a DatasetTrainingDataReferenceLocation object from a json dictionary."""
        args = {}
        if 'dataset_id' in _dict:
            args['dataset_id'] = _dict.get('dataset_id')
        else:
            raise ValueError('Required property \'dataset_id\' not present in DatasetTrainingDataReferenceLocation JSON')
        if 'meta' in _dict:
            args['meta'] = FileTrainingDataReferenceOptions.from_dict(_dict.get('meta'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a DatasetTrainingDataReferenceLocation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'dataset_id') and self.dataset_id is not None:
            _dict['dataset_id'] = self.dataset_id
        if hasattr(self, 'meta') and self.meta is not None:
            _dict['meta'] = self.meta.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this DatasetTrainingDataReferenceLocation object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'DatasetTrainingDataReferenceLocation') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'DatasetTrainingDataReferenceLocation') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class FileAssetTrainingDataReferenceLocation(TrainingDataReferenceLocation):
    """
    File data asset reference location.

    :attr str project_id: (optional) Project id.
    :attr str asset_id: (optional) File data asset id.
    :attr str asset_href: File data asset reference.
    :attr FileTrainingDataReferenceOptions meta: (optional) additional options for
          different types of training data references.
    """

    def __init__(self,
                 asset_href: str,
                 *,
                 project_id: str = None,
                 asset_id: str = None,
                 meta: 'FileTrainingDataReferenceOptions' = None) -> None:
        """
        Initialize a FileAssetTrainingDataReferenceLocation object.

        :param str asset_href: File data asset reference.
        :param str project_id: (optional) Project id.
        :param str asset_id: (optional) File data asset id.
        :param FileTrainingDataReferenceOptions meta: (optional) additional options
               for different types of training data references.
        """
        # pylint: disable=super-init-not-called
        self.project_id = project_id
        self.asset_id = asset_id
        self.asset_href = asset_href
        self.meta = meta

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'FileAssetTrainingDataReferenceLocation':
        """Initialize a FileAssetTrainingDataReferenceLocation object from a json dictionary."""
        args = {}
        if 'project_id' in _dict:
            args['project_id'] = _dict.get('project_id')
        if 'asset_id' in _dict:
            args['asset_id'] = _dict.get('asset_id')
        if 'asset_href' in _dict:
            args['asset_href'] = _dict.get('asset_href')
        else:
            raise ValueError('Required property \'asset_href\' not present in FileAssetTrainingDataReferenceLocation JSON')
        if 'meta' in _dict:
            args['meta'] = FileTrainingDataReferenceOptions.from_dict(_dict.get('meta'))
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a FileAssetTrainingDataReferenceLocation object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'project_id') and self.project_id is not None:
            _dict['project_id'] = self.project_id
        if hasattr(self, 'asset_id') and self.asset_id is not None:
            _dict['asset_id'] = self.asset_id
        if hasattr(self, 'asset_href') and self.asset_href is not None:
            _dict['asset_href'] = self.asset_href
        if hasattr(self, 'meta') and self.meta is not None:
            _dict['meta'] = self.meta.to_dict()
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this FileAssetTrainingDataReferenceLocation object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'FileAssetTrainingDataReferenceLocation') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'FileAssetTrainingDataReferenceLocation') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class PrimaryStorageCredentialsLong(PrimaryStorageCredentials):
    """
    PrimaryStorageCredentialsLong.

    :attr str hostname:
    :attr str username:
    :attr str password:
    :attr str db:
    :attr int port: (optional)
    :attr bool ssl: (optional)
    :attr str sslmode: (optional) (postgresql only).
    :attr str certificate_base64: (optional) DER-encoded certificate in Base64
          encoding. The decoded content must be bound at the beginning by -----BEGIN
          CERTIFICATE----- and at the end by -----END CERTIFICATE-----.
    :attr dict additional_properties: (optional) any additional properties to be
          included in connection url.
    """

    def __init__(self,
                 hostname: str,
                 username: str,
                 password: str,
                 db: str,
                 *,
                 port: int = None,
                 ssl: bool = None,
                 sslmode: str = None,
                 certificate_base64: str = None,
                 additional_properties: dict = None) -> None:
        """
        Initialize a PrimaryStorageCredentialsLong object.

        :param str hostname:
        :param str username:
        :param str password:
        :param str db:
        :param int port: (optional)
        :param bool ssl: (optional)
        :param str sslmode: (optional) (postgresql only).
        :param str certificate_base64: (optional) DER-encoded certificate in Base64
               encoding. The decoded content must be bound at the beginning by -----BEGIN
               CERTIFICATE----- and at the end by -----END CERTIFICATE-----.
        :param dict additional_properties: (optional) any additional properties to
               be included in connection url.
        """
        # pylint: disable=super-init-not-called
        self.hostname = hostname
        self.username = username
        self.password = password
        self.db = db
        self.port = port
        self.ssl = ssl
        self.sslmode = sslmode
        self.certificate_base64 = certificate_base64
        self.additional_properties = additional_properties

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'PrimaryStorageCredentialsLong':
        """Initialize a PrimaryStorageCredentialsLong object from a json dictionary."""
        args = {}
        if 'hostname' in _dict:
            args['hostname'] = _dict.get('hostname')
        else:
            raise ValueError('Required property \'hostname\' not present in PrimaryStorageCredentialsLong JSON')
        if 'username' in _dict:
            args['username'] = _dict.get('username')
        else:
            raise ValueError('Required property \'username\' not present in PrimaryStorageCredentialsLong JSON')
        if 'password' in _dict:
            args['password'] = _dict.get('password')
        else:
            raise ValueError('Required property \'password\' not present in PrimaryStorageCredentialsLong JSON')
        if 'db' in _dict:
            args['db'] = _dict.get('db')
        else:
            raise ValueError('Required property \'db\' not present in PrimaryStorageCredentialsLong JSON')
        if 'port' in _dict:
            args['port'] = _dict.get('port')
        if 'ssl' in _dict:
            args['ssl'] = _dict.get('ssl')
        if 'sslmode' in _dict:
            args['sslmode'] = _dict.get('sslmode')
        if 'certificate_base64' in _dict:
            args['certificate_base64'] = _dict.get('certificate_base64')
        if 'additional_properties' in _dict:
            args['additional_properties'] = _dict.get('additional_properties')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a PrimaryStorageCredentialsLong object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'hostname') and self.hostname is not None:
            _dict['hostname'] = self.hostname
        if hasattr(self, 'username') and self.username is not None:
            _dict['username'] = self.username
        if hasattr(self, 'password') and self.password is not None:
            _dict['password'] = self.password
        if hasattr(self, 'db') and self.db is not None:
            _dict['db'] = self.db
        if hasattr(self, 'port') and self.port is not None:
            _dict['port'] = self.port
        if hasattr(self, 'ssl') and self.ssl is not None:
            _dict['ssl'] = self.ssl
        if hasattr(self, 'sslmode') and self.sslmode is not None:
            _dict['sslmode'] = self.sslmode
        if hasattr(self, 'certificate_base64') and self.certificate_base64 is not None:
            _dict['certificate_base64'] = self.certificate_base64
        if hasattr(self, 'additional_properties') and self.additional_properties is not None:
            _dict['additional_properties'] = self.additional_properties
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this PrimaryStorageCredentialsLong object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'PrimaryStorageCredentialsLong') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'PrimaryStorageCredentialsLong') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class PrimaryStorageCredentialsShort(PrimaryStorageCredentials):
    """
    PrimaryStorageCredentialsShort.

    :attr str uri:
    """

    def __init__(self,
                 uri: str) -> None:
        """
        Initialize a PrimaryStorageCredentialsShort object.

        :param str uri:
        """
        # pylint: disable=super-init-not-called
        self.uri = uri

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'PrimaryStorageCredentialsShort':
        """Initialize a PrimaryStorageCredentialsShort object from a json dictionary."""
        args = {}
        if 'uri' in _dict:
            args['uri'] = _dict.get('uri')
        else:
            raise ValueError('Required property \'uri\' not present in PrimaryStorageCredentialsShort JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a PrimaryStorageCredentialsShort object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'uri') and self.uri is not None:
            _dict['uri'] = self.uri
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this PrimaryStorageCredentialsShort object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'PrimaryStorageCredentialsShort') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'PrimaryStorageCredentialsShort') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class RecordsListResponseDataRecordsResponseCollectionDict(RecordsListResponse):
    """
    dict format.

    :attr int total_count: (optional) Number of all rows which satisfy the query. It
          is calculated and returned when include_total_count query param is set to
          `true`.
    :attr List[DataRecordResponse] records:
    """

    def __init__(self,
                 records: List['DataRecordResponse'],
                 *,
                 total_count: int = None) -> None:
        """
        Initialize a RecordsListResponseDataRecordsResponseCollectionDict object.

        :param List[DataRecordResponse] records:
        :param int total_count: (optional) Number of all rows which satisfy the
               query. It is calculated and returned when include_total_count query param
               is set to `true`.
        """
        # pylint: disable=super-init-not-called
        self.total_count = total_count
        self.records = records

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'RecordsListResponseDataRecordsResponseCollectionDict':
        """Initialize a RecordsListResponseDataRecordsResponseCollectionDict object from a json dictionary."""
        args = {}
        if 'total_count' in _dict:
            args['total_count'] = _dict.get('total_count')
        if 'records' in _dict:
            args['records'] = [DataRecordResponse.from_dict(x) for x in _dict.get('records')]
        else:
            raise ValueError('Required property \'records\' not present in RecordsListResponseDataRecordsResponseCollectionDict JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a RecordsListResponseDataRecordsResponseCollectionDict object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'total_count') and self.total_count is not None:
            _dict['total_count'] = self.total_count
        if hasattr(self, 'records') and self.records is not None:
            _dict['records'] = [x.to_dict() for x in self.records]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this RecordsListResponseDataRecordsResponseCollectionDict object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'RecordsListResponseDataRecordsResponseCollectionDict') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'RecordsListResponseDataRecordsResponseCollectionDict') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class RecordsListResponseDataRecordsResponseCollectionList(RecordsListResponse):
    """
    list format.

    :attr int total_count: (optional) Number of all rows which satisfy the query. It
          is calculated and returned when include_total_count query param is set to
          `true`.
    :attr List[DataRecordResponseList] records:
    """

    def __init__(self,
                 records: List['DataRecordResponseList'],
                 *,
                 total_count: int = None) -> None:
        """
        Initialize a RecordsListResponseDataRecordsResponseCollectionList object.

        :param List[DataRecordResponseList] records:
        :param int total_count: (optional) Number of all rows which satisfy the
               query. It is calculated and returned when include_total_count query param
               is set to `true`.
        """
        # pylint: disable=super-init-not-called
        self.total_count = total_count
        self.records = records

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'RecordsListResponseDataRecordsResponseCollectionList':
        """Initialize a RecordsListResponseDataRecordsResponseCollectionList object from a json dictionary."""
        args = {}
        if 'total_count' in _dict:
            args['total_count'] = _dict.get('total_count')
        if 'records' in _dict:
            args['records'] = [DataRecordResponseList.from_dict(x) for x in _dict.get('records')]
        else:
            raise ValueError('Required property \'records\' not present in RecordsListResponseDataRecordsResponseCollectionList JSON')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a RecordsListResponseDataRecordsResponseCollectionList object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'total_count') and self.total_count is not None:
            _dict['total_count'] = self.total_count
        if hasattr(self, 'records') and self.records is not None:
            _dict['records'] = [x.to_dict() for x in self.records]
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this RecordsListResponseDataRecordsResponseCollectionList object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'RecordsListResponseDataRecordsResponseCollectionList') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'RecordsListResponseDataRecordsResponseCollectionList') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class SPSSCredentials(MLCredentials):
    """
    SPSSCredentials.

    :attr str url:
    :attr str username:
    :attr str password:
    """

    # The set of defined properties for the class
    _properties = frozenset(['url', 'username', 'password'])

    def __init__(self,
                 url: str,
                 username: str,
                 password: str,
                 **kwargs) -> None:
        """
        Initialize a SPSSCredentials object.

        :param str url:
        :param str username:
        :param str password:
        :param **kwargs: (optional) Any additional properties.
        """
        # pylint: disable=super-init-not-called
        self.url = url
        self.username = username
        self.password = password
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'SPSSCredentials':
        """Initialize a SPSSCredentials object from a json dictionary."""
        args = {}
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        else:
            raise ValueError('Required property \'url\' not present in SPSSCredentials JSON')
        if 'username' in _dict:
            args['username'] = _dict.get('username')
        else:
            raise ValueError('Required property \'username\' not present in SPSSCredentials JSON')
        if 'password' in _dict:
            args['password'] = _dict.get('password')
        else:
            raise ValueError('Required property \'password\' not present in SPSSCredentials JSON')
        args.update({k:v for (k, v) in _dict.items() if k not in cls._properties})
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SPSSCredentials object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        if hasattr(self, 'username') and self.username is not None:
            _dict['username'] = self.username
        if hasattr(self, 'password') and self.password is not None:
            _dict['password'] = self.password
        for _key in [k for k in vars(self).keys() if k not in SPSSCredentials._properties]:
            if getattr(self, _key, None) is not None:
                _dict[_key] = getattr(self, _key)
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this SPSSCredentials object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'SPSSCredentials') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'SPSSCredentials') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class SageMakerCredentials(MLCredentials):
    """
    SageMakerCredentials.

    :attr str access_key_id:
    :attr str secret_access_key:
    :attr str region: (optional)
    """

    # The set of defined properties for the class
    _properties = frozenset(['access_key_id', 'secret_access_key', 'region'])

    def __init__(self,
                 access_key_id: str,
                 secret_access_key: str,
                 *,
                 region: str = None,
                 **kwargs) -> None:
        """
        Initialize a SageMakerCredentials object.

        :param str access_key_id:
        :param str secret_access_key:
        :param str region: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        # pylint: disable=super-init-not-called
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region = region
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'SageMakerCredentials':
        """Initialize a SageMakerCredentials object from a json dictionary."""
        args = {}
        if 'access_key_id' in _dict:
            args['access_key_id'] = _dict.get('access_key_id')
        else:
            raise ValueError('Required property \'access_key_id\' not present in SageMakerCredentials JSON')
        if 'secret_access_key' in _dict:
            args['secret_access_key'] = _dict.get('secret_access_key')
        else:
            raise ValueError('Required property \'secret_access_key\' not present in SageMakerCredentials JSON')
        if 'region' in _dict:
            args['region'] = _dict.get('region')
        args.update({k:v for (k, v) in _dict.items() if k not in cls._properties})
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SageMakerCredentials object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'access_key_id') and self.access_key_id is not None:
            _dict['access_key_id'] = self.access_key_id
        if hasattr(self, 'secret_access_key') and self.secret_access_key is not None:
            _dict['secret_access_key'] = self.secret_access_key
        if hasattr(self, 'region') and self.region is not None:
            _dict['region'] = self.region
        for _key in [k for k in vars(self).keys() if k not in SageMakerCredentials._properties]:
            if getattr(self, _key, None) is not None:
                _dict[_key] = getattr(self, _key)
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this SageMakerCredentials object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'SageMakerCredentials') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'SageMakerCredentials') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class ScoringEndpointCredentialsAzureScoringEndpointCredentials(ScoringEndpointCredentials):
    """
    ScoringEndpointCredentialsAzureScoringEndpointCredentials.

    :attr str token:
    """

    # The set of defined properties for the class
    _properties = frozenset(['token'])

    def __init__(self,
                 token: str,
                 **kwargs) -> None:
        """
        Initialize a ScoringEndpointCredentialsAzureScoringEndpointCredentials object.

        :param str token:
        :param **kwargs: (optional) Any additional properties.
        """
        # pylint: disable=super-init-not-called
        self.token = token
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'ScoringEndpointCredentialsAzureScoringEndpointCredentials':
        """Initialize a ScoringEndpointCredentialsAzureScoringEndpointCredentials object from a json dictionary."""
        args = {}
        if 'token' in _dict:
            args['token'] = _dict.get('token')
        else:
            raise ValueError('Required property \'token\' not present in ScoringEndpointCredentialsAzureScoringEndpointCredentials JSON')
        args.update({k:v for (k, v) in _dict.items() if k not in cls._properties})
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a ScoringEndpointCredentialsAzureScoringEndpointCredentials object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'token') and self.token is not None:
            _dict['token'] = self.token
        for _key in [k for k in vars(self).keys() if k not in ScoringEndpointCredentialsAzureScoringEndpointCredentials._properties]:
            if getattr(self, _key, None) is not None:
                _dict[_key] = getattr(self, _key)
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this ScoringEndpointCredentialsAzureScoringEndpointCredentials object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'ScoringEndpointCredentialsAzureScoringEndpointCredentials') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'ScoringEndpointCredentialsAzureScoringEndpointCredentials') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class SparkStructFieldObject(SparkStructField):
    """
    SparkStructFieldObject.

    :attr str name:
    :attr object type:
    :attr bool nullable:
    :attr dict metadata: (optional)
    """

    def __init__(self,
                 name: str,
                 type: object,
                 nullable: bool,
                 *,
                 metadata: dict = None) -> None:
        """
        Initialize a SparkStructFieldObject object.

        :param str name:
        :param object type:
        :param bool nullable:
        :param dict metadata: (optional)
        """
        # pylint: disable=super-init-not-called
        self.name = name
        self.type = type
        self.nullable = nullable
        self.metadata = metadata

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'SparkStructFieldObject':
        """Initialize a SparkStructFieldObject object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        else:
            raise ValueError('Required property \'name\' not present in SparkStructFieldObject JSON')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in SparkStructFieldObject JSON')
        if 'nullable' in _dict:
            args['nullable'] = _dict.get('nullable')
        else:
            raise ValueError('Required property \'nullable\' not present in SparkStructFieldObject JSON')
        if 'metadata' in _dict:
            args['metadata'] = _dict.get('metadata')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SparkStructFieldObject object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'nullable') and self.nullable is not None:
            _dict['nullable'] = self.nullable
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this SparkStructFieldObject object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'SparkStructFieldObject') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'SparkStructFieldObject') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class SparkStructFieldPrimitive(SparkStructField):
    """
    SparkStructFieldPrimitive.

    :attr str name:
    :attr str type:
    :attr bool nullable:
    :attr dict metadata: (optional)
    """

    def __init__(self,
                 name: str,
                 type: str,
                 nullable: bool,
                 *,
                 metadata: dict = None) -> None:
        """
        Initialize a SparkStructFieldPrimitive object.

        :param str name:
        :param str type:
        :param bool nullable:
        :param dict metadata: (optional)
        """
        # pylint: disable=super-init-not-called
        self.name = name
        self.type = type
        self.nullable = nullable
        self.metadata = metadata

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'SparkStructFieldPrimitive':
        """Initialize a SparkStructFieldPrimitive object from a json dictionary."""
        args = {}
        if 'name' in _dict:
            args['name'] = _dict.get('name')
        else:
            raise ValueError('Required property \'name\' not present in SparkStructFieldPrimitive JSON')
        if 'type' in _dict:
            args['type'] = _dict.get('type')
        else:
            raise ValueError('Required property \'type\' not present in SparkStructFieldPrimitive JSON')
        if 'nullable' in _dict:
            args['nullable'] = _dict.get('nullable')
        else:
            raise ValueError('Required property \'nullable\' not present in SparkStructFieldPrimitive JSON')
        if 'metadata' in _dict:
            args['metadata'] = _dict.get('metadata')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a SparkStructFieldPrimitive object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'name') and self.name is not None:
            _dict['name'] = self.name
        if hasattr(self, 'type') and self.type is not None:
            _dict['type'] = self.type
        if hasattr(self, 'nullable') and self.nullable is not None:
            _dict['nullable'] = self.nullable
        if hasattr(self, 'metadata') and self.metadata is not None:
            _dict['metadata'] = self.metadata
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this SparkStructFieldPrimitive object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'SparkStructFieldPrimitive') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'SparkStructFieldPrimitive') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class UnknownCredentials(MLCredentials):
    """
    Unknown service provider credentials.

    """

    def __init__(self,
                 **kwargs) -> None:
        """
        Initialize a UnknownCredentials object.

        :param **kwargs: (optional) Any additional properties.
        """
        # pylint: disable=super-init-not-called
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'UnknownCredentials':
        """Initialize a UnknownCredentials object from a json dictionary."""
        return cls(**_dict)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a UnknownCredentials object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        return vars(self)

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this UnknownCredentials object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'UnknownCredentials') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'UnknownCredentials') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class UserPreferencesGetResponseUserPreferenceValueObject(UserPreferencesGetResponse):
    """
    user preference object value.

    """

    def __init__(self) -> None:
        """
        Initialize a UserPreferencesGetResponseUserPreferenceValueObject object.

        """
        # pylint: disable=super-init-not-called

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'UserPreferencesGetResponseUserPreferenceValueObject':
        """Initialize a UserPreferencesGetResponseUserPreferenceValueObject object from a json dictionary."""
        return cls(**_dict)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a UserPreferencesGetResponseUserPreferenceValueObject object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        return vars(self)

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this UserPreferencesGetResponseUserPreferenceValueObject object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'UserPreferencesGetResponseUserPreferenceValueObject') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'UserPreferencesGetResponseUserPreferenceValueObject') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class UserPreferencesGetResponseUserPreferenceValueString(UserPreferencesGetResponse):
    """
    user preference string value - response string wrapped in an object.

    :attr str value: (optional) response string value.
    """

    def __init__(self,
                 *,
                 value: str = None) -> None:
        """
        Initialize a UserPreferencesGetResponseUserPreferenceValueString object.

        :param str value: (optional) response string value.
        """
        # pylint: disable=super-init-not-called
        self.value = value

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'UserPreferencesGetResponseUserPreferenceValueString':
        """Initialize a UserPreferencesGetResponseUserPreferenceValueString object from a json dictionary."""
        args = {}
        if 'value' in _dict:
            args['value'] = _dict.get('value')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a UserPreferencesGetResponseUserPreferenceValueString object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this UserPreferencesGetResponseUserPreferenceValueString object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'UserPreferencesGetResponseUserPreferenceValueString') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'UserPreferencesGetResponseUserPreferenceValueString') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class UserPreferencesUpdateRequestUserPreferenceValueObject(UserPreferencesUpdateRequest):
    """
    user preference object value.

    """

    def __init__(self) -> None:
        """
        Initialize a UserPreferencesUpdateRequestUserPreferenceValueObject object.

        """
        # pylint: disable=super-init-not-called

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'UserPreferencesUpdateRequestUserPreferenceValueObject':
        """Initialize a UserPreferencesUpdateRequestUserPreferenceValueObject object from a json dictionary."""
        return cls(**_dict)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a UserPreferencesUpdateRequestUserPreferenceValueObject object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        return vars(self)

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this UserPreferencesUpdateRequestUserPreferenceValueObject object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'UserPreferencesUpdateRequestUserPreferenceValueObject') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'UserPreferencesUpdateRequestUserPreferenceValueObject') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class UserPreferencesUpdateRequestUserPreferenceValueString(UserPreferencesUpdateRequest):
    """
    user preference string value - response string wrapped in an object.

    :attr str value: (optional) response string value.
    """

    def __init__(self,
                 *,
                 value: str = None) -> None:
        """
        Initialize a UserPreferencesUpdateRequestUserPreferenceValueString object.

        :param str value: (optional) response string value.
        """
        # pylint: disable=super-init-not-called
        self.value = value

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'UserPreferencesUpdateRequestUserPreferenceValueString':
        """Initialize a UserPreferencesUpdateRequestUserPreferenceValueString object from a json dictionary."""
        args = {}
        if 'value' in _dict:
            args['value'] = _dict.get('value')
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a UserPreferencesUpdateRequestUserPreferenceValueString object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'value') and self.value is not None:
            _dict['value'] = self.value
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this UserPreferencesUpdateRequestUserPreferenceValueString object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'UserPreferencesUpdateRequestUserPreferenceValueString') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'UserPreferencesUpdateRequestUserPreferenceValueString') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

class WMLCredentialsCP4D(MLCredentials):
    """
    WMLCredentials format for OpenScale on Cloud Pak for Data.

    :attr str url: (optional) Required if wml_location is cpd_remote or
          cloud_remote.
    :attr str apikey: (optional) Required if wml_location is cpd_remote or
          cloud_remote.
    :attr str username: (optional) Required if wml_location is cpd_remote.
    :attr str uid: (optional) User ID of a user in the Cloud Pak for Data. If not
          set, the uid extracted from the access token in Authorization header is used.
          This parameter is only applicable if wml_location is cpd_local.
    :attr str wml_location: (optional) If wml_location is not selected, we treat the
          service provider as cpd_local for backward compatibility.
    """

    # The set of defined properties for the class
    _properties = frozenset(['url', 'apikey', 'username', 'uid', 'wml_location'])

    def __init__(self,
                 *,
                 url: str = None,
                 apikey: str = None,
                 username: str = None,
                 uid: str = None,
                 wml_location: str = None,
                 **kwargs) -> None:
        """
        Initialize a WMLCredentialsCP4D object.

        :param str url: (optional) Required if wml_location is cpd_remote or
               cloud_remote.
        :param str apikey: (optional) Required if wml_location is cpd_remote or
               cloud_remote.
        :param str username: (optional) Required if wml_location is cpd_remote.
        :param str uid: (optional) User ID of a user in the Cloud Pak for Data. If
               not set, the uid extracted from the access token in Authorization header is
               used. This parameter is only applicable if wml_location is cpd_local.
        :param str wml_location: (optional) If wml_location is not selected, we
               treat the service provider as cpd_local for backward compatibility.
        :param **kwargs: (optional) Any additional properties.
        """
        # pylint: disable=super-init-not-called
        self.url = url
        self.apikey = apikey
        self.username = username
        self.uid = uid
        self.wml_location = wml_location
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'WMLCredentialsCP4D':
        """Initialize a WMLCredentialsCP4D object from a json dictionary."""
        args = {}
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        if 'apikey' in _dict:
            args['apikey'] = _dict.get('apikey')
        if 'username' in _dict:
            args['username'] = _dict.get('username')
        if 'uid' in _dict:
            args['uid'] = _dict.get('uid')
        if 'wml_location' in _dict:
            args['wml_location'] = _dict.get('wml_location')
        args.update({k:v for (k, v) in _dict.items() if k not in cls._properties})
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a WMLCredentialsCP4D object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        if hasattr(self, 'apikey') and self.apikey is not None:
            _dict['apikey'] = self.apikey
        if hasattr(self, 'username') and self.username is not None:
            _dict['username'] = self.username
        if hasattr(self, 'uid') and self.uid is not None:
            _dict['uid'] = self.uid
        if hasattr(self, 'wml_location') and self.wml_location is not None:
            _dict['wml_location'] = self.wml_location
        for _key in [k for k in vars(self).keys() if k not in WMLCredentialsCP4D._properties]:
            if getattr(self, _key, None) is not None:
                _dict[_key] = getattr(self, _key)
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this WMLCredentialsCP4D object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'WMLCredentialsCP4D') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'WMLCredentialsCP4D') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other

    class WmlLocationEnum(str, Enum):
        """
        If wml_location is not selected, we treat the service provider as cpd_local for
        backward compatibility.
        """
        CPD_LOCAL = 'cpd_local'
        CPD_REMOTE = 'cpd_remote'
        CLOUD_REMOTE = 'cloud_remote'


class WMLCredentialsCloud(MLCredentials):
    """
    WMLCredentialsCloud.

    :attr str apikey: (optional)
    :attr str token: (optional)
    :attr str url:
    :attr str instance_id:
    """

    # The set of defined properties for the class
    _properties = frozenset(['apikey', 'token', 'url', 'instance_id'])

    def __init__(self,
                 url: str,
                 instance_id: str,
                 *,
                 apikey: str = None,
                 token: str = None,
                 **kwargs) -> None:
        """
        Initialize a WMLCredentialsCloud object.

        :param str url:
        :param str instance_id:
        :param str apikey: (optional)
        :param str token: (optional)
        :param **kwargs: (optional) Any additional properties.
        """
        # pylint: disable=super-init-not-called
        self.apikey = apikey
        self.token = token
        self.url = url
        self.instance_id = instance_id
        for _key, _value in kwargs.items():
            setattr(self, _key, _value)

    @classmethod
    def from_dict(cls, _dict: Dict) -> 'WMLCredentialsCloud':
        """Initialize a WMLCredentialsCloud object from a json dictionary."""
        args = {}
        if 'apikey' in _dict:
            args['apikey'] = _dict.get('apikey')
        if 'token' in _dict:
            args['token'] = _dict.get('token')
        if 'url' in _dict:
            args['url'] = _dict.get('url')
        else:
            raise ValueError('Required property \'url\' not present in WMLCredentialsCloud JSON')
        if 'instance_id' in _dict:
            args['instance_id'] = _dict.get('instance_id')
        else:
            raise ValueError('Required property \'instance_id\' not present in WMLCredentialsCloud JSON')
        args.update({k:v for (k, v) in _dict.items() if k not in cls._properties})
        return cls(**args)

    @classmethod
    def _from_dict(cls, _dict):
        """Initialize a WMLCredentialsCloud object from a json dictionary."""
        return cls.from_dict(_dict)

    def to_dict(self) -> Dict:
        """Return a json dictionary representing this model."""
        _dict = {}
        if hasattr(self, 'apikey') and self.apikey is not None:
            _dict['apikey'] = self.apikey
        if hasattr(self, 'token') and self.token is not None:
            _dict['token'] = self.token
        if hasattr(self, 'url') and self.url is not None:
            _dict['url'] = self.url
        if hasattr(self, 'instance_id') and self.instance_id is not None:
            _dict['instance_id'] = self.instance_id
        for _key in [k for k in vars(self).keys() if k not in WMLCredentialsCloud._properties]:
            if getattr(self, _key, None) is not None:
                _dict[_key] = getattr(self, _key)
        return _dict

    def _to_dict(self):
        """Return a json dictionary representing this model."""
        return self.to_dict()

    def __str__(self) -> str:
        """Return a `str` version of this WMLCredentialsCloud object."""
        return json.dumps(self.to_dict(), indent=2)

    def __eq__(self, other: 'WMLCredentialsCloud') -> bool:
        """Return `true` when self and other are equal, false otherwise."""
        if not isinstance(other, self.__class__):
            return False
        return self.__dict__ == other.__dict__

    def __ne__(self, other: 'WMLCredentialsCloud') -> bool:
        """Return `true` when self and other are not equal, false otherwise."""
        return not self == other
