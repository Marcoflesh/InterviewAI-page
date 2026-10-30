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

    def ranked(pool: List[QuestionBank]) -> List[QuestionBank]:
        """Afinidad con la vacante + factor aleatorio para variar entre sesiones."""
        scored = []
        for q in pool:
            q_tokens = _tokenize_context(f"{q.competency} {q.question_text} {q.expected_star_focus}")
            overlap = sum(1 for ct in context_tokens if any(ct[:5] in qt for qt in q_tokens)) if context_tokens else 0
            scored.append((overlap + random.uniform(0.0, 1.8), q))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [q for _, q in scored]

    # Como en una entrevista real: abre con una pregunta amplia y mezcla mitad conductuales
    # (competencias) y mitad técnicas, sin repetir competencia.
    opening = [q for q in questions if q.category == "apertura"]
    behavioral = [q for q in questions if q.category == "conductual_star"]
    technical = [q for q in questions if q.category not in ("apertura", "conductual_star")]

    selected: List[QuestionBank] = []
    used_competencies = set()

    def take(pool: List[QuestionBank], n: int) -> None:
        for q in ranked(pool):
            if n <= 0 or len(selected) >= count:
                return
            if q in selected or q.competency in used_competencies:
                continue
            selected.append(q)
            used_competencies.add(q.competency)
            n -= 1

    if opening:
        take(opening, 1)
    remaining = count - len(selected)
    take(behavioral, (remaining + 1) // 2)
    take(technical, count - len(selected))
    take(behavioral + technical + opening, count - len(selected))  # rellenar si una categoría es corta

    first, rest = selected[:1], selected[1:]
    random.shuffle(rest)
    return first + rest
