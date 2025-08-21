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

import inspect

from ibm_cloud_sdk_core import BaseService

from ibm_watson_openscale.base_classes.tables import Table
from .utils import *
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import Monitors as BaseMonitors
from typing import Tuple

if TYPE_CHECKING:
    from .client import WatsonOpenScaleV2Adapter
    from .base_classes.watson_open_scale_v2 import MonitorMetricRequest, MonitorTagRequest, ApplicabilitySelection, \
        MonitorInstanceSchedule, DetailedResponse

_DEFAULT_LIST_LENGTH = 50


# TODO: Add parameters validation in every method
class MonitorDefinitions(BaseMonitors):
    """
    Manages Monitor Definitions.
    """

    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter') -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        super().__init__(watson_open_scale=self._ai_client)
        self.MONITORS = type('MONITORS_', (), self._create_monitors_enum())

    ################################################
    #    Hidden methods from base monitor class    #
    ################################################
    @property
    def list_instances(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.{inspect.currentframe().f_code.co_name.split('_')[0]}() instead")

    @property
    def add_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.{inspect.currentframe().f_code.co_name.split('_')[0]}() instead")

    @property
    def get_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.{inspect.currentframe().f_code.co_name.split('_')[0]}() instead")

    @property
    def update_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.{inspect.currentframe().f_code.co_name.split('_')[0]}() instead")

    @property
    def delete_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.{inspect.currentframe().f_code.co_name.split('_')[0]}() instead")

    @property
    def run_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, "
            f"please use client.monitor_instances instead")

    @property
    def list_runs(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, "
            f"please use client.monitor_instances instead")

    @property
    def get_run_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, "
            f"please use client.monitor_instances instead")

    @property
    def update_run_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, "
            f"please use client.monitor_instances instead")

    @property
    def get_run_logs_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, "
            f"please use client.monitor_instances instead")

    @property
    def publish_instance_measurements(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, "
            f"please use client.monitor_instances instead")

    @property
    def list_instance_measurements(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, "
            f"please use client.monitor_instances instead")

    @property
    def get_instance_measurement(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, "
            f"please use client.monitor_instances instead")

    @property
    def list_instance_metrics(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, "
            f"please use client.monitor_instances instead")

    @property
    def list_measurements(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, "
            f"please use client.monitor_instances instead")

    def add(self,
            name: str,
            metrics: List['MonitorMetricRequest'],
            tags: List['MonitorTagRequest'],
            description: str = None,
            applies_to: 'ApplicabilitySelection' = None,
            parameters_schema: object = None,
            managed_by: str = None,
            schedule: 'MonitorInstanceSchedule' = None,
            background_mode: bool = True) -> Union['DetailedResponse', Optional[dict]]:
        """
        Add custom monitor.

        :param str name: Monitor UI label (must be unique).
        :param List[MonitorMetricRequest] metrics: A list of metric definition.
        :param List[MonitorTagRequest] tags: Available tags.
        :param str description: (optional) Long monitoring description presented in
               monitoring catalog.
        :param ApplicabilitySelection applies_to: (optional)
        :param object parameters_schema: (optional) JSON schema that will be used
               to validate monitoring parameters when enabled.
        :param str managed_by: (optional)
        :param MonitorInstanceSchedule schedule: (optional) The schedule used to
               control how frequently the target is monitored. The maximum frequency is
               once every 30 minutes.
               Defaults to once every hour if not specified.
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorDisplayForm` result

        A way you may use me:

        >>>  from ibm_watson_openscale import *
        >>>  metrics = [
               MonitorMetricRequest(
                   name='sensitivity',
                   thresholds=[MetricThreshold(
                       type=MetricThresholdTypes.LOWER_LIMIT,
                       default=0.8
                   )]
               ),
               MonitorMetricRequest(
                   name='specificity',
                   thresholds=[MetricThreshold(
                       type=MetricThresholdTypes.LOWER_LIMIT,
                       default=0.75
                   )]
               ),
            ]
        >>>  tags = [
               MonitorTagRequest(
                   name='region',
                   description='customer geographical region'
               )
            ]
        >>>  my_monitor = client.monitor_definitions.add(
                   name='my model performance',
                   metrics=metrics,
                   tags=tags,
                   background_mode=False)
        """
        response = super().add(name=name, metrics=metrics, tags=tags, description=description, applies_to=applies_to,
                               parameters_schema=parameters_schema, managed_by=managed_by, schedule=schedule)
        self.MONITORS = type('MONITORS_', (), self._create_monitors_enum())

        monitor_definition_id = response.result.metadata.id

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                try:
                    details = self.get(monitor_definition_id=monitor_definition_id)
                    return StatusStateType.FINISHED
                except Exception as e:
                    return StatusStateType.ACTIVE

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                try:
                    details = self.get(monitor_definition_id=monitor_definition_id)
                    state = StatusStateType.FINISHED
                except Exception as e:
                    state = StatusStateType.ACTIVE

                if state in [StatusStateType.FINISHED]:
                    return "Successfully finished adding monitor definition", None, response
                else:
                    return "Add monitor definition failed", f'Reason: {e}', response

            return print_synchronous_run(
                'Waiting for end of adding monitor definition {}'.format(monitor_definition_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.FINISHED]
            )

    def delete(self, monitor_definition_id: str, background_mode: bool = True) -> Union[
        'DetailedResponse', Optional[dict]]:
        """
        Delete custom monitor.

        :param str monitor_definition_id: Unique monitor definition ID.
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse

        A way you may use me:

        >>>  client.monitor_definitions.delete(monitor_definition_id='997b1474-00d2-4g05-ac02-287ebfc603b5')
        """
        response = super().delete(monitor_definition_id=monitor_definition_id)

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.list()
                if monitor_definition_id not in str(details.result):
                    return StatusStateType.FINISHED
                else:
                    return StatusStateType.ACTIVE

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.list()
                if monitor_definition_id not in str(details.result):
                    state = StatusStateType.FINISHED
                else:
                    state = StatusStateType.ACTIVE

                if state in [StatusStateType.FINISHED]:
                    return "Successfully finished deleting monitor definition", None, response
                else:
                    return "Delete monitor definition failed", 'Reason: None', response  # TODO: Need to show the reason.

            return print_synchronous_run(
                'Waiting for end of deleting monitor definition {}'.format(monitor_definition_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.FINISHED]
            )

    def update(self,
               monitor_definition_id: str,
               name: str,
               metrics: List['MonitorMetricRequest'],
               tags: List['MonitorTagRequest'],
               description: str = None,
               applies_to: 'ApplicabilitySelection' = None,
               parameters_schema: object = None,
               managed_by: str = None,
               schedule: 'MonitorInstanceSchedule' = None
               ) -> 'DetailedResponse':
        """
        Edit custom monitor.

        Update monitor.

        :param str monitor_definition_id: Unique monitor definition ID.
        :param str name: Monitor UI label (must be unique).
        :param List[MonitorMetricRequest] metrics: A list of metric definition.
        :param List[MonitorTagRequest] tags: Available tags.
        :param str description: (optional) Long monitoring description presented in
               monitoring catalog.
        :param ApplicabilitySelection applies_to: (optional)
        :param object parameters_schema: (optional) JSON schema that will be used
               to validate monitoring parameters when enabled.
        :param str managed_by: (optional)
        :param MonitorInstanceSchedule schedule: (optional) The schedule used to
               control how frequently the target is monitored. The maximum frequency is
               once every 30 minutes.
               Defaults to once every hour if not specified.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorDisplayForm` result

        A way you may use me:

        >>>  from ibm_watson_openscale import *
        >>>  metrics = [
               MonitorMetricRequest(
                   name='sensitivity',
                   thresholds=[MetricThreshold(
                       type=MetricThresholdTypes.LOWER_LIMIT,
                       default=0.7
                   )]
               ),
               MonitorMetricRequest(
                   name='specificity',
                   thresholds=[MetricThreshold(
                       type=MetricThresholdTypes.LOWER_LIMIT,
                       default=0.6
                   )]
               ),
            ]
        >>>  tags = [
               MonitorTagRequest(
                   name='region',
                   description='customer geographical region'.upper()
               )
            ]
        >>>  my_monitor = client.monitor_definitions.update(
               monitor_definition_id='monitor_definition_id',
               name='my model performance',
               metrics=metrics,
               tags=tags)
        """
        response = super().update(monitor_definition_id=monitor_definition_id, name=name, metrics=metrics, tags=tags,
                                  description=description, applies_to=applies_to,
                                  parameters_schema=parameters_schema, managed_by=managed_by, schedule=schedule)
        self.MONITORS = type('MONITORS_', (), self._create_monitors_enum())
        return response

    #################################################
    #    New methods for monitor instances          #
    #################################################
    def show(self, limit: int = 10) -> None:
        """
        Show monitor definitions. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>>  client.monitor_definitions.show()
        >>>  client.monitor_definitions.show(limit=20)
        >>>  client.monitor_definitions.show(limit=None)
        """
        validate_type(limit, u'limit', int, False)

        response = self.list()

        records = [[definition.metadata.id,
                    definition.entity.name,
                    [metric.name for metric in definition.entity.metrics]]
                   for definition in response.result.monitor_definitions]
        columns = ['monitor id', 'monitor name', 'metrics names']

        Table(columns, records).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="Monitor definitions"
        )

    def _create_monitors_enum(self):
        response = self.list()
        return {definition.entity.name.upper().replace(' ', '_'): self._create_metrics_enum(definition)
                for definition in response.result.monitor_definitions}

    def _create_metrics_enum(self, definition):
        return type('Monitor_', (),
                    {
                        'ID': definition.metadata.id,
                        'METRIC': self._create_metrics_properties(definition)
                    })

    @staticmethod
    def _create_metrics_properties(definition):
        return type('MetricProperty_', (),
                    {metric.name.upper().replace(' ', '_').split('(')[0]: metric.id
                     for metric in definition.entity.metrics})
