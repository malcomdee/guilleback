import axios from "axios";

const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000;

export async function getDefaultExercise() {
  const r = await axios.get(`https://back-governance.1zcre0sjim2q.us-south.codeengine.appdomain.cloud/api/default_exercise`);
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
