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

from ibm_watson_openscale.utils.utils import validate_type
from typing import Union
import datetime
import uuid
import json


class PayloadRecord:
    """
    Used during payload logging, describes payload record.

    :param request: scoring request
    :type request: dict

    :param response: scoring response
    :type response: dict

    :param scoring_id: scoring identifier (optional). If not provided random uid is assigned.
    :type scoring_id: str

    :param scoring_timestamp: scoring request timestamp (optional). If not provided current time is assigned.
    :type scoring_timestamp: str

    :param response_time: scoring response time in ms (optional)
    :type response: int
    """

    def __init__(self, request: dict,
                 response: Union[dict, str],
                 scoring_id: str = None,
                 scoring_timestamp: str = None,
                 response_time: int = None,
                 asset_revision: str = None,
                 multiple_records: bool = True) -> None:

        validate_type(request, "request", dict, True)
        validate_type(response, "response", [dict, str], True)
        validate_type(scoring_id, "scoring_id", str, False)
        validate_type(scoring_timestamp, "scoring_timestamp", str, False)
        validate_type(response_time, "response_time", int, False)
        validate_type(asset_revision, "asset_revision", str, False)
        validate_type(multiple_records, "multiple_records", bool, False)

        self.request = request
        self.response = response if type(response) is dict else json.loads(response)
        self.scoring_id = scoring_id
        self.scoring_timestamp = scoring_timestamp
        self.response_time = response_time
        self.asset_revision = asset_revision
        self.multiple_records = multiple_records

    def to_json(self):
        record = {
            'request': self.request,
            'response': self.response
        }

        if self.scoring_timestamp is not None:
            record['scoring_timestamp'] = self.scoring_timestamp
        else:
            record['scoring_timestamp'] = str(datetime.datetime.utcnow().isoformat()) + 'Z'

        if self.scoring_id is not None:
            record['scoring_id'] = self.scoring_id
        else:
            record['scoring_id'] = str(uuid.uuid4())

        if self.response_time is not None:
            record['response_time'] = int(self.response_time)

        if self.asset_revision is not None:
            record['asset_revision'] = str(self.asset_revision)

        record['multiple_records'] = self.multiple_records

        return record
