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

import requests
from .client_errors import AuthorizationError

class EntitlementClient:

    def __init__(self, url, bearer_token, instance_id):
        self.bearer_token = bearer_token
        self.instance_id = instance_id
        # Since we're using v1 API for entitlements
        if url.endswith("openscale"):
            url = url[0:len(url) - 10]
        self.entitlement_url = url + '/v1/entitlements'
        
    def is_entitled(self):
        response = self.get_entitlements()
        plan_name = None
        msg = "You are not authorized to access AI OpenScale instance {}".format(self.instance_id)
        try:
            entitlements = response['entitlements']
            if 'ai_openscale' not in entitlements:
                raise AuthorizationError(msg)

            instances = entitlements['ai_openscale']
            if len(instances) <= 0:
                raise AuthorizationError(msg)

            current_instance = None
            for instance in instances:
                if self.instance_id == instance['id']:
                    current_instance = instance
                    break

            if not current_instance:
                raise AuthorizationError(msg)

            instance_id = current_instance['id']
            if 'plan_name' in current_instance:
                plan_name = current_instance['plan_name']
            if len(instance_id) <= 0:
                raise AuthorizationError(msg)   
        except KeyError:
            raise AuthorizationError("Failed to authenticate")
        return plan_name

    def get_entitlements(self, verify=True):
        response = requests.get(self.entitlement_url, verify=verify, headers=self.get_headers())
        if not response.ok:
            raise AuthorizationError("Failed to authenticate")
        return response.json()

    def get_headers(self):
        headers = {}
        headers["Authorization"] = "Bearer " + self.bearer_token
        headers["Accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        return headers
