from typing import Any, Dict, List
import httpx
from app.config import settings


def generate_improved_star_example(
    question_text: str,
    candidate_response: str,
    target_role: str,
    career_code: str,
) -> str:
    """
    Utiliza `gemini-3.8-flash` o `gpt-4o-mini` (configurados en `.env`) para redactar
    un ejemplo crítico y concreto de cómo debió responderse la pregunta bajo el método STAR.
    """
    prompt = (
        f"Reescribe y mejora de forma rigurosa la siguiente respuesta de entrevista para el puesto de {target_role} ({career_code}) "
        f"aplicando el método STAR (Situación, Tarea, Acción técnica en primera persona y Resultado con métricas cuantitativas).\n"
        f"Pregunta: {question_text}\n"
        f"Respuesta original deficiente o incompleta: {candidate_response}\n"
        "Devuelve un solo párrafo fluido en primera persona sin introducciones."
    )

    # =========================================================================
    # >>> SÍNTESIS DE REPORTE CON GEMINI 3.8 FLASH (GEMINI_API_KEY EN .env) <<<
    # =========================================================================
    if (
        settings.GEMINI_API_KEY
        and not settings.GEMINI_API_KEY.startswith("PON_AQUI")
    ):
        for mdl in [settings.GEMINI_MODEL or "gemini-3.8-flash", "gemini-2.5-flash"]:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{mdl}:generateContent?key={settings.GEMINI_API_KEY}"
                with httpx.Client(timeout=4.0) as client:
                    resp = client.post(
                        url,
                        json={"contents": [{"parts": [{"text": prompt}]}]},
                    )
                    if resp.status_code == 200:
                        candidates = resp.json().get("candidates", [])
                        if candidates:
                            text = candidates[0]["content"]["parts"][0]["text"].strip()
                            if len(text) > 30:
                                return text
            except Exception:
                continue

    # =========================================================================
    # >>> SÍNTESIS DE REPORTE CON GPT-4o MINI (OPENAI_API_KEY EN .env) <<<
    # =========================================================================
    if (
        settings.OPENAI_API_KEY
        and not settings.OPENAI_API_KEY.startswith("PON_AQUI")
    ):
        try:
            with httpx.Client(timeout=4.0) as client:
                resp = client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"},
                    json={
                        "model": settings.OPENAI_CHAT_MODEL or "gpt-4o-mini",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.2,
                        "max_tokens": 200,
                    },
                )
                if resp.status_code == 200:
                    text = resp.json()["choices"][0]["message"]["content"].strip()
                    if len(text) > 30:
                        return text
        except Exception:
            pass

    return (
        f"En un proyecto reciente orientado a {target_role} (Situación), tenía la responsabilidad directa de resolver el problema planteado "
        f"cumpliendo los estándares técnicos y tiempos de entrega (Tarea). Diagnosticué la causa raíz e implementé personalmente la solución aplicando "
        f"herramientas especializadas de {career_code} y pruebas de validación (Acción), logrando reducir los fallos en un 38% y mejorando el tiempo de ejecución en un 45% (Resultado)."
    )


def synthesize_final_report(
    turns_with_evals: List[Dict[str, Any]],
    study_resources: List[Dict[str, Any]],
    target_role: str,
    career_code: str,
    evolution_rate: float,
) -> Dict[str, Any]:
    if not turns_with_evals:
        return {
            "overall_score": 0.0,
            "score_evolution_rate": evolution_rate,
            "dimension_averages": {},
            "weakest_responses": [],
            "action_plan": study_resources[:3],
        }

    overall_score = round(
        sum(float(t["turn_average_score"]) for t in turns_with_evals) / len(turns_with_evals),
        2,
    )

    dim_keys = [
        "star_situation",
        "star_task",
        "star_action",
        "star_result",
        "technical_clarity",
        "relevance",
    ]
    dimension_averages = {
        k: round(sum(float(t[k]) for t in turns_with_evals) / len(turns_with_evals), 2)
        for k in dim_keys
    }

    sorted_turns = sorted(turns_with_evals, key=lambda x: float(x["turn_average_score"]))
    weakest_two = sorted_turns[:2]

    weakest_formatted = []
    for item in weakest_two:
        improved = generate_improved_star_example(
            question_text=item["interviewer_question"],
            candidate_response=item["candidate_response"],
            target_role=target_role,
            career_code=career_code,
        )
        weakest_formatted.append(
            {
                "turn_id": str(item["turn_id"]),
                "question_number": item["question_number"],
                "question_text": item["interviewer_question"],
                "original_response": item["candidate_response"],
                "turn_average_score": float(item["turn_average_score"]),
                "improvement_areas": item["improvement_areas"],
                "improved_star_example": improved,
            }
        )

    return {
        "overall_score": overall_score,
        "score_evolution_rate": evolution_rate,
        "dimension_averages": dimension_averages,
        "weakest_responses": weakest_formatted,
        "action_plan": study_resources,
    }
