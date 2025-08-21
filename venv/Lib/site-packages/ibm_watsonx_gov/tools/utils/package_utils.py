# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import subprocess
import sys
from typing import List

import pkg_resources


def is_package_installed(package_name):
    try:
        pkg_resources.get_distribution(package_name)
        return True
    except pkg_resources.DistributionNotFound:
        return False


def install_and_import_packages(packages: List[str]):
    try:
        # Find missing packages
        missing_packages = []
        for p in packages:
            if not is_package_installed(p):
                missing_packages.append(p)

        # Install missing packages if any
        if missing_packages:
            print(
                f"Installing missing packages: {', '.join(missing_packages)}")
            subprocess.check_call([sys.executable, "-m", "pip",
                                   "install"] + missing_packages)
    except Exception as ex:
        raise ImportError(f"Error while installing {packages}.Details:{ex}")
