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

# TODO: Rewrite each _has_value() method to be part of the base class
from enum import Enum


class InputDataType:
    """
    Describes possible model input data types.

    Contains: [STRUCTURED, UNSTRUCTURED_IMAGE, UNSTRUCTURED_TEXT, UNSTRUCTURED_AUDIO, UNSTRUCTURED_VIDEO]
    """
    STRUCTURED = 'structured'
    UNSTRUCTURED_IMAGE = 'unstructured_image'
    UNSTRUCTURED_TEXT = 'unstructured_text'
    UNSTRUCTURED_AUDIO = 'unstructured_audio'
    UNSTRUCTURED_VIDEO = 'unstructured_video'


class DeploymentTypes:
    """
    Describes possible model deployment types.

    Contains: [ONLINE]
    """
    ONLINE = 'online'


class RecordsFormatTypes:
    """
    Describes possible format types for getting list of records.

    Contains: [DICT, LIST]
    """
    DICT = 'dict'
    LIST = 'list'


class FeedbackType(Enum):
    """
    Describes supported types of feedback format.

    Contains: [WML, DICT, CSV]
    """
    WML = 'WML'
    DICT = 'DICT'
    CSV = 'CSV'
    PAYLOAD = 'PAYLOAD'
    LIST_OF_DICT = 'LIST_OF_DICT'

    @classmethod
    def has_value(cls, value):
        if value in cls._value2member_map_:
            return True
        else:
            raise KeyError("{} is not a feedback type. Use one of: {} as a feedback type.".format(
                value, [item.value for item in FeedbackType]
            ))


class ServiceTypes:
    """
    Describes supported types of service.

    Contains: [WATSON_MACHINE_LEARNING, AMAZON_SAGEMAKER,
                AZURE_MACHINE_LEARNING, CUSTOM_MACHINE_LEARNING,
                SPSS_COLLABORATION_AND_DEPLOYMENT_SERVICES]
    """
    WATSON_MACHINE_LEARNING = "watson_machine_learning"
    AMAZON_SAGEMAKER = "amazon_sagemaker"
    AZURE_MACHINE_LEARNING = "azure_machine_learning"
    CUSTOM_MACHINE_LEARNING = "custom_machine_learning"
    SPSS_COLLABORATION_AND_DEPLOYMENT_SERVICES = 'spss_collaboration_and_deployment_services'


class ResponseTypes:
    """
    Describes supported types of output format.

    Contains: [PANDAS, PYTHON]
    """
    PANDAS = "pandas"
    PYTHON = "python"


class TargetTypes:
    """
    Describes supported types of target format.

    Contains: [SUBSCRIPTION, BUSINESS_APPLICATION, INSTANCE, DATA_MART]
    """
    SUBSCRIPTION = 'subscription'
    BUSINESS_APPLICATION = 'business_application'
    INSTANCE = 'instance'
    DATA_MART = "data_mart"


class FormatTypes:
    """
    Format of the returned data. `full` format compared to `compact` is additive and
    contains `sources` part.
    """
    COMPACT = 'compact'
    FULL = 'full'


class IntervalTypes:
    """
    Time unit in which metrics are grouped and aggregated, interval by interval.
    """
    MINUTE = 'minute'
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'


class AggregationTypes:
    """
    Comma delimited function list constructed from metric name and function, e.g.
    `agg=metric_name:count,:last` that defines aggregations.
    """
    LAST = 'last'
    FIRST = 'first'
    MAX = 'max'
    MIN = 'min'
    SUM = 'sum'
    AVG = 'avg'
    COUNT = 'count'
    STDDEV = 'stddev'


class OnErrorTypes:
    """
    expected behaviour on error.
    """
    STOP = 'stop'
    CONTINUE = 'continue'


class ContentTypes:
    """
    The type of the input. A character encoding can be specified by including a
    `charset` parameter. For example, 'text/csv;charset=utf-8'.
    """
    APPLICATION_JSON = 'application/json'
    TEXT_CSV = 'text/csv'


class DataSetTypes:
    """
    type of the data set.
    """
    MANUAL_LABELING = 'manual_labeling'
    PAYLOAD_LOGGING = 'payload_logging'
    FEEDBACK = 'feedback'
    BUSINESS_PAYLOAD = 'business_payload'
    CUSTOM = 'custom'


class MetricThresholdTypes:
    LOWER_LIMIT = "lower_limit"
    UPPER_LIMIT = "upper_limit"


class StatusStateType:
    ACTIVE = "active"
    RUNNING = "running"
    FINISHED = "finished"
    PREPARING = "preparing"
    SUCCESS = "success"
    COMPLETED = "completed"
    FAILURE = "failure"
    FAILED = "failed"
    ERROR = "error"
    CANCELLED = "cancelled"
    CANCELED = "canceled"


class DatabaseType:
    """
    Describes possible options of choosing database type.

    Contains: [POSTGRESQL, DB2]
    """
    POSTGRESQL = 'postgresql'
    DB2 = 'db2'


class Choose:
    """
    Describes possible options of choosing result from table filtering when only one result is required.

    Contains: [FIRST, LAST, RANDOM]
    """
    FIRST = 'first'
    LAST = 'last'
    RANDOM = 'random'


class ProblemType:
    """
    Describes possible model (problem) types.

    Contains: [regression, binary, multiclass]
    """
    REGRESSION = 'regression'
    BINARY_CLASSIFICATION = 'binary'
    MULTICLASS_CLASSIFICATION = 'multiclass'


class AssetTypes:
    """

    """
    MODEL = "model"
    FUNCTION = "function"


class ExpectedDirectionTypes:
    """
    the indicator specifying the expected direction of the monotonic metric values.
    """
    INCREASING = "increasing"
    DECREASING = "decreasing"
    UNKNOWN = "unknown"


class SchemaUpdateModeTypes:
    """

    """
    NONE = "none"
    AUTO = "auto"


class IntegratedSystemTypes:
    """

    """
    OPEN_PAGES = "open_pages"
    WATSON_DATA_CATALOG = "watson_data_catalog"
    SLACK = "slack"


class OperationTypes:
    """
    The operation to be performed.
    """
    ADD = "add"
    REMOVE = "remove"
    REPLACE = "replace"
    MOVE = "move"
    COPY = "copy"
    TEST = "test"


class ScheduleRepeatTypes:
    """
    The type of interval to monitor the target.
    """
    MINUTE = "minute"
    HOUR = "hour"
    DAY = "day"
    WEEK = "week"
    MONTH = "month"
    YEAR = "year"


class TriggerTypes:
    """
    An identifier representing the source that triggered the run request (optional).
    One of: event, scheduler, user, webhook.
    """
    EVENT = "event"
    SCHEDULER = "scheduler"
    USER = "user"
    WEBHOOK = "webhook"
    BKPI_MANAGER = "bkpi_manager"


class NotificationServiceTypes:
    """
    The messaging service to use, for example, slack or email, or list_ref to indicate
    a previously created notification list.
    """
    SLACK = "slack"
    EMAIL = "email"
    LIST_REF = "list_ref"


class MessageFormatTypes:
    """
    The format of the message text.
    """
    TEXT = "text"
    HTML = "html"


class PayloadFieldTypes:
    """

    """
    STRING = "string"
    NUMBER = "number"


class TrainingDataReferenceType:
    """
    Type of the storage.
    """
    DB2 = "db2"
    COS = "cos"
    
class CP4DWMLLocation:
    """
    CP4D WML Location.
    """
    CPD_LOCAL = 'cpd_local'
    CPD_REMOTE = 'cpd_remote'
    CLOUD_REMOTE = 'cloud_remote'    