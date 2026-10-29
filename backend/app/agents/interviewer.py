from typing import Any, Dict
import httpx
from app.config import settings
from app.agents.state import InterviewGraphState


def contextualize_question_with_vacancy(
    base_question: str,
    target_role: str,
    vacancy_context: str,
    cv_summary: str,
) -> str:
    """
    Adapta la pregunta seleccionada del banco de la carrera al 'Contexto de la vacante'
    y al puesto objetivo del usuario utilizando el Agente Entrevistador (`gpt-4o-mini`
    o `gemini-3.8-flash` configurados en `.env`), o aplica contextualización determinista.
    """
    if not vacancy_context or len(vacancy_context.strip()) < 10:
        return base_question

    prompt = (
        f"Eres un entrevistador técnico crítico y directo para el puesto de '{target_role}'.\n"
        f"Contexto de la vacante: {vacancy_context[:350]}\n"
        f"Perfil del candidato: {cv_summary[:250]}\n"
        f"Pregunta base: {base_question}\n"
        "Adapta ligeramente la pregunta base en un solo párrafo directo (máximo 350 caracteres) "
        "para vincularla específicamente con el contexto de la vacante y el puesto objetivo, "
        "sin agregar saludos ni explicaciones adicionales."
    )

    # =========================================================================
    # >>> AGENTE ENTREVISTADOR CON GPT-4o MINI (OPENAI_API_KEY EN .env) <<<
    # =========================================================================
    if (
        settings.OPENAI_API_KEY
        and not settings.OPENAI_API_KEY.startswith("PON_AQUI")
    ):
        try:
            with httpx.Client(timeout=3.5) as client:
                resp = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                    json={
                        "model": settings.OPENAI_CHAT_MODEL or "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 160,
                    },
                )
                if resp.status_code == 200:
                    text = resp.json()["choices"][0]["message"]["content"].strip()
                    if len(text) > 25:
                        return text
        except Exception:
            pass

    # =========================================================================
    # >>> AGENTE ENTREVISTADOR CON GEMINI 3.8 FLASH (GEMINI_API_KEY EN .env) <<<
    # =========================================================================
    if (
        settings.GEMINI_API_KEY
        and not settings.GEMINI_API_KEY.startswith("PON_AQUI")
    ):
        for mdl in [settings.GEMINI_MODEL or "gemini-3.8-flash", "gemini-2.5-flash"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={settings.GEMINI_API_KEY}"
                with httpx.Client(timeout=3.5) as client:
                    resp = client.post(
                        url,
                        json={"contents": [{"parts": [{"text": prompt}]}]},
                    )
                    if resp.status_code == 200:
                        candidates = resp.json().get("candidates", [])
                        if candidates:
                            text = candidates[0]["content"]["parts"][0]["text"].strip()
                            if len(text) > 25:
                                return text
            except Exception:
                continue

    # Contextualización determinista directa cuando aún no se han colocado las llaves en .env
    short_context = vacancy_context.strip().split(".")[0][:110].strip()
    return f"Considerando que la vacante de {target_role} se enfoca en '{short_context}': {base_question}"


def generate_followup_question_node(state: InterviewGraphState) -> Dict[str, Any]:
    eval_res = state.get("evaluation_result", {})
    low_action = eval_res.get("star_action", 3) < settings.FOLLOWUP_STAR_THRESHOLD
    focus = (
        "las acciones técnicas específicas que ejecutaste personalmente"
        if low_action
        else "el resultado cuantitativo o impacto medible obtenido"
    )
    followup_text = f"Tu respuesta anterior fue ambigua en este punto. Especifica exactamente {focus} en relación con el puesto de {state.get('target_role')}."
    return {
        "session_state": "profundizar_pregunta",
        "next_interviewer_message": followup_text,
    }


def advance_to_next_topic_node(state: InterviewGraphState) -> Dict[str, Any]:
    raw_next_q = state.get("next_question_bank_text") or (
        "Describe otro proyecto relevante donde hayas resuelto un problema técnico crítico y cómo mediste el impacto."
    )
    adapted_q = contextualize_question_with_vacancy(
        base_question=raw_next_q,
        target_role=state.get("target_role", "el puesto"),
        vacancy_context=state.get("job_description_text", ""),
        cv_summary=state.get("anonymized_cv_text", ""),
    )
    return {
        "session_state": "pasar_a_siguiente_tema",
        "next_interviewer_message": adapted_q,
    }


def finalize_interview_node(state: InterviewGraphState) -> Dict[str, Any]:
    return {
        "session_state": "finalizar_entrevista",
        "next_interviewer_message": (
            "Has concluido las preguntas de la entrevista. "
            "Enseguida se presenta la evaluación crítica y el plan de acción."
        ),
    }
