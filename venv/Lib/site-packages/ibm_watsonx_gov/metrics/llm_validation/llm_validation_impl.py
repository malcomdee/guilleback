# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------
import random
import re
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, TypedDict, Union

import pandas as pd

from ibm_watsonx_gov.metrics.llm_validation.llm_validation_constants import max_eval_text_for_synthesis, \
    min_recurrent_evaluation_issues
from ibm_watsonx_gov.metrics.llm_validation.llm_validation_prompts import \
    map_shortcomings_system_prompt, map_shortcomings_human_prompt, \
    recurrent_issues_synthesis_human_prompt, recurrent_issues_synthesis_system_prompt, full_response_eval_human_prompt, \
    full_response_eval_system_prompt, summarization_system_prompt, summarization_human_prompt, \
    shortcomings_clustering_system_prompt, shortcomings_clustering_human_prompt

try:
    from langchain.schema import HumanMessage, SystemMessage
    from langgraph.graph import END, StateGraph
except:
    pass

from tqdm.auto import tqdm
from ibm_watsonx_gov.metrics.llm_validation.evaluation_criteria import (
    EvaluationCriteria, get_default_evaluation_criteria)


class State(TypedDict):
    model_input: str
    model_output: str
    evaluation_text: str
    evaluation_score: Union[int, None]
    evaluation_summary: str
    llm: Any
    evaluation_criteria: EvaluationCriteria




# --- Helper Functions ---
def parse_evaluation_response(response_content):
    """Parses LLM response for evaluation text and score."""
    text = response_content.strip()
    score = None

    # Attempt to find a score line like "Evaluation score: X.Y"
    score_match = re.search(r"Evaluation score:\s*(\d+(?:\.\d+)?)", text, re.IGNORECASE)
    if score_match:
        try:
            s = float(score_match.group(1))
            if 0 <= s <= 1:
                score = s
                # Try to remove the score line and preceding/following whitespace
                text = re.sub(r"(\n|^)\s*Evaluation score:\s*\d+(?:\.\d+)?\s*(\n|$)", "\n", text).strip()

        except ValueError:
            pass

    # Fallback: try to find any float between 0 and 1 if not found above
    if score is None:
        potential_scores = re.findall(r'\b(0(?:\.\d+)?|1(?:\.0+)?)\b', response_content)
        for num_str in reversed(potential_scores):  # Check from end, often score is last
            try:
                s = float(num_str)
                if 0 <= s <= 1:
                    score = s
                    text = text.replace(num_str, "").strip()
                    break
            except ValueError:
                continue

    if score is None:
        print(f"Warning: Could not extract valid score from evaluation response: {response_content}")

    # Clean up common artifacts if needed
    text = text.replace("--- Begin Evaluation ---", "").replace("Textual Evaluation:", "").strip()

    return text, score


def generate_llm_response(llm: Any, system_prompt: str, human_prompt: str) -> str:
    """Generates a response from the LLM given prompts."""
    try:
        messages = [
            SystemMessage(content=str(system_prompt)),
            HumanMessage(content=str(human_prompt))
        ]
        results = llm.invoke(messages)
        return results.content
    except Exception as e:
        return f"LLM Error: {e}"


def run_func_in_threads(func, input_list, max_workers=10, error_prefix="Error: ", progress_desc="Processing tasks"):
    if len(input_list) == 1:
        return [func(*input_list[0])]

    results = [None] * len(input_list)
    with ThreadPoolExecutor(max_workers) as executor:
        future_to_input_idx = {executor.submit(func, *input_list[i]): i
                               for i, _ in enumerate(input_list)}
        for future in tqdm(as_completed(future_to_input_idx), total=len(input_list), desc=progress_desc):
            try:
                result = future.result()
            except Exception as e:
                result = [f"{error_prefix}: {e}"]
            results[future_to_input_idx[future]] = result

        return results


# --- Node Functions ---
def evaluate_response_node(state: State) -> Dict[str, Any]:
    """Evaluates the model's response using the full_response_template."""
    evaluation_criteria_str = state.get(
        "evaluation_criteria", get_default_evaluation_criteria()).to_str()

    system_prompt = full_response_eval_system_prompt.format(
        evaluation_criteria=evaluation_criteria_str
    )
    human_prompt = full_response_eval_human_prompt.format(
        model_input=state['model_input'],
        model_output=state['model_output'],
    )
    evaluation_response = generate_llm_response(
        state["llm"], system_prompt, human_prompt)
    evaluation_text, score = parse_evaluation_response(evaluation_response)
    return {"evaluation_text": evaluation_text, "evaluation_score": score}


def summarize_evaluation_node(state: State) -> Dict[str, str]:
    """Summarizes the generated evaluation text."""
    if not state.get("evaluation_text") or "LLM Error" in state["evaluation_text"]:
        return {"evaluation_summary": "Evaluation text missing or contains error."}

    system_prompt = summarization_system_prompt
    human_prompt = summarization_human_prompt.format(
        evaluation_text=state["evaluation_text"])
    summary = generate_llm_response(state["llm"], system_prompt, human_prompt)
    return {"evaluation_summary": summary.strip()}


# --- Graph Definition ---
def get_evaluation_graph():
    """Builds the simplified evaluation workflow."""
    workflow = StateGraph(State)
    workflow.add_node("evaluate_response", evaluate_response_node)
    workflow.add_node("summarize_evaluation", summarize_evaluation_node)
    workflow.set_entry_point("evaluate_response")
    workflow.add_edge("evaluate_response", "summarize_evaluation")
    workflow.add_edge("summarize_evaluation", END)
    app = workflow.compile()
    return app


# --- Evaluate single records ---
def _evaluate_row(row: pd.Series, app: Any, llm: Any, input_col: str, output_col: str,
                  text_col: str, score_col: str, summary_col: str, evaluation_criteria: EvaluationCriteria = None) -> pd.Series:
    """
    Helper function to evaluate a single row using the pre-compiled graph.
    To be used with df.apply().
    """
    model_input = row.get(input_col)
    model_output = row.get(output_col)

    if not model_input or not model_output:
        return pd.Series({
            text_col: "",
            score_col: None,
            summary_col: ""
        })

    initial_state: State = {
        "model_input": str(model_input),
        "model_output": str(model_output),
        "llm": llm,
        "evaluation_text": "",
        "evaluation_score": None,
        "evaluation_summary": "",
        "evaluation_criteria": evaluation_criteria,
    }

    try:
        final_state = app.invoke(initial_state)
        return pd.Series({
            text_col: final_state.get("evaluation_text", "Error: Text not generated"),
            # Default to None
            score_col: final_state.get("evaluation_score", None),
            summary_col: final_state.get(
                "evaluation_summary", "Error: Summary not generated")
        })
    except Exception as e:
        return pd.Series({
            text_col: f"Error during processing: {e}",
            score_col: None,  # Error -> None score
            summary_col: f"Error during processing: {e}"
        })


def llm_validation_per_record(
        df: pd.DataFrame,
        llm: Any,
        input_col: str = 'model_input',
        output_col: str = 'model_output',
        text_col: str = 'evaluation_text',
        score_col: str = 'evaluation_score',
        summary_col: str = 'evaluation_summary',
        evaluation_criteria: EvaluationCriteria | None = None
) -> pd.DataFrame:
    """
    Evaluates model responses in a DataFrame using a pre-compiled LangGraph.

    Args:
        df: The Pandas DataFrame to process.
        llm: An initialized LangChain compatible LLM instance.
        input_col: Name of the column containing the model input text.
        output_col: Name of the column containing the model output text.
        text_col: Name for the new column for the full evaluation text.
        score_col: Name for the new column for the extracted evaluation score.
        summary_col: Name for the new column for the evaluation summary.
        evaluation_criteria: Optional[EvaluationCriterion] List of evaluation criterion

    Returns:
        The original DataFrame with the new evaluation columns added.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("Input 'df' must be a Pandas DataFrame.")
    if not llm:
        raise ValueError("LLM instance must be provided.")
    if input_col not in df.columns:
        raise ValueError(f"Input column '{input_col}' not found in DataFrame.")
    if output_col not in df.columns:
        raise ValueError(
            f"Output column '{output_col}' not found in DataFrame.")

    app = get_evaluation_graph()
    tqdm.pandas(desc="Evaluating Rows")
    inputs = []
    indices = []
    for i, r in df.iterrows():
        inputs.append([r, app, llm, input_col, output_col, text_col, score_col, summary_col, evaluation_criteria])
        indices.append(i)

    results = run_func_in_threads(
        _evaluate_row, inputs, progress_desc="Evaluating single records")
    results = pd.DataFrame(results)

    df.loc[indices, text_col] = results[text_col]
    df.loc[indices, score_col] = results[score_col]
    df.loc[indices, summary_col] = results[summary_col]

    return df


# --- Aggregation over records ---
def generate_issues_and_map_to_records(summaries_list: List[str],
                                       llm: Any) -> Dict[str, List[int]]:
    """
    Analyzes a column of evaluation summaries to identify and rank recurring issues.
    Map each of the recurring issues back to the original summaries
    Args:
        summaries_list: The list of record level summaries
        llm: An initialized LangChain compatible LLM instance.
    Returns:
        A dictionary mapping form each identified recurring issue to a list of corresponding indices in summaries_list.
    """
    if len(summaries_list) == 0:
        issues_list = []
    elif len(summaries_list) == 1:
        issues_list = summaries_list
    else:
        issues_list = find_recurrent_evaluation_issues(summaries_list, llm)

    # return the error
    if is_issues_list_error(issues_list):
        return {issues_list[0]: []}

    if len(issues_list) > min_recurrent_evaluation_issues:
        issues_list = cluster_similar_issues(issues_list, llm)

    # return the error
    if is_issues_list_error(issues_list):
        return {issues_list[0]: []}

    # since the same summaries use for issue generation and mapping, issues must apply to the single record
    if len(summaries_list) == 1:
        return {issue: [0] for issue in issues_list}

    return map_issues_to_records(summaries_list, llm, issues_list)

def parse_shortcoming_list_response(response_content: str) -> List[str]:
    """Parses LLM response expected to be a Python list of strings."""
    try:
        # Find the list within the response
        list_match = re.search(r'\[\s*(".*?"(?:\s*,\s*".*?")*)\s*\]', response_content, re.DOTALL)
        if list_match:
            list_content = list_match.group(1)
            shortcomings = re.findall(r'"(.*?)"', list_content)
            shortcomings = [s.strip() for s in shortcomings if s.strip()]
            if shortcomings:
                return shortcomings
            else:
                return []
        else:
            return [f"Error during issue summarization: no issues found"]
    except Exception as e:
        return [f"Error during issue summarization: {e}"]


def get_summaries_for_synthesis_as_text(summaries_list: List[str]) -> str:
    valid_summaries = [str(summary) for summary in summaries_list if summary]
    valid_summaries = [
        s for s in valid_summaries
        if not is_summary_error(s)
    ]

    if not valid_summaries:
        return ""

    # Sample texts if there are too many
    if valid_summaries and len(valid_summaries) > max_eval_text_for_synthesis:
        valid_summaries = random.sample(valid_summaries, max_eval_text_for_synthesis)
    return "\n---\n".join(valid_summaries)


def cluster_similar_issues(issues_list: List[str], llm: Any) -> List[str]:
    """
        Analyzes a column of evaluation summaries to identify and rank recurring issues.

        Args:
            issues_list: The initial list of issues
            llm: An initialized LangChain compatible LLM instance.

        Returns:
            A list of strings, each describing a recurring issue after removing duplicates,
            perceived frequency (most frequent first), based on LLM analysis.
            Returns the original list if the LLM call fails.
        """
    system_prompt = shortcomings_clustering_system_prompt
    human_prompt = shortcomings_clustering_human_prompt.format(recurring_issues_list=issues_list)
    try:
        analysis_result = generate_llm_response(llm, system_prompt, human_prompt)
        new_issue_list = parse_shortcoming_list_response(analysis_result)
        if not new_issue_list or is_issues_list_error(new_issue_list):
            # if clustering failed - fallback to original issues list
            return issues_list
        return new_issue_list

    except Exception as e:
        return issues_list



def find_recurrent_evaluation_issues(
        summaries_list: List[str],
        llm: Any,
) -> List[str]:
    """
    Analyzes a column of evaluation summaries to identify and rank recurring issues.

    Args:
        summaries_list: The list of record level summaries
        llm: An initialized LangChain compatible LLM instance.

    Returns:
        A list of strings, each describing a recurring issue, ordered by
        perceived frequency (most frequent first), based on LLM analysis.
        Returns an empty list if no summaries are found or no issues are identified.
        Returns a list containing an error message if the LLM call fails.
    """
    try:
        summaries_text = get_summaries_for_synthesis_as_text(summaries_list)
    except Exception as e:
        summaries_text = ""

    if not summaries_text:
        return []

    system_prompt = recurrent_issues_synthesis_system_prompt
    human_prompt = recurrent_issues_synthesis_human_prompt.format(concatenated_evaluation_text=summaries_text)

    try:
        analysis_result = generate_llm_response(llm, system_prompt, human_prompt)
        return parse_shortcoming_list_response(analysis_result)

    except Exception as e:
        return [f"Error during issue summarization: {e}"]


def analyze_shortcomings_llm(eval_text, llm, shortcomings):
    """
    Use LLM to analyze evaluation text for shortcomings.
    Returns a list of binary values (0 or 1) indicating presence of each shortcoming.
    """

    if eval_text.startswith("Evaluation text missing") or not eval_text:
        return []

    # Create numbered list of shortcomings for the prompt
    shortcomings_list = "\n".join(
        [f"{i + 1}. {s}" for i, s in enumerate(shortcomings)])
    num_shortcomings = len(shortcomings)

    system_prompt = map_shortcomings_system_prompt.format(num_shortcomings=num_shortcomings)
    human_prompt = map_shortcomings_human_prompt.format(shortcomings_list=shortcomings_list,
                                                        num_shortcomings=num_shortcomings,
                                                        eval_text=eval_text)
    try:
        response = generate_llm_response(
            llm, system_prompt, human_prompt).strip()

        # Extract the list from the response if needed
        if '[' in response and ']' in response:
            response = response[response.find(
                '['):response.find(']') + 1].strip("[]")

        binary_values = response.split(',')

        if len(binary_values) == num_shortcomings:
            return [int(value.strip()) for value in binary_values]

        return ["Error in issues selection: bad response format"]

    except Exception as e:
        return [f"Error in issues selection: {e}"]


def is_summary_error(summary):
    return not summary or summary.startswith("Evaluation text missing or contains error.") or "LLM Error" in summary


def is_issues_list_error(issues_list):
    if len(issues_list) == 1:
        if "Error during issue summarization" in issues_list[0]:
            return True
    return False


def map_issues_to_records(summaries_list: List[str], llm, issues_list=List[str]) -> Dict[str, List[int]]:
    """
    Map each record the relevant issues from issues_list.
    Args:
        summaries_list: The list of record level summaries
        llm: An initialized LangChain compatible LLM instance.
        issues_list: The list of common recurring issues
    Returns:
        a dictionary mapping each recurring issue to the indices of the matching summaries in summaries_list
    """

    if not issues_list:
        return {}

    # return the error
    if is_issues_list_error(issues_list):
        return {issues_list[0]: []}

    # Process each evaluation
    issues_counts = {shotrcoming: 0 for shotrcoming in issues_list}
    recurring_issues_per_record = []

    input_list = [[record_summary, llm, issues_list]
                  for record_summary in summaries_list]
    results = run_func_in_threads(analyze_shortcomings_llm, input_list, error_prefix="Error in issues selection",
                                  progress_desc="Mapping issues to records")

    for i, detected_issues_result in enumerate(results):
        if not detected_issues_result:
            identified_issues = []
        elif len(detected_issues_result) == 1 and isinstance(detected_issues_result[0], str):
            identified_issues = detected_issues_result
        else:
            # Create a list of identified shortcomings for this evaluation
            identified_issues = [issues_list[i] for i in range(
                len(issues_list)) if detected_issues_result[i] == 1]
            for issue in identified_issues:
                issues_counts[issue] += 1

        recurring_issues_per_record.append(identified_issues)

    issues_stats = list(issues_counts.items())
    issues_stats.sort(key=lambda x: x[1], reverse=True)
    sorted_issues = [issue[0] for issue in issues_stats]
    issue_to_matching_record_ids = {s: [] for s in sorted_issues}

    for rec_i, record_issues in enumerate(recurring_issues_per_record):
        for record_issue in record_issues:
            issue_to_matching_record_ids[record_issue].append(rec_i)

    return issue_to_matching_record_ids


def reverse_mapping(mapping):
    """
    Reverses a mapping from keys to index lists .
    Uses the order of keys in the original mapping to produce a reverse mapping:
    index -> list of key indices.

    Args:
        mapping (dict): Mapping from keys to list of indices.

    Returns:
        dict: Mapping from index to list of key positions (ints).
    """
    reversed_map = defaultdict(list)

    for i, key in enumerate(mapping):
        for index in mapping[key]:
            reversed_map[index].append(i)

    return dict(reversed_map)
