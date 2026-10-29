import json
import time
from typing import Any, Dict
import httpx
from app.config import settings
from app.agents.state import InterviewGraphState

EVALUATOR_SYSTEM_PROMPT = """Eres el Agente Evaluador (LLM-as-a-Judge) de InterviewAI.
Evalúa la respuesta del candidato de forma objetiva, libre de sesgos demográficos o regionales, calificando de 1 a 5 cada dimensión:
- star_situation (1 a 5): Claridad del contexto o situación inicial.
- star_task (1 a 5): Definición de la responsabilidad u objetivo concreto.
- star_action (1 a 5): Precisión de las acciones individuales ejecutadas por el candidato.
- star_result (1 a 5): Impacto logrado y uso de métricas cuantitativas verificables.
- technical_clarity (1 a 5): Rigor y claridad conceptual para la carrera y puesto objetivo.
- relevance (1 a 5): Alineación directa con la pregunta planteada y el rol.

Devuelve ÚNICAMENTE un objeto JSON válido con estas llaves exactas:
{
  "star_situation": int,
  "star_task": int,
  "star_action": int,
  "star_result": int,
  "technical_clarity": int,
  "relevance": int,
  "strengths": "string breve y directo",
  "improvement_areas": "string breve y accionable"
}"""


def _heuristic_star_fallback(response_text: str, aux: Dict[str, Any]) -> Dict[str, Any]:
    """
    Evaluación determinista de respaldo en caso de que el contenedor local de Ollama
    aún esté descargando el modelo o exceda el umbral de tiempo de respuesta.
    """
    word_count = int(aux.get("response_word_count", 0))
    metrics_count = int(aux.get("quantitative_metrics_count", 0))
    lower = response_text.lower()

    has_situation = any(w in lower for w in ["proyecto", "cuando", "en mi", "durante", "equipo", "contexto", "empresa", "semestre"])
    has_task = any(w in lower for w in ["objetivo", "meta", "encarg", "responsab", "debía", "tenía que", "reto", "problema"])
    has_action = any(w in lower for w in ["implement", "diseñ", "program", "analic", "constru", "desarroll", "optimic", "configur", "propuse", "realic"])

    s_score = min(5, max(2, (3 if has_situation else 2) + (1 if word_count >= 35 else 0) + (1 if word_count >= 65 else 0)))
    t_score = min(5, max(2, (3 if has_task else 2) + (1 if word_count >= 40 else 0) + (1 if word_count >= 70 else 0)))
    a_score = min(5, max(2, (3 if has_action else 2) + (1 if word_count >= 45 else 0) + (1 if word_count >= 75 else 0)))
    r_score = min(5, max(1, 2 + min(3, metrics_count)))
    tech_score = min(5, max(2, round((a_score + r_score) / 2)))
    rel_score = min(5, max(3, round((s_score + t_score + a_score) / 3)))

    strengths = (
        "Buena estructuración de acciones e inclusión de métricas cuantificables."
        if metrics_count > 0
        else "Exposición clara del contexto y de las actividades realizadas en el proyecto."
    )
    improvements = (
        "Profundizar en los detalles técnicos de implementación y contrastar alternativas evaluadas."
        if metrics_count > 0
        else "Cuantificar el resultado final con porcentajes, tiempos ahorrados o indicadores de impacto."
    )

    return {
        "star_situation": s_score,
        "star_task": t_score,
        "star_action": a_score,
        "star_result": r_score,
        "technical_clarity": tech_score,
        "relevance": rel_score,
        "strengths": strengths,
        "improvement_areas": improvements,
    }


def evaluate_candidate_turn_node(state: InterviewGraphState) -> Dict[str, Any]:
    """
    Nodo del Agente Evaluador en LangGraph.
    Invoca a Ollama con salida estructurada JSON y aplica reintento/fallback seguro.
    """
    start_ts = time.perf_counter()
    aux = state.get("auxiliary_features", {})
    user_prompt = (
        f"Carrera: {state.get('career_code')}\n"
        f"Puesto Objetivo: {state.get('target_role')} ({state.get('seniority_level')})\n"
        f"Pregunta Actual: {state.get('current_question_text')}\n"
        f"Respuesta del Candidato: {state.get('candidate_response')}\n"
        f"Metadatos Auxiliares Regex: {json.dumps(aux, ensure_ascii=False)}\n"
    )

    eval_data = None
    json_valid = True

    for attempt in range(2):
        try:
            with httpx.Client(timeout=2.2) as client:
                resp = client.post(
                    f"{settings.OLLAMA_BASE_URL}/api/chat",
                    json={
                        "model": settings.OLLAMA_MODEL,
                        "messages": [
                            {"role": "system", "content": EVALUATOR_SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "format": "json",
                        "stream": False,
                        "options": {"temperature": 0.1},
                    },
                )
                if resp.status_code == 200:
                    raw_content = resp.json().get("message", {}).get("content", "{}")
                    parsed = json.loads(raw_content)
                    required = {
                        "star_situation",
                        "star_task",
                        "star_action",
                        "star_result",
                        "technical_clarity",
                        "relevance",
                        "strengths",
                        "improvement_areas",
                    }
                    if required.issubset(parsed.keys()):
                        eval_data = {
                            "star_situation": max(1, min(5, int(parsed["star_situation"]))),
                            "star_task": max(1, min(5, int(parsed["star_task"]))),
                            "star_action": max(1, min(5, int(parsed["star_action"]))),
                            "star_result": max(1, min(5, int(parsed["star_result"]))),
                            "technical_clarity": max(1, min(5, int(parsed["technical_clarity"]))),
                            "relevance": max(1, min(5, int(parsed["relevance"]))),
                            "strengths": str(parsed["strengths"]),
                            "improvement_areas": str(parsed["improvement_areas"]),
                        }
                        break
        except Exception:
            json_valid = attempt == 0
            continue

    if eval_data is None:
        eval_data = _heuristic_star_fallback(state.get("candidate_response", ""), aux)

    avg_score = round(
        (
            eval_data["star_situation"]
            + eval_data["star_task"]
            + eval_data["star_action"]
            + eval_data["star_result"]
            + eval_data["technical_clarity"]
            + eval_data["relevance"]
        )
        / 6.0,
        2,
    )
    eval_data["turn_average_score"] = avg_score
    latency_ms = int((time.perf_counter() - start_ts) * 1000)

    return {
        "evaluation_result": eval_data,
        "evaluation_latency_ms": latency_ms,
        "json_format_valid": json_valid,
    }
