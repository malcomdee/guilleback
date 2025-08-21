# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

from enum import Enum

LLMValidation = "llm_validation"
max_eval_text_for_synthesis = 150
min_recurrent_evaluation_issues =  5

class LLMValidationFields(Enum):
    INPUT_FIELD = "model_input"
    OUTPUT_FIELD = "model_output"
    TEXT_FIELD = "evaluation_text"
    SCORE_FIELD = "evaluation_score"
    SUMMARY_FIELD = "evaluation_summary"
    RECURRING_ISSUE_FIELD = "recurring_issues"
    RECURRING_ISSUE_IDS_FIELD = "recurring_issues_ids"
    EVALUATION_CRITERIA_FIELD = "evaluation_criteria"
