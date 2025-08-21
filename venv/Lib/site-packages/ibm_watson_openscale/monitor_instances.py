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

import inspect

from typing import Tuple, Any, BinaryIO

from ibm_cloud_sdk_core import BaseService

from ibm_watson_openscale.base_classes.tables import Table
from .utils import *
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import Instances as BaseInstances
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import Runs, Measurements, Metrics,ExplanationTasks, DriftService, Target, ExplainabilityService
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import get_sdk_headers
from ibm_watson_openscale.supporting_classes.enums import TargetTypes
from ibm_watson_openscale.mrm_monitoring import MrmMonitoring

if TYPE_CHECKING:
    from .client import WatsonOpenScaleV2Adapter
    from ibm_watson_openscale.base_classes.watson_open_scale_v2 import DetailedResponse, Target, \
        MonitorInstanceParameters, MetricThresholdOverride, \
        MonitorInstanceSchedule

_DEFAULT_LIST_LENGTH = 50


class MonitorInstances(BaseInstances):
    """
    Manages Monitor Instances.
    """

    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter') -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        self.runs = Runs(self._ai_client)
        self.measurements = Measurements(ai_client)
        self.explanation = ExplanationTasks(ai_client)
        self.explanation_service = ExplainabilityService(ai_client)
        self.drift = DriftService(ai_client)
        self.mrm_monitoring = MrmMonitoring(ai_client)
        super().__init__(watson_open_scale=self._ai_client)

    ################################################
    #    Hidden methods from base monitor class    #
    ################################################
    @property
    def get_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.{inspect.currentframe().f_code.co_name.split('_')[0]}() instead")

    @property
    def add(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.create() instead")

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
    def list_instances(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.{inspect.currentframe().f_code.co_name.split('_')[0]}() instead")

    @property
    def add_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.create() instead")

    @property
    def run_instance(self, *args, **kwargs) -> None:
        raise AttributeError(
            f"{inspect.currentframe().f_code.co_name}() is not implemented, please use "
            f"client.monitor_definitions.{inspect.currentframe().f_code.co_name.split('_')[0]}() instead")

    #################################################
    #    Overridden methods for monitor instances   #
    #################################################

    def run(
            self,
            monitor_instance_id: str,
            triggered_by: str = None,
            parameters = None,
            business_metric_context = None,
            background_mode: bool = True) -> Any:
        """
        Trigger monitoring run.
        :param str monitor_instance_id: Unique monitor instance ID.
        :param str triggered_by: (optional) An identifier representing the source
               that triggered the run request (optional). One of: event, scheduler, user,
               webhook.
        :param MonitorInstanceParameters parameters: (optional) Monitoring
               parameters consistent with the `parameters_schema` from the monitor
               definition.
        :param MonitoringRunBusinessMetricContext business_metric_context:
               (optional) Properties defining the business metric context in the triggered
               run of AI metric calculation.
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitoringRun` result

        A way you may use me:

        >>> monitor_instance_run_info = client.monitor_instances.run(
                background_mode=False,
                monitor_instance_id='997b1474-00d2-4g05-ac02-287ebfc603b5'
             )
        """
        #runs = Runs(watson_open_scale=self._ai_client)
        response = self.runs.add(monitor_instance_id=monitor_instance_id, triggered_by=triggered_by,
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

    def list(self,
             data_mart_id: str = None,
             monitor_definition_id: str = None,
             target_target_id: str = None,
             target_target_type: str = None) -> 'DetailedResponse':
        """
        List monitor instances.

        :param str data_mart_id: (optional) comma-separeted list of IDs.
        :param str monitor_definition_id: (optional) comma-separeted list of IDs.
        :param str target_target_id: (optional) comma-separeted list of IDs.
        :param str target_target_type: (optional) comma-separeted list of types.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorInstanceCollection` result

        A way you may use me:

        >>> monitor_instances_info = client.monitor_instances.list(
                data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
             )
        """
        response = super().list(data_mart_id=data_mart_id,
                                          monitor_definition_id=monitor_definition_id,
                                          target_target_id=target_target_id,
                                          target_target_type=target_target_type)
        return response

    def show(self, limit: int = 10,
             data_mart_id: str = None,
             monitor_definition_id: str = None,
             target_target_id: str = None,
             target_target_type: str = None) -> None:
        """
        Show monitor instances. By default 10 records will be shown.

        :param limit: Maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int
        :param str data_mart_id: (optional) comma-separeted list of IDs.
        :param str monitor_definition_id: (optional) comma-separeted list of IDs.
        :param str target_target_id: (optional) comma-separeted list of IDs.
        :param str target_target_type: (optional) comma-separeted list of types.
        
        :return: None

        A way you might use me is:

        >>> client.monitor_instances.show()
        >>> client.monitor_instances.show(limit=20)
        >>> client.monitor_instances.show(20)
        """
        validate_type(limit, u'limit', int, False)

        response = self.list(data_mart_id=data_mart_id,monitor_definition_id=monitor_definition_id,target_target_id=target_target_id,target_target_type=target_target_type)

        records = [[instances.entity.data_mart_id,
                    instances.entity.status.state,
                    instances.entity.target.target_id,
                    instances.entity.target.target_type,
                    instances.entity.monitor_definition_id,
                    instances.metadata.created_at,
                    instances.metadata.id]
                   for instances in response.result.monitor_instances]
        columns = ['data_mart_id', 'status', 'target_id', 'target_type', 'monitor_definition_id',
                   'created_at', 'id']

        Table(columns, records).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="Monitor instances"
        )

    def show_metrics(self, monitor_instance_id: str, limit: int = 10):
        """
        Show metrics for monitor instance.

        :param monitor_instance_id: ID of the monitor instance.
        :type monitor_instance_id: str
        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int
        :return: None

        A way you might use me is:

        >>> client.monitor_instances.show_metrics(monitor_instance_id='997b1474-00d2-4g05-ac02-287ebfc603b5')
        """
        from datetime import timedelta, datetime
        start_time = datetime.now() - timedelta(days=7)
        end_time = datetime.now()
        
        #runs = Runs(watson_open_scale=self._ai_client)
        response = self.runs.list(monitor_instance_id=monitor_instance_id)

        records = []
        measurements = Measurements(watson_open_scale=self._ai_client)
        for run_id in [run.metadata.id for run in response.result.runs]:
            response = measurements.list(
                monitor_instance_id=monitor_instance_id,
                start=start_time,
                end=end_time,
                run_id=run_id
            )

            records.extend([[measurement.entity.timestamp,
                             metric.id,
                             measurement.metadata.id,
                             metric.value,
                             metric.lower_limit,
                             metric.upper_limit,
                             ['{}:{}'.format(tag.id, tag.value) for tag in value.tags],
                             measurement.entity.monitor_definition_id,
                             measurement.entity.monitor_instance_id,
                             measurement.entity.run_id,
                             measurement.entity.target.target_type,
                             measurement.entity.target.target_id]
                            for measurement in response.result.measurements for value in measurement.entity.values for
                            metric in
                            value.metrics])

        columns = ['ts',
                   'id',
                   'measurement_id',
                   'value',
                   'lower_limit',
                   'upper_limit',
                   'tags',
                   'monitor_definition_id',
                   'monitor_instance_id',
                   'run_id',
                   'target_type',
                   'target_id']

        Table(columns, records).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="{} Monitor Runs Metrics from: {}  till: {}".format(monitor_instance_id, start_time, end_time)
        )

    def create(self,
               monitor_definition_id: str,
               target: 'Target',
               data_mart_id: str = None,
               parameters: 'MonitorInstanceParameters' = None,
               thresholds: 'List[MetricThresholdOverride]' = None,
               schedule: 'MonitorInstanceSchedule' = None,
               managed_by: str = None,
               training_data_stats: dict = None,
               background_mode: bool = True,
               **kwargs) -> Union['DetailedResponse', Optional[dict]]:
        """
        Create monitor instance.

        :param str data_mart_id:
        :param str monitor_definition_id:
        :param Target target:
        :param MonitorInstanceParameters parameters: (optional) Monitoring
               parameters consistent with the `parameters_schema` from the monitor
               definition.
        :param list[MetricThresholdOverride] thresholds: (optional)
        :param MonitorInstanceSchedule schedule: (optional) The schedule used to
               control how frequently the target is monitored. The maximum frequency is
               once every 30 minutes.
               Defaults to once every hour if not specified.
        :param str managed_by: (optional)
        :param training_data_stats: Training statistic json generated using training stats notebook (https://github.com/IBM-Watson/aios-data-distribution/blob/master/training_statistics_notebook.ipynb)
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorInstanceResponse` result

        A way you might use me is:

        >>> from ibm_watson_openscale import *
        >>> target = Target(
                target_type=TargetTypes.SUBSCRIPTION,
                target_id='997b1474-00d2-4g05-ac02-287ebfc603b5'
             )
        >>> parameters = MonitorInstanceParameters(
                min_feedback_data_size=50
             )
        >>> thresholds = [
                MetricThresholdOverride(
                    metric_id=client.monitor_definitions.MONITORS.QUALITY.METRIC.ACCURACY,
                    type=MetricThresholdTypes.LOWER_LIMIT,
                    value=0.7
                )
             ]
        >>> monitor_instances_info = client.monitor_instances.create(
                data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                background_mode=False,
                monitor_definition_id=client.monitor_definitions.MONITORS.QUALITY.ID,
                target=target,
                parameters=parameters,
                thresholds=thresholds
             )
        """
        if training_data_stats is None:
            response = super().add(data_mart_id=data_mart_id, monitor_definition_id=monitor_definition_id,
                                            target=target, parameters=parameters, thresholds=thresholds,
                                            schedule=schedule, managed_by=managed_by)
            monitor_instance_id = response.result.metadata.id
            return self.__check_for_finished_status(background_mode, monitor_instance_id,response = response)
        else:
            if len(training_data_stats) == 0:
                raise Exception("training_data_stats is empty. Please re-generate and use it")
            return self.__create_monitor_from_training_stats(data_mart_id,training_data_stats, kwargs, background_mode)
        
    def delete(self,
               monitor_instance_id: str,
               background_mode: bool = True) -> Union['DetailedResponse', Optional[dict]]:
        """
        Delete monitor instance.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse

        A way you might use me is:

        >>> ai_client_v2.monitor_instances.delete(
                background_mode=False,
                monitor_instance_id='997b1474-00d2-4g05-ac02-287ebfc603b5'
             )
        """
        response = super().delete(monitor_instance_id=monitor_instance_id)

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.list()
                if monitor_instance_id not in str(details.result):
                    return StatusStateType.FINISHED
                else:
                    return StatusStateType.ACTIVE

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.list()
                if monitor_instance_id not in str(details.result):
                    state = StatusStateType.FINISHED
                else:
                    state = StatusStateType.ACTIVE

                if state in [StatusStateType.FINISHED]:
                    return "Successfully finished deleting monitor instance", None, response
                else:
                    return "Delete monitor instance failed", 'Reason: None', response  # TODO: Need to show the reason.

            return print_synchronous_run(
                'Waiting for end of deleting monitor instance {}'.format(monitor_instance_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.FINISHED]
            )

    def get(self, monitor_instance_id: str) -> 'DetailedResponse':
        """
        Get monitor instance details.

        :param str monitor_instance_id: Unique monitor instance ID.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorInstanceResponse` result

        A way you might use me is:

        >>> monitor_instance_info = client.monitor_instances.get(
                monitor_instance_id='997b1474-00d2-4g05-ac02-287ebfc603b5'
             )
        """
        response = super().get(monitor_instance_id=monitor_instance_id)
        return response

    def update(self,
               monitor_instance_id: str,
               patch_document: List['PatchDocument'],
               update_metadata_only: bool = None) -> 'DetailedResponse':
        """
        Update monitor instance.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param List[PatchDocument] patch_document:
        :param bool update_metadata_only: (optional) Flag that allows to control if
               the underlaying actions related to the monitor reconfiguration should be
               triggered.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorInstanceResponse` result
        """
        response = super().update(monitor_instance_id=monitor_instance_id, patch_document=patch_document,
                                           update_metadata_only=update_metadata_only)
        return response

    def _verify_table(self, data_set_id: str = None) -> None:
        """
        Verify if particular dataset/table exists and is loaded with any data.

        :param data_set_id: ID of the data set to check
        """
        validate_type(data_set_id, 'data_set_id', str, True)
        if self._ai_client.data_sets.get_records_count(data_set_id=data_set_id) == 0:
            raise MissingPayload(self.__class__.__name__, '{} data set table is empty.'.format(data_set_id))

    def get_metrics_count(self, monitor_instance_id: str, start: 'datetime', end: 'datetime',
                          interval: str = None, filter: str = None, group: str = None):
        """
        Get the count of the metrics.

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
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataMartGetMonitorInstanceMetrics` result

        A way you might use me is:

        >>> metrics_count = client.monitor_instances.get_metrics_count(
                monitor_instance_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                start=start_time,
                end=end_time,
             )
        """
        metrics = Metrics(self._ai_client)
        response = metrics.list(monitor_instance_id=monitor_instance_id, start=start, end=end,
                                                 agg='count', interval=interval, filter=filter, group=group)
        return response
    
    def get_metrics(self, monitor_instance_id: str, start: 'datetime', end: 'datetime',
                          interval: str = None, filter: str = None, group: str = None):
        """
        Get all the generated metrics between start and end date for specific monitor instance id

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
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataMartGetMonitorInstanceMetrics` result

        A way you might use me is:

        >>> metrics_count = client.monitor_instances.get_metrics_count(
                monitor_instance_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                start=start_time,
                end=end_time,
             )
        """
        metrics = Metrics(self._ai_client)
        response = metrics.list(monitor_instance_id=monitor_instance_id, start=start, end=end,
                                                 agg='last', interval=interval, filter=filter, group=group)
        return response
    
    def upload_drift_model(self, model_path: str, data_mart_id: str, subscription_id: str,
                           archive_name: str = "user_drift.tar.gz", enable_data_drift: bool = True,
                           enable_model_drift: bool = True) -> 'DetailedResponse':
        """
        Upload a Drift model to be able to compute Drift monitor.

        :param str model_path: (required) path to the drift model
        :param str data_mart_id: (required) data_mart ID
        :param str subscription_id: (required) subscription ID
        :param str archive_name: (optional) Archive name to use while storing tarball in datamart
        :param str enable_data_drift: (optional) If data drift is expected to be enabled for this subscription.
            If set to True, archive is verified to contain a valid data constraints json file.
        :param str enable_model_drift: (optional) If model drift is expected to be enabled for this subscription.
            If set to True, archive is verified to contain a valid drift model pickle file.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.

        A way you might use me is:

        >>> client.monitor_instances.upload_drift_model(
                model_path='drift_models/drift_detection_model.tar.gz',
                data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                subscription_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
             )
        """

        drift_model = open(model_path, mode="rb").read()

        response = self.drift.drift_archive_post(data_mart_id, subscription_id, drift_model, archive_name=archive_name, enable_data_drift=enable_data_drift, enable_model_drift=enable_model_drift)

        return response
    
    def download_drift_model(self, monitor_instance_id: str) -> "DetailedResponse":
        """
        Downloads the model.

        :param str monitor_instance_id: (required) The Drift monitor instance ID.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.

        A way you might use me is:

        >>> client.monitor_instances.download_drift_model(
            monitor_instance_id="0a9a4b85-f2bb-46de-850b-f033d7d37d9a"
            )
        """

        response = self.drift.drift_archive_get(monitor_instance_id)

        return response
    
    def download_drift_model_metadata(self, monitor_instance_id: str) -> "DetailedResponse":
        """
        Downloads the model metadata.

        :param str monitor_instance_id: (required) The Drift monitor instance ID.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.

        A way you might use me is:

        >>> client.monitor_instances.download_drift_model_metadata(
            monitor_instance_id="0a9a4b85-f2bb-46de-850b-f033d7d37d9a"
            )
        """

        response = self.drift.drift_archive_head(monitor_instance_id)
        return response
    
    def list_runs(self,
        monitor_instance_id: str, start: str = None,limit: int = None):
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
        
        #runs = Runs(watson_open_scale=self._ai_client)
        return self.runs.list(monitor_instance_id = monitor_instance_id, start=start,limit=limit)
        
    def get_run_details(self, monitor_instance_id: str, monitoring_run_id: str, **kwargs ):
        """
        Get monitoring run details.
        :param str monitor_instance_id: Unique monitor instance ID.
        :param str monitoring_run_id: Unique monitoring run ID.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitoringRun` result
        """
        #runs = Runs(watson_open_scale=self._ai_client)
        return self.runs.get(monitor_instance_id=monitor_instance_id, monitoring_run_id=monitoring_run_id)
        
    def explanation_tasks(self, scoring_ids: List[str], input_rows: List[dict] = None, explanation_types: List[str] = None, subscription_id = None,**kwargs ):
        """
        Compute explanations.

        Submit tasks for computing explanation of predictions.

        :param List[str] scoring_ids: IDs of the scoring transaction.
        :param List[dict] input_rows: (optional) List of scoring transactions.
        :param List[str] explanation_types: (optional) Types of explanations to
               generate.
        :param str subscription_id: (optional) Unique subscription ID.               
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `PostExplanationTaskResponse` result
        """    
        
        return self.explanation.add(scoring_ids=scoring_ids, input_rows=input_rows, explanation_types=explanation_types, subscription_id = subscription_id,**kwargs)
    
    def get_explanation_tasks(self, explanation_task_id: str, **kwargs ):
        """
        Get explanation.

        Get explanation for the given explanation task id.

        :param str explanation_task_id: ID of the explanation task.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `GetExplanationTaskResponse` result
        """
        return self.explanation.get(explanation_task_id=explanation_task_id)
    
    def get_all_explaination_tasks(self, offset= None,limit = None,subscription_id = None,scoring_id = None,status = None,**kwargs):
        """
        List all explanations.

        List of all the computed explanations.

        :param int offset: (optional) offset of the explanations to return.
        :param int limit: (optional) Maximum number of explanations to return.
        :param str subscription_id: (optional) Unique subscription ID.
        :param str scoring_id: (optional) ID of the scoring transaction.
        :param str status: (optional) Status of the explanation task.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `GetExplanationTasksResponse` result
        """
        return self.explanation.list(offset= offset,limit = limit,subscription_id = subscription_id,scoring_id = scoring_id,status = status,**kwargs)
    
    def get_measurement_details(self, monitor_instance_id: str,measurement_id: str, **kwargs ):
        """
        Get Measurement details.
        Get Measurement info for the given measurement and monitor  instance id.
        :param str monitor_instance_id: ID of the monitor instance.
        :param str measurement_id: ID of the measurement.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `MonitorMeasurementResponse` result
        """
        return self.measurements.get(monitor_instance_id=monitor_instance_id, measurement_id=measurement_id, **kwargs)
    
    #private method to check for finished state
    def __check_for_finished_status(self, background_mode, monitor_instance_id, response):
        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.get(monitor_instance_id=monitor_instance_id)
                return details.result.entity.status.state

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.get(monitor_instance_id=monitor_instance_id)
                state = details.result.entity.status.state

                if state in [StatusStateType.ACTIVE]:
                    return "Monitor instance successfully created", None, details
                else:
                    return "Monitor instance creation failed with status: {}".format(state), \
                           'Reason: {}'.format(["code: {}, message: {}".format(error.code, error.message) for error in
                                                details.result.entity.status.failure.errors]), details

            return print_synchronous_run(
                'Waiting for end of monitor instance creation {}'.format(monitor_instance_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.ACTIVE]
            )
    
    #private method to create monitors from training stats        
    def __create_monitor_from_training_stats(self, data_mart_id, training_stats_info, params, background_mode):
        subscription_id = params.get("subscription_id")
        
        validate_type(data_mart_id, 'data_mart_id', str, True)
        validate_type(subscription_id, 'subscription_id', str, True)
        
        responses = {}
        if 'fairness_configuration' in training_stats_info:
            target = Target(
                target_type=TargetTypes.SUBSCRIPTION,
                target_id=subscription_id
            )
            parameters = training_stats_info["fairness_configuration"]["parameters"]
            parameters["model_type"] = training_stats_info['common_configuration']['problem_type']
            thresholds = training_stats_info["fairness_configuration"]["thresholds"]
            print("Creating fairness monitor")                                    
            response = super().add(
                data_mart_id=data_mart_id,
                background_mode=False,
                monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.FAIRNESS.ID,
                target=target,
                parameters=parameters,
                thresholds=thresholds)
            
            mon_resp = self.__check_for_finished_status(background_mode, response.result.metadata.id, response = response)
            responses[self._ai_client.monitor_definitions.MONITORS.FAIRNESS.ID] = mon_resp.result.to_dict()
            
        if 'explainability_configuration' in training_stats_info:
            target = Target(
                target_type=TargetTypes.SUBSCRIPTION,
                target_id=subscription_id
            )
            parameters = {
                "enabled": True,
                "training_statistics": training_stats_info["explainability_configuration"]
            }
            print("Creating Explain monitor")
            response = super().add(
                data_mart_id=data_mart_id,
                background_mode=False,
                monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.EXPLAINABILITY.ID,
                target=target,
                parameters=parameters
            )   
            
            mon_resp = self.__check_for_finished_status(background_mode, response.result.metadata.id, response = response) 
            responses[self._ai_client.monitor_definitions.MONITORS.EXPLAINABILITY.ID] = mon_resp.result.to_dict()
            
            return responses
     
    def add_measurements(self,
        monitor_instance_id: str, monitor_measurement_request: List['MonitorMeasurementRequest'], **kwargs ):
        """
        Publish measurement data to OpenScale.

        Publish measurement data to OpenScale for a specific monitor instance.

        :param str monitor_instance_id: Unique monitor instance ID.
        :param List[MonitorMeasurementRequest] monitor_measurement_request:
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """  
        
        return self.measurements.add(monitor_instance_id=monitor_instance_id,monitor_measurement_request=monitor_measurement_request,**kwargs)  
    
    def upload_explainability_archive(self, subscription_id: str, archive: BinaryIO, **kwargs ):
        """
        Upload explainability archives.

        API to upload explainability archives such as the Perturbations scoring response
        archive. The api can also be used to update the archive.

        :param str subscription_id: Unique subscription ID.
        :param BinaryIO archive: explanation Archive
        :rtype: DetailedResponse
        """
        
        return self.explanation_service.explainability_archive_post(subscription_id=subscription_id,body=archive,**kwargs )
    
    def get_explainability_archive(self, subscription_id: str, **kwargs ):
        """
        Retrieves the Explainability archives.

        API to retrieve the Explainability archives.

        :param str subscription_id: Unique subscription ID.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse
        """
        
        return self.explanation_service.explainability_archive_get(subscription_id=subscription_id,**kwargs )
            