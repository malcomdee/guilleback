
# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import json

import jwt
import requests
from ibm_cloud_sdk_core.authenticators import (CloudPakForDataAuthenticator,
                                               IAMAuthenticator)
from jwt.exceptions import DecodeError
from requests.exceptions import HTTPError

from ibm_watsonx_gov.utils.authenticator import Authenticator


class WXAIClient():
    """
    Client class to validate user entitlements
    """

    def __init__(self, service_url: str, authenticator: CloudPakForDataAuthenticator | IAMAuthenticator, disable_ssl_verification: bool, is_cpd: bool):
        self.service_url = service_url
        self.authenticator = authenticator
        self.disable_ssl_verification = disable_ssl_verification
        self.is_cpd = is_cpd

    def validate_user(self):
        entitlements_url = f"{self.service_url}/v2/entitlements"
        # create a token using the authenticator
        if self.is_cpd:
            creds = {
                "url": self.service_url,
                "username": self.authenticator.token_manager.username
            }
            if self.authenticator.token_manager.password:
                creds.update(
                    {"password": self.authenticator.token_manager.password})
            if self.authenticator.token_manager.apikey:
                creds.update(
                    {"api_key": self.authenticator.token_manager.apikey})

            auth = Authenticator(
                credentials=creds,
                use_cpd=self.is_cpd,
                use_ssl=(not self.disable_ssl_verification),
            )
            bearer_token = auth.authenticate()
        else:
            bearer_token = self.authenticator.token_manager.get_token()

        if not self.is_cpd:
            # decode the token and get bss
            try:
                decoded_token = jwt.decode(bearer_token, options={
                                           "verify_signature": False})
                bss_account_id = decoded_token["account"]["bss"]
            except jwt.InvalidTokenError as e:
                raise DecodeError(
                    f"Failed while decoding the token. Token is invalid: {e}")

            entitlements_url = f"{entitlements_url}?bss_account_id={bss_account_id}"

        # call entitlements api and check for data_science_experience
        response = requests.get(entitlements_url, headers={
                                "Authorization": f"Bearer {bearer_token}"}, verify=not self.disable_ssl_verification)
        if response.status_code == 200:
            response_json = json.loads(response.text)
            dsx = response_json.get("entitlements", {}).get(
                "data_science_experience")
            if not dsx:
                raise ValueError("User is not authorized.")
            else:
                return True
        else:
            raise HTTPError(
                f"Request failed with status code: {response.status_code}")
