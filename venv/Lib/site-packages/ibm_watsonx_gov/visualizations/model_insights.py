# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
import ast

import ipywidgets as widgets
import matplotlib.pyplot as plt
import pandas as pd
from IPython.display import HTML, display
from itables.widget import ITable
from matplotlib.axes import Axes
from matplotlib_venn import venn2, venn2_circles, venn3, venn3_circles
from matplotlib_venn.layout.venn2 import \
    DefaultLayoutAlgorithm as Venn2DefaultLayoutAlgorithm
from matplotlib_venn.layout.venn3 import \
    DefaultLayoutAlgorithm as Venn3DefaultLayoutAlgorithm

from ibm_watsonx_gov.config.gen_ai_configuration import GenAIConfiguration
from ibm_watsonx_gov.entities.enums import TaskType
from ibm_watsonx_gov.entities.metric import GenAIMetric
from ibm_watsonx_gov.utils.gov_sdk_logger import GovSDKLogger

from .metric_descriptions import metric_description_mapping


class ModelInsights():
    """
    Class to display venn diagrams using metric violations
    NOTE: For venn diagram interactivity, `ipympl` (jupyter-matplotlib) Jupyter extension needs to be installed
    """
    # Color constants used to style the circles
    PURPLE = "#8A3FFC"
    CYAN = "#1192E8"
    TEAL = "#009D9A"
    COLORS = [PURPLE, CYAN, TEAL]

    # general constants
    MAX_METRIC_GROUP_SIZE = 3
    DEFAULT_SELECTED_METRICS_COUNT = 9

    def __init__(
            self,
            configuration: GenAIConfiguration,
            metrics: list[GenAIMetric],
    ) -> None:
        """
        ModelInsights construction. This will parse and validate the configuration

        Notes:
            - The visualization and interactivity features in the module are not supported
             by the jupyter notebook within VS Code. It is recommended to use Jupyter notebook
             or Jupyter lab from the web browser to take advantage of the features of this module
            - Supported task types: 'question_answering', 'classification', 'summarization',
                                    'generation', 'extraction', 'retrieval_augmented_generation'

        Args:
            configuration (GenAIConfiguration): Metric evaluation configuration
            metrics (list[GenAIMetric]): List of metrics to visualize
        """
        self.logger = GovSDKLogger.get_logger(__name__)
        self.configuration: GenAIConfiguration = configuration
        self.metrics: list[GenAIMetric] = metrics
        self.metric_config = self.__parse_metrics_object(self.metrics)
        self.df: pd.DataFrame = None
        self.violation_sets: set = {}
        self.violations = pd.DataFrame()
        self.config_metric_ids = []
        self.selected_patch_id = None
        self.venn_diagram_callback_id = None
        self.violation_summary_and_table_output = widgets.Output()
        self.faithfulness_attributions_output = widgets.Output()
        self.metric_groups = []

        self.__init_stylesheet()

    def __parse_metrics_object(self, metrics: list[GenAIMetric]):
        parsed_metrics = {}
        for metric in metrics:
            metric_name = metric.name
            if metric.method:
                metric_name += f".{metric.method}"
            for metric_threshold in metric.thresholds:
                parsed_metrics[metric_name] = {
                    "type": metric_threshold.type,
                    "threshold": metric_threshold.value,
                }
        return parsed_metrics

    def __reset_state(self):
        """
        Helper to reset the object state.
        """
        self.violation_sets = {}
        self.violations = pd.DataFrame()
        self.config_metric_ids = []
        self.selected_patch_id = None
        self.venn_diagram_callback_id = None
        self.metric_groups = []

    def __init_stylesheet(self):
        """
        Helper to initialize all needed custom css for the html components
        """
        styles = HTML(
            """
            <style>
                .reset_input_style > input {
                    border: unset !important;
                    background: unset !important;
                }

                .violations_table td {
                    white-space: nowrap; text-overflow:ellipsis; overflow: hidden; max-width:1px;
                }

                .tooltip {
                    position: relative;
                }
                .tooltip .tooltiptext {
                    visibility: hidden;
                    width: 120px;
                    background-color: #555;
                    color: #fff;
                    text-align: center;
                    border-radius: 6px;
                    padding: 5px 0;
                    position: absolute;
                    z-index: 1;
                    bottom: 125%;
                    left: 50%;
                    margin-left: -60px;
                    opacity: 0;
                    transition: opacity 0.3s;
                }
                .tooltip .tooltiptext::after {
                    content: "";
                    position: absolute;
                    top: 100%;
                    left: 50%;
                    margin-left: -5px;
                    border-width: 5px;
                    border-style: solid;
                    border-color: #555 transparent transparent transparent;
                }
                .tooltip:hover .tooltiptext {
                    visibility: visible;
                    opacity: 1;
                }
                mark:hover {
                    background-color: white !important;
                }
            </style>
            """
        )

        try:
            display(styles)
        except Exception as e:
            message = f"Failed to inject css styling. {e}"
            self.logger.error(message)
            raise (message)

    def __process_df(self, metric_df: pd.DataFrame):
        """
        Parse the dataframe based on the provided config
        """
        self.logger.info(
            f"processing the input metrics dataframe with {metric_df.columns}")

        # Check if the required columns exist based on the task_type
        required_columns = []
        if self.configuration.task_type == TaskType.RAG.value:
            required_columns.extend(
                [*self.configuration.output_fields, *self.configuration.input_fields,
                    *self.configuration.context_fields]
            )
        else:
            self.logger.info(
                f"Dataframe columns were not validated for task_type: '{self.configuration.task_type}'"
            )

        missing_columns = set(required_columns) - set(metric_df.columns)
        if len(missing_columns) > 0:
            message = f"Missing columns from the dataframe. {missing_columns}"
            self.logger.error(message)
            raise Exception(message)

        for metric in self.metrics:
            metric_id = f"{metric.name}.{metric.method}" if metric.method else metric.name
            self.logger.info(
                f"metric_id: {metric_id}, config: {metric.thresholds}")

            if metric_id not in metric_df.columns:
                self.logger.warning(
                    f"metric_id {metric_id} is not present in the dataframe"
                )
                continue

            if len(metric.thresholds) == 1:
                if metric.thresholds[0].type == "lower_limit":
                    violated_records = metric_df[metric_df[metric_id]
                                                 < metric.thresholds[0].value]
                else:
                    violated_records = metric_df[metric_df[metric_id]
                                                 > metric.thresholds[0].value]
            else:
                lower_limit = None
                upper_limit = None

                for threshold in metric.thresholds:
                    if threshold.type == "lower_limit":
                        lower_limit = threshold.value
                    else:
                        upper_limit = threshold.value

                if lower_limit is None or upper_limit is None:
                    message = f"Invalid metrics thresholds. duplicated threshold type. {metric.thresholds}"
                    self.logger.error(message)
                    raise Exception(message)

                violated_records = metric_df[(metric_df[metric_id] > upper_limit) & (
                    metric_df[metric_id] < lower_limit)]

            self.violation_sets[metric_id] = set(violated_records.index)
            self.violations = pd.concat(
                [self.violations, violated_records])

            self.config_metric_ids.append(
                {
                    "metric_id": metric_id,
                    "violation_count": (
                        len(self.violation_sets[metric_id])
                        if metric_id in violated_records.keys()
                        else 0
                    ),
                }
            )

        # Compute the default metric grouping
        self.df = metric_df
        self.__find_metric_grouping()

        self.logger.info(
            f"Finished processing input dataframe. {self.config_metric_ids}"
        )

    def __metric_overlaps(self, metric_id: str, config_filter=None):
        """
        Helper method to check for violations overlap between metrics. this will return a list of the provided
        metric id and the top two metric ids with the largest overlap.
        """
        self.logger.info(
            f"getting metric overlap for metric_id {metric_id}. filters: {config_filter}"
        )

        if metric_id not in self.violation_sets:
            # no violations for this metric id, we can skip it
            self.logger.info("No violations for {metric_id}. Skipping")
            return

        intersections = []  # list to store a tuple of metric id and intersection size
        current_set = self.violation_sets[metric_id]
        for violation, v in self.violation_sets.items():
            if violation == metric_id:
                # skip comparing to self
                continue
            if config_filter is not None and violation not in config_filter:
                # skip comparing with metrics that are selected
                continue

            # check if the metric id already added to a group already
            is_used = False
            for i in range(len(self.metric_groups)):
                for j in range(len(self.metric_groups[i])):
                    if violation == self.metric_groups[i][j]:
                        is_used = True
                        break
                if is_used:
                    break
            if is_used:
                continue

            intersections.append((violation, len(v.intersection(current_set))))

        # sort the metrics by the size of the intersection
        intersections = sorted(intersections, key=lambda x: x[1], reverse=True)
        self.logger.info(
            f"sorted overlaps with metric_id {metric_id} = {intersections}"
        )

        # return a list of the current metric id and the top two metrics by intersection size
        return [metric_id] + [
            intersections[i][0] for i in range(min(len(intersections), 2))
        ]

    def __find_metric_grouping(self, config_filter=None):
        """
        Function to find metrics grouping to be used for generating the venn diagrams.
        The logic is to find the metric id with the most violations, then group it with the
        metrics with the most overlap with it.
        """
        self.logger.info(
            f"building metric grouping. filter {config_filter}")

        # Sort the metric ids descending by the number of the violations
        sorted_metrics = sorted(
            self.config_metric_ids, key=lambda d: d["violation_count"], reverse=True
        )

        # temporary list to keep track of metric ids that we already grouped
        used_metric_ids = []
        for i in range(len(sorted_metrics)):
            self.logger.info(
                f"Checking metric grouping for {sorted_metrics[i]}")

            # Check if the violation count is 0, since the list is sorted, this means we can break from
            # the for loop as all the rest of metrics do no have any violations
            if sorted_metrics[i]["violation_count"] == 0:
                self.logger.info(
                    "Metric does not have any violation -- metric grouping is done"
                )
                break

            # Check if we already included this metric in another group
            if sorted_metrics[i]["metric_id"] in used_metric_ids:
                self.logger.info("Metric already used. skipping")
                continue

            # In case the current metric id is not in the config filter (not selected) we can skip this iteration
            if (
                config_filter is not None
                and sorted_metrics[i]["metric_id"] not in config_filter
            ):
                self.logger.info(
                    "Metric is not included in the filter. skipping")
                continue

            # Check which other unused metrics that have the most overlap with the current metric id
            self.metric_groups.append(
                self.__metric_overlaps(
                    sorted_metrics[i]["metric_id"], config_filter)
            )

            # Mark add the current metric id and the other metrics grouped with is as used
            used_metric_ids.extend(self.metric_groups[-1])

            # Check if we reached the configured group size and break
            if len(self.metric_groups) == self.MAX_METRIC_GROUP_SIZE:
                self.logger.info(
                    f"Reached the maximum group size: {self.MAX_METRIC_GROUP_SIZE} -- metric grouping is done"
                )
                break

        self.logger.info(
            f"Finished finding metric grouping. metric groups: {self.metric_groups}"
        )

    def __is_in_circle(
        self,
        circle_center_x: float,
        circle_center_y: float,
        circle_r: float,
        x: float,
        y: float,
    ):
        """
        Helper to identify if a given point is in a circle.
        """
        if (x - circle_center_x) * (x - circle_center_x) + (y - circle_center_y) * (
            y - circle_center_y
        ) <= circle_r * circle_r:
            return True
        else:
            return False

    def render_venn_diagrams(self, group_index=None, filters=None):
        """
        Function to render multiple interactive venn diagrams
        """
        self.logger.info(
            f"Rendering venn diagrams. group_index: {group_index}, filters: {filters}"
        )

        # Reset the context of matplotlib, this insures we start with an empty figure
        plt.clf()
        plt.close("all")

        # If we have the group index, we need to check if at least one item is selected in the filters
        if group_index is not None:
            num_of_diagrams = 1 if any(list(filters.values())) else 0
        else:
            # Check how many venn diagrams (plots) to draw
            num_of_diagrams = len(self.metric_groups)

        self.logger.info(
            f"Number of venn diagrams to render is {num_of_diagrams}")

        if num_of_diagrams == 0:
            self.logger.warning("No venn diagrams to render.")
            print("There are no diagrams to display.")
            return

        # Set up the diagrams layout
        # align diagrams horizontally
        fig, axes = plt.subplots(1, num_of_diagrams)
        plt.tight_layout()

        diagram_list = []

        # 2 or more venn diagrams
        if num_of_diagrams > 1:
            fig.set_figwidth(fig.get_figwidth() * num_of_diagrams * 0.8)
            for i in range(num_of_diagrams):
                self.logger.info(
                    f"building venn diagram #{i} out of {num_of_diagrams}"
                )
                # set the config for each of the filters
                metric_filters = {}
                for metric in self.metric_groups[i]:
                    metric_filters[metric] = True
                diagram_list.append(
                    (
                        axes[i],
                        self.__build_venn(filters=metric_filters, ax=axes[i]),
                        self.metric_groups[i],
                    )
                )

        # One venn diagram only
        elif num_of_diagrams == 1:
            metric_filters = {}

            # Check if there metric id filter is provided, otherwise use all metrics in the group
            if filters is not None:
                for metric_id, is_used in filters.items():
                    if is_used is True:
                        metric_filters[metric_id] = is_used
            else:
                for metric in self.metric_groups[
                    0 if group_index is None else group_index
                ]:
                    metric_filters[metric] = True

            diagram_list.append(
                (
                    axes,
                    self.__build_venn(filters=metric_filters, ax=axes),
                    list(metric_filters.keys()),
                )
            )

        @self.violation_summary_and_table_output.capture()
        def venn_callback(event):
            """
            On click handler for venn diagrams. This will determine which venn diagram got clicked
            and update the violation summary and table to reflect the patch that got selected
            """
            self.logger.info(f"Handling venn diagram click event: {event}")
            self.logger.info(f"Diagrams to be processed: {diagram_list}")
            self.logger.info(
                f"Selected patch_id: {self.selected_patch_id}")
            # Start by clearing the UI, this includes the violation summary and violation table
            self.violation_summary_and_table_output.clear_output()
            self.faithfulness_attributions_output.clear_output()

            # Check if we have a selected patch already and update the style
            if self.selected_patch_id is not None:
                # go over all the venn diagrams and set the opacity
                for ax, venn, _ in diagram_list:
                    for patch in venn.patches:
                        if patch is not None:
                            patch.set_alpha(0.25)

            # Identify the clicked diagram, set the patch opacity, and determine which records to display
            for ax, venn, labels in diagram_list:

                # If the event is not in this venn diagram, skip to the next one
                if not ax.in_axes(event):
                    continue

                # Determine which circles are located on the clicked coordinates, this insures we consider
                # the intersection between circles
                clicked_metric_ids = {}  # dict to store which metric ids got clicked
                for i in range(len(venn.centers)):
                    if i >= len(labels):
                        clicked_metric_ids[""] = False
                        break
                    clicked_metric_ids[labels[i]] = self.__is_in_circle(
                        venn.centers[i].x,
                        venn.centers[i].y,
                        venn.radii[i],
                        event.xdata,
                        event.ydata,
                    )

                # Determine the patch id
                patch_id = ""
                for _, is_selected in clicked_metric_ids.items():
                    patch_id = patch_id + ("1" if is_selected is True else "0")

                # The click event was not on any patch, no further actions need to be done
                if patch_id in ["00", "000"]:
                    return

                # reduce the opacity of all patches
                for patch in venn.patches:
                    if patch is not None:
                        patch.set_alpha(0.10)

                # set the opacity of the selected patch
                patch = venn.get_patch_by_id(patch_id)
                patch.set_alpha(1)
                self.selected_patch_id = (ax, patch_id)

                # Determine the selected record ids based on the patch id
                violated_record_ids = set()
                for i in range(min(len(patch_id), len(labels))):
                    if patch_id[i] == "1":
                        if len(violated_record_ids) == 0:  # First record to be added
                            violated_record_ids = self.violation_sets.get(
                                labels[i], set()
                            )
                        else:
                            violated_record_ids = violated_record_ids.intersection(
                                self.violation_sets.get(labels[i], set())
                            )

                for i in range(min(len(patch_id), len(labels))):
                    if patch_id[i] == "0":
                        violated_record_ids = (
                            violated_record_ids
                            - self.violation_sets.get(labels[i], set())
                        )

                # Check how many violated records under each metric id from the clicked venn diagram
                metric_ids_violation_count = {}
                for metric_id in labels:
                    metric_ids_violation_count[metric_id] = len(
                        violated_record_ids.intersection(
                            self.violation_sets[metric_id])
                    )

                self.logger.info(
                    f"Updated venn diagram. selected_patch_id: {self.selected_patch_id}, metric_ids_violation_count: {metric_ids_violation_count}"
                )

                # Update the UI based on the clicked section of the venn diagram
                self.print_violation_summary(metric_ids_violation_count)
                self.show_violations_table_by_violation_ids(
                    list(violated_record_ids))

        # Register matplotlib callback to handle all clicks on the plots
        self.venn_diagram_callback_id = plt.gcf().canvas.mpl_connect(
            "button_press_event", venn_callback
        )

        plt.show()

    def __build_venn(self, filters: dict[str, any], ax: Axes):
        """
        Helper function to generate a single venn diagram and implement its styling
        """
        self.logger.info(
            f"Building venn diagram. filters: {filters}, ax: {ax}")

        # Check the filters and processed violation sets to determine what violations we would add to the venn diagrams
        # items from filters object will be ignored if the metric id does not exist in the config, dataframe, or has no violations
        sets = []
        labels = []
        for key, value in filters.items():
            if key in self.violation_sets.keys() and value is True:
                if len(self.violation_sets[key]) > 0:
                    sets.append(self.violation_sets.get(key, set()))
                    labels.append(key)
        venn = None
        circles = []  # Store circles object to be able to style the borders
        try:
            if len(sets) == 1:
                # matplotlib_venn does not support diagrams with 1 set only. We need to
                # add an empty set and hide it in this case
                venn = venn2(
                    [sets[0], set()],
                    set_labels=labels,
                    set_colors=self.COLORS[0:2],
                    alpha=0.25,
                    ax=ax,
                )
                circles = venn2_circles(
                    subsets=[sets[0], set()], linewidth=1, ax=ax)

                # hide the 0 from the empty set and move the label to the center
                venn.hide_zeroes()
                label = venn.get_label_by_id("A")
                label.set_horizontalalignment("center")
            elif len(sets) == 2:
                venn = venn2(
                    sets,
                    set_labels=labels,
                    set_colors=self.COLORS[0:2],
                    alpha=0.25,
                    ax=ax,
                    layout_algorithm=Venn2DefaultLayoutAlgorithm(
                        fixed_subset_sizes=(1, 1, 1)
                    ),
                )
                circles = venn2_circles(
                    subsets=sets,
                    linewidth=1,
                    ax=ax,
                    layout_algorithm=Venn2DefaultLayoutAlgorithm(
                        fixed_subset_sizes=(1, 1, 1)
                    ),
                )
            elif len(sets) == 3:
                venn = venn3(
                    sets,
                    set_labels=labels,
                    set_colors=self.COLORS,
                    alpha=0.25,
                    ax=ax,
                    layout_algorithm=Venn3DefaultLayoutAlgorithm(
                        fixed_subset_sizes=(1, 1, 1, 1, 1, 1, 1)
                    ),
                )
                circles = venn3_circles(
                    subsets=sets,
                    linewidth=1,
                    ax=ax,
                    layout_algorithm=Venn3DefaultLayoutAlgorithm(
                        fixed_subset_sizes=(1, 1, 1, 1, 1, 1, 1)
                    ),
                )
            else:
                self.logger.warning(
                    "No metrics were selected for the venn diagram")
                print("you must select 1 to 3 metrics to display the venn diagram")

            # Set the circles borders
            for circle, color in zip(circles, self.COLORS):
                circle.set_edgecolor(color)
        except Exception as e:
            message = f"Failed to build venn diagrams. {e}"
            self.logger.error(message)
            raise Exception(message)

        return venn

    def __get_faithfulness_highlight(self, score: float):
        """
        Helper to translate the faithfulness score to text
        """
        if score >= 0.75:
            return "Faithful"
        if score < 0.75 and score >= 0.3:
            return "Somewhat faithful"
        return "Unfaithful"

    def __highlight_faithfulness(self, input: str, attributions: list[tuple[str, float]]):
        """
        Helper to highlight sections of the input based on a list of substrings and their scores.
        This is intended to highlight the faithfulness attributions in both answers and contexts.
        Note: this helper does not handle attributions overlapping.
        """
        # Remove unwanted whitespaces
        result = " ".join(input.split())

        # Go over each attribution and highlight in the context based on its score
        for attribution in attributions:
            # Remove unwanted whitespaces
            attribution_value = " ".join(attribution[0].split())

            # Determine the highlight color
            color = ""
            if attribution[1] >= 0.75:
                color = "green"
            elif attribution[1] < 0.75 and attribution[1] >= 0.3:
                color = "yellow"
            else:
                color = "red"

            # Find the attribution in the context and highlight
            result = result.replace(
                attribution_value,
                f"""
                <mark style='background-color: {color}' class='tooltip'>{attribution[0]}<span class='tooltiptext'>faithfulness score: {attribution[1]}</span></mark>
                """
            )
        return result

    def render_faithfulness_attributions(self, selected_violation):
        """
        This function will render a table of each faithfulness attribution of the answer with its score. When
        a row is selected, the contexts will be listed with each attribution highlighted and color coded based on its score.
        """
        # The object is converted to a string in the dataframe if it was loaded as a csv, we need to parse it back to a dict
        if isinstance(selected_violation["faithfulness_attributions"], str):
            faithfulness_attributions = ast.literal_eval(
                selected_violation["faithfulness_attributions"]
            )
        else:
            faithfulness_attributions = selected_violation["faithfulness_attributions"]

        attributions_df = pd.DataFrame.from_dict(faithfulness_attributions)

        attributions_table = ITable(
            # only display certain columns
            df=attributions_df[["output_text", "faithfulness_score"]],
            caption="Faithfulness attributions",
            classes="display wrap compact",
            select="single",
        )
        attributions_output = widgets.Output()

        @attributions_output.capture()
        def on_row_clicked(change):
            """
            Callback handler when a row is selected. It will list all the context with highlighting which sections of the context
            attributed to the answer and its faithfulness score
            """
            attributions_output.clear_output()

            try:
                # Check if we do not need to render the attributions, this would be in these cases:
                #   - The update is to deselect a record
                #   - The faithfulness attributions is not provided in the dataframe
                if (
                    len(change["new"]) < 1
                    or "faithfulness_attributions" not in self.df.columns
                ):
                    return

                # Go over all the attributions and build a dict for the data that will be rendered
                attributions_data = {}
                for attribution in faithfulness_attributions[change["new"][0]]["attributions"]:
                    attributions_data[attribution["feature_name"]
                                      ] = selected_violation[attribution["feature_name"]]

                    # Create a list of tuples that contain the attribution text and its score, this will be used to
                    # highlight the sections in the context
                    attrib_tuple = []
                    for feature_value, faithfulness_score in zip(attribution["feature_values"], attribution["faithfulness_scores"]):
                        attrib_tuple.append(
                            (feature_value, faithfulness_score))

                    attributions_data[attribution["feature_name"]] = self.__highlight_faithfulness(
                        attributions_data[attribution["feature_name"]], attrib_tuple)

                html = ""
                for context_column in self.configuration.context_fields:
                    context = attributions_data.get(
                        context_column, selected_violation[context_column])
                    html += f"<h3>{context_column}</h3>"
                    html += f"<p>{context}</p>"

                display(HTML(html))
            except Exception as e:
                message = f"Failed to render faithfulness attributions. {e}"
                self.logger.error(message)
                raise Exception(message)

        # Connect row selection callback
        attributions_table.observe(on_row_clicked, names=["selected_rows"])

        display(attributions_table, attributions_output)

    def render_question_and_answer_faithfulness(self, selected_violation):
        """
        Function to parse the faithfulness attributions, build html code, and display it
        """
        self.logger.info(
            f"Rendering question and answer faithfulness. Selected violation: {selected_violation}"
        )

        try:
            display(
                HTML(
                    f"""
                        <div>
                            <h2>Question</h2>
                            <p>{selected_violation[self.configuration.input_fields[0]]}</p>
                            <h2>Answer</h2>
                            <ul>
                                <li>{selected_violation[self.configuration.output_fields[0]]}</li>
                                <li>{self.__get_faithfulness_highlight(selected_violation['faithfulness'])} {selected_violation['faithfulness']}</li>
                            </ul>
                        <div>
                        """
                )
            )
        except Exception as e:
            message = f"Failed to render faithfulness attributions. {e}"
            self.logger.error(message)
            raise Exception(message)

    def show_violations_table_by_violation_ids(self, violation_ids: list[int]):
        """
        Function to display records by in ids list
        """
        self.logger.info(
            f"Displaying violation table by violation ids. Total violations: {len(violation_ids)}"
        )

        try:
            violations_table = ITable(
                # Select violated records by id
                df=self.df[self.df.index.isin(violation_ids)],
                caption="Violated Records",
                buttons=[{"extend": "csvHtml5", "text": "Download"}],
                classes="display nowrap compact violations_table",
                select="single",
            )
        except Exception as e:
            message = f"Failed to create violation table. {e}"
            self.logger.error(message)
            raise Exception(message)

        @self.faithfulness_attributions_output.capture()
        def on_row_clicked(change):
            """
            Callback handler when a row is selected. This will display the record faithfulness attribution if it exist.
            """
            # Reset the faithfulness attributions section
            self.faithfulness_attributions_output.clear_output()

            self.logger.info(
                f"Violation table row selected. Event: {change}")

            # Check if we do not need to render the attributions, this would be in these cases:
            #   - The update is to deselect a record
            #   - The faithfulness attributions is not provided in the dataframe
            if (
                len(change["new"]) < 1
                or "faithfulness_attributions" not in self.df.columns
            ):
                return

            # Pass all columns of the selected row to be rendered in the attributions section
            self.render_question_and_answer_faithfulness(
                violations_table.df.iloc[change["new"][0]]
            )
            self.render_faithfulness_attributions(
                violations_table.df.iloc[change["new"][0]]
            )

        # Connect row selection callback
        violations_table.observe(on_row_clicked, names=["selected_rows"])

        # Display the table and the faithfulness attributions below it
        try:
            display(violations_table, self.faithfulness_attributions_output)
        except Exception as e:
            message = f"Failed to render violation table. {e}"
            self.logger.error(message)
            raise Exception(message)

    def __reset_venn_diagram(self):
        """
        Resets the diagram by clearing matplotlib, disconnecting on click callback, and clearing the selected patch
        """
        self.logger.info("Resetting Venn Diagrams.")
        plt.clf()
        plt.gcf().canvas.mpl_disconnect(self.venn_diagram_callback_id)
        self.selected_patch_id = None

    def print_violation_summary(self, metric_ids_violation_count):
        """
        Helper method to format and display the violated records summary. This will highlight this information:
            - metric id
            - configured threshold
            - number of violated records
        """
        self.logger.info(
            f"Printing violation summary. Metric ids violation count: {metric_ids_violation_count}"
        )

        html_violations_list = []
        for metric_id, count in metric_ids_violation_count.items():
            html_violations_list.append(
                f"""
            <li>{metric_id} ({self.metric_config[metric_id]['threshold']})
                <ul>
                    <li>{count} violated records</li>
                </ul>
            </li>
            """
            )

        try:
            display(
                HTML(
                    f"""
                <div>
                    <h3>Violations:</h3>
                    <ul>
                        {''.join(html_violations_list)}
                    </ul>
                </div>
                """
                )
            )
        except Exception as e:
            message = f"Failed to render violation summary. {e}"
            self.logger.error(message)
            raise Exception(message)

    def __print_rca(self, metric_ids_violation_count: dict[str, int]):
        """
        Function to print the root cause analysis to the user
        Note: This depends on ibm_metrics_plugin
        """
        raise Exception("RCA is not supported.")
        self.logger.info(
            f"Printing RCA. Metric ids violation count: {metric_ids_violation_count}"
        )
        # Based on the count, build the argument generate the RCA and build the html metric RCA list
        evaluation_analysis_argument = ""
        rca_metrics_html = ""
        for metric_id, count in metric_ids_violation_count.items():
            evaluation_analysis_argument += (
                f"{metric_id}:eq:{'low' if count > 0 else 'high'},"
            )
            rca_metrics_html += (
                f"<li>{'Low' if count > 0 else 'High'}: {metric_id}</li>"
            )

        try:
            # Generate the RCA using the metrics plugin
            rca = EvalAnalysisProvider().get_metrics_eval_analysis(
                evaluation_analysis_argument
            )
        except Exception as e:
            message = f"Failed to get metric evaluation analysis. {e}"
            self.logger.error(message)
            raise Exception(message)

        # Build the html based on the generated RCA values
        causes_html = ""
        for cause in rca["causes"]:
            causes_html += f"<li>{cause}</li>"

        # Build the accordion for the recommendations section, this needs to be added into
        # an output widget to then be displayed in the accordion
        recommendations_html = ""
        for recommendation in rca["recommendations"]:
            recommendations_html += f"<li>{recommendation}</li>"
        recommendations_output = widgets.Output()
        with recommendations_output:
            try:
                display(
                    HTML(
                        f"""
                             <h2>Recommendations</h2>
                             <ul>
                                {recommendations_html}
                             </ul>
                             """
                    )
                )
            except Exception as e:
                message = f"Failed to render recommendations. {e}"
                self.logger.error(message)
                raise Exception(message)

        recommendations_accordion = widgets.Accordion(
            children=[recommendations_output], titles=[
                "See recommended actions"]
        )

        try:
            display(
                HTML(
                    f"""
                    <h1>Root cause analysis</h1>
                    <ul>
                        {rca_metrics_html}
                    </ul>
                    <h3>What does this mean?</h3>
                    <p>{rca['description']}</p>
                    <h3>What could be the cause?</h3>
                    <ul>
                        {causes_html}
                    </ul>"""
                ),
                recommendations_accordion,
            )
        except Exception as e:
            message = f"failed to render RCA. {e}"
            self.logger.error(message)
            raise Exception(message)

    def __get_metric_id_description(self, metric_id: str) -> widgets.Output:
        """
        Helper to create an icon with metric id description
        """
        output = widgets.Output(layout={'align_self': 'center'})
        metric_description = metric_description_mapping.get(metric_id, None)

        # If the metric id description exist, populate the output widget, otherwise keep it empty
        if metric_description:
            with output:
                metric_description_icon = widgets.Text(
                    value="\u24D8", tooltip=metric_description)
                metric_description_icon.add_class("reset_input_style")
                metric_description_icon.disabled = True
                metric_description_icon.layout = widgets.Layout(width='35px')
                display(metric_description_icon)

        return output

    def show_all_metrics_dropdown(self):
        """
        Function to render the widget UI. This will render the following:
            - Dropdown component to select metrics
            - Default selected metrics based on the top metrics with violated records
            - Venn diagrams of the selected metrics

        Note: For the venn diagrams to be interactive `ipympl` backend should by enabled, this can be done by:
            - installing ipympl Jupyter extension
            - explicitly enable `ipympl` backend by adding this line to the notebook `%matplotlib ipympl`
        """
        self.logger.info("Displaying interactive metric id drop down view")

        # Create an output widget for each component, this helps in customizing the layout of the ui
        dropdown_output = widgets.Output()
        checkbox_output = widgets.Output()
        venn_output = widgets.Output()

        # Sort the metric based on the number of violated records
        sorted_metrics = sorted(
            self.config_metric_ids, key=lambda d: d["violation_count"], reverse=True
        )

        # Define the dropdown widget to select the metric ids
        dropdown = widgets.Dropdown(
            options=[metric["metric_id"] for metric in sorted_metrics],
            description="Metrics",
        )

        # Select the top metrics with violation based on the configured limit
        selected_metrics = [metric["metric_id"]
                            for metric in sorted_metrics[0:3]]

        self.logger.info(
            f"Dropdown metrics: {sorted_metrics}, selected metrics: {selected_metrics}"
        )

        def add_to_checkboxes(metric_id: str):
            """
            Callback handler to add metrics to the checkbox list, this will be called when selecting a metric from the dropdown.
            """
            self.logger.info(
                f"Metric id: {metric_id} is being added the checkboxes list"
            )

            checkbox_metrics = {}
            metric_descriptions = {}
            checkbox_output.clear_output()

            # Add the metric id to the list if it is not there already
            if metric_id not in selected_metrics:
                selected_metrics.append(metric_id)

            self.logger.info(
                f"Updated selected metrics: {selected_metrics}")

            # create the checkbox widgets based on the selected metric ids
            for metric in selected_metrics:
                checkbox_metrics[metric] = widgets.Checkbox(
                    value=True, description=metric
                )
                metric_descriptions[metric] = self.__get_metric_id_description(
                    metric)

            def on_checkbox_updated(**kwargs):
                """
                Callback handler that gets triggered by adding / removing items from the checkbox list. This handler will update the venn
                diagram on any change on the metric list
                This will be triggered by these two cases:
                    - If a new metric is selected from the dropdown
                    - If a metric got unselected from the checkbox
                """
                self.logger.info(
                    f"Checkboxes are updated. kwargs {kwargs}")

                # Clear the venn diagrams before updating them to show the new selection
                self.__reset_venn_diagram()
                venn_output.clear_output()

                # Find which metrics got deselected and remove them from the UI
                for k, v in kwargs.items():
                    if v is False:
                        try:
                            if k in selected_metrics:
                                selected_metrics.remove(k)
                            checkbox_metrics[k].close()
                            metric_description = metric_descriptions.pop(
                                k, None)
                            if metric_description:
                                metric_description.close()
                        except Exception as e:
                            message = f"Failed to remove checkbox from the list. {e}"
                            self.logger.error(message)
                            raise Exception(message)

                # Reset the current groups and regenerate them based on the new selection
                self.metric_groups = []
                self.__find_metric_grouping(selected_metrics)
                with venn_output:
                    self.render_venn_diagrams()

            # Connect the call back to update the checkboxes when an item is deselected
            interactive_checkboxes = widgets.interactive_output(
                on_checkbox_updated, checkbox_metrics
            )
            with checkbox_output:
                try:
                    checkboxes_list = []
                    for checkbox, metric_description in zip(list(checkbox_metrics.values()), list(metric_descriptions.values())):
                        checkboxes_list.append(
                            widgets.HBox([checkbox, metric_description]))
                    ui = widgets.VBox(checkboxes_list)
                    display(ui, interactive_checkboxes)
                except Exception as e:
                    message = f"Failed to display checkboxes. {e}"
                    self.logger.error(message)
                    raise Exception(message)

        # Connect the callback to update the checkboxes when a metric id is selected from the dropdown
        with dropdown_output:
            widgets.interact(add_to_checkboxes, metric_id=dropdown)

        try:
            display(
                widgets.HBox(
                    [
                        venn_output,
                        widgets.VBox(
                            [dropdown_output, checkbox_output],
                            layout=widgets.Layout(margin="33px 0 0 0"),
                        ),
                    ]
                ),
                self.violation_summary_and_table_output,
            )
        except Exception as e:
            message = f"Failed to display dropdown menu and checkboxes. {e}"
            self.logger.error(message)
            raise Exception(message)

    def show_checkboxes_with_venn(self, metric_group_index: int):
        """
        Display venn diagram for the selected metric group along with checkboxes to select which metrics should be shown
        """
        if metric_group_index >= len(self.metric_groups):
            message = f"Metric group index ({metric_group_index}) is out of bound"
            self.logger.error(message)
            raise Exception(message)

        self.logger.info(
            f"Showing venn diagram with metric group index: {metric_group_index}, metric ids {self.metric_groups[metric_group_index]}"
        )

        # create the checkbox widgets based on the selected metric ids
        checkbox_metrics = {}
        metric_descriptions = {}
        for metric in self.metric_groups[metric_group_index]:
            checkbox_metrics[metric] = widgets.Checkbox(
                value=True, description=metric)
            metric_descriptions[metric] = self.__get_metric_id_description(
                metric)
        venn_diagram_output = widgets.Output()
        checkboxes_output = widgets.Output()

        def on_checkbox_updated(**kwargs):
            """
            Helper to handle checkboxes updates. This will trigger rerendering the venn diagram based on the new selection.
            """
            self.logger.info(f"Checkboxes updated: {kwargs}")
            venn_diagram_output.clear_output()
            with venn_diagram_output:
                self.render_venn_diagrams(metric_group_index, filters=kwargs)

        # Connect the call back to update the checkboxes when an item is deselected
        interactive_checkboxes = widgets.interactive_output(
            on_checkbox_updated, checkbox_metrics
        )
        with checkboxes_output:
            try:
                checkboxes_list = []
                for checkbox, metric_description in zip(list(checkbox_metrics.values()), list(metric_descriptions.values())):
                    checkboxes_list.append(widgets.HBox(
                        [checkbox, metric_description]))
                ui = widgets.VBox(checkboxes_list)
                display(ui, interactive_checkboxes)
            except Exception as e:
                message = f"Failed to display interactive checkboxes. {e}"
                self.logger.error(message)
                raise Exception(message)

        checkboxes_output.layout = widgets.Layout(margin="33px 0 0 0")

        try:
            display(widgets.HBox(
                [venn_diagram_output, checkboxes_output]))
        except Exception as e:
            message = f"Failed to display venn diagram and checkboxes output. {e}"
            self.logger.error(message)
            raise Exception(message)

    def display_metrics(self, metrics_result: pd.DataFrame):
        """Method to display ModelInsights

        Args:
            metrics_result (pd.DataFrame): _description_
        """
        # Process the DataFrame
        self.__reset_state()
        self.__process_df(metrics_result)

        # Check if there were no violations
        if len(self.violations) == 0:
            print("No violations were detected.")
            return

        # Check if we need to display the custom metrics tab,
        # this is needed when we have more than one metric group
        show_custom_metrics_tab: bool = len(self.metric_groups) > 1

        # The number of tabs should be the number of found groups, if we have more than one
        # metric group an extra tab is added for custom metric selection
        tabs_count = len(self.metric_groups) + 1 \
            if show_custom_metrics_tab else len(self.metric_groups)

        self.logger.info(
            "Displaying venn diagrams using tabs. Total tab count: {tabs_count}"
        )

        # create tabs with the the length of the groups
        tabs = widgets.Tab()
        tab_output = widgets.Output()  # Reuse the same output for all tabs..
        tabs_content = [tab_output for _ in range(tabs_count)]
        tabs_titles = [str(i + 1) for i in range(tabs_count)]
        tabs.children = tabs_content
        tabs.titles = tabs_titles

        # render content for the default
        with tab_output:
            self.show_checkboxes_with_venn(0)
            try:
                display(self.violation_summary_and_table_output)
            except Exception as e:
                message = f"Failed to display violation summary and table output. {e}"
                self.logger.error(message)
                raise Exception(message)

        @tab_output.capture()
        def on_tab_change(event):
            """
            Callback handler to render the content on tab change.
            """
            self.logger.info(f"Tab changed. event {event}")

            # We are only interested in tab change events
            if event["name"] != "selected_index":
                return

            # Clear all the content of the tab
            tab_output.clear_output()
            self.violation_summary_and_table_output.clear_output()
            self.faithfulness_attributions_output.clear_output()
            self.__reset_venn_diagram()

            # If the last tab is selected and we have custom metric tab then render it
            if show_custom_metrics_tab and event["new"] == tabs_count - 1:
                self.show_all_metrics_dropdown()
            else:
                # If the previous tab was the custom tab, re compute the metric groups
                if show_custom_metrics_tab and event["old"] == tabs_count - 1:
                    self.metric_groups = []
                    self.__find_metric_grouping()

                # Render the venn diagram based which metric group corresponds to the selected tab
                self.show_checkboxes_with_venn(event["new"])
                try:
                    display(self.violation_summary_and_table_output)
                except Exception as e:
                    message = f"Failed to display violation summary and table output. {e}"
                    self.logger.error(message)
                    raise Exception(message)

        # Register callback handler for tabs events
        tabs.observe(on_tab_change)

        try:
            display(tabs)
        except Exception as e:
            message = f"Failed to display tabs. {e}"
            self.logger.error(message)
            raise Exception(message)
