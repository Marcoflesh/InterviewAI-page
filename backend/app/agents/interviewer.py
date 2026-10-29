from typing import Any, Dict
import httpx
from app.config import settings
from app.agents.state import InterviewGraphState


def generate_followup_question_node(state: InterviewGraphState) -> Dict[str, Any]:
    """
    Nodo del Agente Entrevistador para profundización adaptativa (solo se activa si
    allow_followups=True y la puntuación en Acción o Resultado fue menor al umbral).
    """
    eval_res = state.get("evaluation_result", {})
    low_action = eval_res.get("star_action", 3) < settings.FOLLOWUP_STAR_THRESHOLD
    focus = (
        "las acciones técnicas específicas que tú ejecutaste personalmente"
        if low_action
        else "el resultado cuantitativo o impacto medible (porcentajes, tiempos o métricas)"
    )

    prompt = (
        f"Genera una sola pregunta breve y amable en español para pedir al candidato que profundice en {focus} "
        f"respecto a su respuesta anterior: '{state.get('candidate_response')[:300]}'. "
        "No incluyas saludos largos ni etiquetas."
    )

    followup_text = f"Para complementar este punto, ¿podrías detallar {focus} que obtuviste en esa situación?"
    try:
        with httpx.Client(timeout=1.8) as client:
            resp = client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3},
                },
            )
            if resp.status_code == 200:
                generated = resp.json().get("response", "").strip()
                if len(generated) > 15:
                    followup_text = generated
    except Exception:
        pass

    return {
        "session_state": "profundizar_pregunta",
        "next_interviewer_message": followup_text,
    }


def advance_to_next_topic_node(state: InterviewGraphState) -> Dict[str, Any]:
    """
    Nodo del Agente Entrevistador que avanza directamente a la siguiente pregunta
    aleatoria preseleccionada del banco de preguntas de la carrera del candidato,
    evitando preguntas de seguimiento innecesarias.
    """
    next_q = state.get("next_question_bank_text") or (
        "Cuéntame sobre otro proyecto clave de tu carrera en el que hayas resuelto un problema complejo y cómo mediste el resultado."
    )
    return {
        "session_state": "pasar_a_siguiente_tema",
        "next_interviewer_message": next_q,
    }


def finalize_interview_node(state: InterviewGraphState) -> Dict[str, Any]:
    """
    Nodo terminal del grafo cuando se completan las preguntas de la sesión.
    """
    return {
        "session_state": "finalizar_entrevista",
        "next_interviewer_message": (
            "Has completado todas las preguntas de la entrevista. "
            "Enseguida puedes consultar tu reporte final y plan de acción."
        ),
    }
