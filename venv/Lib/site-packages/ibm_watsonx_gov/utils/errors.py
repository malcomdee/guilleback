
# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import sys
from http import HTTPStatus

from ibm_watsonx_gov.utils.gov_sdk_logger import GovSDKLogger

logger = GovSDKLogger.get_logger(__name__)


class ClientError(Exception):
    def __init__(self, code, message, reason=None):
        self.code = code
        self.message = message
        self.reason = reason
        logger.debug(str(self.code) + ": " +
                     str(self.message) + ('\nReason: ' + str(self.reason) if sys.exc_info()[0] is not None else ''))

    def __str__(self):
        return str(self.code) + ": " + str(self.message) + ('\nReason: ' + str(self.reason)
                                                            if sys.exc_info()[0] is not None else '')


class AuthorizationError(ClientError, ValueError):
    def __init__(self, code, message, reason=None):
        ClientError.__init__(self, code=code, message=message, reason=reason)


class UnsupportedOperationError(ClientError, ValueError):
    def __init__(self, message, reason=None):
        ClientError.__init__(
            self, code=HTTPStatus.NOT_IMPLEMENTED, message=message, reason=reason)
