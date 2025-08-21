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

from io import BufferedReader
from typing import Tuple, Dict

from .utils import *
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import Runs as BaseRuns
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import Measurements


_DEFAULT_LIST_LENGTH = 50


class Runs(BaseRuns):
    """
    Manages Monitor instance Runs.
    """

    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter') -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        super().__init__(watson_open_scale=self._ai_client)
        
    def run(self, monitor_instance_id,triggered_by, parameters, business_metric_context, expiration_date, background_mode = True):
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
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitoringRun` result
        """
        runs = Runs(watson_open_scale=self._ai_client)
        response = runs.add(monitor_instance_id=monitor_instance_id, triggered_by=triggered_by,
                                        parameters=parameters, business_metric_context=business_metric_context)

        run_id = response.result.metadata.id

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.get_run_details(monitor_instance_id=monitor_instance_id, monitoring_run_id=run_id)
                return details.result.entity.status.state

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.get_run_details(monitor_instance_id=monitor_instance_id, monitoring_run_id=run_id)
                state = details.result.entity.status.state

                if state in [StatusStateType.FINISHED]:
                    return "Successfully finished run", None, details
                else:
                    return "Run failed with status: {}".format(state), \
                           'Reason: {}'.format(["code: {}, message: {}".format(error.code, error.message) for error in
                                                details.result.entity.status.failure.errors]), details

            return print_synchronous_run(
                'Waiting for end of monitoring run {}'.format(run_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.FINISHED]
            )
            
        return response
    

    