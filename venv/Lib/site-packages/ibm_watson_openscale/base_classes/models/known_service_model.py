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
from ibm_watson_openscale.supporting_classes import *
from ibm_watson_openscale.supporting_classes.monitoring_config import *
from ibm_watson_openscale.utils import *

class KnownServiceModel():
    def __init__(self, service_type, model_uid, deployment_uid, space_uid=None, problem_type=None, input_data_type=None,
                 training_data_reference=None, test_data_df=None, label_column=None, prediction_column=None, probability_column=None,
                 feature_columns=None, categorical_columns=None, favorable_classes=None, unfavorable_classes=None,
                 quality_config=None, fairness_config=None, drift_config=None):

        validate_type(model_uid, 'model_uid', str, True)
        validate_type(deployment_uid, 'deployment_uid', str, True)
        validate_type(space_uid, 'space_uid', str, False)
        validate_enum(problem_type, 'problem_type', ProblemType, False)
        validate_enum(input_data_type, 'input_data_type', InputDataType, False)
        validate_type(training_data_reference, 'training_data_reference', [TrainingDataReference, dict], False, subclass=True)
        validate_pandas_dataframe(test_data_df, "test_data_df", False)
        validate_type(label_column, 'label_column', str, False)
        validate_type(prediction_column, 'prediction_column', str, False)
        validate_type(probability_column, 'probability_column', str, False)
        validate_type(feature_columns, 'feature_columns', list, False)
        validate_type(categorical_columns, 'categorical_columns', list, False)
        validate_type(favorable_classes, 'favorable_classes', list, False)
        validate_type(unfavorable_classes, 'unfavorable_classes', list, False)
        validate_type(quality_config, "quality_config", [MonitoringConfig, dict], False, subclass=True)
        validate_type(fairness_config, "fairness_config", [MonitoringConfig, dict], False, subclass=True)
        validate_type(drift_config, "drift_config", [MonitoringConfig, dict], False, subclass=True)

        #Model.__init__(self, model_uid=model_uid, deployment_uid=deployment_uid)
        self.service_type = service_type
        self.model_uid = model_uid
        self.deployment_uid = deployment_uid
        self.space_uid = space_uid
        self.problem_type = problem_type
        self.input_data_type = input_data_type
        self.training_data_reference = training_data_reference
        self.test_data_df = test_data_df
        self.label_column = label_column
        self.prediction_column = prediction_column
        self.probability_column = probability_column
        self.feature_columns = feature_columns
        self.categorical_columns = categorical_columns
        self.favorable_classes = favorable_classes
        self.unfavorable_classes = unfavorable_classes

        if quality_config is None:
            quality_config = QualityMonitoringConfig()
        else:
            if isinstance(quality_config, dict):
                quality_config = QualityMonitoringConfig(config_dict=quality_config)

        if drift_config is None:
            drift_config = DriftMonitoringConfig()
        else:
            if isinstance(drift_config, dict):
                drift_config = DriftMonitoringConfig(config_dict=drift_config)

        if fairness_config is None:
            fairness_config = FairnessMonitoringConfig(favorable_classes=favorable_classes, unfavorable_classes=unfavorable_classes)
        else:
            if isinstance(fairness_config, dict):
                fairness_config = FairnessMonitoringConfig(config_dict=fairness_config)

        self.quality_config = quality_config
        self.drift_config = drift_config
        self.fairness_config = fairness_config
        
        

