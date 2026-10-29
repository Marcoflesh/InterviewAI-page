import random
from typing import List
from sqlalchemy.orm import Session
from app.models import QuestionBank


def select_randomized_questions_for_career(
    db: Session, career_code: str, count: int = 5
) -> List[QuestionBank]:
    """
    Selecciona aleatoriamente entre 5 y 10 preguntas autocontenidas del banco de preguntas
    correspondiente a la carrera del estudiante, evitando repetición dentro de la sesión.
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

    if len(questions) <= count:
        shuffled = list(questions)
        random.shuffle(shuffled)
        return shuffled

    return random.sample(questions, k=count)
