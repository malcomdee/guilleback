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

from ibm_watson_openscale.utils import validate_type


class Metric:
    """
    Used during custom monitor registration, describes metrics passed to custom monitor.

    :param name: name of the metric
    :type name: str
    :param description: description of the metric (optional)
    :type description: str
    :param lower_limit_default: lower control limit default value (optional)
    :type lower_limit_default: float
    :param upper_limit_default: upper control limit default value (optional)
    :type upper_limit_default: float
    :param required: is this metric obligatory? (default value True)
    :type required: bool
    """

    def __init__(self, name, description=None, lower_limit_default=None, upper_limit_default=None, required=True):
        validate_type(name, 'name', str, True)
        validate_type(description, 'description', str, False)
        validate_type(lower_limit_default, 'lower_limit', float, False)
        validate_type(upper_limit_default, 'upper_limit', float, False)
        validate_type(required, 'required', bool, False)

        self.name = name
        self.description = description
        self.lower_limit = lower_limit_default
        self.upper_limit = upper_limit_default
        self.required = required
        self.thresholds = []

        if self.lower_limit is not None:
            self.thresholds.append({"type": "lower_limit", "default": self.lower_limit})

        if self.upper_limit is not None:
            self.thresholds.append({"type": "upper_limit", "default": self.upper_limit})

    def _to_json(self):
        json_object = {
            'name': self.name,
            'required': self.required
        }

        if self.description is not None:
            json_object['description'] = self.description

        if len(self.thresholds) > 0:
            json_object['thresholds'] = self.thresholds

        return json_object
