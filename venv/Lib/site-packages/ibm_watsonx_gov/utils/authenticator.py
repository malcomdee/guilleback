# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import json

from ibm_watsonx_gov.utils.gov_sdk_logger import GovSDKLogger
from ibm_watsonx_gov.utils.rest_util import RestUtil


class Authenticator:
    """
    Helper class to authenticate with IBM Cloud and CPD
    """

    def __init__(self, credentials: dict, use_cpd: bool, use_ssl: bool) -> None:
        """
        Initialize the authenticator object

        Args:
            credentials (dict): A dictionary containing the necessary credentials for authentication.
            use_cpd (bool): A boolean indicating whether to authenticate with CPD or IBM Cloud.
        """
        self.__credentials: dict[str, str] = credentials
        self.__use_cpd: bool = use_cpd
        self.__iam_token: str = None
        self.__use_ssl: bool = use_ssl
        self.logger = GovSDKLogger.get_logger(__name__)

    def authenticate(self) -> str:
        """
        Function to complete the authentication flow with either IBM Cloud or CPD based
        on the configuration. This will set self.__iam_token and return the token to the user
        """
        self.logger.info("Authenticating the client")
        if self.__use_cpd:
            self.logger.info("Authenticating the client with CPD")
            self.__iam_token = self.__get_iam_token_cpd()
        else:
            self.logger.info("Authenticating the client with ibm cloud")
            self.__iam_token = self.__get_iam_token_cloud()

        self.logger.info("Client authenticated successfully")
        return self.__iam_token

    def get_iam_token(self) -> str:
        """
        This function retrieves an IAM token from the instance variables. If the token does not exist, it raises an exception.

        Returns:
            str: IAM token
        """
        if not self.__iam_token:
            message = "Not authenticated yet."
            self.logger.error(message)
            raise Exception(message)
        return self.__iam_token

    def __get_iam_token_cloud(self) -> None:
        """
        Method to authenticate the client with ibm cloud.
        """
        self.logger.info("Authenticating using cloud credentials")

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

        data = {
            "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
            "response_type": "cloud_iam",
            "apikey": self.__credentials["apikey"],
        }

        try:
            response = RestUtil.request_with_retry().post(
                url=f"{self.__credentials['iam_url']}/identity/token",
                data=data,
                headers=headers,
                allow_redirects=True,
                verify=self.__use_ssl,
            )
            response.raise_for_status()
        except Exception as e:
            message = f"Failed to authenticate. {e}"
            self.logger.error(message)
            raise Exception(message)

        try:
            json_response = response.json()
            return json_response["access_token"]
        except Exception as e:
            message = f"Failed to parse authentication response. {e}"
            self.logger.error(message)
            raise Exception(message)

    def __get_iam_token_cpd(self) -> None:
        """
        Method to authenticate the client with CPD.
        """
        self.logger.info("Authenticating using cpd credentials")

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        data = {
            "username": self.__credentials["username"],
        }

        # Check if the authentication is done using password or api key and it to the payload
        if "password" in self.__credentials.keys():
            data["password"] = self.__credentials["password"]
        elif "api_key" in self.__credentials.keys():
            data["api_key"] = self.__credentials["api_key"]

        try:
            response = RestUtil.request_with_retry().post(
                url=f"{self.__credentials['url']}/icp4d-api/v1/authorize",
                data=json.dumps(data).encode("utf-8"),
                headers=headers,
                allow_redirects=True,
                verify=self.__use_ssl,
            )
            response.raise_for_status()
        except Exception as e:
            message = f"Failed to authenticate. {e}"
            self.logger.error(message)
            raise Exception(message)

        try:
            json_response = response.json()
            return json_response["token"]
        except Exception as e:
            message = f"Failed to parse authentication response. {e}"
            self.logger.error(message)
            raise Exception(message)
