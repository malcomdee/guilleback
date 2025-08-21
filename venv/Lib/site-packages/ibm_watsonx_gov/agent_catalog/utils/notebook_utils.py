# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from pathlib import Path

import nbformat
from IPython.display import display
from pandas import json_normalize

from ..clients.ai_agent_client import list_agents


def get_all_code_from_notebook(notebook_path: str, main_method_name: str) -> str:
    """
    Reads all code cells from a Jupyter notebook and returns combined Python code.

    Args:
        notebook_path: Path of the notebook
        main_method_name: Name of the method to stop reading after this method in the notebook
    Returns:
        str: collected code from notebook cells
    """
    notebook_path = Path(notebook_path).expanduser().resolve()
    
    with open(notebook_path, 'r', encoding='utf-8') as f:
        nb = nbformat.read(f, as_version=4)

    code_cells = [cell.source for cell in nb.cells if cell.cell_type == 'code']
    collected_code = []

    for cell_code in code_cells:
        if "pip" in cell_code:
            continue
        collected_code.append(cell_code)
        if main_method_name in cell_code:
            break  # Stop after reaching the main method
            
    return "\n\n".join(collected_code)

def display_agents(search_text: str = None):
    """
    Display the agents output in a dataframe

    Args:
        search_text: text to search in the agents name, display name, description and summary fields
    """

    try:
        if search_text is not None:
            agent_resp = list_agents(search_text=search_text)
        else:
            agent_resp = list_agents()
        rename_columns = {'entity.asset_name': 'agent_name','entity.category': 'category',
            'entity.service_provider_type': 'service_provider_type'}
        selected_columns = ["agent_name","category","service_provider_type"]
        df = json_normalize(agent_resp['agents'],  sep='.')
        # Rename the columns for clarity
        df.rename(columns=rename_columns, inplace=True)
        df = df.dropna()
        df = (df[selected_columns])
        # Display table
        display(df)
    except Exception as e:
        raise Exception(f"Failed to display agents dataframe table. Reason: {e}")


