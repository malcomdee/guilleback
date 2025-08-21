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

"""
File containing constants used throughout the Watson OpenScale Python V2 SDK.
"""

DEFAULT_SERVICE_URL = "https://api.aiopenscale.cloud.ibm.com/openscale"
LITE_PLAN = "lite"

RESOURCES_URL_MAPPING = {
    "https://aiopenscale-dev.us-south.containers.appdomain.cloud/openscale": "https://resource-controller.test.cloud.ibm.com/v2/resource_instances",
    "https://aiopenscale-dev.us-south.containers.appdomain.cloud": "https://resource-controller.test.cloud.ibm.com/v2/resource_instances",
    "https://api.aiopenscale.test.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://aiopenscale.test.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://api.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://api.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://aiopenscale.test.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://api.aiopenscale.test.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://eu-de.api.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://eu-de.api.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://eu-de.aiopenscale.cloud.ibm.com/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://eu-de.aiopenscale.cloud.ibm.com": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://aios-yp-cr.us-south.containers.appdomain.cloud": "https://resource-controller.cloud.ibm.com/v2/resource_instances",
    "https://aios-yp-cr.us-south.containers.appdomain.cloud/openscale": "https://resource-controller.cloud.ibm.com/v2/resource_instances"
}