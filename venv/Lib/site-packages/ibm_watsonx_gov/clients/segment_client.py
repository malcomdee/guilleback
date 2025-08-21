# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import requests

from ibm_watsonx_gov.utils.gov_sdk_logger import GovSDKLogger

logger = GovSDKLogger.get_logger(__name__)


class SegmentClient():

    def __init__(self, api_client):
        self.api_client = api_client

    def trigger_segment_endpoint(self, segment_data):

        try:
            segment_publish_url = "{0}/v2/segment/events".format(
                self.api_client.service_url)
            token = self.api_client.authenticator.token_manager.get_token()
            iam_headers = {
                "Content-Type": "application/json",
                "accept": "application/json",
                "Authorization": f"Bearer {token}"
            }
            response = requests.post(
                url=segment_publish_url,
                headers=iam_headers,
                json=segment_data
            )
            if not response.ok:
                errors = response.json().get("errors")
                logger.debug(
                    f"Failed to send segment events. Details: {errors}")
        except Exception as ex:
            logger.debug(f"Failed to send segment events. Details: {ex}")
