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

from ibm_watson_openscale.base_classes.watson_open_scale_v2 import *
from ibm_watson_openscale.supporting_classes.enums import *
from ibm_watson_openscale.utils import *

def create_service_binding(ai_client, space_uid, engine_credentials, service_type = "watson_machine_learning", operational_space_id = "pre_production"):
    
    validate_type(ai_client, 'ai_client', WatsonOpenScaleV2, True)
    validate_type(engine_credentials, "engine_credentials", dict, True)
    
    
    binding_exists = False
    bindings = ai_client.service_providers.list().result.to_dict()["service_providers"]
    
    service_provider_id = None
    #if service_type != ServiceTypes.WATSON_MACHINE_LEARNING:
    #    raise Exception('Support for other engine types "{}" coming soon '.format(service_type))
    
    for binding_details in bindings:
        if service_type == ServiceTypes.WATSON_MACHINE_LEARNING:
            if "entity" in binding_details and "deployment_space_id" in binding_details["entity"]:
                if binding_details["entity"]["deployment_space_id"] == space_uid and binding_details["entity"]["operational_space_id"] == operational_space_id:
                    service_provider_id = binding_details["metadata"]["id"]
                    break
    
    credentials = None
    provider_name = None
    if service_type == ServiceTypes.WATSON_MACHINE_LEARNING:
        provider_name = "WML OneAPI"
        credentials = WMLCredentialsCloud(
                apikey=None,
                instance_id=None,
                url=None
            ) 
    elif service_type == ServiceTypes.AMAZON_SAGEMAKER: 
        provider_name="AWS OneAPI"
        space_uid = None
        credentials=SageMakerCredentials(
            access_key_id=engine_credentials['access_key_id'],
            secret_access_key=engine_credentials['secret_access_key'],
            region=engine_credentials['region']
        ) 
                
    if service_provider_id is None:
        service_provier_info = ai_client.service_providers.add(
            service_type = service_type,
            background_mode=False,
            name=provider_name,
            deployment_space_id = space_uid,
            operational_space_id = operational_space_id,
            credentials=credentials
        )
        print("Binding created successfully")
        service_provider_id = service_provier_info.result.metadata.id
    else:
        print("Using existing binding {}".format(service_provider_id))

    return service_provider_id