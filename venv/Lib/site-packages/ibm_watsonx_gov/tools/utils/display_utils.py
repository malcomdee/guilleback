# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import pandas as pd

try:
    import itables
    from itables import init_notebook_mode
    init_notebook_mode(all_interactive=True)
except Exception as e:
    pass


def display_tools(column_list: list = []):
    from ..clients.ai_tool_client import list_tools
    if len(column_list) == 0:
        column_list = ["asset_name", "service_provider_type",
                       "category"]

    details = list_tools()
    tools = details['tools'] or []
    if len(tools) > 0:
        df = pd.DataFrame(tools)['entity'].values
        df1 = pd.DataFrame(list(df))[column_list]
        df1 = df1.dropna()

        # Rename the column for ease of use
        df1 = df1.rename(columns={'asset_name': 'tool_name'})
    else:
        df1 = pd.DataFrame()

    itables.show(df1)
