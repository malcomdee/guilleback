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

from ibm_watson_openscale.utils import *

class Feature:
    """
    Used during setting fairness monitoring, describes features passed to fairness monitoring.

    :param name: name of feature
    :type name: str
    :param majority: range of feature values for majorities
    :type majority: list of list of ints
    :param minority: range of feature values for minorities
    :type minority: list of list of ints
    :param threshold: threshold
    :type threshold: float
    """
    def __init__(self, name, majority, minority, threshold):
        validate_type(name, 'name', str, True)
        validate_type(majority, 'majority', list, True)
        validate_type(minority, 'minority', list, True)
        validate_type(threshold, 'threshold', float, True)

        self.name = name
        self.majority = majority
        self.minority = minority
        self.threshold = threshold

    def _to_json(self):
        return {
            'feature': self.name,
            'majority': self.majority,
            'minority': self.minority,
            'threshold': self.threshold
        }
