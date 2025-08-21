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

#from .business_applications import BusinessApplications
from .data_marts import DataMarts
from .data_sets import DataSets
from .monitor_definitions import MonitorDefinitions
from .monitor_instances import MonitorInstances
from .service_providers import ServiceProviders
from .subscriptions import Subscriptions
from .model import Model
from .utils import *
from .utils.entitlement_client import EntitlementClient 
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import WatsonOpenScaleV2
from ibm_watson_openscale.utils import constants
from ibm_cloud_sdk_core.authenticators import BearerTokenAuthenticator, CloudPakForDataAuthenticator, IAMAuthenticator
from ibm_watson_openscale.supporting_classes.cp4d_authenticator import CloudPak40ForDataAuthenticator

import os

##############################################################################
# Service
##############################################################################

class WatsonOpenScaleV2Adapter(WatsonOpenScaleV2):
    """
        Watson OpenScale client.

        :var version: Returns version of the python library.
        :vartype version: str

        :var authenticator: Returns passed authenticator.
        :vartype authenticator: IAMAuthenticator, CloudPakForDataAuthenticator

        :var data_marts: Manages data_marts module
        :vartype data_marts: ibm_watson_openscale.data_marts.DataMarts

        :var service_providers: Manages service_providers module
        :vartype service_providers: ibm_watson_openscale.service_providers.ServiceProviders

        :var subscriptions: Manages subscriptions module
        :vartype subscriptions: ibm_watson_openscale.subscriptions.Subscriptions

        :var data_sets: Manages data_sets module
        :vartype data_sets: ibm_watson_openscale.data_sets.DataSets

        :var monitor_definitions: Manages monitor_definitions module
        :vartype monitor_definitions: ibm_watson_openscale.monitor_definitions.MonitorDefinitions

        :var monitor_instances: Manages monitor_instances module
        :vartype monitor_instances: ibm_watson_openscale.monitor_instances.MonitorInstances

        #:var business_applications: Manages business_applications module
        #:vartype business_applications: ibm_watson_openscale.business_applications.BusinessApplications

        A way you might use me is:

        >>> from ibm_watson_openscale import APIClient
        >>> client = APIClient(authenticator=authenticator, service_url=service_url) # client will use default service_instance_id
        >>> client = APIClient(authenticator, service_url) # client will use default service_url and default service_instance_id
        >>> client = APIClient(authenticator=authenticator, service_url=service_url, service_instance_id=service_instance_id)
        >>> client = APIClient(authenticator=authenticator, service_url=service_url, service_instance_id=service_instance_id,bedrock_url=bedrock_url ) 
        >>> client = APIClient(authenticator, service_url, service_instance_id)
        """

    @classmethod
    def new_instance(cls, service_name: str = None) -> "WatsonOpenScaleV2Adapter":
        """
        This class method should be used only if you have stored your credentials
        in the separate file or in the ENV variable.

        :param service_name: Unique name of the service to configure.
        :paramtype service_name: str
        :return: ibm_watson_openscale.APIClient

        A way you might use me is:

        >>> from ibm_watson_openscale import APIClient
        >>> client = APIClient.new_instance(service_name="openscale-1")
        >>> client = APIClient.new_instance(service_name="openscale-2")
        >>> client = APIClient.new_instance("openscale")
        """
        validate_type(service_name, "service_name", str, True)
        service = super().new_instance(service_name=service_name)
        return service

    def __init__(self,
                 authenticator: Optional[Union["BearerTokenAuthenticator", "CloudPakForDataAuthenticator", "IAMAuthenticator","CloudPak40ForDataAuthenticator"]] = None,
                 service_url: str=None,
                 service_instance_id: Optional[str]=None, bedrock_url: str=None) -> None:
        """
        :param service_url: URL of the WOS service eg. https://api.aiopenscale.cloud.ibm.com
        :type service_url: str (required)
        :param service_instance_id: service instance id
        :type service_instance_id: str (required)
        :type bedrock_url: Foundational services (common-services-route ) url. User needs to get this url from CP4D admin. This url is required only when iam-integration is enabled on CP4D 4.0.x cluster
                           Note: This parameter is not required for CP4D version 3.5.x or less
        param Authenticator authenticator: The authenticator specifies the authentication mechanism.
               Get up to date information from https://github.com/IBM/python-sdk-core/blob/master/README.md
               about initializing the authenticator of your choice.
        """
        validate_type(authenticator, "authenticator", [BearerTokenAuthenticator, CloudPakForDataAuthenticator, IAMAuthenticator, CloudPak40ForDataAuthenticator], True)
        self.version = version()
        
        #make use of new authenticator class which works for 3.5.x and 4.x.x(iamintegration=true)
        if isinstance(authenticator, CloudPakForDataAuthenticator):
            url = authenticator.token_manager.url[0:authenticator.token_manager.url.index("/",9)]
            username = authenticator.token_manager.username
            password = authenticator.token_manager.password
            apikey = authenticator.token_manager.apikey
            authenticator = CloudPak40ForDataAuthenticator(url=url,
                                        username=username,
                                        password=password,
                                        apikey = apikey,
                                        disable_ssl_verification=True,
                                        bedrock_url = bedrock_url)
        
        self.authenticator = authenticator
        self.service_instance_id = service_instance_id
        self.plan_name = None
        self.check_entitlements = False
        super().__init__(authenticator=self.authenticator)

        if authenticator is not None:
            validate_type(service_url, "service_url", str, False)
            validate_type(service_instance_id, "service_instance_id", str, False)
            if type(authenticator) is IAMAuthenticator:
                self.check_entitlements = True
            self.data_marts = DataMarts(self)
            self.service_providers = ServiceProviders(self)
            self.subscriptions = Subscriptions(self)
            self.data_sets = DataSets(self)
            self.monitor_definitions = None
            #self.business_applications = BusinessApplications(self)
            
            if isinstance(authenticator, (BearerTokenAuthenticator,CloudPakForDataAuthenticator, CloudPak40ForDataAuthenticator)):
                if service_url is None:
                    # Service URL is mandatory to be provided for the token path or CP4D
                    raise MissingValue("service_url", "Service URL is mandatory to be provided with IAM token or CP4D.")

            # Setting the default service URI if not provided
            if isinstance(authenticator, ( CloudPakForDataAuthenticator, CloudPak40ForDataAuthenticator) ):
                # Taking the Service URL from authenticator in case not provided
                service_url = authenticator.token_manager.url[0:-24] if service_url is None else service_url
            else:
                # Defaulting to YPPROD for cloud in case Service URL is not provided
                service_url = constants.DEFAULT_SERVICE_URL if service_url is None else service_url

            # Removing training `/` is present from URI
            service_url = service_url[0:len(service_url) - 1] if service_url[-1] == "/" else service_url

            # Checking if it is CP4D environment

            self.is_cp4d = False
            if isinstance(authenticator, ( CloudPakForDataAuthenticator, CloudPak40ForDataAuthenticator) ):
                self.is_cp4d = True
            elif isinstance(authenticator, BearerTokenAuthenticator):
                self.is_cp4d = check_if_cp4d(service_url)

            super().set_disable_ssl_verification(self.is_cp4d)

            self.service_instance_id = get_instance_guid(self.authenticator, self.is_cp4d, service_url) if service_instance_id is None else service_instance_id

            self._generate_service_url(is_cp4d=self.is_cp4d, service_url=service_url, instance_id=self.service_instance_id)
                
            # Check entitlement for Cloud only
            if self.check_entitlements is True:
                token = None
                if type(self.authenticator) in [CloudPakForDataAuthenticator, IAMAuthenticator, CloudPak40ForDataAuthenticator]:
                    token = self.authenticator.token_manager.get_token()
                else:
                    token = self.authenticator.bearer_token
                entitlements = EntitlementClient(service_url, token, self.service_instance_id)
                self.plan_name = entitlements.is_entitled()
            self.monitor_instances = MonitorInstances(self)    
            self.monitor_definitions = MonitorDefinitions(self)
            
            self.model = Model(self)

    def _generate_service_url(self, is_cp4d: bool, service_url: str = None, instance_id: Optional[str] = None) -> None:
        """
        Generates service url when it is not provided by the user.

        :param str service_url: url to the service (required)
        :param str instance_id: ID of the service instance (optional)
        """
        if instance_id is None:
            instance_id = get_instance_guid(self.authenticator, is_cp4d=is_cp4d, service_url=service_url)
        
        if service_url.endswith("openscale"):
            self.set_service_url("{}/{}".format(service_url, instance_id))
        else:
            self.set_service_url("{}/{}/{}".format(service_url, "openscale", instance_id))

    def configure_service(self, *args, **kwargs) -> None:
        """
        Overloaded base method to configure the service (read service_url and store it).
        Additional functionality: dynamically creates additional enums.
        """
        super().configure_service(*args, **kwargs)
        validate_type(self.service_url, "service_url", str, True)
        instance_id = get_instance_guid(self.authenticator, self.service_url)
        self.set_service_url("{}/{}".format(self.service_url, instance_id))
        self.monitor_definitions = MonitorDefinitions(self)
