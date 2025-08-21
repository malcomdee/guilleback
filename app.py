import os, json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

from services.watsonx_client import build_wxa_model, correct_answer, hap_pii_detect, anti_burst_sleep
from services.governance_eval import evaluate_governance, evaluate_governance_text

load_dotenv()
app = Flask(__name__)
# CORS explícito para dev
CORS(
    app,
    resources={r"/api/*": {"origins": ["http://localhost:3001", "http://127.0.0.1:3001"]}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=False,
)

# Si alguna vista no aplica CORS por error, garantizamos los headers aquí
@app.after_request
def add_cors_headers(resp):
    origin = request.headers.get("Origin")
    if origin in ("http://localhost:3001", "http://127.0.0.1:3001"):
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp

# Manejo genérico de preflight
@app.route("/api/<path:_>", methods=["OPTIONS"])
def cors_preflight(_):
    return ("", 204)

DEFAULT_CONTEXT = """Perfil extenso: Guillermo Treister

Formación académica
Guillermo Treister es Ingeniero Civil en Informática por la Universidad de Chile y cuenta con un Diploma en Gestión de Negocios otorgado por la Universidad Adolfo Ibáñez.

Trayectoria profesional
Actualmente ocupa el cargo de Latin America Watson AI Apps Executive en IBM, liderando soluciones de IA en LATAM. También ha sido Gerente Técnico Cloud en IBM Chile.

Visión y enfoque sobre la IA
Ética y responsabilidad: insiste en IA gobernable, explicable y confiable.
IA generativa: destaca su carácter disruptivo para crear contenido.
Democratización tecnológica: uso por no especialistas.
"""

DEFAULT_LINKS = [
    "https://latam.tivit.com/prensa/descubriendo-su-potencial-en-el-mundo-de-los-negocios",
    "https://itbuilderslive.com/2023/personas/guillermo-treister/",
    "https://txsplus.com/2022/06/guillermo-treister-latin-america-watson-ai-apps-executive-de-ibm-entrega-las-claves-sobre-la-importancia-de-la-ia-etica/",
]

DEFAULT_QUIZ = [
    {"question": "¿Quién es el Ingeniero Civil en Informática por la Universidad de Chile y diplomado en Gestión de Negocios por la Universidad Adolfo Ibáñez?",
     "ideal_answer": "Guillermo Treister."},
    {"question": "¿Quién actualmente lidera como Latin America Watson AI Apps Executive en IBM y ha sido Gerente Técnico Cloud en IBM Chile?",
     "ideal_answer": "Guillermo Treister."},
    {"question": "¿Quién ha defendido que la IA debe ser gobernable, explicable y confiable, destacando la necesidad de vigilancia continua para evitar sesgos?",
     "ideal_answer": "Guillermo Treister."},
    {"question": "¿Quién define la IA generativa como disruptiva por su velocidad y coherencia para crear contenido, y aboga por su democratización?",
     "ideal_answer": "Guillermo Treister."},
]

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/api/evaluate")
def evaluate():
    """
    Body JSON:
    {
      "quiz": [{"question": "...", "ideal_answer": "..."}],
      "answers": ["...", "..."],
      "context": "...",
      "system_prompt": "...",
      "normalize_answers": true
    }
    """
    data = request.get_json(force=True) or {}
    quiz = data.get("quiz") or DEFAULT_QUIZ
    answers = data.get("answers") or []
    context = data.get("context") or DEFAULT_CONTEXT
    system_prompt = data.get("system_prompt") or "Eres un asistente útil y seguro. Responde con precisión y sin divulgar datos sensibles."
    normalize = bool(data.get("normalize_answers", True))

    # 1) Governance metrics
    metrics_rows = evaluate_governance(quiz, answers, context, system_prompt, normalize_answers=normalize)

    # 2) HAP/PII + watsonx.ai correction (secuencial)
    model, err = build_wxa_model()
    results = []
    for i, q in enumerate(quiz):
        row = metrics_rows[i] if i < len(metrics_rows) else {}
        ans = answers[i] if i < len(answers) else ""
        flags = hap_pii_detect(ans)
        row.update(flags)

        if err:
            row.update({"wx_verdict": None, "wx_explanation": None, "wx_improved_answer": None, "wx_raw": err})
        else:
            corr = correct_answer(model, q["question"], ans, context, system_prompt)
            row.update(corr)
            anti_burst_sleep()
        results.append(row)

    return jsonify({"results": results})

@app.get("/api/default_exercise")
def default_exercise():
    return jsonify({
        "topic": "Guillermo Treister",
        "objective": DEFAULT_CONTEXT,
        "used_sources": DEFAULT_LINKS,
        "quiz": DEFAULT_QUIZ
    })






@app.post("/api/governance/score")
def governance_score():
    """
    Body: { "text": "..." }
    Respuesta: { "<metric>": float(0..1), ... }
    """
    try:
        data = request.get_json(force=True) or {}
        text = (data.get("text") or "").strip()
        if not text:
            return jsonify({"error": "text requerido"}), 400

        scores = evaluate_governance_text(text)  # dict con claves de métricas
        # Aseguramos 0..1 y solo numéricos
        clean = {}
        for k, v in (scores or {}).items():
            try:
                if v is None:
                    continue
                f = float(v)
                clean[k] = max(0.0, min(1.0, f))
            except Exception:
                pass
        return jsonify(clean)
    except Exception as e:
        return jsonify({"error": str(e)}), 500




if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
