"""
Carga el banco de preguntas investigado (app/data/preguntas_software.json) en la tabla
question_bank. Es idempotente: solo inserta las preguntas que aún no existen (misma
carrera y mismo texto), así funciona en bases nuevas y en volúmenes de Docker existentes.
"""
import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Career, QuestionBank

logger = logging.getLogger("interviewai.seed")
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "preguntas_software.json"


def seed_question_bank(db: Session) -> int:
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    careers = {c.career_code for c in db.query(Career.career_code).all()}
    existing = {(q.career_code, q.question_text) for q in db.query(QuestionBank.career_code, QuestionBank.question_text).all()}
    added = 0
    for item in data["preguntas"]:
        key = (item["career_code"], item["question_text"])
        if item["career_code"] not in careers or key in existing:
            continue
        db.add(QuestionBank(
            career_code=item["career_code"],
            category=item["category"],
            seniority_level=item.get("seniority_level", "Junior / Intern"),
            competency=item["competency"][:120],
            question_text=item["question_text"],
            expected_star_focus=item["expected_star_focus"],
            active=True,
        ))
        existing.add(key)
        added += 1
    db.commit()
    if added:
        logger.info("Banco de preguntas: %s preguntas nuevas cargadas desde %s", added, DATA_FILE.name)
    return added
