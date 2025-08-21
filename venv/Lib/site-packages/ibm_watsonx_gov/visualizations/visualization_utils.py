# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

import pandas as pd
from IPython.display import Image, display
from itables.widget import ITable


def display_table(df: pd.DataFrame):
    """
    Function to display the dataframe
    """

    try:
        dataframe_table = ITable(
            df=df,
            caption="Records",
            buttons=[{"extend": "csvHtml5", "text": "Download"}],
            classes="display nowrap compact violations_table",
            options={
                "columnDefs": [
                    # Enable search on all columns
                    {"searchable": True, "targets": "_all"},
                    # Enable sorting on all columns
                    {"orderable": True, "targets": "_all"},
                ],
            }
        )

        # Display table
        display(dataframe_table)
    except Exception as e:
        raise Exception(f"Failed to display dataframe table. Reason: {e}")


def display_message_with_frame(message: str, frame_width: int = 80, frame_char: str = '='):
    frame_border = frame_char*frame_width
    print(f"\n{frame_border}\n{message}\n{frame_border}\n")


def display_mermaid_graph(runnable_graph, width=300, height=200):
    """
    Renders a LangChain Runnable Graph using Mermaid.

    Args:
        runnable_graph (StateGraph): Langgraph object
        width (int, optional): Graph image width. Defaults to 300.
        height (int, optional): Graph image height. Defaults to 200.
    """
    import nest_asyncio
    from langchain_core.runnables.graph import (CurveStyle, MermaidDrawMethod,
                                                NodeStyles)

    nest_asyncio.apply()

    try:
        image_data = runnable_graph.get_graph().draw_mermaid_png(
            curve_style=CurveStyle.NATURAL,
            node_colors=NodeStyles(
                first="#ffdfba", last="#baffc9", default="#fad7de"),
            wrap_label_n_words=9,
            output_file_path=None,
            draw_method=MermaidDrawMethod.PYPPETEER,
            background_color="white",
            padding=5,
        )
        display(Image(image_data, width=width, height=height))
    except Exception as e:
        raise Exception(f"Failed to render mermaid graph: {e}")
