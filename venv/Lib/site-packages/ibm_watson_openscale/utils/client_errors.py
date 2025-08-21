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

import logging
import sys


class ClientError(Exception):
    def __init__(self, error_msg, reason=None):
        self.error_msg = error_msg
        self.reason = reason
        # logging.getLogger(__name__).warning(self.__str__())
        logging.getLogger(__name__).debug(
            str(self.error_msg) + ('\nReason: ' + str(self.reason) if sys.exc_info()[0] is not None else ''))

    def __str__(self):
        return str(self.error_msg) + ('\nReason: ' + str(self.reason) if self.reason is not None else '')


class MissingValue(ClientError, ValueError):
    def __init__(self, value_name, reason=None):
        ClientError.__init__(self, 'No \"' + value_name + '\" provided.', reason)


class MissingDeployment(ClientError, ValueError):
    def __init__(self, value_name, reason=None):
        ClientError.__init__(self, f"There are 0 deployments for data_mart: \"{value_name[0]}\" and service_provider: \"{value_name[1]}\"", reason)


class MissingPayload(ClientError, ValueError):
    def __init__(self, value_name, reason=None):
        ClientError.__init__(self,
                             'There is no any payload logged in the payload table. Firstly, please log a payload, then enable {}'.format(
                                 value_name), reason)


class MissingDataSet(ClientError, ValueError):
    def __init__(self, value_name, reason=None):
        ClientError.__init__(self, '{} data set does not exist. Make sure that you correctly added '
                                   'subscription/quality monitor. Try to run data_sets.store_data_set_id() '
                                   'once more'.format(value_name), reason)


class StateNotActive(ClientError, ValueError):
    def __init__(self, value_name, reason=None):
        ClientError.__init__(self,
                             '{} state is not active. Please make sure you have enabled/created {} firstly'.format(
                                 value_name, value_name), reason)


class IncorrectValue(ClientError, ValueError):
    def __init__(self, value_name, reason=None):
        ClientError.__init__(self, 'Incorrect \"' + value_name + '\" provided.', reason)


class IncorrectParameter(ClientError, ValueError):
    def __init__(self, parameter_name, reason=None):
        ClientError.__init__(self, 'Unsupported parameter \"' + parameter_name + '\" provided.', reason)


class MissingMetaProp(MissingValue):
    def __init__(self, name, reason=None):
        ClientError.__init__(self, 'Missing meta_prop with name: \'{}\'.'.format(name), reason)


class NotUrlNorUID(ClientError, ValueError):
    def __init__(self, value_name, value, reason=None):
        ClientError.__init__(self, 'Invalid value of \'{}\' - it is not url nor uid: \'{}\''.format(value_name, value),
                             reason)


class InvalidCredentialsProvided(MissingValue):
    def __init__(self, reason=None):
        MissingValue.__init__(self, 'WML credentials', reason)


class ApiRequestFailure(ClientError):
    def __init__(self, error_msg, response, reason=None):
        self.response = response
        ClientError.__init__(self, '{} ({} {})\nStatus code: {}, body: {}'.format(
            error_msg, response.request.method,
            response.request.url,
            response.status_code,
            response.text if response.apparent_encoding is not None else '[binary content, ' + str(
                len(
                    response.content)) + ' bytes]'),
                             reason)


class UnexpectedType(ClientError, ValueError):
    def __init__(self, el_name, expected_type, actual_type):
        ClientError.__init__(self, 'Unexpected type of \'{}\', expected: {}, actual: \'{}\'.'.format(
            el_name,
            '\'{}\''.format(
                expected_type) if type(
                expected_type) == type else expected_type,
            actual_type))

class AuthorizationError(ClientError, ValueError): 
    def __init__(self, msg, reason=None): 
        ClientError.__init__(self, msg,reason)      
        