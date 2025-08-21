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

from typing import Tuple

from ibm_cloud_sdk_core import BaseService

from ibm_watson_openscale.base_classes.tables import Table
from .utils import *
from ibm_watson_openscale.base_classes.watson_open_scale_v2 import DataMarts as BaseDataMarts

if TYPE_CHECKING:
    from .client import WatsonOpenScaleV2Adapter

_DEFAULT_LIST_LENGTH = 50


# TODO: Add parameters validation in every method
class DataMarts(BaseDataMarts):
    """
    Manages Database instance.
    """

    def __init__(self, ai_client: 'WatsonOpenScaleV2Adapter') -> None:
        validate_type(ai_client, 'ai_client', BaseService, True)
        self._ai_client = ai_client
        super().__init__(watson_open_scale=self._ai_client)

    def show(self, limit: Optional[int] = 10) -> None:
        """
        Show Data marts. By default 10 records will be shown.

        :param limit: Maximal number of fetched rows. By default set to 10. (optional)
        :type limit: int

        A way you might use me is:

        >>> client.data_marts.show()
        >>> client.data_marts.show(limit=20)
        >>> client.data_marts.show(limit=None)
        """
        validate_type(limit, u'limit', int, False)

        response = self.list()

        records = [[data_mart.entity.name,
                    data_mart.entity.description,
                    data_mart.entity.internal_database,
                    data_mart.entity.status.state,
                    data_mart.metadata.created_at,
                    data_mart.metadata.id
                    ] for data_mart in response.result.data_marts]
        columns = ['name', 'description', 'internal_database', 'status', 'created_at', 'id']

        Table(columns, records).list(
            limit=limit,
            default_limit=_DEFAULT_LIST_LENGTH,
            title="Data Marts"
        )

    def add(self,
            name: str = None,
            description: str = None,
            service_instance_crn: str = None,
            internal_database: bool = None,
            database_configuration: 'DatabaseConfigurationRequest' = None,
            force: bool = None,
            background_mode: bool = True) -> 'DetailedResponse':
        """
        Add the data mart.
        Configure database connection for the data mart.

        :param str name: (optional) Name of the data mart.
        :param str description: (optional) Description of the data mart.
        :param str service_instance_crn: (optional) Can be omitted if user token is
               used for authorization.
        :param bool internal_database: (optional) If `true` the internal database
               managed by AI OpenScale is provided for the user.
        :param DatabaseConfigurationRequest database_configuration: (optional)
               Database configuration ignored if internal database is requested
               (`internal_database` is `true`).
        :param bool force: (optional) force update of metadata and db credentials
               (assumption is that the new database is already prepared and populated).
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse with `DataMartDatabaseResponse` result

        A way you might use me is:

        >>> from ibm_watson_openscale import *
        >>> client.data_marts.add(
                background_mode=False,
                name="My Data Mart",
                description="Description of the data mart...",
                database_configuration=DatabaseConfigurationRequest(
                    database_type='postgresql',
                    instance_id='crn:v1:bluemix:public:databases-for-postgresql:us-south:a/***',
                    credentials=PrimaryStorageCredentialsLong(
                        hostname='some hostname',
                        username='some username',
                        password='some password',
                        db='database name',
                        port=50000,
                        ssl=True,
                        sslmode='verify-full',
                        certificate_base64='***'
                    ),
                    location=LocationSchemaName(
                        schema_name='name of the database schema'
                    )
                )
             )
        """
        response = super().add(name=name, description=description, service_instance_crn=service_instance_crn,
                               internal_database=internal_database, database_configuration=database_configuration,
                               force=force)
        data_mart_id = response.result.metadata.id

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.get(data_mart_id=data_mart_id)
                return details.result.entity.status.state

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.get(data_mart_id=data_mart_id)
                state = details.result.entity.status.state

                if state in [StatusStateType.ACTIVE]:
                    return "Successfully finished adding data mart", None, details
                else:
                    return "Add data mart failed with status: {}".format(state), \
                           'Reason: {}'.format(["code: {}, message: {}".format(error.code, error.message) for error in
                                                details.result.entity.status.failure.errors]), details

            return print_synchronous_run(
                'Waiting for end of adding data mart {}'.format(data_mart_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.ACTIVE]
            )

    def delete(self,
               data_mart_id: str,
               force: bool = None,
               background_mode: bool = True) -> 'DetailedResponse':
        """
        Delete the data mart.

        :param str data_mart_id: ID of the data mart.
        :param bool force: (optional) force hard delete.
        :param background_mode: if set to True, run will be in asynchronous mode, if set to False
                it will wait for result (optional)
        :type background_mode: bool
        :return: A `DetailedResponse` containing the result, headers and HTTP status code.
        :rtype: DetailedResponse

        A way you might use me is:

        >>> client.data_marts.delete(
                background_mode=False,
                data_mart_id='id of the datamart',
                force=True
             )
        """
        response = super().delete(data_mart_id=data_mart_id, force=force)

        if background_mode:
            return response
        else:
            def check_state() -> dict:
                details = self.list()
                if data_mart_id not in str(details.result):
                    return StatusStateType.FINISHED
                else:
                    return StatusStateType.ACTIVE

            def get_result() -> Union[Tuple[str, Union[None, str], 'DetailedResponse']]:
                details = self.list()
                if data_mart_id not in str(details.result):
                    state = StatusStateType.FINISHED
                else:
                    state = StatusStateType.ACTIVE

                if state in [StatusStateType.FINISHED]:
                    return "Successfully finished deleting data mart", None, response
                else:
                    return "Delete data mart failed", 'Reason: None', response  # TODO: Need to show the reason.

            return print_synchronous_run(
                'Waiting for end of deleting data mart {}'.format(data_mart_id),
                check_state,
                get_result=get_result,
                success_states=[StatusStateType.FINISHED]
            )
