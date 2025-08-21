# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import logging


class GovSDKLogger:
    """
    Logger for watsonx governance SDK
    """
    DEFAULT_LOG_LEVEL = logging.WARN

    @staticmethod
    def get_logger(name):
        """
        Function the return a logger object.
        Params:
        name (str): The name of the logger.
        Returns:
        logging.Logger: A logger object
        """
        logger = logging.getLogger(name)
        logger.propagate = False
        if not logger.hasHandlers():
            logger.setLevel(GovSDKLogger.DEFAULT_LOG_LEVEL)
            logger.propagate = False
            handler = logging.StreamHandler()
            logger.addHandler(handler)
            formatter = logging.Formatter(
                "[%(asctime)s]-[%(name)s]-[ %(levelname)s ]-[Line %(lineno)d] ~~> %(message)s"
            )
            handler.setFormatter(formatter)
        return logger
