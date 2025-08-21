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

import datetime
import time,requests

from ibm_cloud_sdk_core.authenticators import CloudPakForDataAuthenticator, IAMAuthenticator
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import *
from ibm_watson_openscale.supporting_classes.enums import *
from ibm_watson_openscale.supporting_classes import *
from ibm_watson_openscale.utils import *

GET_EVALUATION_STATUS_RETRIES = 32
GET_EVALUATION_STATUS_INTERVAL = 10
MRM_RISK_EVALUATIONS_HREF_PATTERN = u'{}/v2/monitoring_services/mrm/monitor_instances/{}/risk_evaluations'
MRM_RISK_EVALUATION_STATUS_HREF_PATTERN = u'{}/v2/subscriptions/{}/risk_evaluation_status'


@logging_class
class MrmMonitoring:
    """Manage model risk management monitoring for asset."""

    def __init__(self, ai_client):
        self._ai_client = ai_client
        #self._hrefs_v2 = AIHrefDefinitionsV2(ai_client._service_credentials)
        self._monitor_instance_id = None

    def enable(self, subscription_id):
        """
        Enables model risk management monitoring. The monitor is being run hourly.

        A way you might use me is:

        >>> client.monitor_instances.mrm_monitoring.enable()
        """
        
        target = Target(
            target_type=TargetTypes.SUBSCRIPTION,
            target_id=subscription_id
        )
        parameters = {}
        
        response = self._ai_client.monitor_instances.create(
            data_mart_id=self._ai_client.service_instance_id,
            background_mode=False,
            monitor_definition_id="mrm",
            target=target,
            parameters=parameters
        ).result
        self._monitor_instance_id = response.metadata.id

    def get_details(self):
        """
        Returns details of model risk management monitoring configuration.

        :return: configuration of quality monitoring
        :rtype: dict
        """
        monitor_instance_details = {}
        if self._monitor_instance_id is not None:
            monitor_instance_details = self._ai_client.monitor_instances.get(monitor_instance_id=self._monitor_instance_id).result.to_dict()
        
        return monitor_instance_details

    def disable(self):
        """
        Disables quality monitoring.
        """
        if self.get_details()["entity"]["status"]["state"] not in ["active"]:
            raise ClientError('Monitor is not enabled, so it cannot be disabled.')

        self._ai_client.monitor_instances.delete(monitor_instance_id=self._monitor_instance_id, background_mode = False)
    
    def run_risk_evaluations(self, test_data_df, test_data_set_name=None, publish_lineage="true", publish_fact="true"):
        """
        Runs a risk evaluation against the test data provided.

        :param test_data_df: the test data against which the risk evaluation must be performed
        :type test_data_df: pandas dataframe

        :param test_data_set_name: the name of the test data csv
        :type test_data_set_name: str

        :param publish_lineage: the flag to indicate if a lineage event should be published,
        provided an integration system reference to Watson Knowledge Catalog exists
        :type publish_lineage: str
        
        :param publish_fact: the flag to indicate whether monitor metrics should be published to factsheet or not
        :type publish_fact: str

        A way you might use me is:

        >>> client.monitor_instances.mrm_monitoring..run_risk_evaluations(test_data_df, test_data_set_name='test_data.csv')
        """
       
        headers = self.__get_headers(self._ai_client)
        headers["Content-Type"] = "text/csv"
        payload = bytearray(test_data_df.head(200).to_csv(index=False), 'utf-8')
        url = MRM_RISK_EVALUATIONS_HREF_PATTERN.format(self._ai_client.service_url,self._monitor_instance_id) + "?test_data_set_name={}&publish_lineage={}&publish_fact={}".format(
                    test_data_set_name, publish_lineage, publish_fact)
        try:
            #response = self._ai_client.requests_session.post(url, data=payload, headers=headers)
            response = requests.post(url, data=payload, headers=headers)
        except TypeError:
            #response = self._ai_client.requests_session.post(url, data=bytes(payload), headers=headers)
            response = requests.requests_session.post(url, data=bytes(payload), headers=headers)

        response = handle_response(202, u'mrm risk evaluations accepted', response)
        return response
    
    
    def get_risk_evaluations(self):

        headers = self.__get_headers(self._ai_client)
        url = MRM_RISK_EVALUATIONS_HREF_PATTERN.format(self._ai_client.service_url, self._monitor_instance_id)
        #response = self._ai_client.requests_session.get(url, headers=headers)
        response = requests.get(url, headers=headers)

        response = handle_response(200, u'mrm risk evaluations status', response)
        return response

    def get_result(self, check_completion_status=True):
        status, response = self._check_risk_evaluations_status(check_completion_status)
        if status is not None and status.lower() in ["finished", "completed"]:
            if "entity" in response and "parameters" in response["entity"]:
                parameters = response["entity"]["parameters"]
                if "measurement_id" in parameters:
                    measurement_id = parameters["measurement_id"]
                    measurement_response = self._ai_client.monitor_instances.get_measurement_details(monitor_instance_id=self._monitor_instance_id,measurement_id=measurement_id)
                    response = measurement_response.result.to_dict()
                    return response

        return response

    def _check_risk_evaluations_status(self, check_completion_status=True):

        status = None
        response = None

        print("Checking for status of risk evaluation run")
        for i in range(GET_EVALUATION_STATUS_RETRIES):
            response = self.get_risk_evaluations()
            if "entity" in response and "status" in response["entity"]:
                status = response["entity"]["status"]["state"]

            if status is not None:
                if not check_completion_status:
                    break
                import datetime
                print(datetime.datetime.utcnow().strftime('%H:%M:%S'), status.lower())
                if status.lower() in ["finished", "completed"]:
                    break
                elif "error" in status.lower():
                    print(response)
                    break

            time.sleep(GET_EVALUATION_STATUS_INTERVAL)

        return status, response
    
    def update_risk_evaluation_status(self, subscription_id, payload=None):
        """
        Updates the risk evaluation status of a given subscription

        :param subscription_id: the identifier of the subscription
        :type subscription_id: str

        :param payload: the risk evaluation status patch payload
        :type payload: dict

        >>> client.monitor_instances.mrm_monitoring.update_risk_evaluation_status('subscription_uid')
        """

        validate_type(subscription_id, "subscription_id", str, True)
        validate_type(payload, "payload", dict, True)

        headers = self.__get_headers(self._ai_client)
        headers["Content-Type"] = "application/json"
        url = MRM_RISK_EVALUATION_STATUS_HREF_PATTERN.format(self._ai_client.service_url,subscription_id) 
        response = requests.put(url, json=payload, headers=headers)

        response = handle_response(200, u'mrm risk evaluation status', response)
        return response
    
    def approve(self, model_id):

        """
        Approves a model for production

        :param model: the details of the model which should be approved
        :type model: KnownServiceModel
        """

        self._subscription = None
        subscriptions = self._ai_client.subscriptions.list().result.to_dict()["subscriptions"]
        for subscription in subscriptions:
            asset_id = subscription['entity']['asset']['asset_id']
            if asset_id == model_id:
                self._subscription = subscription
                break    
        if self._subscription is None:
            raise Exception("Could not find the subscription for model {}".format(model_id))    
        
        # approve payload
        payload = {
            "state": "approved"
        }

        self.update_risk_evaluation_status(self._subscription['metadata']['id'], payload)
        print("Model approved successfully")

        return self._subscription
       
    
    def __get_headers(self,client):
        token = client.authenticator.token_manager.get_token() if  ( isinstance(client.authenticator, IAMAuthenticator) or (isinstance(client.authenticator, CloudPakForDataAuthenticator))) else client.authenticator.bearer_token
        iam_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % token
        }
        return iam_headers