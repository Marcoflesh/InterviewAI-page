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
    Utiliza Ollama para redactar un ejemplo mejorado bajo la metodología STAR
    para una de las dos respuestas más débiles de la sesión. Incluye respaldo inmediato.
    """
    prompt = (
        f"Reescribe y mejora la siguiente respuesta de entrevista para el puesto de {target_role} ({career_code}) "
        f"aplicando de forma concisa el método STAR (Situación, Tarea, Acción y Resultado con métricas cuantitativas).\n"
        f"Pregunta: {question_text}\n"
        f"Respuesta original: {candidate_response}\n"
        "Devuelve un párrafo fluido en primera persona sin etiquetas de requerimientos."
    )

    try:
        with httpx.Client(timeout=3.0) as client:
            resp = client.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.2},
                },
            )
            if resp.status_code == 200:
                text = resp.json().get("response", "").strip()
                if len(text) > 30:
                    return text
    except Exception:
        pass

    return (
        f"En un proyecto reciente orientado a {target_role} (Situación), asumí la responsabilidad de resolver el reto planteado en la pregunta "
        f"definiendo criterios técnicos medibles desde el inicio (Tarea). Implementé una solución estructurada validando cada etapa con pruebas "
        f"y herramientas propias de {career_code} (Acción), logrando reducir los tiempos de ejecución en un 35% y cumpliendo el 100% de los criterios de calidad (Resultado)."
    )


def synthesize_final_report(
    turns_with_evals: List[Dict[str, Any]],
    study_resources: List[Dict[str, Any]],
    target_role: str,
    career_code: str,
    evolution_rate: float,
) -> Dict[str, Any]:
    """
    Identifica las dos respuestas con menor puntaje promedio, genera ejemplos redactados
    de mejora bajo el método STAR y estructura el Plan de Acción Personalizado.
    """
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
