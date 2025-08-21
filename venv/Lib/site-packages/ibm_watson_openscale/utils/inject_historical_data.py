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

import random
import json
from datetime import datetime, timedelta, timezone
from ibm_watson_openscale.utils import validate_type
from ibm_watson_openscale import *
from ibm_watson_openscale.supporting_classes.enums import FeedbackType
import os

current_time = datetime.utcnow().isoformat() + 'Z'


class HistoricalData:
    def __init__(self, ai_client: 'APIClient' = None):
        validate_type(ai_client, 'ai_client', APIClient, True)
        self.current_time = datetime.utcnow().isoformat() + 'Z'
        self.ai_client = ai_client

    def load_historical_kpi_measurement(self, file_path, monitor_instance_id,
                                        day_template="history_payloads_{}.json", days=7, batch_id_start=0,
                                        ignore_metrics=None, batch_id_template="batch-id-{}"):

        with open(file_path) as json_file:
            historical_kpi = json.load(json_file)

        measurement = historical_kpi['history_payloads_0.json'][0]
        metric_names = [metric['id'] for metric in measurement['metrics']]

        monitor_details = self.ai_client.monitor_instances.get(
            monitor_instance_id=monitor_instance_id
        )

        monitor_definition_id = monitor_details.result.entity.monitor_definition_id
        monitor_definition_details = self.ai_client.monitor_definitions.get(
            monitor_definition_id=monitor_definition_id
        )
        tags = monitor_definition_details.result.entity.tags

        payload = []

        batch_id_number = batch_id_start

        for day in range(0, days):
            payload_day_json = day_template.format(day)
            if payload_day_json in historical_kpi.keys():
                for h_measurements in historical_kpi[payload_day_json]:
                    metrics_dict = {}
                    for tag in tags:
                        if 'batch_id' in tag['id']:
                            metrics_dict[tag['id']] = batch_id_template.format(batch_id_number)

                    for name in metric_names:
                        for h_metric in h_measurements['metrics']:
                            if name == h_metric['id']:
                                if ignore_metrics is None or name not in ignore_metrics:
                                    metrics_dict[name] = h_metric['value']

                    start_time = datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%S.%fZ") - timedelta(
                        hours=batch_id_number)
                    start_time = start_time.replace(tzinfo=timezone.utc)

                    payload.append(MonitorMeasurementRequest(
                        timestamp=start_time,
                        metrics=[MonitorMeasurementMetrics.from_dict(metrics_dict)]
                    ))
                    batch_id_number += 1

        response = self.ai_client.monitor_instances.store_measurements(
            monitor_instance_id=monitor_instance_id,
            monitor_measurement_request=payload
        )
        print(response.result)

    def load_historical_drift_measurement(self, file_path, business_application_id, monitor_instance_id,
                                          day_template="history_payloads_{}.json", days=7,
                                          batch_id_start=0,
                                          batch_id_template="batch-id-{}", bkpis_file_path=None):

        with open(file_path) as json_file:
            historical_drift = json.load(json_file)

        payload = []

        # Mock for correlations
        if bkpis_file_path is None:
            bkpis_file_path = os.path.join(os.curdir, 'datasets', 'German_credit_risk', 'historical_records',
                                           'history_kpi.json')

        with open(bkpis_file_path) as json_file:
            historical_bkpis = json.load(json_file)
        # --------- end of mock -----------

        batch_id_number = batch_id_start

        for day in range(0, days):
            for h_measurements, kpi_measurement in zip(historical_drift[day_template.format(day)],
                                                       historical_bkpis[day_template.format(day)]):
                acc_number_accepted = \
                    [metric['value'] / 600 for metric in kpi_measurement['metrics'] if
                     metric['id'] == 'accepted_credits'][0]
                acc_daily_revenue = [metric['value'] / 2500 for metric in kpi_measurement['metrics'] if
                                     metric['id'] == 'credit_amount_granted'][0]

                start_time = datetime.strptime(current_time, "%Y-%m-%dT%H:%M:%S.%fZ") - timedelta(hours=batch_id_number)
                start_time = start_time.replace(tzinfo=timezone.utc)

                payload.append(MonitorMeasurementRequest(
                    timestamp=start_time,
                    metrics=[MonitorMeasurementMetrics(drift_magnitude=1 - acc_number_accepted,
                                                       predicted_accuracy=acc_number_accepted,
                                                       data_drift_magnitude=1 - acc_number_accepted,
                                                       transaction_batch_id=batch_id_template.format(batch_id_number),
                                                       business_application_id=business_application_id,
                                                       business_metric_id="accepted_credits"),
                             MonitorMeasurementMetrics(drift_magnitude=1 - acc_daily_revenue,
                                                       predicted_accuracy=acc_daily_revenue,
                                                       data_drift_magnitude=1 - acc_daily_revenue,
                                                       transaction_batch_id=batch_id_template.format(batch_id_number),
                                                       business_application_id=business_application_id,
                                                       business_metric_id="credit_amount_granted")]
                ))
                batch_id_number += 1

        response = self.ai_client.monitor_instances.store_measurements(
            monitor_instance_id=monitor_instance_id,
            monitor_measurement_request=payload
        )
        print(response.result)
