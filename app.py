import os
import time
import datetime
import io
import csv
import requests
import re

from flask import Flask, request, jsonify, Response
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
    resources={r"/api/*": {"origins": ["http://localhost:3001", "http://127.0.0.1:3001",
                                       "https://application-36.1zvd1ciw0wl5.us-south.codeengine.appdomain.cloud",  "https://application-8c.1zvd1ciw0wl5.us-south.codeengine.appdomain.cloud",]}},
    methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-User-Name"],
    supports_credentials=False,
)

@app.after_request
def add_cors_headers(resp):
    origin = request.headers.get("Origin")
    if origin in (
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://application-36.1zvd1ciw0wl5.us-south.codeengine.appdomain.cloud",
        "https://application-8c.1zvd1ciw0wl5.us-south.codeengine.appdomain.cloud",
    ):
        resp.headers["Access-Control-Allow-Origin"] = origin
        resp.headers["Vary"] = "Origin"
    resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    resp.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-User-Name"
    return resp

@app.route("/api/<path:_>", methods=["OPTIONS"])
def cors_preflight(_):
    return ("", 204)

# -----------------------
# Defaults (tu ejercicio)
# -----------------------
DEFAULT_CONTEXT = """Guillermo Treister es Latin America Watson AI Apps Executive en IBM. Es Ingeniero Civil en Informática (U. de Chile) y tiene un Diploma en Gestión de Negocios (U. Adolfo Ibáñez). Su trabajo pone énfasis en IA ética y en el marco Trustworthy AI de IBM (trazabilidad, explicabilidad y gobernanza). Ha colaborado —desde su rol en IBM— con el Ministerio de Ciencia en instancias vinculadas al Plan Nacional de Inteligencia Artificial para promover buenas prácticas y una implantación responsable de la IA en Chile. Nota de desambiguación: esta colaboración no implica que Treister sea funcionario público ni que “trabaje en el Ministerio”. Además, destaca que la IA Generativa es disruptiva por la velocidad y la coherencia con que permite crear contenido, acercándola a audiencias no expertas y a casos de negocio.
"""

DEFAULT_LINKS = [
    "https://txsplus.com/2022/06/guillermo-treister-latin-america-watson-ai-apps-executive-de-ibm-entrega-las-claves-sobre-la-importancia-de-la-ia-etica/",
    "https://itbuilderslive.com/2023/personas/guillermo-treister/",
    "https://latam.tivit.com/prensa/descubriendo-su-potencial-en-el-mundo-de-los-negocios"
]

DEFAULT_QUIZ = [
    {
        "question": "En su rol en IBM, ¿con qué organismo ha colaborado Guillermo Treister en el marco del Plan Nacional de IA en Chile? (Evita confundir colaboración con empleo público.)",
        "ideal_answer": "Ha colaborado —desde IBM— con el Ministerio de Ciencia en instancias del Plan Nacional de Inteligencia Artificial, dentro de un enfoque de IA ética/Trustworthy AI."
    }
]


# -----------------------
# Db2 REST — configurado “como la CMD”
# -----------------------
# Si quieres volver a .env, reemplaza estas 4 constantes por os.getenv(...)
DB2_REST_BASE     = os.getenv("DB2_REST_BASE", "https://api.db2.cloud.ibm.com/v5/ibm")
DB2_DEPLOYMENT_ID = os.getenv("DB2_DEPLOYMENT_ID")
DB2_UID           = os.getenv("DB2_UID")
DB2_PWD           = os.getenv("DB2_PWD")
DB2_DB            = os.getenv("DB2_DB", "bludb")
# schema/tabla EXACTOS (con comillas) como en tu prueba
DB2_SCHEMA = DB2_UID.upper()                 # -> VNV00798
TABLE_NAME = "GOVERNANCE_RESULTS"
TABLE_QNAME = f"\"{DB2_SCHEMA}\".\"{TABLE_NAME}\""   # -> "VNV00798"."GOVERNANCE_RESULTS"

def _rest_headers(token: str | None = None):
    h = {"Content-Type": "application/json", "X-Deployment-Id": DB2_DEPLOYMENT_ID}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h
def _dbapi_base() -> str:
    """Lee DB2_DBAPI_BASE del .env (p.ej. https://bpe61bfd0365e9u4psdglite.db2.cloud.ibm.com/dbapi/v4)."""
    b = os.getenv("DB2_DBAPI_BASE")
    if not b:
        raise RuntimeError("DB2_DBAPI_BASE no definido en .env (debe terminar en /dbapi/v4)")
    return b.rstrip("/")

def _db2_rest_token() -> str:
    url = f"{_dbapi_base()}/auth/tokens"
    r = requests.post(url, headers=_rest_headers(),
                      json={"userid": DB2_UID, "password": DB2_PWD}, timeout=30)
    if r.status_code >= 300:
        raise RuntimeError(f"Error auth REST Db2: {r.status_code} {r.text}")
    data = r.json() if r.text else {}
    tok = data.get("token") or data.get("id_token")
    if not tok:
        raise RuntimeError(f"Auth sin token: {data}")
    return tok


def _db2_sql_job(token: str, commands: str, *, limit: int = 1000, stop_on_error: str = "yes") -> str:
    r = requests.post(
        f"{_dbapi_base()}/sql_jobs",
        headers=_rest_headers(token),
        json={"commands": commands, "limit": limit, "separator": ";", "stop_on_error": stop_on_error},
        timeout=60,
    )
    if r.status_code >= 300:
        raise RuntimeError(f"Error creando SQL job: {r.status_code} {r.text}")
    job_id = (r.json() or {}).get("id")
    if not job_id:
        raise RuntimeError(f"Respuesta sin id de job: {r.text}")
    return job_id


def _db2_sql_fetch(token: str, job_id: str, timeout_sec: int = 30) -> dict:
    url = f"{_dbapi_base()}/sql_jobs/{job_id}"
    t0 = time.time()
    while True:
        r = requests.get(url, headers=_rest_headers(token), timeout=30)
        if r.status_code >= 300:
            raise RuntimeError(f"Error consultando SQL job: {r.status_code} {r.text}")
        data = r.json() if r.text else {}
        status = (data.get("status") or data.get("state") or "").lower()
        if status in ("completed", "succeeded", "completed successfully"):
            return data
        if status in ("failed", "error"):
            return data
        if time.time() - t0 > timeout_sec:
            return data
        time.sleep(0.8)


def _ensure_results_table(token: str):
    check_sql = f"""
        SELECT 1
        FROM SYSCAT.TABLES
        WHERE TABSCHEMA = '{DB2_SCHEMA}' AND TABNAME = '{TABLE_NAME}'
        FETCH FIRST 1 ROW ONLY
    """
    job_id = _db2_sql_job(token, check_sql)
    info = _db2_sql_fetch(token, job_id)
    rows = (((info.get("results") or [{}])[0]).get("rows")) or []
    if rows:
        return  # ya existe

    create_sql = f"""
        CREATE TABLE {TABLE_QNAME} (
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
    job_id = _db2_sql_job(token, create_sql)
    _db2_sql_fetch(token, job_id)

def _sql_escape(s: str) -> str:
    return (s or "").replace("'", "''")

def _pct100(x):
    try:
        return round(float(x) * 100.0, 2)
    except Exception:
        return None

# -----------------------
# Endpoints
# -----------------------
@app.get("/health")
def health():
    return {"ok": True}

# ---------------- Helper para limpiar la alerta ----------------
def clean_alert_text(text: str, max_lines: int = 2, max_chars: int = 240) -> str:
    """
    Limpia salidas del modelo para dejar solo la alerta breve:
    - quita fences ```...```
    - quita prefijos tipo 'Alerta:' o repeticiones de la instrucción
    - conserva 1-2 líneas, tope de caracteres
    """
    s = str(text or "").strip()

    # elimina fences ```...``` (con o sin json)
    s = re.sub(r"^```(?:json)?\s*|\s*```$", "", s, flags=re.I | re.M)

    # elimina líneas que parecen ser la instrucción
    s = re.sub(r"(?i)eres un asistente.*?(?=\n|$)", "", s).strip()

    # quita prefijos como "Alerta:" / "Advertencia:" / "Atención:"
    s = re.sub(r"(?i)^(alerta|advertencia|atención)\s*:\s*", "", s).strip()

    # colapsa espacios
    s = re.sub(r"\s+", " ", s).strip()

    # corta por líneas (mantén 1-2)
    lines = [ln.strip() for ln in re.split(r"[\r\n]+", s) if ln.strip()]
    s = " ".join(lines[:max_lines]).strip()

    # limita por caracteres
    if len(s) > max_chars:
        s = s[:max_chars].rstrip() + "…"

    return s


# ---------------- Endpoint principal ----------------
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
    system_prompt = data.get("system_prompt") or (
        "Eres un asistente útil y seguro. Responde con precisión y sin divulgar datos sensibles."
    )
    normalize = bool(data.get("normalize_answers", True))

    # 1) Métricas de governance (incluye las 4 de calidad + otras)
    metrics_rows = evaluate_governance(
        quiz, answers, context, system_prompt, normalize_answers=normalize
    )

    # 2) Modelo de watsonx.ai (para corrección + alertas)
    model, err = build_wxa_model()

    results = []
    for i, q in enumerate(quiz):
        # base: fila con métricas de governance calculadas por pregunta
        row = metrics_rows[i] if i < len(metrics_rows) else {}
        ans = answers[i] if i < len(answers) else ""

        # 2.a) HAP/PII (detecciones auxiliares)
        try:
            flags = hap_pii_detect(ans)
            if isinstance(flags, dict):
                row.update(flags)
        except Exception:
            # no romper si el detector falla
            pass

        # 2.b) Governance "extra" sobre el texto libre (excluyendo 4 métricas de calidad)
        try:
            g_scores = evaluate_governance_text(ans) or {}
            EXCLUDE = {"answer_similarity", "answer_relevance", "faithfulness", "context_relevance"}
            flagged = {
                k: float(v)
                for k, v in g_scores.items()
                if k not in EXCLUDE and isinstance(v, (int, float)) and float(v) > 0.0
            }

            if flagged:
                # Si hay activaciones, pedimos a wx.ai una alerta breve y clara para el usuario
                alert_txt = None
                try:
                    if model is not None and not err:
                        probs = ", ".join(
                            f"{k.replace('_', ' ')}: {(v*100):.1f}%"
                            for k, v in sorted(flagged.items(), key=lambda x: -x[1])
                        )
                        prompt_alert = (
                            "Eres un asistente de cumplimiento y seguridad.\n"
                            "Dado el siguiente análisis de riesgo por métricas (0-100%), redacta UNA alerta breve "
                            "(máximo 2 líneas) en español, clara y empática, recomendando prudencia. No incluyas nada más.\n\n"
                            f"Métricas activadas: {probs}\n"
                            f"Texto del usuario: '''{ans}'''"
                        )
                        raw = model.generate_text(prompt=prompt_alert)
                        alert_txt = clean_alert_text(raw)  # <-- limpieza para no mostrar la instrucción
                    else:
                        # Fallback si no hay modelo
                        top = sorted(flagged.items(), key=lambda x: -x[1])[:3]
                        probs = ", ".join(f"{k.replace('_',' ')} {(v*100):.0f}%" for k, v in top)
                        alert_txt = (
                            f"⚠️ Cuidado: se detecta riesgo en {probs}. "
                            "Revisa antes de enviar información sensible o dañina."
                        )
                except Exception:
                    # Fallback por cualquier error del generador
                    top = sorted(flagged.items(), key=lambda x: -x[1])[:3]
                    probs = ", ".join(f"{k.replace('_',' ')} {(v*100):.0f}%" for k, v in top)
                    alert_txt = (
                        f"⚠️ Cuidado: se detecta riesgo en {probs}. "
                        "Revisa antes de enviar."
                    )

                row.update({
                    "gov_flags": flagged,   # dict {metric: 0..1}
                    "gov_alert": alert_txt  # string
                })
        except Exception:
            # no interrumpir el flujo si governance-text falla
            pass

        # 2.c) Corrección / veredicto con watsonx.ai
        if err:
            row.update({
                "wx_verdict": None,
                "wx_explanation": None,
                "wx_improved_answer": None,
                "wx_raw": err
            })
        else:
            try:
                corr = correct_answer(
                    model,
                    q.get("question", ""),
                    ans,
                    context,
                    system_prompt
                )
                if isinstance(corr, dict):
                    row.update(corr)
            except Exception as _e:
                # incluir información mínima si hubiera fallo
                row.setdefault("wx_raw", str(_e))
            anti_burst_sleep()

        results.append(row)

    return jsonify({"results": results})








@app.get("/api/default_exercise")
def default_exercise():
    return jsonify({"topic": "Guillermo Treister", "objective": DEFAULT_CONTEXT, "used_sources": DEFAULT_LINKS, "quiz": DEFAULT_QUIZ})

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
    Espera: { "results": [ { "wx_verdict": "...", "answer_similarity": 0..1, "answer_relevance": 0..1,
                              "faithfulness": 0..1, "context_relevance": 0..1 }, ... ] }
    Nombre hardcodeado para validar: "malcom".
    """
    data = request.get_json(force=True) or {}
    results = data.get("results") or []
    nombre = (data.get("name") or request.headers.get("X-User-Name") or "Anon").strip()[:128]

    try:
        token = _db2_rest_token()
        _ensure_results_table(token)

        inserts = []
        for idx, r in enumerate(results, start=1):
            veredicto = (r.get("wx_verdict") or "")[:16]
            a = _pct100(r.get("answer_similarity"))
            b = _pct100(r.get("answer_relevance"))
            c = _pct100(r.get("faithfulness"))
            d = _pct100(r.get("context_relevance"))
            sql = (
                f"INSERT INTO {TABLE_QNAME} "
                "(NOMBRE, FECHA, PREGUNTA, VEREDICTO, ANSWER_SIMILARITY, ANSWER_RELEVANCE, FAITHFULNESS, CONTEXT_RELEVANCE) "
                f"VALUES ('{_sql_escape(nombre)}', CURRENT DATE, {idx}, "
                f"'{_sql_escape(veredicto)}', "
                f"{'NULL' if a is None else a:.2f} , "
                f"{'NULL' if b is None else b:.2f} , "
                f"{'NULL' if c is None else c:.2f} , "
                f"{'NULL' if d is None else d:.2f})"
            )
            inserts.append(sql)

        if inserts:
            job_id = _db2_sql_job(token, ";\n".join(inserts), stop_on_error="no")
            _db2_sql_fetch(token, job_id, timeout_sec=45)

        return jsonify({"ok": True, "inserted": len(inserts)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ====== Helpers para /api/results ======


def _parse_date_any(d: str | None) -> str | None:
    """Acepta YYYY-MM-DD o DD-MM-YYYY (o con /). Devuelve YYYY-MM-DD o None."""
    if not d:
        return None
    d = d.strip()
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"):
        try:
            return datetime.datetime.strptime(d, fmt).date().isoformat()
        except Exception:
            pass
    return None

def _int_or_default(v, d, lo=1, hi=1000):
    try:
        x = int(v)
        return max(lo, min(hi, x))
    except Exception:
        return d

# ====== /api/results (JSON) ======
@app.get("/api/results")
def get_results():
    viewer = (request.headers.get("X-User-Name") or "").strip().lower()
    is_owner = (viewer == "malcom")

    # 1) parseo normal
    name  = (request.args.get("name") or "").strip()
    dfrom = _parse_date_any(request.args.get("from"))
    dto   = _parse_date_any(request.args.get("to"))
    limit = _int_or_default(request.args.get("limit"), 100, 1, 500)

    # 2) si NO es malcom, forzar restricciones
    if not is_owner:
        if not viewer:
            return jsonify({"ok": False, "error": "nombre requerido"}), 400
        name = viewer
        hoy = datetime.date.today().isoformat()
        dfrom = hoy
        dto   = hoy
        limit = min(max(int(limit or 100), 1), 200)


    """
    Query params:
      - name: filtrar por NOMBRE (exacto)
      - from: fecha desde
      - to:   fecha hasta
      - limit: filas (1..500, default 100)
    """
    try:
        name  = (request.args.get("name") or "").strip()
        dfrom = _parse_date_any(request.args.get("from"))
        dto   = _parse_date_any(request.args.get("to"))
        limit = _int_or_default(request.args.get("limit"), 100, 1, 500)

        where = []
        if name:
            where.append(f"NOMBRE = '{_sql_escape(name[:128])}'")
        if dfrom:
            where.append(f"FECHA >= DATE '{dfrom}'")
        if dto:
            where.append(f"FECHA <= DATE '{dto}'")
        where_sql = ("WHERE " + " AND ".join(where)) if where else ""

        sql = f"""
            SELECT
              ID,
              NOMBRE,
              VARCHAR_FORMAT(FECHA, 'YYYY-MM-DD') AS FECHA,
              PREGUNTA,
              VEREDICTO,
              ANSWER_SIMILARITY,
              ANSWER_RELEVANCE,
              FAITHFULNESS,
              CONTEXT_RELEVANCE
            FROM {TABLE_QNAME}
            {where_sql}
            ORDER BY ID DESC
            FETCH FIRST {limit} ROWS ONLY
        """

        token  = _db2_rest_token()
        job_id = _db2_sql_job(token, sql, limit=limit)
        info   = _db2_sql_fetch(token, job_id, timeout_sec=30)

        res0 = (info.get("results") or [{}])[0]
        cols = res0.get("columns") or []
        rows = res0.get("rows") or []
        out  = [dict(zip(cols, r)) for r in rows]

        return jsonify({"ok": True, "rows": out, "count": len(out)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

# ====== /api/results.csv (CSV) ======
@app.get("/api/results.csv")
def get_results_csv():

    data = request.get_json(force=True) or {}
    results = data.get("results") or []
    nombre = (data.get("name") or request.headers.get("X-User-Name") or "Anon").strip()[:128]

    viewer = (request.headers.get("X-User-Name") or "").strip().lower()
    is_owner = (viewer == "malcom")

    # Si NO es malcom, forzar restricciones
    if not is_owner:
        # name = el propio viewer (obligatorio)
        if not name:
            name = viewer
        if not name:
            return jsonify({"ok": False, "error": "nombre requerido"}), 400

        # forzar hoy
        hoy = datetime.date.today().isoformat()
        dfrom = hoy
        dto   = hoy

        # límite razonable (opcional)
        try:
            limit = min(max(int(limit or 100), 1), 200)
        except Exception:
            limit = 100



    """Mismos filtros que /api/results pero devuelve CSV descargable."""
    try:
        name  = (request.args.get("name") or "").strip()
        dfrom = _parse_date_any(request.args.get("from"))
        dto   = _parse_date_any(request.args.get("to"))
        limit = _int_or_default(request.args.get("limit"), 100, 1, 500)

        where = []
        if name:
            where.append(f"NOMBRE = '{_sql_escape(name[:128])}'")
        if dfrom:
            where.append(f"FECHA >= DATE '{dfrom}'")
        if dto:
            where.append(f"FECHA <= DATE '{dto}'")
        where_sql = ("WHERE " + " AND ".join(where)) if where else ""

        sql = f"""
            SELECT
              ID,
              NOMBRE,
              VARCHAR_FORMAT(FECHA, 'YYYY-MM-DD') AS FECHA,
              PREGUNTA,
              VEREDICTO,
              ANSWER_SIMILARITY,
              ANSWER_RELEVANCE,
              FAITHFULNESS,
              CONTEXT_RELEVANCE
            FROM {TABLE_QNAME}
            {where_sql}
            ORDER BY ID DESC
            FETCH FIRST {limit} ROWS ONLY
        """

        token  = _db2_rest_token()
        job_id = _db2_sql_job(token, sql, limit=limit)
        info   = _db2_sql_fetch(token, job_id, timeout_sec=30)

        res0 = (info.get("results") or [{}])[0]
        cols = res0.get("columns") or []
        rows = res0.get("rows") or []

        buf = io.StringIO()
        w   = csv.writer(buf)
        w.writerow(cols or ["ID","NOMBRE","FECHA","PREGUNTA","VEREDICTO",
                            "ANSWER_SIMILARITY","ANSWER_RELEVANCE","FAITHFULNESS","CONTEXT_RELEVANCE"])
        for r in rows:
            w.writerow(r)

        return Response(
            buf.getvalue(),
            mimetype="text/csv; charset=utf-8",
            headers={"Content-Disposition": "attachment; filename=resultados.csv"},
        )
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500














# -----------------------
# Main
# -----------------------
if __name__ == "__main__":
    port = int(os.getenv("PORT", "8080"))
    app.run(host="0.0.0.0", port=port, debug=True)
