import os, json, time, datetime, base64, pathlib, site
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

# --- Tus servicios existentes (watsonx + governance) ---
from services.watsonx_client import build_wxa_model, correct_answer, hap_pii_detect, anti_burst_sleep
from services.governance_eval import evaluate_governance, evaluate_governance_text

load_dotenv()
app = Flask(__name__)

# -----------------------
# CORS explícito para dev/prod
# -----------------------
CORS(
    app,
    resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3001",
                "http://127.0.0.1:3001",
                "https://frontend-governance.1zcre0sjim2q.us-south.codeengine.appdomain.cloud",
            ]
        }
    },
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    supports_credentials=False,
)

@app.after_request
def add_cors_headers(resp):
    origin = request.headers.get("Origin")
    if origin in (
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://frontend-governance.1zcre0sjim2q.us-south.codeengine.appdomain.cloud",
    ):
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return resp

@app.route("/api/<path:_>", methods=["OPTIONS"])
def cors_preflight(_):
    return ("", 204)

# -----------------------
# Defaults (tu ejercicio)
# -----------------------
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
    {"question": "¿Quién es el Ingeniero Civil en Informática por la Universidad de Chile y diplomado en Gestión de Negocios por la Universidad Adolfo Ibáñez?", "ideal_answer": "Guillermo Treister."},
    {"question": "¿Quién actualmente lidera como Latin America Watson AI Apps Executive en IBM y ha sido Gerente Técnico Cloud en IBM Chile?", "ideal_answer": "Guillermo Treister."},
    {"question": "¿Quién ha defendido que la IA debe ser gobernable, explicable y confiable, destacando la necesidad de vigilancia continua para evitar sesgos?", "ideal_answer": "Guillermo Treister."},
    {"question": "¿Quién define la IA generativa como disruptiva por su velocidad y coherencia para crear contenido, y aboga por su democratización?", "ideal_answer": "Guillermo Treister."},
]

# -----------------------
# Db2 REST (config desde .env)
# -----------------------
DB2_REST_BASE = os.getenv("DB2_REST_BASE", "").rstrip("/")  # ej: https://<host>
DB2_DEPLOYMENT_ID = os.getenv("DB2_DEPLOYMENT_ID", "")      # CRN de deployment (a veces requiere URL-encode)
DB2_UID  = os.getenv("DB2_UID", "")
DB2_PWD  = os.getenv("DB2_PWD", "")
DB2_DB   = os.getenv("DB2_DB", "bludb")  # no siempre requerido por REST, pero lo dejamos

def _rest_headers(token: str | None = None):
    h = {
        "Content-Type": "application/json",
        "X-Deployment-Id": DB2_DEPLOYMENT_ID,  # requerido por el API v4
    }
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def _db2_rest_token():
    """
    Obtiene token vía /dbapi/v4/auth/tokens usando usuario/password de la instancia.
    """
    if not (DB2_REST_BASE and DB2_DEPLOYMENT_ID and DB2_UID and DB2_PWD):
        raise RuntimeError("Config REST incompleta: DB2_REST_BASE, DB2_DEPLOYMENT_ID, DB2_UID, DB2_PWD son requeridas")
    url = f"{DB2_REST_BASE}/dbapi/v4/auth/tokens"
    resp = requests.post(url, headers=_rest_headers(), json={"userid": DB2_UID, "password": DB2_PWD}, timeout=30)
    if resp.status_code >= 300:
        raise RuntimeError(f"Error auth REST Db2: {resp.status_code} {resp.text}")
    data = resp.json() if resp.text else {}
    token = data.get("token") or data.get("id_token")  # distintos nombres según despliegue
    if not token:
        raise RuntimeError(f"Auth sin token. Respuesta: {data}")
    return token

def _db2_sql_job(token: str, commands: str, stop_on_error: str = "no", limit: int = 1000):
    """
    Lanza un job SQL (puede ser múltiples INSERT separados por ;) y devuelve el id de job.
    """
    url = f"{DB2_REST_BASE}/dbapi/v4/sql_jobs"
    payload = {
        "commands": commands,
        "limit": limit,
        "separator": ";",
        "stop_on_error": stop_on_error,
    }
    resp = requests.post(url, headers=_rest_headers(token), json=payload, timeout=60)
    if resp.status_code >= 300:
        raise RuntimeError(f"Error creando SQL job: {resp.status_code} {resp.text}")
    data = resp.json()
    job_id = data.get("id")
    if not job_id:
        raise RuntimeError(f"Respuesta sin id de job: {data}")
    return job_id

def _db2_sql_fetch(token: str, job_id: str, timeout_sec: int = 30):
    """
    Consulta el estado/resultado del job hasta completar o agotar tiempo.
    """
    url = f"{DB2_REST_BASE}/dbapi/v4/sql_jobs/{job_id}"
    t0 = time.time()
    while True:
        resp = requests.get(url, headers=_rest_headers(token), timeout=30)
        if resp.status_code >= 300:
            raise RuntimeError(f"Error consultando SQL job: {resp.status_code} {resp.text}")
        data = resp.json() if resp.text else {}
        status = data.get("status") or data.get("state")
        if status in ("completed", "succeeded", "completed successfully"):
            return data
        if status in ("failed", "error"):
            return data
        if time.time() - t0 > timeout_sec:
            return data
        time.sleep(0.8)

def _ensure_results_table(token: str):
    """
    Crea la tabla GOVERNANCE_RESULTS si no existe (consulta SYSCAT.TABLES primero).
    Columnas pedidas: nombre, fecha, veredicto + 4 métricas (%).
    """
    check_sql = (
        "SELECT 1 FROM SYSCAT.TABLES "
        "WHERE TABNAME = 'GOVERNANCE_RESULTS' AND TABSCHEMA = CURRENT SCHEMA "
        "FETCH FIRST 1 ROW ONLY"
    )
    job = _db2_sql_job(token, check_sql, stop_on_error="yes")
    info = _db2_sql_fetch(token, job)
    exists = False
    try:
        rows = (info.get("results") or [{}])[0].get("rows") or []
        exists = len(rows) > 0
    except Exception:
        pass
    if exists:
        return

    create_sql = """
    CREATE TABLE GOVERNANCE_RESULTS (
      ID INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
      NOMBRE VARCHAR(128),
      FECHA DATE,
      PREGUNTA SMALLINT,
      VEREDICTO VARCHAR(16),
      ANSWER_SIMILARITY DECIMAL(5,2),
      ANSWER_RELEVANCE  DECIMAL(5,2),
      FAITHFULNESS      DECIMAL(5,2),
      CONTEXT_RELEVANCE DECIMAL(5,2)
    )
    """
    job = _db2_sql_job(token, create_sql, stop_on_error="yes")
    _db2_sql_fetch(token, job)

def _sql_escape(s: str) -> str:
    return (s or "").replace("'", "''")

def _pct100(x):
    try:
        return round(float(x) * 100.0, 2)
    except Exception:
        return None

def _insert_results(token: str, name: str, results: list[dict]):
    """
    Inserta N filas (una por pregunta) en GOVERNANCE_RESULTS.
    """
    today = datetime.date.today().isoformat()  # YYYY-MM-DD
    sql_cmds = []
    for idx, r in enumerate(results, start=1):
        veredicto = (r.get("wx_verdict") or "")[:16]
        a = _pct100(r.get("answer_similarity"))
        b = _pct100(r.get("answer_relevance"))
        c = _pct100(r.get("faithfulness"))
        d = _pct100(r.get("context_relevance"))
        # usamos CURRENT DATE para la fecha del día del insert
        sql = (
            "INSERT INTO GOVERNANCE_RESULTS "
            "(NOMBRE, FECHA, PREGUNTA, VEREDICTO, ANSWER_SIMILARITY, ANSWER_RELEVANCE, FAITHFULNESS, CONTEXT_RELEVANCE) "
            f"VALUES ('{_sql_escape(name[:128])}', CURRENT DATE, {idx}, '{_sql_escape(veredicto)}', "
            f"{'NULL' if a is None else a}, "
            f"{'NULL' if b is None else b}, "
            f"{'NULL' if c is None else c}, "
            f"{'NULL' if d is None else d})"
        )
        sql_cmds.append(sql)

    # Múltiples INSERT en un solo job
    joined = ";\n".join(sql_cmds)
    job = _db2_sql_job(token, joined, stop_on_error="no")
    info = _db2_sql_fetch(token, job, timeout_sec=45)
    return info

# -----------------------
# Endpoints
# -----------------------
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

    # 1) Métricas de governance (tu evaluador)
    metrics_rows = evaluate_governance(quiz, answers, context, system_prompt, normalize_answers=normalize)

    # 2) HAP/PII + corrección watsonx.ai
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

        scores = evaluate_governance_text(text)
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

# -----------------------
# Guardado en Db2 (REST) al presionar "Comprobar"
# -----------------------
@app.post("/api/save_results")
def save_results():
    """
    Body JSON:
    {
      "name": "valor_cookie",
      "results": [
        {
          "wx_verdict": "Correcta|Mejorable|Incorrecta",
          "answer_similarity": 0..1,
          "answer_relevance":  0..1,
          "faithfulness":      0..1,
          "context_relevance": 0..1
        }, ... (uno por pregunta)
      ]
    }
    """
    payload = request.get_json(force=True) or {}
    name = (payload.get("name") or "").strip()
    results = payload.get("results") or []
    if (not name) or (not isinstance(results, list)) or (not results):
        return jsonify({"error": "name y results son requeridos"}), 400

    try:
        token = _db2_rest_token()
        _ensure_results_table(token)
        info = _insert_results(token, name, results)
        return jsonify({"ok": True, "job": info.get("id"), "status": info.get("status")})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------
# Main
# -----------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8000"))
    app.run(host="0.0.0.0", port=port, debug=True)
