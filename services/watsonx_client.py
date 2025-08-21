# services/watsonx_client.py
import os
import re
import json
import time
from typing import Optional, Tuple

WXA_URL         = (os.getenv("WXA_URL") or "").strip().rstrip("/")
WXA_PROJECT_ID  = (os.getenv("WXA_PROJECT_ID") or os.getenv("WXA_PROJECTID") or "").strip()
WXA_MODEL       = (os.getenv("WXA_MODEL") or "ibm/granite-3-8b-instruct").strip()
WXG_APIKEY      = (os.getenv("WATSONX_APIKEY") or os.getenv("WATSONX_API_KEY") or "").strip()
WXA_DELAY_MS    = int(os.getenv("WXA_DELAY_MS") or "600")

def build_wxa_model() -> Tuple[Optional[object], Optional[str]]:
    """
    Devuelve (model, error). Si hay error, model=None y error contiene el motivo.
    No usa 'auth_type' (las versiones recientes del SDK no lo aceptan).
    """
    if not (WXA_URL and WXG_APIKEY and WXA_PROJECT_ID):
        return None, "watsonx.ai no configurado (faltan WXA_URL/WATSONX_APIKEY/WXA_PROJECT_ID)"

    try:
        from ibm_watsonx_ai import Credentials
        from ibm_watsonx_ai.foundation_models import ModelInference

        creds = Credentials(url=WXA_URL, api_key=WXG_APIKEY)  # <- sin auth_type
        model = ModelInference(
            model_id=WXA_MODEL,
            credentials=creds,
            project_id=WXA_PROJECT_ID,
            params={
                "decoding_method": "greedy",
                "max_new_tokens": 250,
                "temperature": 0.0,
                "return_options": {"input_text": True},
            },
        )
        return model, None
    except Exception as e:
        return None, f"Error creando modelo watsonx.ai: {e}"

def _extract_last_valid_json(text: str):
    clean = re.sub(r"^```(?:json)?\s*|\s*```$", "", str(text).strip(), flags=re.I | re.M)
    last = None
    for m in re.findall(r"\{[\s\S]*?\}", clean):
        try:
            cand = json.loads(m)
            if isinstance(cand, dict) and {
                "verdict", "explanation", "improved_answer"
            } <= set(cand.keys()):
                last = cand
        except Exception:
            continue
    return last

def correct_answer(model, question: str, user_answer: str, context_text: str, system_prompt: str) -> dict:
    """
    Devuelve dict con:
    wx_verdict, wx_explanation, wx_improved_answer, wx_raw
    """
    if model is None:
        return {
            "wx_verdict": None,
            "wx_explanation": None,
            "wx_improved_answer": None,
            "wx_raw": "watsonx.ai no disponible",
        }

    strict = (
        'Responde ÚNICAMENTE con un objeto JSON válido. Sin texto adicional. '
        'Claves: "verdict" (Correcta|Mejorable|Incorrecta), '
        '"explanation" (breve), '
        '"improved_answer" (una sola oración fiel al contexto).'
    )

    prompt = (
        f"{system_prompt}\n\n{strict}\n\n"
        f'Contexto:\n""" {context_text} """\n\n'
        f"Pregunta: {question}\n"
        f"Respuesta_del_usuario: {user_answer}\n"
        "Evalúa y propone una versión mejorada."
    )

    try:
        raw = model.generate_text(prompt=prompt)
        data = _extract_last_valid_json(raw)
        if not isinstance(data, dict):
            return {
                "wx_verdict": None,
                "wx_explanation": None,
                "wx_improved_answer": None,
                "wx_raw": str(raw),
            }
        return {
            "wx_verdict": data.get("verdict"),
            "wx_explanation": data.get("explanation"),
            "wx_improved_answer": data.get("improved_answer"),
            "wx_raw": str(raw),
        }
    except Exception as e:
        return {
            "wx_verdict": None,
            "wx_explanation": None,
            "wx_improved_answer": None,
            "wx_raw": f"Error watsonx.ai: {e}",
        }

def hap_pii_detect(_: str) -> dict:
    # Si luego quieres mover el detect REST aquí, implementa y devuelve flags reales.
    return {}

def anti_burst_sleep():
    time.sleep(max(0, WXA_DELAY_MS) / 1000.0)
