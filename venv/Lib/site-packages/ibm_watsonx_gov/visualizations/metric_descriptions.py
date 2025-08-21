# ----------------------------------------------------------------------------------------------------
# IBM Confidential
# Licensed Materials - Property of IBM
# 5737-H76, 5900-A3Q
# © Copyright IBM Corp. 2025  All Rights Reserved.
# US Government Users Restricted Rights - Use, duplication or disclosure restricted by
# GSA ADPSchedule Contract with IBM Corp.
# ----------------------------------------------------------------------------------------------------

# Mapping to store metrics with their descriptions
metric_description_mapping = {
    "accuracy": "Accuracy is proportion of correct predictions.",
    "adversarial_robustness": "This metric checks how well the prompt template can resist jailbreak and prompt injection attacks.",
    "answer_relevance": "Answer relevance measures how relevant the answer or generated text is to the question sent to the LLM. This is one of the ways to determine the quality of your model.The answer relevance score is a value between 0 and 1.A value closer to 1 indicates that the answer is more relevant to the given question.A value closer to 0 indicates that the answer is less relevant to the question.",
    "answer_similarity": "Answer similarity measures how similar the answer or generated text is to the ground truth or reference answer as judged by a LLM.The answer similarity score is a value between 0 and 1.A value closer to 1 indicates that the answer is more similar to the reference value.A value closer to 0 indicates that the answer is less similar to the reference value.",
    "bleu": "BLEU (Bilingual Evaluation Understudy) is an algorithm for evaluating the quality of text which has been machine-translated from one natural language to another.The metric values are in the range of 0 to 1, higher value is better.",
    "brier_score": "The Brier score measures the mean squared difference between the predicted probability and the target value",
    "exact_match": "A given predicted string's exact match score is 1 if it is the exact same as its reference string, and is 0 otherwise.",
    "faithfulness": "Faithfulness measures how faithful the model output or generated text is to the context sent to the LLM.The faithfulness score is a value between 0 and 1.A value closer to 1 indicates that the output is more faithful or grounded and less hallucinated.A value closer to 0 indicates that the output is less faithful or grounded and more hallucinated.",
    "flesch_reading_ease": "The Readability score determines readability, complexity, and grade level of the model's output.A score between 90-100 means Very Easy to Read,80-89 means Easy to Read,70-79 means Fairly Easy to Read,60-69 means Standard to Read,50-59 means Fairly Difficult to Read,30-49 means Difficult to Read,0-29 means Very Confusing to R",
    "hap_input_score": "HAP measures if the provided content contains any Hate, Abuse and Profanity. Uses the HAP related model from Watson NLP to measure this metric. This metric measures if there exists any HAP in the input data.",
    "hap_score": "HAP measures if the provided content contains any Hate, Abuse and Profanity. Uses the HAP related model from Watson NLP to measure this metric. This metric measures if there exists any HAP in the output data.",
    "meteor": "METEOR (Metric for Evaluation of Translation with Explicit ORdering) is a machine translation evaluation metric, which is calculated based on the harmonic mean of precision and recall, with recall weighted more than precision.The metric values are in the range of 0 to 1, higher value is better.",
    "normalized_f1": "The normalized F1 metric value in a given evaluation.",
    "normalized_precision": "The normalized precision metric value in a given evaluation.",
    "normalized_recall": "The normalized recall metric value in a given evaluation.",
    "pii": "PII measures if the provided content contains any Personally Identifiable Information. This metric measures if there exists any PII in the output data.",
    "pii_input": "PII measures if the provided content contains any Personally Identifiable Information. This metric measures if there exists any PII in the input data.",
    "prompt_injection": "Attacks that trick the system by combining harmful user input with the trusted prompt created by the  developer.",
    "question_robustness": "Metric for evaluating spelling robustness, grammar robustness in the questions.",
    "roc_auc": "Area under recall and false positive rate curve.",
    "rouge_score": "ROUGE, or Recall-Oriented Understudy for Gisting Evaluation, is a set of metrics and a software package used for evaluating automatic summarization and machine translation software in natural language processing.Generative text quality monitor calculates rouge1, rouge2, rougeL, and rougeLSum to compare an automatically produced summary or translation against a reference or a set of references (human-produced) summary or translation.The metric values are in the range of 0 to 1, higher value is better.",
    "sari": "SARI (system output against references and against the input sentence) is a metric used for evaluating automatic text simplification systems. The metric compares the predicted simplified sentences against the reference and the source sentences. It explicitly measures the goodness of words that are added, deleted and kept by the system.The range of values for the SARI score is between 0 and 100 -- the higher the value, the better the performance of the model being evaluated, with a SARI of 100 being a perfect score.",
    "unsuccessful_requests": "The unsuccessful requests metric measures the ratio of questions answered unsuccessfully out of the total number of questions.The unsuccessful requests score is a value between 0 and 1.A value closer to 0 indicates that the model is successfully answering the questions.A value closer to 1 indicates the model is not able to answer the questions.",
    "f1_measure": "Harmonic mean of precision and recall.",
    "precision": "Proportion of correct predictions in predictions of positive class.",
    "recall": "Proportion of correct predictions in positive class.",
    "jaccard_similarity": "Jaccard similarity measures the similarity between sets of text data, which is used to quantify the similarity between two sets of words or tokens in text.",
    "cosine_similarity": "Cosine similarity is a fundamental similarity metric widely used in various fields, including NLP, large language models, information retrieval, text summarization, text generation.",
    "abstractness": "Abstractness measures the ratio of n-grams in the generated text output that do not appear in the source content of the foundation model.The abstractness score is a value between 0 and 1. Higher scores indicate high abstractness in the generated text output.",
    "compression": "Compression measures how much shorter the summary is when compared to the input text. It calculates the ratio between the number of words in the original text and the number of words in the foundation model output. The compression score is a value above 0. Higher scores indicate that the summary is more concise when compared to the original text.",
    "coverage": "Coverage measures the extent that the foundation model output is generated from the model input by calculating the percentage of output text that is also in the input. The coverage score is a value between 0 and 1. A higher score close to 1 indicates that higher percentage of output words are within the input text.",
    "density": "Density measures how extractive the summary in the foundation model output is from the model input by calculating the average of extractive fragments that closely resemble verbatim extractions from the original text. The density score is a value above 0. Lower scores indicate that the model output is more abstractive and on average the extractive fragments do not closely resemble verbatim extractions from the original text.",
    "repetitiveness": "Repetitiveness measures the percentage of n-grams that repeat in the foundation model output by calculating the number of repeated n-grams and the total number of n-grams in the model output.The repetitiveness score is a value between 0 and 1.",
    "average_precision": "Average Precision evaluates whether all the relevant contexts are ranked higher or not. It is the mean of the precision scores of relevant contexts. The average precision is a value between 0 and 1.A value of 1 indicates that all the relevant contexts are ranked higher.A value of 0 indicates that none of the retrieved contexts are relevant.",
    "context_relevance": "Context relevance assesses the degree to which the retrieved context is relevant to the question sent to the LLM. This is one of the ways to determine the quality of your retrieval system.The context relevance score is a value between 0 and 1.<br></br>A value closer to 1 indicates that the context is more relevant to your question in the prompt.A value closer to 0 indicates that the context is less relevant to your question in the prompt.",
    "hit_rate": "Hit Rate measures whether there is atleast one relevant context among the retrieved contexts. The hit rate value is either 0 or 1. A value of 1 indicates that there is at least one relevant context. A value of 0 indicates that there is no relevant context in the retrieved contexts.",
    "ndcg": "Normalized Discounted Cumulative Gain or NDCG measures the ranking quality of the retrieved contexts.The ndcg is a value between 0 and 1.A value of 1 indicates that the retrieved contexts are ranked in the correct order.",
    "reciprocal_rank": "Reciprocal rank is the reciprocal of the rank of the first relevant context.The retrieval reciprocal rank is a value between 0 and 1.A value of 1 indicates that the first relevant context is at first position.A value of 0 indicates that none of the relevant contexts are retrieved.",
    "retrieval_precision": "Retrieval Precision measures the quantity of relevant contexts from the total contexts retrieved. The retrieval precision is a value between 0 and 1.A value of 1 indicates that all the retrieved contexts are relevant.A value of 0 indicates that none of the retrieved contexts are relevant.",
    "micro_f1": "It is computed by taking the harmonic mean of precision and recall.",
    "macro_f1": "It is computed by taking the arithmetic mean of all the per-class F1 scores.",
    "micro_precision": "It is the ratio of number of correct predictions over all classes to the number of total predictions.",
    "micro_recall": "It is the ratio of number of correct predictions over all classes to the number of true samples.",
    "macro_precision": "It is the ratio of number of correct predictions over all classes to the number of total predictions.",
    "macro_recall": "It calculates the recall for each individual label or class separately and then takes the average of those recall scores."
}
