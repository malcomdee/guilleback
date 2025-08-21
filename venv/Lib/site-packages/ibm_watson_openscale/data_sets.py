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

from io import BufferedReader
from typing import Tuple, Dict

from ibm_cloud_sdk_core import BaseService

from ibm_watson_openscale.base_classes.tables import Table
from ibm_watson_openscale.base_classes.common import get_sdk_headers
from .utils import *
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import DataSets as BaseDataSets
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import Records, Requests
from ibm_watson_openscale.supporting_classes.payload_record import PayloadRecord

if TYPE_CHECKING:
    from .client import WatsonOpenScaleV2Adapter
    from ibm_watson_openscale.base_classes.watson_open_scale_v2 import DetailedResponse, ScoringPayloadRequest

_DEFAULT_LIST_LENGTH = 50


class DataSets(BaseDataSets):
    """
    Manages Data Sets.
    """

    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter') -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        super().__init__(watson_open_scale=self._ai_client)

    def show(self, limit: int = 10,
             target_target_id: str = None,
             target_target_type: str = None,
             type: str = None,
             managed_by: str = None,
             **kwargs) -> None:
        """
        Show data sets. By default 10 records will be shown.

        :param limit: maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int
        :param str target_target_id: (optional) ID of the data set target (e.g.
               subscription ID, business application ID).
        :param str target_target_type: (optional) type of the target.
        :param str type: (optional) type of the data set.
        :param str managed_by: (optional) ID of the managing entity (e.g. business
               application ID).
        :param dict headers: A `dict` containing the request headers               
        :return: None

        A way you might use me is:

        >>>   client.data_sets.show()
        >>>   client.data_sets.show(limit=20)
        >>>   client.data_sets.show(limit=None)
        """
        validate_type(limit, u'limit', int, False)

        response = self.list(target_target_id = target_target_id,
             target_target_type = target_target_type,
             type = type,
             managed_by = managed_by,
             **kwargs)

        records = [[data_set.entity.data_mart_id,
                    data_set.entity.status.state,
                    data_set.entity.target.target_id,
                    data_set.entity.target.target_type,
                    data_set.entity.type,
                    data_set.metadata.created_at,
                    data_set.metadata.id
                    ] for data_set in response.result.data_sets]
        columns = ['data_mart_id', 'status', 'target_id', 'target_type', 'type', 'created_at', 'id']

        Table(columns, records).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="Data sets"
        )

    def add(self,
            data_mart_id: str,
            name: str,
            type: str,
            target: 'Target',
            data_schema: 'SparkStruct',
            description: str = None,
            schema_update_mode: str = None,
            location: 'LocationTableName' = None,
            managed_by: str = None,
            background_mode: bool = True) -> Union['DetailedResponse', Optional[dict]]:
        """
        Create Data Set.

        :param str data_mart_id:
        :param str name:
        :param str type:
        :param Target target:
        :param SparkStruct data_schema:
        :param str description: (optional)
        :param str schema_update_mode: (optional)
        :param LocationTableName location: (optional)
        :param str managed_by: (optional)
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataSetResponse` result

        A way you might use me is:

        >>> from ibm_watson_openscale import *
        >>> target = Target(
                 target_id='subscription_id',
                  target_type=TargetTypes.SUBSCRIPTION
               )
        >>> data_schema = SparkStruct(
                  type='struct',
                  fields=[
                      SparkStructField(
                          name='CheckingStatus',
                          type='string',
                          nullable=True,
                          metadata={'columnInfo': {'columnLength': 64},
                                    'measure': 'discrete',
                                    'modeling_role': 'feature'}
                      ),
                      SparkStructField(
                          name='LoanDuration',
                          type='integer',
                          nullable=True,
                          metadata={'modeling_role': 'feature'}
                      ),
                      SparkStructField(
                          name='asset_revision',
                          type='string',
                          nullable=True,
                          metadata={}
                      )
                  ]
               )
        >>> custom_dataset_info = client.data_sets.add(
                  target=target,
                  name='custom dataset',
                  type='custom',
                  data_schema=data_schema,
                  data_mart_id='997b1474-00d2-4g05-ac02-287ebfc603b5'
               )
        """
        response = super().add(data_mart_id=data_mart_id, target=target, name=name, type=type,
                               data_schema=data_schema,
                               description=description, schema_update_mode=schema_update_mode, location=location,
                               managed_by=managed_by)

        data_set_id = response.result.metadata.id

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.get(data_set_id=data_set_id)
                return details.result.entity.status.state

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.get(data_set_id=data_set_id)
                state = details.result.entity.status.state

                if state in [StatusStateType.ACTIVE]:
                    return "Successfully finished adding data set", None, details
                else:
                    return "Add data set failed with status: {}".format(state), \
                           'Reason: {}'.format(["code: {}, message: {}".format(error.code, error.message) for error in
                                                details.result.entity.status.failure.errors]), details

            return print_synchronous_run(
                'Waiting for end of adding data set {}'.format(data_set_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.ACTIVE]
            )

    def delete(self, data_set_id: str, background_mode: bool = True) -> Union['DetailedResponse', Optional[dict]]:
        """
        Delete Data Set.

        :param str data_set_id: ID of the data set.
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse

        A way you may use me:

        >>> client.data_sets.delete(data_set_id='997b1474-00d2-4g05-ac02-287ebfc603b5')
        """
        response = super().delete(data_set_id=data_set_id)

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.list()
                if data_set_id not in str(details.result):
                    return StatusStateType.FINISHED
                else:
                    return StatusStateType.ACTIVE

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.list()
                if data_set_id not in str(details.result):
                    state = StatusStateType.FINISHED
                else:
                    state = StatusStateType.ACTIVE

                if state in [StatusStateType.FINISHED]:
                    return "Successfully finished deleting data set", None, response
                else:
                    return "Delete data set failed", 'Reason: None', response  # TODO: Need to show the reason.

            return print_synchronous_run(
                'Waiting for end of deleting data set {}'.format(data_set_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.FINISHED]
            )

    def store_records(self,
                      data_set_id: str,
                      request_body: Union[str, 'BufferedReader', List['PayloadRecord'], List[List], List[Dict]],
                      header: bool = None,
                      skip: int = None,
                      limit: int = None,
                      delimiter: str = None,
                      on_error: str = None,
                      csv_max_line_length: float = None,
                      background_mode: bool = True) -> Union['DetailedResponse', Optional[dict]]:
        """
        Store records to specific data set.

        :param str data_set_id: ID of the data set.
        :param list[ScoringPayloadRequest] scoring_payload_request:
        :param bool header: (optional) if not provided service will attempt to
               automatically detect header in the first line.
        :param int skip: (optional) skip number of rows from input.
        :param int limit: (optional) limit for number of processed input rows.
        :param str delimiter: (optional) delimiter character for data provided as
               csv.
        :param str on_error: (optional) expected behaviour on error.
        :param float csv_max_line_length: (optional) maximum length of single line
               in bytes (default 10MB).
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `Status` result

        A way you might use me is:

        >>> from ibm_watson_openscale import *
        >>> store_record_info = client.data_sets.store_records(
              request_body=[
                        {
                          "GENDER": "M",
                          "PRODUCT_LINE": "Golf Equipment",
                          "AGE": 25,
                          "MARITAL_STATUS": "Unspecified",
                          "PROFESSION": "Sales"
                        },
                        {
                          "GENDER": "M",
                          "PRODUCT_LINE": "Sport shoes",
                          "AGE": 28,
                          "MARITAL_STATUS": "Married",
                          "PROFESSION": "Sales"
                        },
                        {
                          "GENDER": "F",
                          "PRODUCT_LINE": "Sport shoes",
                          "AGE": 25,
                          "MARITAL_STATUS": "Single",
                          "PROFESSION": "Software Developer"
                        }
                  ],
              data_set_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
          )
        >>> from ibm_watson_openscale.supporting_classes.payload_record import PayloadRecord
        >>> store_record_info = client.data_sets.store_records(
              request_body=[PayloadRecord(
                   scoring_id='42e62c3ae2244f0d851009dec4754d74',
                   request={
                      "fields": ["CheckingStatus", "LoanDuration", "CreditHistory", "LoanPurpose",
                          "LoanAmount", "ExistingSavings", "EmploymentDuration", "InstallmentPercent", "Sex",
                          "OthersOnLoan", "CurrentResidenceDuration", "OwnsProperty", "Age", "InstallmentPlans",
                          "Housing", "ExistingCreditsCount", "Job", "Dependents", "Telephone", "ForeignWorker"],
                      "values": [["less_0", 4, "all_credits_paid_back", "car_new", 250, "less_100", "less_1", 2,
                          "male", "none", 1, "real_estate", 26, "stores", "rent", 1, "unskilled", 1,
                          "none", "yes"]]
                      },
                   response={
                      "fields": ["CheckingStatus", "LoanDuration", "CreditHistory", "LoanPurpose", "LoanAmount",
                          "ExistingSavings", "EmploymentDuration", "InstallmentPercent", "Sex", "OthersOnLoan",
                          "CurrentResidenceDuration", "OwnsProperty", "Age", "InstallmentPlans", "Housing",
                          "ExistingCreditsCount", "Job", "Dependents", "Telephone", "ForeignWorker",
                          "CheckingStatus_IX", "CreditHistory_IX", "EmploymentDuration_IX", "ExistingSavings_IX",
                          "ForeignWorker_IX", "Housing_IX", "InstallmentPlans_IX", "Job_IX", "LoanPurpose_IX",
                          "OthersOnLoan_IX", "OwnsProperty_IX", "Sex_IX", "Telephone_IX", "features", "rawPrediction",
                          "probability", "prediction", "predictedLabel"],
                      "values": [["less_0", 4, "all_credits_paid_back", "car_new", 250, "less_100", "less_1", 2,
                          "male", "none", 1, "real_estate", 26, "stores", "rent", 1, "unskilled", 1, "none", "yes",
                          1.0, 3.0, 3.0, 0.0, 0.0, 1.0, 1.0, 1.0, 0.0, 0.0, 2.0, 0.0, 0.0, [1.0, 3.0, 0.0, 0.0, 3.0,
                          0.0, 0.0, 2.0, 1.0, 1.0, 1.0, 0.0, 0.0, 4.0, 250.0, 2.0, 1.0, 4.0, 26.0, 1.0, 1.0],
                          [19.600662549552556, 0.39933745044744245], [0.9800331274776278, 0.01996687252237212],
                          0.0, "No Risk"]]
                      },
                   response_time=460
               )],
              data_set_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
          )
          
        >>> csv_buffer_reader = io.open('path_to_csv', mode="rb")
        >>> store_record_info = client.data_sets.store_records(
              request_body=csv_buffer_reader,
              delimiter=',',
              header=True,
              limit=100,
              data_set_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
              csv_max_line_length = 8196
          )
        """
        records_client = Records(watson_open_scale=self._ai_client)
        
        if isinstance(request_body, BufferedReader):
            validate_type(request_body, "request_body", [str, BufferedReader], True)
            validate_type(header, "header", bool, True)
            validate_type(delimiter, "delimiter", str, True)
            validate_type(csv_max_line_length, "csv_max_line_length", int, True)
            response = records_client.add(
                on_error='continue',
                delimiter=delimiter,
                header=header,
                limit=limit,
                request_body=request_body,
                csv_max_line_length=csv_max_line_length,
                skip=skip,
                data_set_id=data_set_id,
                content_type='text/csv')

        elif isinstance(request_body, list) and request_body and isinstance(request_body[0], PayloadRecord):
            response = records_client.add(
                request_body=[record.to_json() for record in request_body],
                limit=limit,
                data_set_id=data_set_id,
                content_type='application/json')

        elif isinstance(request_body, list) and request_body and isinstance(request_body[0], dict) and \
                'fields' in str(request_body) and 'values' in str(request_body):
            response = records_client.add(
                request_body=request_body,
                limit=limit,
                data_set_id=data_set_id,
                content_type='application/json')

        elif isinstance(request_body, list) and request_body and isinstance(request_body[0], dict):
            response = records_client.add(
                request_body=request_body,
                limit=limit,
                data_set_id=data_set_id,
                content_type='application/json')

        else:
            raise IncorrectParameter(
                'request_body',
                reason=f"request_body parameter should be one of: "
                       f"[BufferedReader, List[PayloadRecord], List[Dict[fields, values]], List[Dict]]")

        request_id = response.headers._store['location'][1].split('/')[-1]

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.get_update_status(data_set_id=data_set_id, request_id=request_id)
                return details.result.state

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.get_update_status(data_set_id=data_set_id, request_id=request_id)
                state = details.result.state
                if state in [StatusStateType.ACTIVE]:
                    return "Successfully finished storing records", None, details
                else:
                    return "Store records failed with status: {}".format(state), \
                           'Reason: {}'.format(details.result.failure), details

            return print_synchronous_run(
                'Waiting for end of storing records with request id: {}'.format(request_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.ACTIVE]
            )

    def get_update_status(self,
                          data_set_id: str,
                          request_id: str) -> 'DetailedResponse':
        """
        Get status of the specific request.

        :param str data_set_id: ID of the data set.
        :param str request_id: ID of the request.
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `Status` result

        A way you might use me is:

        >>> update_status = client.data_sets.get_update_status(
              data_set_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
              request_id='7843-00d35462-346-ac0672-7357'
           )
        """
        requests_client = Requests(watson_open_scale=self._ai_client)
        return requests_client.get(data_set_id=data_set_id, request_id=request_id)
    '''
    def get_request_status(self, data_set_id: str, request_id: str, **kwargs) -> 'DetailedResponse':
        """
        Get status of the specific request.
        :param str data_set_id: ID of the data set.
        :param str request_id: ID of the request.
        :param dict headers: A `dict` containing the request headers
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `Status` result
        """

        if data_set_id is None:
            raise ValueError('data_set_id must be provided')
        if request_id is None:
            raise ValueError('request_id must be provided')
        headers = {}
        if 'headers' in kwargs:
            headers.update(kwargs.get('headers'))
        sdk_headers = get_sdk_headers(service_name=self._ai_client.DEFAULT_SERVICE_NAME, service_version='V2',
                                      operation_id='data_sets_get_request_status')
        headers.update(sdk_headers)

        url = '/v2/data_sets/{0}/requests/{1}'.format(
            *self._ai_client.encode_path_vars(data_set_id, request_id))
        request = self._ai_client.prepare_request(method='GET',
                                                          url=url,
                                                          headers=headers)

        response = self._ai_client.send(request)
        print(response.result)
        response.result = Status.from_dict(response.result)
        return response
    '''

    def get_list_of_records(self,
                            data_set_id: str,
                            limit: int = 100,
                            start: 'datetime' = None,
                            end: 'datetime' = None,
                            offset: int = None,
                            annotations: List[str] = None,
                            filter: str = None,
                            include_total_count: bool = None,
                            format: str = None,
                            output_type: str = None,
                            include_internal_columns = False,return_payload_raw_data = False) -> Union['DetailedResponse', 'DataFrame']:
        """
        List data set records.

        :param str data_set_id: ID of the data set.
        :param int limit: By default it will return 100 records. If the
               value is greater than 1000 than it will be truncated.
        :param datetime start: (optional) return records with timestamp greater
               than or equal to `start` parameter. Date string should be in the UTC ISO 8601 format. Ex: 2021-06-10T09:43:53.309Z
        :param datetime end: (optional) return records with timestamp lower than
               `end` parameter. Date string should be in the UTC ISO 8601 format. Ex: 2021-06-10T09:43:53.309Z
        :param int offset: (optional) offset of returned records.
        :param list[str] annotations: (optional) return record annotations with
               given names.
        :param str filter: (optional) return records for which transaction ids in
               associated data set the condition is met, format:
               {data_set_id}.{field_name}:{op}:{value}.
        :param bool include_total_count: (optional) If total_count should be
               included. It can have performance impact if total_count is calculated.
        :param str filter: (optional) return records for which transaction ids in
               associated data set the condition is met, format:
               {data_set_id}.{field_name}:{op}:{value}.
        :param str format: (optional) What JSON format to use on output.
        :param str output_type: (optional) type of the response data to be present, default is 'dict',
                available option is 'pandas'
        :param bool include_internal_columns: (optional) Flag to retrieve internal columns
        :param bool return_payload_raw_data: (optional) Flag to retrieve only the raw data which was used for scoring. 
                                  Applicable to only Payload Logging data and format is 'pandas'    
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataRecordsResponseCollection` result

        A way you might use me is:

        >>> records = client.data_sets.get_list_of_records(data_set_id='997b1474-00d2-4g05-ac02-287ebfc603b5')
        >>> records = client.data_sets.get_list_of_records(data_set_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                                                           format=RecordsFormatTypes.DICT
           )
        >>> records = client.data_sets.get_list_of_records(data_set_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                                                           format=RecordsFormatTypes.LIST
           )
        >>> records = client.data_sets.get_list_of_records(data_set_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                                                           output_type=ResponseTypes.PYTHON
           )
        >>> records = client.data_sets.get_list_of_records(data_set_id='997b1474-00d2-4g05-ac02-287ebfc603b5',
                                                           output_type=ResponseTypes.PANDAS
           )
        """
        records_client = Records(watson_open_scale=self._ai_client)
        
        response = records_client.list(data_set_id=data_set_id, start=start, end=end,
                                               limit=limit, offset=offset, annotations=annotations, filter=filter,
                                               include_total_count=include_total_count, format=format)
        
        if output_type is not None and ResponseTypes.PANDAS == output_type:
            from pandas import DataFrame
            # note: issue: planning-sdk-squad #1367
            # fields = list(response.result.records[0].entity.values.keys())
            # values = [list(record.entity.values.values()) for record in response.result.records]
            if len(response.result['records']) > 0:
                if format == RecordsFormatTypes.DICT or format is None:
                    fields = list(response.result['records'][0]['entity']['values'].keys())
                    if include_internal_columns:
                        values = [[value for value, field in zip(list(record['entity']['values'].values()), fields) ] for record in response.result['records']]
                    else:    
                        values = [[value for value, field in zip(list(record['entity']['values'].values()), fields) if
                               not field.startswith('_')] for record in response.result['records']]

                else:
                    fields = list(response.result['records'][0]['fields'])
                    if include_internal_columns:
                        values = [
                            [value for value, field in zip(list(record['values']), fields) ] for record in response.result['records']]
                    else:    
                        values = [
                            [value for value, field in zip(list(record['values']), fields) if not field.startswith('_')] for
                            record in response.result['records']]
                        
                if include_internal_columns:
                    fields = [field for field in fields]
                else:             
                    fields = [field for field in fields if not field.startswith('_')]

            else:
                fields = []
                values = []
            
            df = DataFrame.from_records(values, columns=fields)    
            if return_payload_raw_data and len(fields)>0:   
                all_fields = self.get(data_set_id=data_set_id).result.entity.data_schema.fields
                input_features = []
                for field in all_fields:
                    if ('modeling_role' in field['metadata']) and (field['metadata']['modeling_role']=='feature'):
                        input_features.append(field['name'])    
                df = df[input_features]
                
            response.result = df

        return response

    def show_records(self,
                     data_set_id: str = None,
                     limit: int = 10) -> None:
        """
        Show data set records. By default 10 records will be shown.

        :param str data_set_id: ID of the data set.
        :param limit: Maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int
        :return: None

        A way you might use me is:

        >>> client.data_sets.show_records(data_set_id='997b1474-00d2-4g05-ac02-287ebfc603b5')
        """

        records: 'DataFrame' = self.get_list_of_records(
            data_set_id=data_set_id,
            limit=limit,
            output_type='pandas').result

        rows = records.values.tolist()
        col_names = records.columns.tolist()

        Table(col_names, rows).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="Data Set {} Records".format(
                data_set_id
            )
        )

    def print_records_schema(self, data_set_id: str = None) -> None:
        """
        Show data set records. By default 10 records will be shown.

        :param str data_set_id: ID of the data set.
        :return: None

        A way you might use me is:

        >>> client.data_sets.print_records_schema(data_set_id='997b1474-00d2-4g05-ac02-287ebfc603b5')
        """

        schema = self.get(data_set_id=data_set_id).result.entity.data_schema

        schema = schema.to_dict()
        schema_records = [[field['name'],
                           field['type'],
                           field['nullable']
                           ] for field in schema['fields']]

        Table(['name', 'type', 'nullable'], schema_records).list(
            title='Schema of {} data set'.format(data_set_id))

    def get_records_count(self,
                          data_set_id: str = None) -> int:
        """
        Count data set records.

        :param data_set_id: ID of the data set.
        :return: int

        A way you might use me is:

        >>> number_of_records = client.data_sets.get_records_count(data_set_id='997b1474-00d2-4g05-ac02-287ebfc603b5')
        """
        response = self.get_list_of_records(data_set_id=data_set_id, include_total_count=True, limit=0)
        # note: issue: planning-sdk-squad #1367
        #return response.result.total_count
        return response.result.get('total_count')
