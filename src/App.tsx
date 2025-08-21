import React, { useEffect, useMemo, useState } from "react";
import { Theme, Button, TextArea, Tag, InlineLoading } from "@carbon/react";
import { DonutChart } from "@carbon/charts-react";
import { Exercise, Score } from "./types";
import { getDefaultExercise, evaluatePayload } from "./api";
import GovernanceDemo from "./GovernanceDemo";
import image from "../assets/Picture1.png";

// ====== Utils ======
const pct = (x: number | null | undefined) =>
  x == null ? "—" : `${(x * 100).toFixed(1)}%`;
const toPctNum = (x: number | null | undefined) =>
  x == null ? 0 : Math.max(0, Math.min(100, Math.round(x * 100)));

const donutMetricDefs: { key: keyof Score; label: string }[] = [
  { key: "answer_similarity", label: "Answer Similarity" },
  { key: "faithfulness", label: "Faithfulness" },
  { key: "answer_relevance", label: "Answer Relevance" },
  { key: "context_relevance", label: "Context Relevance" },
 /*
  { key: "evasiveness", label: "Evasiveness" },
  { key: "topic_relevance", label: "Topic Relevance" },
  { key: "profanity", label: "Profanity" },
  { key: "sexual_content", label: "Sexual Content" },
  { key: "violence", label: "Violence" },
  { key: "social_bias", label: "Social Bias" },
  { key: "harm", label: "Harm" },
  { key: "harm_engagement", label: "Harm Engagement" },
  { key: "jailbreak", label: "Jailbreak" },
  { key: "unethical_behavior", label: "Unethical Behavior" },
  */
];

function MetricTags({ r }: { r: Score }) {
  return (
    <div style={{ display: "flex", gap: 8, alignItems: "center", flexWrap: "wrap" }}>
      {r.answer_similarity != null && <Tag type="green">Similarity: {pct(r.answer_similarity)}</Tag>}
      {r.faithfulness != null && <Tag type="blue">Faithfulness: {pct(r.faithfulness)}</Tag>}
      {r.answer_relevance != null && <Tag type="cyan">Ans Rel: {pct(r.answer_relevance)}</Tag>}
      {r.context_relevance != null && <Tag type="teal">Ctx Rel: {pct(r.context_relevance)}</Tag>}
{/*
  {r.evasiveness != null && <Tag type="purple">Evasiveness: {pct(r.evasiveness)}</Tag>}
  {r.topic_relevance != null && <Tag type="gray">Topic Rel: {pct(r.topic_relevance)}</Tag>}
  {r.text_reading_ease != null && <Tag type="cool-gray">Flesch: {r.text_reading_ease.toFixed(1)}</Tag>}
  {r.text_grade_level != null && <Tag type="warm-gray">F-K Grade: {r.text_grade_level.toFixed(1)}</Tag>}
  {(r.hap_flag || r.pii_flag) && <span style={{ width: 8 }} />}
  {r.hap_flag && <Tag type="red">HAP detectado</Tag>}
  {Array.isArray(r.hap_labels) && r.hap_labels.map((lbl, i) => (<Tag key={`hap-${i}`} type="red">{lbl}</Tag>))}
  {r.pii_flag && <Tag type="magenta">PII detectado</Tag>}
  {Array.isArray(r.pii_entities) && r.pii_entities.map((ent, i) => (<Tag key={`pii-${i}`} type="magenta">{ent}</Tag>))}
*/}

    </div>
  );
}

function MetricDonuts({ r }: { r: Score }) {
  const donuts = useMemo(
    () =>
      donutMetricDefs
        .map((def) => ({ ...def, value: (r[def.key] as number | null | undefined) ?? null }))
        .filter((m) => m.value != null),
    [r]
  );
  if (!donuts.length) return null;

  return (
    <div style={{ display: "grid", gap: 8, gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))" }}>
      {donuts.map((m, i) => (
        <DonutChart
          key={i}
          data={[
            { group: m.label, value: toPctNum(m.value) },
            { group: "Resto", value: 100 - toPctNum(m.value) },
          ]}
          options={{ title: m.label, height: "200px", legend: { alignment: "center" }, tooltip: { enabled: true } }}
        />
      ))}
    </div>
  );
}

function WxCorrection({ r, idx }: { r: Score; idx: number }) {
  React.useEffect(() => {
    if (r && r.wx_raw) {
      // eslint-disable-next-line no-console
      console.log(`[wx.ai][Pregunta ${idx + 1}] raw:`, r.wx_raw);
    }
  }, [r, idx]);

  if (!r.wx_verdict && !r.wx_explanation && !r.wx_improved_answer) return null;
  const verdictType = r.wx_verdict === "Correcta" ? "green" : r.wx_verdict === "Mejorable" ? "yellow" : "red";

  return (
    <div className="wx-panel">
      <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8 }}>
        {r.wx_verdict && <Tag type={verdictType as any}>Veredicto: {r.wx_verdict}</Tag>}
        {r.wx_improved_answer && <Tag type="teal">Sugerencia</Tag>}
      </div>
      {r.wx_explanation && <p style={{ margin: "4px 0 8px 0" }}>{r.wx_explanation}</p>}
      {r.wx_improved_answer && (
        <div className="wx-suggestion">
          <strong>Versión mejorada:</strong> {r.wx_improved_answer}
        </div>
      )}
    </div>
  );
}

export default function App() {
  // Tabs: "exercise" y "govdemo"
  const [tab, setTab] = useState<"exercise" | "govdemo">("exercise");

  // Estado ejercicio
  const [exercise, setExercise] = useState<Exercise>({});
  const quiz = exercise.quiz ?? [];
  const [answers, setAnswers] = useState<string[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [results, setResults] = useState<Score[]>([]);
  const [systemPrompt, setSystemPrompt] = useState(
    "Eres un asistente útil y seguro. Responde con precisión y sin divulgar datos sensibles."
  );
  const [normalize, setNormalize] = useState(true);

  useEffect(() => {
    // Carga ejercicio solo si estamos en la pestaña de ejercicio
    if (tab !== "exercise") return;
    getDefaultExercise().then((data) => {
      setExercise(data);
      setAnswers((data?.quiz ?? []).map(() => ""));
    });
  }, [tab]);

  const submit = async () => {
    if (!quiz.length) return;
    setSubmitting(true);
    const payload = {
      quiz: quiz.map((q) => ({ question: q.question, ideal_answer: q.ideal_answer })),
      answers,
      context: exercise.objective || "",
      system_prompt: systemPrompt,
      normalize_answers: normalize,
    };
    const { results } = await evaluatePayload(payload);
    setResults(results as Score[]);
    setSubmitting(false);
  };

  const ready = (quiz?.length ?? 0) > 0 && answers.length === quiz.length;

  return (
    <Theme theme="white">
      <div className="ibm-shell">
        {/* Header IBM */}
        <header className="ibm-header">
          <img className="ibm-header__logo" src={image} alt="IBM" />
          <div className="ibm-header__title">BeeLink</div>
        </header>

        {/* Tabs */}
        <main className="ibm-container">
          <div className="ibm-card" style={{ display: "flex", gap: 8 }}>
            <Button kind={tab === "exercise" ? "primary" : "tertiary"} onClick={() => setTab("exercise")}>
              Ejercicio (Guillermo)
            </Button>
            <Button kind={tab === "govdemo" ? "primary" : "tertiary"} onClick={() => setTab("govdemo")}>
              Governance Demo
            </Button>
          </div>

          {/* Pestaña: Ejercicio */}
          {tab === "exercise" && (
            <>
              <h3 style={{ margin: 0 }}>Ejercicio: {exercise.topic || "—"}</h3>

              {exercise.objective && (
                <section className="ibm-context">
                  <strong>Contexto (puedes ocultarlo):</strong>
                  <p style={{ margin: "6px 0", whiteSpace: "pre-wrap" }}>{exercise.objective}</p>
                  {!!exercise.used_sources?.length && (
                    <p className="ibm-links" style={{ margin: "8px 0 0 0" }}>
                      <strong>Fuentes para leer:</strong>{" "}
                      {exercise.used_sources.map((u, i) => (
                        <a key={i} href={u} target="_blank" rel="noreferrer">
                          {(() => {
                            try { return new URL(u).hostname; } catch { return u; }
                          })()}
                        </a>
                      ))}
                    </p>
                  )}
                </section>
              )}

              {/* Opciones */}
              <section className="ibm-card" style={{ display: "grid", gap: 8 }}>
                <label>
                  <div style={{ fontWeight: 600 }}>System prompt</div>
                  <textarea
                    value={systemPrompt}
                    onChange={(e) => setSystemPrompt(e.target.value)}
                    rows={3}
                    className="cds--text-area"
                    style={{ width: "100%" }}
                  />
                </label>
                <label style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <input type="checkbox" checked={normalize} onChange={(e) => setNormalize(e.target.checked)} />
                  Normalizar respuestas (sin tildes/puntuación)
                </label>
              </section>

              {ready && (
                <div className="ibm-grid">
                  {quiz.map((q, idx) => {
                    const r = results[idx] || {};
                    return (
                      <section key={idx} className="ibm-card" style={{ display: "grid", gap: 12 }}>
                        <div>
                          <strong>Pregunta {idx + 1}</strong>
                          <p style={{ margin: "6px 0 0 0" }}>{q.question}</p>
                        </div>

                        <TextArea
                          labelText="Tu respuesta"
                          placeholder="Escribe aquí…"
                          value={answers[idx] ?? ""}
                          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => {
                            const value = e.target.value;
                            setAnswers((prev) => {
                              const safe = Array.isArray(prev) ? prev : [];
                              const next = [...safe];
                              next[idx] = value;
                              return next;
                            });
                          }}
                        />

                        <div style={{ display: "grid", gap: 12 }}>
                          <MetricTags r={r} />
                          <MetricDonuts r={r} />
                          <WxCorrection r={r} idx={idx} />
                        </div>
                      </section>
                    );
                  })}
                </div>
              )}

              <div className="ibm-actions">
                <Button kind="primary" onClick={submit} disabled={!quiz.length || submitting}>
                  {submitting ? "Evaluando…" : "Comprobar"}
                </Button>
                {submitting && <InlineLoading description="Esperando resultados…" />}
              </div>
            </>
          )}

          {/* Pestaña: Governance Demo */}
          {tab === "govdemo" && <GovernanceDemo />}
        </main>
      </div>
    </Theme>
  );
}
