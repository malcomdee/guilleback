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

import json
from datetime import datetime, timedelta
from ibm_watson_openscale.utils import validate_type, FeedbackType
from ibm_watson_openscale.supporting_classes.payload_record import PayloadRecord
from ibm_watson_openscale import APIClient
import csv
import os


class DemoData:
    def __init__(self, ai_client: 'APIClient' = None):
        validate_type(ai_client, 'ai_client', APIClient, True)
        self.current_time = datetime.utcnow().isoformat() + 'Z'
        self.ai_client = ai_client

    def load_demo_business_payload(self,
                                   data_set_id: str,
                                   file_path: str = os.getcwd(),
                                   file_name: str = "history_business_payloads_week.csv",
                                   background_mode: bool = True,
                                   limit: int = 1000) -> None:
        payload_file = os.path.join(file_path, file_name)

        def _num(string_value):
            try:
                return float(string_value)
            except ValueError:
                return string_value

        with open(payload_file) as f:
            reader = csv.DictReader(f)
            list_payload = [row for row in reader]
            historical_business_payload = []

            hourly_records = len(list_payload) // 24 // 7
            index = 0
            for n_day in range(7):
                for hour in range(24):
                    for i in range(hourly_records):
                        record = dict(list_payload[index])
                        for field in record.keys():
                            record[field] = _num(record[field])

                        record['timestamp'] = str(self._get_score_time(n_day, hour))
                        historical_business_payload.append(record)
                        index += 1

            self.ai_client.data_sets.store_records(
                background_mode=background_mode,
                request_body=historical_business_payload,
                data_set_id=data_set_id,
                limit=limit
            )

    def load_demo_scoring_payload(self,
                                  data_set_id: str,
                                  file_path: str = os.getcwd(),
                                  day_template: str = "history_correlation_payloads_{}.json",
                                  days: int = 7,
                                  background_mode: bool = True,
                                  limit: int = 1000) -> None:

        print("Loading historical scoring payload...")

        for n_day in range(days):
            print("Day {} injection.".format(n_day))
            record_list = []
            payload_file = os.path.join(file_path, day_template.format(n_day))
            with open(payload_file) as f:
                historical_payload = json.load(f)
                hourly_records = len(historical_payload) // 24
                index = 0
                for hour in range(24):
                    for i in range(hourly_records):
                        req = historical_payload[index]['request']
                        resp = historical_payload[index]['response']
                        scoring_id = None
                        if 'scoring_id' in historical_payload[index]:
                            scoring_id = historical_payload[index]['scoring_id']
                        response_time = None
                        if 'response_time' in historical_payload[index]:
                            response_time = historical_payload[index]['response_time']
                        score_time = str(self._get_score_time(n_day, hour))
                        record_list.append(PayloadRecord(scoring_id=scoring_id, request=req, response=resp,
                                                         scoring_timestamp=score_time, response_time=response_time))
                        index += 1

            self.ai_client.data_sets.store_records(
                background_mode=background_mode,
                request_body=historical_payload,
                data_set_id=data_set_id,
                limit=limit
            )
            print("Daily loading finished.")

    @staticmethod
    def _get_score_time(day, hour):
        return datetime.utcnow() + timedelta(hours=(-(24 * day + hour + 1)))
