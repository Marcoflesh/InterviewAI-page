import random
import re
from typing import List
from sqlalchemy.orm import Session
from app.models import QuestionBank


def _tokenize_context(text: str) -> set:
    if not text:
        return set()
    words = re.findall(r"[a-záéíóúñü0-9]{4,}", text.lower())
    return set(words)


def select_randomized_questions_for_career(
    db: Session,
    career_code: str,
    count: int = 17,
    vacancy_context: str = "",
    cv_text: str = "",
    target_role: str = "",
) -> List[QuestionBank]:
    """
    Selecciona entre 15 y 20 preguntas del banco de la carrera priorizando aquellas
    que tienen mayor afinidad semántica con el 'Contexto de la vacante', el puesto
    objetivo y el CV del candidato, combinadas con muestreo aleatorio para variedad.
    """
    questions = (
        db.query(QuestionBank)
        .filter(
            QuestionBank.career_code == career_code,
            QuestionBank.active.is_(True),
        )
        .all()
    )

    if not questions:
        questions = (
            db.query(QuestionBank).filter(QuestionBank.active.is_(True)).all()
        )

    context_tokens = _tokenize_context(f"{target_role} {vacancy_context} {cv_text}")
    if not context_tokens:
        shuffled = list(questions)
        random.shuffle(shuffled)
        return shuffled[:count]

    # Calificar afinidad de cada pregunta con el contexto de la vacante + ligero factor aleatorio
    scored = []
    for q in questions:
        q_tokens = _tokenize_context(f"{q.competency} {q.question_text} {q.expected_star_focus}")
        overlap = sum(
            1 for ct in context_tokens if any(ct[:5] in qt for qt in q_tokens)
        )
        score = overlap + random.uniform(0.0, 1.8)
        scored.append((score, q))

    scored.sort(key=lambda item: item[0], reverse=True)
    selected = [item[1] for item in scored[:count]]
    return selected
