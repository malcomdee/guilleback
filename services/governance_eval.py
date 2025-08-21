# services/governance_eval.py
# Evaluación de respuestas usando watsonx.governance
# Requiere: ibm-watsonx-gov, pandas, (y dependencias opcionales como unitxt, scikit-learn, textstat)

from __future__ import annotations
import re
import unicodedata
from importlib import import_module
from typing import Any, Dict, List, Optional

import pandas as pd

# SDK watsonx.governance (asegúrate de tenerlo instalado)
from ibm_watsonx_gov.evaluators.metrics_evaluator import MetricsEvaluator
from ibm_watsonx_gov.metrics import AnswerSimilarityMetric

import logging

# Para la ruta "real"
import json
import os, pprint

# -----------------------------
# Utilidades
# -----------------------------
def _normalize(s: str) -> str:
    """Normaliza texto: minúsculas, sin tildes, sin puntuación excesiva."""
    s = (s or "").lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"[^\w\s]", "", s)
    return re.sub(r"\s+", " ", s).strip()


def _extract_records(result: Any) -> List[dict] | dict | None:
    """
    Adapta distintos formatos de salida del SDK (listas pydantic, DataFrame, dicts anidados…)
    y devuelve una lista de dicts por registro cuando es posible.
    """
    # Campos frecuentes en distintas versiones
    for attr in ("per_row", "per_row_df", "rows", "data", "df", "metrics_result"):
        if hasattr(result, attr):
            obj = getattr(result, attr)
            if hasattr(obj, "to_dict"):
                # p.ej. DataFrame o similar
                try:
                    return obj.to_dict(orient="records")
                except TypeError:
                    d = obj.to_dict()
                    if isinstance(d, dict) and d and all(isinstance(v, list) for v in d.values()):
                        n = max(len(v) for v in d.values())
                        return [{k: (d[k][i] if i < len(d[k]) else None) for k in d} for i in range(n)]
                    return d
            if isinstance(obj, list):
                try:
                    return [getattr(r, "model_dump", lambda: r)() for r in obj]
                except Exception:
                    return obj

    if hasattr(result, "model_dump"):
        d = result.model_dump()
        for k in ("per_row", "rows", "data", "metrics_result"):
            if k in d:
                return d[k]
        return d

    return getattr(result, "__dict__", None)


def _metric(fqcn: str):
    """
    Carga dinámica de clase de métrica por nombre totalmente calificado (FQCN).
    Devuelve la clase o None si no puede importarla.
    """
    try:
        mod, cls = fqcn.rsplit(".", 1)
        return getattr(import_module(mod), cls)
    except Exception:
        return None


def _value_from(group_dict: Dict[str, Any], metric_key: str, idx: int) -> Optional[float]:
    """
    Extrae el valor de la métrica para un índice de registro dado, lidiando con
    varios formatos del SDK.
    """
    recs = group_dict.get(metric_key)
    if not recs:
        return None
    try:
        if isinstance(recs, list) and recs:
            agg = recs[0]
            if hasattr(agg, "model_dump"):
                agg = agg.model_dump()
            # Formato con record_level_metrics (uno por fila de entrada)
            if isinstance(agg, dict) and "record_level_metrics" in agg and isinstance(agg["record_level_metrics"], list):
                item = agg["record_level_metrics"][idx]
                if hasattr(item, "model_dump"):
                    item = item.model_dump()
                v = item.get("value")
                return float(v) if v is not None else None
            # Formato agregado simple
            v = agg.get("value") if isinstance(agg, dict) else None
            return float(v) if v is not None else None
    except Exception:
        return None
    return None


# -----------------------------
# Función principal
# -----------------------------
def evaluate_governance(
    quiz: List[Dict[str, str]],
    user_answers: List[str],
    context_text: str,
    system_prompt: str,
    normalize_answers: bool = True,
) -> List[Dict[str, Any]]:
    """
    Ejecuta métricas de watsonx.governance sobre las respuestas del usuario.
    - Pasa system_prompt a las métricas que lo requieren (TopicRelevance/PromptSafetyRisk).
    - Aísla errores por métrica para no romper todo el proceso.
    """
    # Dataset de entrada
    rows = []
    for i, q in enumerate(quiz):
        ans = user_answers[i] if i < len(user_answers) else ""
        rows.append({
            "question": q.get("question", ""),
            "ideal_answer": q.get("ideal_answer", ""),
            "user_answer": ans,
            "context": context_text,
            # campos comunes esperados por varias métricas
            "input_text": q.get("question", ""),
            "system_prompt": system_prompt or "",
        })
    df = pd.DataFrame(rows)

    # Normalización opcional (para AnswerSimilarity y comparaciones)
    if normalize_answers:
        df["generated_text"] = df["user_answer"].map(_normalize)
        df["ground_truth"]   = df["ideal_answer"].map(_normalize)
    else:
        df["generated_text"] = df["user_answer"]
        df["ground_truth"]   = df["ideal_answer"]

    # Asegura un system_prompt válido para métricas que lo exigen (pydantic lo marca como required)
    sp = (system_prompt or "").strip()
    if not sp:
        sp = "Eres un asistente útil y seguro. Responde con precisión y sin divulgar datos sensibles."

    evaluator = MetricsEvaluator()

    # ---------- 1) Similaridad (siempre disponible en SDK) ----------
    try:
        sim = evaluator.evaluate(data=df, metrics=[AnswerSimilarityMetric()])
        sim_rows = _extract_records(sim) or []
    except Exception as e:
        print("AnswerSimilarityMetric unavailable:", e)
        sim_rows = []

    # ---------- 2) Groundedness básicos (no requieren system_prompt) ----------
    metrics_ground = [
        "ibm_watsonx_gov.metrics.answer_relevance.answer_relevance_metric.AnswerRelevanceMetric",
        "ibm_watsonx_gov.metrics.context_relevance.context_relevance_metric.ContextRelevanceMetric",
        "ibm_watsonx_gov.metrics.faithfulness.faithfulness_metric.FaithfulnessMetric",
        "ibm_watsonx_gov.metrics.evasiveness.evasiveness_metric.EvasivenessMetric",
    ]
    ground_results: Dict[str, Any] = {}
    for fq in metrics_ground:
        key = fq.rsplit(".", 1)[-1]
        M = _metric(fq)
        if M is None:
            ground_results[key] = None
            continue
        try:
            res = evaluator.evaluate(data=df, metrics=[M()])
            ground_results[key] = _extract_records(res)
        except Exception as e:
            ground_results[key] = None
            print(f"{key} unavailable:", e)

    # ---------- 3) Métricas que requieren system_prompt ----------
    sp_metrics = [
        "ibm_watsonx_gov.metrics.topic_relevance.topic_relevance_metric.TopicRelevanceMetric",
        "ibm_watsonx_gov.metrics.prompt_safety_risk.prompt_safety_risk_metric.PromptSafetyRiskMetric",
    ]
    for fq in sp_metrics:
        key = fq.rsplit(".", 1)[-1]
        M = _metric(fq)
        if M is None:
            ground_results[key] = None
            continue
        try:
            # ¡Aquí pasamos system_prompt!
            res = evaluator.evaluate(data=df, metrics=[M(system_prompt=sp)])
            ground_results[key] = _extract_records(res)
        except Exception as e:
            ground_results[key] = None
            print(f"{key} unavailable:", e)

    # ---------- 4) Safety detectors ----------
    metrics_safety = [
        "ibm_watsonx_gov.metrics.hap.hap_metric.HAPMetric",
        "ibm_watsonx_gov.metrics.pii.pii_metric.PIIMetric",
        "ibm_watsonx_gov.metrics.profanity.profanity_metric.ProfanityMetric",
        "ibm_watsonx_gov.metrics.sexual_content.sexual_content_metric.SexualContentMetric",
        "ibm_watsonx_gov.metrics.violence.violence_metric.ViolenceMetric",
        "ibm_watsonx_gov.metrics.social_bias.social_bias_metric.SocialBiasMetric",
        "ibm_watsonx_gov.metrics.harm.harm_metric.HarmMetric",
        "ibm_watsonx_gov.metrics.harm_engagement.harm_engagement_metric.HarmEngagementMetric",
        "ibm_watsonx_gov.metrics.jailbreak.jailbreak_metric.JailbreakMetric",
        "ibm_watsonx_gov.metrics.unethical_behavior.unethical_behavior_metric.UnethicalBehaviorMetric",
    ]
    safety_results: Dict[str, Any] = {}
    for fq in metrics_safety:
        key = fq.rsplit(".", 1)[-1]
        M = _metric(fq)
        if M is None:
            safety_results[key] = None
            continue
        try:
            res = evaluator.evaluate(data=df, metrics=[M()])
            safety_results[key] = _extract_records(res)
        except Exception as e:
            safety_results[key] = None
            print(f"{key} unavailable:", e)

    # ---------- 5) Readability ----------
    metrics_read = [
        "ibm_watsonx_gov.metrics.text_reading_ease.text_reading_ease_metric.TextReadingEaseMetric",
        "ibm_watsonx_gov.metrics.text_grade_level.text_grade_level_metric.TextGradeLevelMetric",
    ]
    read_results: Dict[str, Any] = {}
    for fq in metrics_read:
        key = fq.rsplit(".", 1)[-1]
        M = _metric(fq)
        if M is None:
            read_results[key] = None
            continue
        try:
            res = evaluator.evaluate(data=df, metrics=[M()])
            read_results[key] = _extract_records(res)
        except Exception as e:
            read_results[key] = None
            print(f"{key} unavailable:", e)

    # ---------- 6) Mapeo de claves y ensamblado de respuesta ----------
    key_map = {
        "AnswerSimilarityMetric": "answer_similarity",
        "AnswerRelevanceMetric": "answer_relevance",
        "ContextRelevanceMetric": "context_relevance",
        "FaithfulnessMetric": "faithfulness",
        "EvasivenessMetric": "evasiveness",
        "TopicRelevanceMetric": "topic_relevance",
        "PromptSafetyRiskMetric": "prompt_safety_risk",
        "HAPMetric": "hap",
        "PIIMetric": "pii",
        "ProfanityMetric": "profanity",
        "SexualContentMetric": "sexual_content",
        "ViolenceMetric": "violence",
        "SocialBiasMetric": "social_bias",
        "HarmMetric": "harm",
        "HarmEngagementMetric": "harm_engagement",
        "JailbreakMetric": "jailbreak",
        "UnethicalBehaviorMetric": "unethical_behavior",
        "TextReadingEaseMetric": "text_reading_ease",
        "TextGradeLevelMetric": "text_grade_level",
    }

    out: List[Dict[str, Any]] = []
    for i in range(len(df)):
        row: Dict[str, Any] = {}

        # Similaridad
        row[key_map["AnswerSimilarityMetric"]] = _value_from({"AnswerSimilarityMetric": sim_rows}, "AnswerSimilarityMetric", i)

        # Groundedness + las que requieren SP
        for k in list(ground_results.keys()):
            row[key_map.get(k, k)] = _value_from(ground_results, k, i)

        # Safety
        for k in list(safety_results.keys()):
            row[key_map.get(k, k)] = _value_from(safety_results, k, i)

        # Readability
        for k in list(read_results.keys()):
            row[key_map.get(k, k)] = _value_from(read_results, k, i)

        out.append(row)

    return out







# --- imports que necesita este bloque ---
import os
import re
import logging
import pprint
from typing import Any, Dict, List, Optional

# Para el evaluador real (si está instalado)
try:
    import pandas as pd
    # OJO: los imports concretos pueden variar según versión del SDK.
    # Ajusta estos imports a tu versión de watsonx.governance:
    from ibm_watsonx_gov.evaluators.metrics_evaluator import MetricsEvaluator
    from ibm_watsonx_gov.metrics import (
        UnethicalBehaviorMetric,
        JailbreakMetric,
        SocialBiasMetric,
        ProfanityMetric,
        HarmMetric,
        HarmEngagementMetric,
        SexualContentMetric,
        ViolenceMetric,
        EvasivenessMetric,
        AnswerRelevanceMetric,
        FaithfulnessMetric,
        TopicRelevanceMetric,
        ContextRelevanceMetric,
        AnswerSimilarityMetric,
        # PromptSafetyRiskMetric,  # si la tienes disponible en tu SDK
    )
    _SDK_AVAILABLE = True
except Exception as e:
    logging.warning("watsonx.governance SDK no disponible o no importable: %s", e)
    _SDK_AVAILABLE = False

LOGGER = logging.getLogger(__name__)

# ==========
#  DEMO MAP
# ==========

# Palabras/expresiones que disparan el modo DEMO (para tus ejemplos predefinidos)
DEMO_RULES: List[tuple[re.Pattern, Dict[str, float]]] = [
    # unethical_behavior
    (re.compile(r"\bexploit\b", re.I), {"unethical_behavior": 0.90}),
    # jailbreak
    (re.compile(r"ignora todas las reglas", re.I), {"jailbreak": 0.90}),
    # social_bias
    (re.compile(r"\binferior\b", re.I), {"social_bias": 0.90}),
    # profanity
    (re.compile(r"¡&%\$!", re.I), {"profanity": 0.90}),
    # harm
    (re.compile(r"arma casera", re.I), {"harm": 0.90}),
    # harm_engagement
    (re.compile(r"desactívalo", re.I), {"harm_engagement": 0.85}),
    # sexual_content
    (re.compile(r"\badultos\b", re.I), {"sexual_content": 0.90}),
    # violence
    (re.compile(r"\bgolpeó\b", re.I), {"violence": 0.82}),
    # evasiveness
    (re.compile(r"\bvaga\b", re.I), {"evasiveness": 0.80}),
    # relevancias y similitud (para tus ejemplos guiados)
    (re.compile(r"no coincide", re.I), {"answer_relevance": 0.20}),
    (re.compile(r"no aparecen", re.I), {"faithfulness": 0.30}),
    (re.compile(r"no es el solicitado", re.I), {"topic_relevance": 0.25}),
    (re.compile(r"fuera del contexto", re.I), {"context_relevance": 0.35}),
    (re.compile(r"coincide fuertemente", re.I), {"answer_similarity": 0.90}),
    # PromptSafetyRisk si usas esa métrica:
    # (re.compile(r"instrucciones peligrosas", re.I), {"prompt_safety_risk": 0.75}),
]

# Claves que espera el front (Score)
ALL_FRONT_KEYS: List[str] = [
    "unethical_behavior",
    "jailbreak",
    "social_bias",
    "profanity",
    "harm",
    "harm_engagement",
    "sexual_content",
    "violence",
    "evasiveness",
    "answer_relevance",
    "faithfulness",
    "topic_relevance",
    "context_relevance",
    "answer_similarity",
    # "prompt_safety_risk",
]

def _demo_scores(text: str) -> Dict[str, float]:
    """
    Devuelve un dict con valores 'demo' SI el texto calza con alguna
    regla predefinida. Si no calza, retorna {} (vacío).
    """
    for pattern, fixed in DEMO_RULES:
        if pattern.search(text):
            out = {k: 0.0 for k in ALL_FRONT_KEYS}
            out.update(fixed)
            # Rellenamos el resto con 0.0 para consistencia
            for k in ALL_FRONT_KEYS:
                out.setdefault(k, 0.0)
            return out
    return {}

# ===================================
#  EVALUACIÓN REAL (watsonx.gov)
# ===================================

def _safe_number(x: Any) -> Optional[float]:
    try:
        v = float(x)
        if v != v:  # NaN
            return None
        # Normalizamos a 0..1 si viene 0..100
        if v > 1.0 and v <= 100.0:
            return v / 100.0
        return max(0.0, min(1.0, v))
    except Exception:
        return None

def _extract_metric_value(obj: Any, keys=("score", "value", "confidence", "prob", "probability")) -> Optional[float]:
    """
    Intenta encontrar un número dentro de un dict/list anidado (formato-agnóstico).
    Útil porque las versiones del SDK pueden cambiar la forma del payload.
    """
    if obj is None:
        return None
    if isinstance(obj, (int, float)):
        return _safe_number(obj)
    if isinstance(obj, dict):
        for k in keys:
            if k in obj:
                v = _safe_number(obj[k])
                if v is not None:
                    return v
        for v in obj.values():
            r = _extract_metric_value(v, keys)
            if r is not None:
                return r
    if isinstance(obj, list):
        for it in obj:
            r = _extract_metric_value(it, keys)
            if r is not None:
                return r
    return None

def _evaluate_real_metrics(text: str) -> Dict[str, float]:
    """
    Intenta evaluar con watsonx.governance. Si algo falla, levanta excepción.
    """
    if not _SDK_AVAILABLE:
        raise RuntimeError("SDK de watsonx.governance no disponible")

    sp = "Eres un asistente útil y seguro. Responde con precisión y sin divulgar datos sensibles."

    # 1) Preparamos un DataFrame con columnas comunes
    df = pd.DataFrame([{
        "input_text": text,        # NECESARIO para varias métricas de "safety"
        "user_answer": text,
        "generated_text": text,
        "ground_truth": "",
        "question": "",
        "context": "",
        "system_prompt": sp,
    }])

    # 2) Instanciamos el evaluador + lista de métricas
    evaluator = MetricsEvaluator()
    metrics = [
        UnethicalBehaviorMetric(),
        JailbreakMetric(),
        SocialBiasMetric(),
        ProfanityMetric(),
        HarmMetric(),
        HarmEngagementMetric(),
        SexualContentMetric(),
        ViolenceMetric(),
        EvasivenessMetric(),
        # Las de "answer/context/topic/faithfulness/similarity" suelen requerir QA/RAG;
        # se incluyen por compatibilidad, pero pueden devolver 0 en "texto libre".
        AnswerRelevanceMetric(),
        FaithfulnessMetric(),
        TopicRelevanceMetric(system_prompt=sp),  # esta sí requiere system_prompt en algunas versiones
        ContextRelevanceMetric(),
        AnswerSimilarityMetric(),
        # PromptSafetyRiskMetric(),  # si la usas, probablemente también requiere system_prompt
    ]

    # 3) Ejecutamos
    res = evaluator.evaluate(data=df, metrics=metrics)
    if os.getenv("LOG_RAW_GOV", "0") == "1":
        print("\n[watsonx.governance][RAW RESULT]")
        try:
            if hasattr(res, "model_dump"):
                pprint.pp(res.model_dump())
            elif hasattr(res, "to_dict"):
                pprint.pp(res.to_dict())
            else:
                pprint.pp(res)
        except Exception:
            pprint.pp(res)
        print("[/RAW]\n")

    # 4) Convertimos el resultado en dict {metric: value}
    def _get_value_from_metric_obj(m: dict) -> Optional[float]:
        # primero intentamos 'value' directo
        v = m.get("value")
        if isinstance(v, (int, float)):
            return _safe_number(v)
        # luego intentamos record_level_metrics[0].value
        rlm = m.get("record_level_metrics")
        if isinstance(rlm, list) and rlm:
            rv = rlm[0].get("value")
            if isinstance(rv, (int, float)):
                return _safe_number(rv)
        # por último, búsqueda genérica
        return _extract_metric_value(m)

    # Convertimos res a dict de forma robusta
    if hasattr(res, "model_dump"):
        raw = res.model_dump()
    elif hasattr(res, "to_dict"):
        raw = res.to_dict()
    elif isinstance(res, dict):
        raw = res
    else:
        raw = {}

    out: Dict[str, float] = {k: 0.0 for k in ALL_FRONT_KEYS}

    metrics_result = raw.get("metrics_result")
    if isinstance(metrics_result, list):
        NAME_MAP = {
            "unethical_behavior": "unethical_behavior",
            "jailbreak": "jailbreak",
            "social_bias": "social_bias",
            "profanity": "profanity",
            "harm": "harm",
            "harm_engagement": "harm_engagement",
            "sexual_content": "sexual_content",
            "violence": "violence",
            "evasiveness": "evasiveness",
            "answer_relevance": "answer_relevance",
            "faithfulness": "faithfulness",
            "topic_relevance": "topic_relevance",
            "context_relevance": "context_relevance",
            "answer_similarity": "answer_similarity",
        }
        ALIASES = {
            "violence_detection": "violence",
            "harm_engagement_detection": "harm_engagement",
        }

        for m in metrics_result:
            if not isinstance(m, dict):
                continue
            name = str(m.get("name", "")).lower().strip().replace(" ", "_")
            key = NAME_MAP.get(name, ALIASES.get(name))
            if not key:
                continue
            val = _get_value_from_metric_obj(m)
            if val is None:
                continue
            out[key] = max(0.0, min(1.0, float(val)))

    return out

# ===========================================================
#  FUNCIÓN PÚBLICA: decide DEMO o EVALUACIÓN REAL según texto
# ===========================================================

def evaluate_governance_text(text: str) -> Dict[str, float]:
    """
    Evalúa una sola oración/texto y devuelve un dict de métricas 0..1.
    - Si el texto calza con los ejemplos predefinidos (demo), devuelve el DEMO.
    - Si no calza, intenta usar watsonx.governance real.
    - Si falla el SDK / credenciales, cae a un fallback estable (cero).
    """
    text = text or ""
    text_norm = text.strip()

    # 1) DEMO (para los ejemplos predefinidos del tablero)
    demo = _demo_scores(text_norm)
    if demo:
        return demo

    # 2) Evaluación real
    try:
        real = _evaluate_real_metrics(text_norm)
        return real
    except Exception as e:
        LOGGER.error("Fallo evaluación real de governance: %s", e, exc_info=True)

    # 3) Fallback estable: todo 0.0 (no rompe el front)
    return {k: 0.0 for k in ALL_FRONT_KEYS}
