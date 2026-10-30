"""
Carga el banco de preguntas investigado (app/data/preguntas_software.json) en la tabla
question_bank. Es idempotente: solo inserta las preguntas que aún no existen (misma
carrera y mismo texto), así funciona en bases nuevas y en volúmenes de Docker existentes.
"""
import json
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.models import Career, GoldenDataset, QuestionBank

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


DATA_DIR = DATA_FILE.parent
# La tabla exige un puntaje numérico; para ejemplos externos que solo traen la etiqueta
# "fuerte"/"débil" se guarda un valor representativo y queda en revisión humana.
LABEL_SCORE = {"fuerte": 4.0, "debil": 1.0}


def seed_golden_dataset(db: Session) -> int:
    """Carga en golden_dataset las pruebas de internet y el set de calibración (idempotente)."""
    careers = {c.career_code for c in db.query(Career.career_code).all()}
    existing = {r.sample_response for r in db.query(GoldenDataset.sample_response).all()}
    rows = []
    web = json.loads((DATA_DIR / "pruebas_web_star.json").read_text(encoding="utf-8"))
    for it in web["items"]:
        src = web["fuentes"][it["fuente"]]
        rows.append(GoldenDataset(
            career_code=it["career_code"], competency_rubric=it["competencia"][:150],
            sample_question=it["pregunta"], sample_response=it["respuesta"],
            human_expert_score=LABEL_SCORE[it["etiqueta"]], hitl_review_status="pending_review",
            reviewer_notes=(f"[{it['id']}] Etiqueta externa '{it['etiqueta']}' de {src['nombre']} ({src['url']}). "
                            f"Motivo según la fuente: {it['motivo_de_la_fuente']} El puntaje numérico es "
                            f"representativo (fuerte=4.0, débil=1.0) y requiere revisión humana."),
        ))
    for line in (DATA_DIR / "calibracion_star.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        it = json.loads(line)
        score = round(sum(it["esperado"].values()) / 6.0, 2)
        rows.append(GoldenDataset(
            career_code=it["career_code"], competency_rubric=f"Calibración STAR ({it['nivel']})",
            sample_question=it["pregunta"], sample_response=it["respuesta"],
            human_expert_score=score, hitl_review_status="pending_review",
            reviewer_notes=(f"[{it['id']}] Sintético, calificado con la rúbrica de 30 indicadores; "
                            f"no validado por humanos. Indicadores: {' '.join(it['indicadores_esperados']) or 'ninguno'}."),
        ))
    added = 0
    for r in rows:
        if r.career_code in careers and r.sample_response not in existing:
            db.add(r)
            existing.add(r.sample_response)
            added += 1
    db.commit()
    if added:
        logger.info("Golden dataset: %s respuestas de referencia cargadas", added)
    return added
