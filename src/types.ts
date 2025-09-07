export type QuizItem = { 
  question: string; 
  ideal_answer: string; 
  source_ids?: string[]; 
};

export type Exercise = { 
  topic?: string; 
  objective?: string; 
  used_sources?: string[]; 
  quiz?: QuizItem[]; 
};

export type Score = {
  // === Métricas de calidad principales ===
  prompt_safety_risk?: number | null;
  answer_similarity?: number | null;
  faithfulness?: number | null;
  answer_relevance?: number | null;
  context_relevance?: number | null;
  evasiveness?: number | null;
  topic_relevance?: number | null;

  // === Detecciones HAP / PII ===
  hap_flag?: boolean;
  hap_labels?: string[];
  pii_flag?: boolean;
  pii_entities?: string[];

  // === Métricas adicionales de governance ===
  profanity?: number | null;
  sexual_content?: number | null;
  violence?: number | null;
  social_bias?: number | null;
  harm?: number | null;
  harm_engagement?: number | null;
  jailbreak?: number | null;
  unethical_behavior?: number | null;

  // === Métricas de legibilidad ===
  text_reading_ease?: number | null;
  text_grade_level?: number | null;

  // === Resultados watsonx.ai ===
  wx_verdict?: string | null;
  wx_explanation?: string | null;
  wx_improved_answer?: string | null;
  wx_raw?: string | null;

  // === NUEVO: governance extendido ===
  /** Métricas extra detectadas por governance (distintas de las 4 de calidad). */
  gov_flags?: Record<string, number>;
  /** Alerta breve generada cuando gov_flags tiene activaciones. */
  gov_alert?: string | null;
};
