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

import base64
import io
# Supress info and warning logs from the libraries
import logging
import os
import random
import ssl
import sys
import tempfile
import uuid

import ibm_boto3
import ibm_botocore
import ibm_db
import ibm_db_dbi
import pandas as pd
import pandas.io.sql as psql
from ibm_botocore.client import Config
from ibm_botocore.exceptions import CredentialRetrievalError
from retrying import retry

from ibm_watson_openscale.utils.client_errors import MissingValue, ClientError


logging.getLogger("ibm_boto3").setLevel(logging.CRITICAL)
logging.getLogger("ibm_botocore").setLevel(logging.CRITICAL)

CONNECTION_TIMEOUT = 180 # Timeout in seconds for Db2 connections


class DataReader(object):
    
    @staticmethod
    def get_input_data(connection_details, categorical_columns=None, max_row_or_data_size=None, random_sample=False, is_icp=False):
        source = connection_details.get("type")
        supported_sources = ["bluemixcloudobjectstorage", "cos", "db2", "dashdb"]
        if source is None or source not in supported_sources:
            raise MissingValue(u"type", "Supplied training data reference connection details doesn't have type value")
        if source == 'bluemixcloudobjectstorage' or source == "cos":
            return CosDataReader(connection_details).get_input_data(categorical_columns, max_row_or_data_size, random_sample)
        elif source == 'db2' or source=='dashdb':
            return Db2DataReader(connection_details, is_icp).get_input_data(max_row_or_data_size, random_sample)


class CosDataReader(DataReader):
    def __init__(self, connection_details):
        self.validate_connection_details(connection_details)
        
    def validate_connection_details(self, connection_details):
        connection = connection_details.get('connection')
        if connection is None or connection == '':
            raise MissingValue(u"connection", "Supplied COS credentials doesn't have connection value")
        self.api_key = connection.get('api_key')
        if self.api_key is None or self.api_key == '':
            raise MissingValue(u"api_key", "Supplied COS credentials doesn't have api_key value")
        self.resource_instance_id = connection.get('resource_instance_id')
        if self.resource_instance_id is None or self.resource_instance_id == '':
            raise MissingValue(u"resource_instance_id", "Supplied COS credentials doesn't have resource_instance_id value")
        self.auth_endpoint = connection.get('auth_endpoint')
        if self.auth_endpoint is None:
            self.auth_endpoint = connection.get('iam_url')
            if self.auth_endpoint is None:
                raise MissingValue(u"iam_url", "Supplied COS credentials doesn't have iam_url value")
        self.service_endpoint = connection.get('service_endpoint')
        if self.service_endpoint is None:
            self.service_endpoint = connection.get('url')
            if self.service_endpoint is None:
                raise MissingValue(u"service_endpoint", "Supplied COS credentials doesn't have service_endpoint value")
        location = connection_details.get('location')
        if location is None or location == '':
            raise MissingValue(u"location", "Supplied COS credentials doesn't have location value")
        self.file_name = location.get('file_name')
        if self.file_name is None or self.file_name == '':
            raise MissingValue(u"file_name", "Supplied COS credentials doesn't have file_name value")
        self.bucket = location.get('bucket')
        if self.bucket is None or self.bucket == '':
            raise MissingValue(u"bucket", "Supplied COS credentials doesn't have bucket value")
    
    def get_input_data(self, categorical_columns=None, max_row_or_data_size=None, random_sample=False):

        input_data_df = None
        logging.debug("Started reading input data from Bluemix COS")
        try:
            cos = ibm_boto3.resource("s3",
                                    ibm_api_key_id=self.api_key,
                                    ibm_service_instance_id=self.resource_instance_id,
                                    ibm_auth_endpoint=self.auth_endpoint,
                                    config=Config(signature_version="oauth"),
                                    endpoint_url=self.service_endpoint)

                # 500 mb in bytes
            size_to_read = 1024 * 1024 * 500
            obj = cos.Object(self.bucket, self.file_name).get()
            content_length = obj["ContentLength"]
            input_data_df = None
            dtype_dict = {}
            if categorical_columns is not None:
                for col_name in categorical_columns:
                    dtype_dict[col_name] = "object"
            if max_row_or_data_size is not None:
                first_idx = 0
                chunk_size = max_row_or_data_size
                if random_sample == True:
                    chunk_size = max_row_or_data_size * 5
                    logging.debug('Reading data in chunk size of ' + str(chunk_size))
                for df in pd.read_csv(io.BytesIO(obj["Body"].read()), sep=None, encoding="utf-8", engine="python",iterator=True, chunksize=chunk_size, dtype=dtype_dict):
                    if first_idx == 0:
                        input_data_df = df.copy()
                        first_idx = -1
                    else:
                        input_data_df = pd.concat([df, input_data_df],ignore_index=True)

                input_data_df = input_data_df.reset_index(drop=True)

                if random_sample == True:
                    logging.debug('Reading random rows ' + str(max_row_or_data_size))
                    dataframe_size = len(input_data_df)
                    if dataframe_size > max_row_or_data_size:
                        input_data_df = input_data_df.sample(n=max_row_or_data_size, random_state=random.randint(1, 10),replace = True)
                else:
                    if len(input_data_df) > max_row_or_data_size:
                        input_data_df = input_data_df[:max_row_or_data_size]
            else:
                if size_to_read > content_length:
                    # If sep is None, python engine can detect the separator internally which c based engine cannot do
                    # So setting sep to None and using python engine will add support for tab separated files as well.
                    input_data_df = pd.read_csv(io.BytesIO(obj["Body"].read()), sep=None, encoding="utf-8", engine="python", dtype=dtype_dict)
                else:
                    input_data_df = pd.read_csv(io.BytesIO(obj['Body'].read(size_to_read)), sep=None, encoding="utf-8", engine="python", dtype=dtype_dict)
                    input_data_df.drop(input_data_df.tail(1).index,inplace=True)

            logging.debug('Completed reading input data from Bluemix COS using CosDataReader.')

        except UnicodeDecodeError as error:
            error_message = "Bluemix COS file provided as input data reference is not UTF-8 encoded."
            logging.error(error_message)
            raise ClientError(error_message)
        except ibm_botocore.exceptions.ClientError as ce:
            error_message = "There was a problem retrieving the file {} in bucket {} from COS. Reason: {}".format(
                self.file_name, self.bucket, ce.response)
            logging.error(error_message)
            raise ClientError(error_message)
        except ibm_botocore.exceptions.CredentialRetrievalError as cre:
            error_details = cre.args
            raise ClientError(error_details)
        except Exception as e:
            logging.error(str(e))
            raise ClientError(str(e))
        return input_data_df


class Db2DataReader(DataReader):

    db2_error_tuple = (
        '08' # Class Code 08: Connection Exception
    )

    def __init__(self, connection_details, is_icp=False):
        
        self.is_icp_env = is_icp
        self.validate_connection_details(connection_details)
        
        self.cert_file = None
        self.get_connection()
        self.row_id_column = "row_id_{}".format(uuid.uuid4())
        self.use_row_id = self.__use_db2_row_id()

    def __use_db2_row_id(self):
        try:
            psql.read_sql('SELECT rowid as \"{ROW_ID}\", * FROM "{SCHEMA_NAME}"."{TABLE_NAME}" ORDER BY \"{ROW_ID}\" LIMIT 1'.format(
                ROW_ID=self.row_id_column, SCHEMA_NAME=str(self.schema_name).upper(), TABLE_NAME=self.table_name), self.connection)
        except Exception as ex:
            ex_str = str(ex)
            logging.error(ex_str)
            if all(x in ex_str for x in ["SQLSTATE=42703", "SQLCODE=-206", "\"ROWID\" is not valid in the context where it is used."]):
                return False
            else:
                raise ClientError(ex_str)
        return True

    def get_connection(self):
        logging.debug("Started getting DB connection.")
        try:
            dsn="DATABASE="+self.db_name+";HOSTNAME="+self.hostname+";PORT="+str(self.port)+";PROTOCOL=TCPIP;UID="+str(self.username).lower()+";PWD="+self.password+";CONNECTTIMEOUT=" + str(CONNECTION_TIMEOUT)+ ";"
            # if in icp, and when ssl is on, then set the certificate as well.
            if self.is_icp_env:
                if self.ssl:
                    self.create_certificate_file()
                    dsn = dsn + "SECURITY=ssl;SSLServerCertificate=" + self.cert_file + ";"
            else:
                dsn = dsn + "SECURITY=ssl;"
            # Create the connection
            self.connection = self.get_connection_with_retry(dsn)
        except Exception as e:
            self.delete_certificate_file()
            logging.exception(str(e), exc_info=True)
            raise ClientError(str(e))
            
        logging.debug("Finished getting DB connection")
    
    @retry(stop_max_attempt_number=3, wait_exponential_multiplier=1000)
    def get_connection_with_retry(self, dsn: str):
        """Retry scoring with wait of 2^x * 1000 milliseconds between each retry"""
        ibm_db_conn = ibm_db.connect(dsn, "", "")
        return ibm_db_dbi.Connection(ibm_db_conn)

    def create_certificate_file(self):
        if self.certificate_base64:
            # if certificate already set in the connection_details
            if 'BEGIN CERTIFICATE' not in self.certificate_base64:
                # If 'BEGIN CERTIFICATE' is not present, assuming that it will be a base64 encoded.
                certificate = base64.b64decode(self.certificate_base64.strip()).decode()
            else:
                certificate = self.certificate_base64.strip()
        else:
            # else get it from the host
            certificate = ssl.get_server_certificate((str(self.hostname), int(self.port)))
        with tempfile.NamedTemporaryFile(mode="w", prefix="db2ssl_", suffix="_cert.arm", delete=False) as f:
            self.cert_file = f.name
            f.write(certificate)

    def delete_certificate_file(self):
        if self.cert_file is not None:
            if (os.path.isfile(self.cert_file)):
                try:
                    os.remove(self.cert_file)
                except:
                    logging.warning("Failed to delete cert file " + self.cert_file + ".")

    def close_connection(self):
        try:
            if self.connection:
                self.connection.close()
        except Exception:
            logging.warning("Failed attempting to close DB2 connection.")

    def validate_connection_details(self, connection_details):
        connection = connection_details.get("connection")
        if connection is None or connection == '':
            raise MissingValue(u"connection", "Supplied DB credentials doesn't have connection value")
        self.db_name = connection.get("database_name")
        if self.db_name is None or self.db_name == '':
            raise MissingValue(u"database_name", "Supplied DB credentials doesn't have database_name value")
        self.hostname = connection.get("hostname")
        if self.hostname is None or self.hostname == '':
            self.hostname = connection.get("host")
            if self.hostname is None or self.hostname == '':
                raise MissingValue(u"hostname", "Supplied DB credentials doesn't have hostname value")
        self.username = connection.get("username")
        if self.username is None or self.username == '':
            raise MissingValue(u"username", "Supplied DB credentials doesn't have username value")
        self.password = connection.get("password")
        if self.password is None or self.password == '':
            raise MissingValue(u"password", "Supplied DB credentials doesn't have password value")
        self.port = connection.get("port")
        if self.port is None or self.port == "":
            if self.is_icp_env:
                # Default non SSL port for DB2 on ICP
                self.port = "50000"
            else:
                # Use the default SSL port for DB2 on Cloud
                self.port = "50001"
        self.ssl = connection.get("ssl")
        if self.ssl is None:
            self.ssl = False
        self.certificate_base64 = connection.get("certificate_base64")
            
        location = connection_details.get("location")
        if location is None or location == '':
            raise MissingValue(u"location", "Supplied DB credentials doesn't have location value")
        self.schema_name = location.get("schema_name")
        if self.schema_name is None or self.schema_name == '':
            raise MissingValue(u"schema_name", "Supplied DB credentials doesn't have schema_name value")
        self.table_name = location.get("table_name")
        if self.table_name is None or self.table_name == '':
            raise MissingValue(u"table_name", "Supplied DB credentials doesn't have table_name value")
        

    def get_query_to_execute(self, limit: str, offset: str, random_sample = False):
        # Query with OFFSET, LIMIT is constructed
        if self.use_row_id:
            sql_statement =  'SELECT rowid as \"{ROW_ID}\", * FROM {SCHEMA_NAME}.\"{TABLE_NAME}\" ORDER BY \"{ROW_ID}\" LIMIT {LIMIT} OFFSET {OFFSET}'.format(ROW_ID=self.row_id_column, SCHEMA_NAME=str(self.schema_name).upper(), TABLE_NAME=self.table_name, LIMIT=limit, OFFSET=offset)
        else:
            sql_statement =  'SELECT row_number() over() as \"{ROW_ID}\", * FROM "{SCHEMA_NAME}"."{TABLE_NAME}" ORDER BY \"{ROW_ID}\" LIMIT {LIMIT} OFFSET {OFFSET}'.format(ROW_ID=self.row_id_column, SCHEMA_NAME=str(self.schema_name).upper(), TABLE_NAME=self.table_name, LIMIT=limit, OFFSET=offset)
        if random_sample==True:
            sql_statement = 'SELECT * FROM {SCHEMA_NAME}.\"{TABLE_NAME}\" order by rand() fetch first {LIMIT} rows only'.format(SCHEMA_NAME=str(self.schema_name).upper(), TABLE_NAME=self.table_name, LIMIT=limit)

        return sql_statement

    def get_input_data(self, max_row_or_data_size = None, random_sample = False):
        """
        Fetches the input data from the DB2 source and returns it as a pandas DataFrame
        """

        logging.debug("Started reading input data from Db2")

        offset = 0
        limit = 10000
        if max_row_or_data_size is not None:
            limit = max_row_or_data_size
        dfs = []
        total_rows_read = 0
        try:
            while True:
                chunk_df = psql.read_sql(self.get_query_to_execute(
                    limit, str(offset), random_sample), self.connection)

                # Assert if the size of the rows object is less than 500 mb when the rows from current result is appended
                obj_size_in_mb = (sys.getsizeof(
                    dfs) + sys.getsizeof(chunk_df)) / (1024**2)
                if float("%.2f" % obj_size_in_mb) > 500.00:
                    logging.debug(
                        "Rows fetched object size becomes > 500 mb in this iteration; terminating")
                    break

                total_rows_read = total_rows_read + len(chunk_df)
                if max_row_or_data_size is not None:
                    if total_rows_read >= max_row_or_data_size:
                        dfs.append(chunk_df)
                        break

                dfs.append(chunk_df)

                # if the rows_count is less than the limit it means we have read all the rows
                rows_count = chunk_df.shape[0]
                if rows_count < limit:
                    break

                offset += rows_count

        except Exception as ex:
            logging.error('Exception occurred while getting input data, with error {}'.format(str(ex)))
            raise ex
        finally:
            self.close_connection()
            self.delete_certificate_file()
        df = pd.concat(dfs)

        if max_row_or_data_size is not None and len(df) > max_row_or_data_size:
            #Keep only max_row_or_data_size rows in dataframe
            df = df[:max_row_or_data_size]

        logging.debug('Completed reading input data from DB2 using Db2DataReader: ')
        #Drop the row id column if it's a regular query
        if random_sample is False:
            df.drop(columns=[self.row_id_column], inplace=True)

        return df
