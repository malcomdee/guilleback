import axios from "axios";

const BASE = import.meta.env.VITE_API_BASE || "https://application-33.1zvd1ciw0wl5.us-south.codeengine.appdomain.cloud";

export async function getDefaultExercise() {
  const r = await axios.get(`${BASE}/api/default_exercise`);
  return r.data;
}

export async function evaluatePayload(payload: {
  quiz: { question: string; ideal_answer: string }[];
  answers: string[];
  context: string;
  system_prompt: string;
  normalize_answers: boolean;
}) {
  const r = await axios.post(`${BASE}/api/evaluate`, payload);
  return r.data as { results: any[] };
}




// añade en api.ts
export async function fetchResults(params: { name?: string; from?: string; to?: string; limit?: number } = {}) {
  const q = new URLSearchParams();
  if (params.name) q.set("name", params.name);
  if (params.from) q.set("from", params.from);
  if (params.to) q.set("to", params.to);
  if (params.limit) q.set("limit", String(params.limit));
  const res = await fetch(`/api/results?${q.toString()}`);
  const data = await res.json();
  if (!res.ok || !data.ok) throw new Error(data?.error || "Error consultando resultados");
  return data.rows as any[];
}
