# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

# Convert string to bytes and encode
import base64
import os
import json

from ibm_watsonx_gov.utils.python_utils import get


# Source code encoder
def get_base64_encoding(tool_code: str):
    return base64.b64encode(tool_code.encode()).decode()


# Decode the base64 string
def get_base64_decoding(encoded_code: str):
    return base64.b64decode(encoded_code).decode()


# Validate envs:
def validate_envs(tool_name: str, env_list: list = []):
    if len(env_list) == 0:
        return env_list

    import os
    missing_envs = []
    for env in env_list:
        value = os.getenv(env)
        if value is None:
            missing_envs.append(env)

    if len(missing_envs) > 0:
        raise Exception(
            f"Please set environment values :{missing_envs} for using the tool:{tool_name}")


# Extracting bss_account id from user_token
def get_bss_account_id(token: str):
    payload_b64 = token.split('.')[1]
    padding = '=' * (-len(payload_b64) % 4)
    payload_b64 = base64.urlsafe_b64decode(payload_b64 + padding)
    payload = json.loads(payload_b64)
    return get(payload, "bss", default="")


# Processing endpoint response
def process_result(result):
    try:
        if result.text:
            try:
                result = json.loads(result.text)
            except json.JSONDecodeError:
                raise Exception(result.text)

            if result.get("errors"):
                raise Exception(result.get("errors"))
            return result
        raise Exception(f"Empty response received. Status code: {result.status_code}")
    except Exception as e:
        raise Exception(str(e))
