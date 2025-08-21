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

import datetime
import logging
import time
import uuid

import json

from ibm_watson_openscale.base_classes.watson_open_scale_v2 import *
from ibm_watson_openscale.supporting_classes.enums import *
from ibm_watson_openscale.supporting_classes import *
from ibm_watson_openscale.supporting_classes.feature import Feature
from ibm_watson_openscale.supporting_classes.monitoring_config import ConfigSummary
from ibm_watson_openscale.utils import *
from ibm_watson_openscale.utils.model_utils import *

from ibm_watson_openscale.base_classes.models.known_service_model import KnownServiceModel

POST_AUTO_DETECTION = "{}/v2/monitoring_services/fairness/subscriptions/{}/auto_detect"
GET_AUTO_DETECTION = "{}/v2/monitoring_services/fairness/subscriptions/{}/auto_detect"

class Model:
    """
    Manage model evaluation.

    """

    def __init__(self, ai_client):
        from ibm_watson_openscale import APIClient
        validate_type(ai_client, 'ai_client', APIClient, True)
        self._logger = logging.getLogger(__name__)
        self._ai_client = ai_client
        self.is_icp = False
        self._model = None
        #self._hrefs_v2 = AIHrefDefinitionsV2(ai_client._service_credentials)
        self._evaluated = False
        self._evaluation_result = None
        self._subscription = None

    def evaluate(self, model: KnownServiceModel, db_credentials=None, schema=None, engine_credentials=None,
                 publish_lineage="true", publish_fact = "true"):
        """
        Evaluates a given model for risk

        :param model: the details of the model which should be evaluated
        :type model: KnownServiceModel

        :param db_credentials: describes the instance which should be connected
        :type db_credentials: dict

        :param schema: schema in your database under which the tables should be created
        :type schema: str

        :param engine_credentials: you can use internally provided database. Please note that this db comes with limitations.
        :type engine_credentials: dict

        :param publish_lineage: flag to indicate if a lineage event should be published for the evaluation done
        :type publish_lineage: str
        
        :param publish_fact: flag to indicate whether fact should be published or not for the evaluation done
        :type publish_fact: str

        A way you might use me is:

        >>> from ibm_watson_openscale.base_classes.models.engine_models.wml import WatsonMachineLearningModel
        >>>
        >>> model = WatsonMachineLearningModel(model_uid=pre_prod_model_uid,
        >>>                           deployment_uid=pre_prod_deployment_uid,
        >>>                           space_uid = space_id,
        >>>                           label_column = label_column,
        >>>                           training_data_reference=cos_training_data,
        >>>                           test_data_df=df,
        >>>                           training_data_reference=training_data_reference,
        >>>                           favorable_classes=['No Risk'],
        >>>                           unfavorable_classes=['Risk']
        >>>                           quality_config=quality_config, fairness_config=fairness_config, drift_config=drift_config
        >>>                           )
        >>>
        >>> ai_client.model.evaluate(model, engine_credentials=WML_CREDENTIALS)
        """

        self._model = model

        # 1. Setup data mart
        print("Setting up Datamart...")
        datamart_details = self._setup_data_mart(db_credentials=db_credentials, schema_name=schema)
        datamart_id = datamart_details['metadata']['id']

        # 2. Create bindings
        print("Setting up Service Binding...")
        #binding_uid = self._bind_engine(model.service_type, engine_credentials=engine_credentials)
        binding_uid = create_service_binding(self._ai_client, self._model.space_uid, engine_credentials,self._model.service_type)
        
        # 3. Validate model details
        print("Validating model...")
        self._model.validate(self._ai_client, binding_uid, self.is_icp)

        # 4. Create subscription
        print("Creating Subscription...")
        self._subscription = self._subscribe_model(datamart_id,binding_uid)
        subscription_id = self._subscription.metadata.id

        # 5. Add record to payload logging table
        print("Adding payload record...")
        self._add_payload_logging_record(self._subscription)

        # 6. Update asset properties from updated output data schema
        self._subscription = self._update_asset_properties(self._subscription.to_dict())

        # 6. Enable monitors
        print("Enabling Monitors...")
        self._enable_monitors(datamart_id,subscription_id)

        # Enable this flag, so that configuration summary can be queried on this class
        self._evaluated = True
        
        # 7. Run MRM evaluation
        print("Triggering Mrm risk evaluations request...")
        self._ai_client.monitor_instances.mrm_monitoring.run_risk_evaluations(test_data_df=self._model.test_data_df,
                                                               test_data_set_name=self._get_test_data_set_name(),
                                                               publish_lineage=publish_lineage, publish_fact=publish_fact)

        # 8. Grab MRM evaluation result
        print("Grabbing Mrm risk evaluations results...")
        self._evaluation_result = self._ai_client.monitor_instances.mrm_monitoring.get_result()
        print(self._evaluation_result)
        print("Mrm risk evaluation finished successfully")

        # 8. Return measurement response (along with URL dashboard link to model summary)
        return

    def get_configuration_summary(self, print_summary=True):
        """
        Returns all the  monitor configuration details

        :param print_summary: prints the individual monitor configuration
        :type print_summary: bool

        :return: configuration summary
        :type: ConfigSummary

        A way you might use me is:

        >>> ai_client.model.get_configuration_summary()
        >>> ai_client.model.get_configuration_summary(print_summary=False)
        """

        if print_summary:
            if self._model.quality_config is not None:
                print_text_header_h2("Quality Configuration")
                print(self._model.quality_config.get())

            if self._model.drift_config is not None:
                print_text_header_h2("Drift Configuration")
                print(self._model.drift_config.get())

            if self._model.fairness_config is not None:
                print_text_header_h2("Fairness Configuration")
                print(self._model.fairness_config.get())

        return ConfigSummary(self._model.quality_config, self._model.drift_config, self._model.fairness_config)

    def get_result(self, include_config=True):
        """
        Returns the result of the risk evaluation along with the monitor configuration summary

        :param include_config: indicates if the monitor configuration summary should also be returned
        :type include_config: bool

        :return: evaluation result
        :type: dict

        A way you might use me is:

        >>> ai_client.model.get_result()
        >>> ai_client.model.get_result(include_config=False)
        """

        if not self._evaluated:
            raise ClientError("Evaluate method has not be called")

        if include_config:
            self.get_configuration_summary()

        if self._evaluation_result is not None:
            print_text_header_h2("Evaluation Result")
            print(self._get_insights_url() + "/" + self._model.deployment_uid)
            print("")
            print(json.dumps(self._evaluation_result, indent=4))

        return self._evaluation_result

    def _get_insights_url(self):
        aios_url = self._ai_client.service_url[0:self._ai_client.service_url.index("/openscale")]
        if self.is_icp:
            insights_url = aios_url + "/aiopenscale/insights"
        else:
            temp_url = aios_url.replace('api.', '')
            insights_url = temp_url + "/aiopenscale/insights"
        return insights_url

    def _setup_data_mart(self, db_credentials=None, schema_name=None):

        self.is_icp = self._ai_client.is_cp4d

        try:
            self._ai_client.data_marts.get(self._ai_client.service_instance_id)
            print('Using existing datamart')
        except:
            raise Exception("Creation of new datamart not implemented")
            '''
            if db_credentials is not None:
                print('Setting up external datamart')
                self._ai_client.data_marts.setup(db_credentials=db_credentials, schema=schema_name)
            else:
                print('Setting up internal datamart')
                self._ai_client.data_marts.setup(internal_db=True)
            '''    

        return self._ai_client.data_marts.get(self._ai_client.service_instance_id).result.to_dict()

    def _bind_engine(self, service_type, engine_credentials=None):

        binding_exists = False
        bindings = self._ai_client.service_providers.list().result.to_dict()["service_providers"]
        
        label = "pre_production"
        service_provider_id = None
        if service_type != "watson_machine_learning":
            raise Exception('Support for other engine types "{}" coming soon '.format(service_type))
            
        validate_type(self._model.space_uid, "space_uid", str, True)
        
        for binding_details in bindings:
            if "entity" in binding_details and "deployment_space_id" in binding_details["entity"]:
                if binding_details["entity"]["deployment_space_id"] == self._model.space_uid and binding_details["entity"]["operational_space_id"] == label:
                    service_provider_id = binding_details["metadata"]["id"]
                    break
                    
        if service_provider_id is None:
            service_provier_info = self._ai_client.service_providers.add(
                service_type = service_type,
                background_mode=False,
                name="WMLInstance_{}".format(self._model.space_uid),
                deployment_space_id = self._model.space_uid,
                operational_space_id = label,
                credentials=WMLCredentialsCloud(
                    apikey=None,
                    instance_id=None,
                    url=None
                )
            )
            print("Binding created successfully")
            service_provider_id = service_provier_info.result.metadata.id
        else:
            print("Using existing binding {}".format(service_provider_id))

        return service_provider_id

    def _subscribe_model(self, data_mart_id,binding_uid):

        subscriptions = self._ai_client.subscriptions.list().result.to_dict()["subscriptions"]
        for subscription in subscriptions:
            sub_name = subscription['entity']['asset']['name']
            if sub_name == self._model.deployment_name:
                self._ai_client.subscriptions.delete(subscription['metadata']['id'],background_mode=False)
                print('Deleted existing subscription for', self._model.deployment_name)
                break

        # Retrieve the deployment information
        deployment_asset = self._ai_client.service_providers.get_deployment_asset(
                data_mart_id=data_mart_id,
                service_provider_id=binding_uid,
                deployment_id = self._model.deployment_uid,
                deployment_space_id = self._model.space_uid
                
            )
        asset = Asset(
            asset_id=deployment_asset['entity']['asset']['asset_id'],
            name=deployment_asset['entity']['asset']['name'],
            url=deployment_asset['entity']['asset']['url'],
            asset_type=deployment_asset['entity']['asset']['asset_type'] if 'asset_type' in
                                                                                           deployment_asset[
                                                                                               'entity'][
                                                                                               'asset'] else 'model',
            problem_type=self._model.problem_type,
            model_type=deployment_asset['entity']['asset_properties']['model_type'],
            runtime_environment=deployment_asset['entity']['asset_properties']['runtime_environment'],
            input_data_type=InputDataType.STRUCTURED,
        )
        
        desc = None
        if 'description' in deployment_asset['entity']:
            desc = deployment_asset['entity']['description']
        scoring_end_point = ScoringEndpointRequest(url=deployment_asset['entity']['scoring_endpoint']['url'] )
        deployment = AssetDeploymentRequest(
            deployment_id=deployment_asset['metadata']['guid'],
            url=deployment_asset['metadata']['url'],
            name=deployment_asset['entity']['name'],
            description=desc,
            deployment_type=deployment_asset['entity']['type'],
            scoring_endpoint = scoring_end_point
        )
        # TODO convert into TrainingDataReference object
        
        training_data_reference = None
        if self._model.training_data_reference==None:
            training_data_reference = None
        else:    
            training_info = self._model.training_data_reference
            if training_info['type']=="cos":
                training_data_reference = TrainingDataReference(type=training_info['type'],
                                  location=COSTrainingDataReferenceLocation(
                                      bucket=training_info['location']['bucket'],
                                      file_name=training_info['location']['file_name']),
                                  connection=COSTrainingDataReferenceConnection(
                                      resource_instance_id=training_info['connection']['resource_instance_id'],
                                      url=training_info['connection']['url'],
                                      api_key=training_info['connection']['api_key'],
                                      iam_url=training_info['connection']['iam_url']),
                                  name = training_info['location']['file_name']
                                  )
            else:
               training_data_reference =  TrainingDataReference(type=training_info['type'],
                                  location=DB2TrainingDataReferenceLocation(
                                      table_name=training_info['location']['table_name'],
                                      schema_name=training_info['location']['db2_schema_name']),
                                  connection=DB2TrainingDataReferenceConnection(
                                      hostname = training_info['connection']['hostname'],
                                      username=training_info['connection']['username'],
                                      password=training_info['connection']['password'],
                                      database_name=training_info['connection']['db']
                                    ),
                                    name = training_info['location']['file_name']
                                  )
        asset_properties = AssetPropertiesRequest(
            transaction_id_field='transaction_id',
            label_column=self._model.label_column,
            #TODO Find what should be the value
            predicted_target_field='predictedLabel',
            prediction_field=self._model.prediction_column,
            probability_fields=self._model.probability_column,
            feature_fields=self._model.feature_columns,
            categorical_fields=self._model.categorical_columns,
            training_data_reference = training_data_reference,
            training_data_schema = None,
            input_data_schema = None,
            output_data_schema = None
        )
            
        subscription = self._ai_client.subscriptions.add(
            data_mart_id=data_mart_id,
            service_provider_id=binding_uid,
            asset=asset,
            deployment=deployment,
            asset_properties=asset_properties,
            background_mode=False
        ).result

        print("Subscription created successfully. Id {}".format(subscription.metadata.id))

        return subscription

    def _add_payload_logging_record(self, subscription, record_count=1):
        print("Sending Payload records to Datamart")
        self._model.add_payload_logging_record(record_count, self.is_icp)
        count = 0
        print("Waiting 30 seconds for payload records to reach datamart")
        time.sleep(30)
            #count = subscription.payload_logging.get_records_count()
        payload_id = self._ai_client.data_sets.list(type=DataSetTypes.PAYLOAD_LOGGING, 
                                                target_target_id=subscription.metadata.id, 
                                                target_target_type=TargetTypes.SUBSCRIPTION).result.data_sets[0].metadata.id
        print("Total payload logging records {}".format(self._ai_client.data_sets.get_records_count(payload_id)))                                                         

    def _enable_monitors(self, data_mart_id, subscription_id):
        
        target = Target(
            target_type=TargetTypes.SUBSCRIPTION,
            target_id=subscription_id
        )
        
        # Infer features if they are not provided by user
        enable_fairness = True
        if self._model.fairness_config.features is None:
            status, response = self._get_recommended_features(subscription_id)
            # if there was error while infering the features or no features were found then don't enable fairness
            if 'features' not in response['parameters']:
                enable_fairness = False
            else:    
                recommended_features = response['parameters']['features']
                all_recommended_features = []
                for rec_feature in recommended_features:
                    feat = Feature(rec_feature['feature'],rec_feature['recommended_majority'],rec_feature['recommended_minority'],rec_feature['recommended_threshold'])
                    all_recommended_features.append(feat)
                self._model.fairness_config.features = all_recommended_features     
            
        # Enable Fairness Monitor
        if enable_fairness is True:
            features = self._model.fairness_config.features
            fairness_features = []
            for feature in features:
                f = {
                    "feature": feature.name,
                    "majority":feature.majority,
                    "minority":feature.minority,
                    "threshold": feature.threshold
                }
                fairness_features.append(f)
            
            parameters = {
                "min_records": self._model.fairness_config.min_records,
                "favourable_class": self._model.fairness_config.favorable_classes,
                "unfavourable_class": self._model.fairness_config.unfavorable_classes,
                "features" : fairness_features
            }
            
            thresholds = []
            for feature in features:
                thresholds.append(
                    {
                        "metric_id": "fairness_value",
                        "specific_values": [
                            {
                                "applies_to": [
                                    {
                                        "type": "tag",
                                        "value": feature.name,
                                        "key": "feature"
                                    }
                                ],
                                "value": int(feature.threshold * 100)
                            }
                        ],
                        "type": "lower_limit",
                        "value": int(feature.threshold * 100)
                    }
                )
            
            fairness_monitor_details = self._ai_client.monitor_instances.create(
                data_mart_id=data_mart_id,
                background_mode=False,
                monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.FAIRNESS.ID,
                target=target,
                parameters=parameters,
                thresholds = thresholds
            ).result
            print("Enabled Fairness monitor successfully") 
        else:
            print("Not Enabled Fairness monitor because features were not inferred")
            
        # Enable Quality Monitor
        parameters = {
                "min_feedback_data_size" : self._model.quality_config.min_records
        }
        thresholds = [
            MetricThresholdOverride(
                metric_id=self._ai_client.monitor_definitions.MONITORS.QUALITY.METRIC.ACCURACY,
                type=MetricThresholdTypes.LOWER_LIMIT,
                value=self._model.quality_config.threshold
            )
        ]
        
        quality_monitor_details = self._ai_client.monitor_instances.create(
            data_mart_id=data_mart_id,
            monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.QUALITY.ID,
            target=target,
            parameters=parameters,
            thresholds = thresholds,
            background_mode=False
        ).result
        print("Enabled Quality monitor successfully")

        # Enable Explainability monitor
        parameters = {
            'enabled':True
        }
        explainability_details = self._ai_client.monitor_instances.create(
            data_mart_id=data_mart_id,
            background_mode=False,
            monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.EXPLAINABILITY.ID,
            target=target,
            parameters=parameters
        ).result
        print("Enabled Explaination monitor successfully")
        
        
        # Enable Drift Monitor
        parameters = {
            "min_samples": self._model.drift_config.min_records,
            "train_drift_model":True,
            "drift_threshold":self._model.drift_config.threshold
            #"enable_model_drift": True,
            #"enable_data_drift": True
        }
        thresholds = [
            MetricThresholdOverride(
                metric_id=self._ai_client.monitor_definitions.MONITORS.DRIFT.METRIC.DROP_IN_ACCURACY,
                type=MetricThresholdTypes.LOWER_LIMIT,
                value=self._model.drift_config.threshold
            )
        ]
        
        drift_monitor_details = self._ai_client.monitor_instances.create(
            data_mart_id=data_mart_id,
            background_mode=False,
            monitor_definition_id=self._ai_client.monitor_definitions.MONITORS.DRIFT.ID,
            target=target,
            parameters=parameters,
            thresholds = thresholds
        ).result
        print("Enabled Drift monitor successfully")   
        
        # Enable Mrm Monitor
        self._ai_client.monitor_instances.mrm_monitoring.enable(subscription_id) 
    
    def _get_fairness_features_for_config(self, recommended_attributes):

        fairness_features = []
        if recommended_attributes is not None and "parameters" in recommended_attributes and "features" in \
                recommended_attributes["parameters"]:
            recommended_features = recommended_attributes["parameters"]["features"]
            for rf in recommended_features:
                fairness_features.append(
                    Feature(name=rf["feature"], majority=rf["majority"], minority=rf["minority"],
                            threshold=self._model.fairness_config.threshold))

        return fairness_features

    def _update_asset_properties(self, subscription_details):

        #subscription = self._ai_client.subscriptions.get(subscription.uid)
        #subscription_details = subscription.get_details()

        feature_columns = []
        categorical_columns = []
        prediction_column = None
        probability_columns = []

        if subscription_details is not None and "entity" in subscription_details:
            subscription_entity = subscription_details["entity"]
            if "asset_properties" in subscription_entity:
                asset_properties = subscription_entity["asset_properties"]
                if "output_data_schema" in asset_properties:
                    output_data_schema = asset_properties["output_data_schema"]
                    if "fields" in output_data_schema:
                        for field in output_data_schema["fields"]:
                            if "metadata" in field and "modeling_role" in field["metadata"]:
                                modeling_role = field["metadata"]["modeling_role"]
                                if modeling_role == "prediction":
                                    prediction_column = field["name"]
                                if modeling_role == "probability":
                                    probability_columns.append(field["name"])
                                if modeling_role == "feature":
                                    feature_columns.append(field["name"])
                                    if field["type"] == "string":
                                        categorical_columns.append(field["name"])
                                if "measure" in field["metadata"]:
                                    measure = field["metadata"]["measure"]
                                    if measure == "discrete":
                                        categorical_columns.append(field["name"])

        patch_subscription_payload = []
        if len(feature_columns) > 0:
            feature_columns_op = JsonPatchOperation(
                op=OperationTypes.REPLACE,
                path="/asset_properties/feature_fields",
                value=feature_columns
            )
            
            patch_subscription_payload.append(feature_columns_op)

        if len(categorical_columns) > 0:
            
            categorical_columns_op = JsonPatchOperation(
                op=OperationTypes.REPLACE,
                path="/asset_properties/categorical_fields",
                value=list(dict.fromkeys(categorical_columns))
            )
            
            patch_subscription_payload.append(categorical_columns_op)

        if prediction_column is not None:
            prediction_column_op = JsonPatchOperation(
                op=OperationTypes.REPLACE,
                path="/asset_properties/prediction_field",
                value=prediction_column
            )
            patch_subscription_payload.append(prediction_column_op)

        if len(probability_columns) > 0:
            probability_columns_op = JsonPatchOperation(
                op=OperationTypes.REPLACE,
                path="/asset_properties/probability_fields",
                value=probability_columns
            )
            patch_subscription_payload.append(probability_columns_op)

        response = None
        try:
            response = self._ai_client.subscriptions.update(subscription_id = subscription_details['metadata']['id'],patch_document=patch_subscription_payload)
        except ApiRequestFailure:
            raise ApiRequestFailure(u'Updating asset properties in subscrption failed. {} ', ApiRequestFailure)

        print("Asset properties updated in subscription")
        return subscription_details

    @staticmethod
    def _get_test_data_set_name():
        import datetime 
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"
        return "Evaluation-{}.csv".format(datetime.datetime.utcnow().strftime(date_format))
    
    def _get_recommended_features(self, subscription_id, check_completion_status=True):

        url = POST_AUTO_DETECTION.format(self._ai_client.service_url,subscription_id)
        payload = {
            "favourable_class": self._model.fairness_config.favorable_classes, 
            "unfavourable_class": self._model.fairness_config.unfavorable_classes
        }
        response = requests.post(url, json=payload,headers=self._get_headers())
        handle_response(202, u' Request to infer recommended features for Fairness accepted', response)
        
        status = None
        response = None

        print("Checking for status of inferring recommended features for Fairness")
        for i in range(10):
            url = GET_AUTO_DETECTION.format(self._ai_client.service_url,subscription_id)
            response = requests.get(url, headers=self._get_headers()).json()
            if "recommendation_status" in response['parameters'] :
                status = response["parameters"]["recommendation_status"]

            if status is not None:
                if not check_completion_status:
                    break
                import datetime
                print(datetime.datetime.utcnow().strftime('%H:%M:%S'), status.lower())
                if status.lower() in ["finished", "completed"]:
                    break
                elif "error" in status.lower() or "failed" in status.lower():
                    print(response)
                    break

            time.sleep(10)

        return status, response
    
    
    
    def _get_headers(self):
        token = self._ai_client.authenticator.token_manager.get_token() if  ( isinstance(self._ai_client.authenticator, IAMAuthenticator) or (isinstance(self._ai_client.authenticator, CloudPakForDataAuthenticator))) else self._ai_client.authenticator.bearer_token
        iam_headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer %s" % token
        }
        return iam_headers    
