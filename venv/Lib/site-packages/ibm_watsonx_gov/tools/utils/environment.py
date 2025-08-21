# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import os
import warnings

from ...entities.enums import Region
from ...utils.python_utils import get_environment_variable_value
from .platform_url_mapping import ALLOWED_PLATFORM_URL, PROD_PLATFORM_URL
from ...utils.url_mapping import WATSONX_REGION_URLS


def get_property_value(property_name, default=None):
    if os.environ.get(property_name):
        return os.environ.get(property_name)
    else:
        return default


def get_base_url():
    is_cpd = get_is_cpd()

    if is_cpd:
        watsonx_url = get_environment_variable_value(
            possible_env_variables=["WATSONX_URL", "PLATFORM_URL", "WXG_URL"])
        if not watsonx_url:
            raise Exception(
                "The WATSONX_URL cannot be empty for CPD environment")
    else:
        watsonx_region = get_property_value(property_name="WATSONX_REGION")
        platform_url = get_property_value(property_name="PLATFORM_URL")

        if watsonx_region:
            watsonx_region_map = WATSONX_REGION_URLS.get(watsonx_region)
            if not watsonx_region_map:
                raise Exception(
                    f"\nThe WATSONX_REGION '{watsonx_region}' is invalid or not supported.\n"
                    f"Supported WATSONX_REGION are: {', '.join(Region.values())}."
                )
            watsonx_url = watsonx_region_map.dai_url
        elif platform_url:
            if platform_url not in ALLOWED_PLATFORM_URL:
                raise Exception(
                    f"\nThe platform URL '{platform_url}' is invalid or not supported.\n"
                    f"Supported platform URLs are:\n{', '.join(PROD_PLATFORM_URL.keys())}."
                )
            watsonx_url = platform_url
        else:
            warnings.warn(
                "Since WATSONX_REGION is not provided in the environment variable, the Dallas region will be used as the default.",
                UserWarning)
            # Setting Dallas region as default if not provided.
            os.environ["PLATFORM_URL"] = "https://api.dataplatform.cloud.ibm.com"
            watsonx_url = get_property_value(property_name="PLATFORM_URL")

    return watsonx_url


def get_authenticator_url():
    base_url = get_base_url()
    if get_is_cpd():
        return base_url
    else:
        return ALLOWED_PLATFORM_URL.get(base_url)


def get_api_key():
    return get_property_value(property_name="WATSONX_APIKEY")


def get_cpd_password():
    return get_property_value(property_name="WATSONX_PASSWORD")


def get_cpd_username():
    return get_property_value(property_name="WATSONX_USERNAME")


def get_is_cpd():
    watsonx_version = get_property_value(property_name="WATSONX_VERSION")
    if watsonx_version:
        return True
    else:
        return False


def get_ssl_verification():
    verify = get_property_value(
        property_name="WATSONX_DISABLE_SSL", default=False)
    return str(verify).lower() in ("false", "0", "no")


def get_service_instance_id():
    return get_property_value(property_name="WXG_SERVICE_INSTANCE_ID")


def get_wxai_url():
    return get_property_value(property_name="WXAI_URL")
