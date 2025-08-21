export type QuizItem = { question: string; ideal_answer: string; source_ids?: string[] };
export type Exercise = { topic?: string; objective?: string; used_sources?: string[]; quiz?: QuizItem[] };

export type Score = {
  prompt_safety_risk?: number | null;
  answer_similarity?: number | null;
  faithfulness?: number | null;
  answer_relevance?: number | null;
  context_relevance?: number | null;
  evasiveness?: number | null;
  topic_relevance?: number | null;

  hap_flag?: boolean;
  hap_labels?: string[];
  pii_flag?: boolean;
  pii_entities?: string[];

  profanity?: number | null;
  sexual_content?: number | null;
  violence?: number | null;
  social_bias?: number | null;
  harm?: number | null;
  harm_engagement?: number | null;
  jailbreak?: number | null;
  unethical_behavior?: number | null;

  text_reading_ease?: number | null;
  text_grade_level?: number | null;

  wx_verdict?: string | null;
  wx_explanation?: string | null;
  wx_improved_answer?: string | null;
  wx_raw?: string | null;
};
