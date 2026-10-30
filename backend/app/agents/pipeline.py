"""
Trabajo de los agentes en segundo plano para que el chat responda al instante.

1) Preguntas: el Agente Entrevistador redacta por adelantado las siguientes
   QUESTION_PREFETCH_AHEAD preguntas (ventana deslizante) mientras el usuario
   escribe. En cada turno la siguiente pregunta ya está lista.
2) Evaluación: la respuesta se guarda y la siguiente pregunta se devuelve de
   inmediato; el Agente Evaluador califica en segundo plano y el frontend consulta
   el resultado (GET /api/sessions/{id}/turns/{turn_id}/evaluation).

Funciona con un solo proceso de backend (como en Docker). Si el caché se pierde
(reinicio), todo se recalcula bajo demanda: nunca se bloquea la entrevista.
"""
import logging
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from typing import Dict, Iterable, Optional, Tuple

from sqlalchemy.exc import IntegrityError

from app.config import settings
from app.database import SessionLocal
from app.models import InterviewSession, MessageTurn, ModelEvaluation
from app.services.anonymizer import extract_auxiliary_features

logger = logging.getLogger("interviewai.pipeline")

# Colas separadas para que una no frene a la otra (las llamadas a la IA solo esperan red).
_priority = ThreadPoolExecutor(max_workers=16, thread_name_prefix="agent-priority")   # 1.ª pregunta / al momento
_background = ThreadPoolExecutor(max_workers=32, thread_name_prefix="agent-questions")  # siguientes preguntas
_eval_pool = ThreadPoolExecutor(max_workers=32, thread_name_prefix="agent-eval")        # evaluaciones

_lock = threading.Lock()
_questions: Dict[Tuple[str, int], Tuple[float, Future]] = {}
_evaluations: Dict[str, Future] = {}
_TTL_SECONDS = 3 * 60 * 60


def _purge_old() -> None:
    now = time.time()
    for key in [k for k, (ts, _) in _questions.items() if now - ts > _TTL_SECONDS]:
        _questions.pop(key, None)
    for key in [k for k, f in _evaluations.items() if f.done()]:
        _evaluations.pop(key, None)


# ---------------------------------------------------------------------------
# Preguntas
# ---------------------------------------------------------------------------
def _humanize(base_question: str, role: str, vacancy: str, cv: str) -> str:
    from app.agents.interviewer import humanize_question

    return humanize_question(base_question, role, vacancy, cv)


def prefetch_questions(session_id: str, questions: Iterable[Tuple[int, str]], role: str,
                       vacancy: str, cv: str, priority_index: Optional[int] = None) -> None:
    with _lock:
        _purge_old()
        for idx, base in questions:
            key = (session_id, idx)
            if key in _questions:
                continue
            pool = _priority if idx == priority_index else _background
            _questions[key] = (time.time(), pool.submit(_humanize, base, role, vacancy, cv))


def get_question(session_id: str, idx: int, base_question: str, role: str, vacancy: str,
                 cv: str, wait_seconds: float) -> str:
    """Pregunta humanizada si está lista en `wait_seconds`; si no, la del banco (ya es natural)."""
    with _lock:
        entry = _questions.get((session_id, idx))
        if entry is None:
            fut = _priority.submit(_humanize, base_question, role, vacancy, cv)
            _questions[(session_id, idx)] = (time.time(), fut)
        else:
            fut = entry[1]
    try:
        return fut.result(timeout=wait_seconds) or base_question
    except FutureTimeout:
        logger.info("pregunta %s de la sesión aún en preparación: se usa la del banco", idx + 1)
        return base_question
    except Exception:
        logger.exception("No se pudo humanizar la pregunta")
        return base_question


def forget_session(session_id: str) -> None:
    with _lock:
        for key in [k for k in _questions if k[0] == session_id]:
            _questions.pop(key, None)


# ---------------------------------------------------------------------------
# Evaluaciones
# ---------------------------------------------------------------------------
def evaluate_and_store(turn_id: str) -> Optional[dict]:
    """Evalúa un turno guardado y escribe su ModelEvaluation (idempotente)."""
    from app.agents.evaluator import evaluate_candidate_turn_node

    db = SessionLocal()
    try:
        existing = db.query(ModelEvaluation).filter(ModelEvaluation.turn_id == turn_id).first()
        if existing:
            return None
        turn = db.query(MessageTurn).filter(MessageTurn.turn_id == turn_id).first()
        if not turn:
            return None
        sess = db.query(InterviewSession).filter(InterviewSession.session_id == turn.session_id).first()
        if not sess:
            return None
        state = {
            "session_id": str(sess.session_id),
            "career_code": sess.career_code,
            "target_role": sess.target_role,
            "seniority_level": sess.seniority_level,
            "job_description_text": sess.job_description_text,
            "current_question_text": turn.interviewer_question,
            "candidate_response": turn.candidate_response,
            "auxiliary_features": extract_auxiliary_features(turn.candidate_response),
        }
        session_pk, turn_pk = sess.session_id, turn.turn_id
        db.commit()  # no retener la conexión mientras responde la IA

        out = evaluate_candidate_turn_node(state)
        ev = out["evaluation_result"]
        db.add(ModelEvaluation(
            turn_id=turn_pk,
            session_id=session_pk,
            star_situation=ev["star_situation"],
            star_task=ev["star_task"],
            star_action=ev["star_action"],
            star_result=ev["star_result"],
            technical_clarity=ev["technical_clarity"],
            relevance=ev["relevance"],
            turn_average_score=ev["turn_average_score"],
            strengths=ev["strengths"],
            improvement_areas=ev["improvement_areas"],
            evaluation_latency_ms=out["evaluation_latency_ms"],
            json_format_valid=out["json_format_valid"],
        ))
        db.commit()
        logger.info("evaluación lista turn=%s fuente=%s latency_ms=%s",
                    str(turn_pk)[:8], ev.get("evaluator_source"), out["evaluation_latency_ms"])
        return ev
    except IntegrityError:
        db.rollback()  # otra tarea ya la guardó, o la cuenta se borró
        return None
    except Exception:
        db.rollback()
        logger.exception("Falló la evaluación en segundo plano del turno %s", turn_id)
        return None
    finally:
        db.close()


def submit_evaluation(turn_id: str) -> None:
    with _lock:
        _purge_old()
        _evaluations[turn_id] = _eval_pool.submit(evaluate_and_store, turn_id)


def wait_for_evaluations(turn_ids: Iterable[str], timeout_seconds: float) -> None:
    """Espera las evaluaciones en curso; las que no tengan tarea se calculan ahora."""
    deadline = time.time() + timeout_seconds
    for tid in turn_ids:
        with _lock:
            fut = _evaluations.get(tid)
        if fut is not None:
            try:
                fut.result(timeout=max(0.1, deadline - time.time()))
                continue
            except FutureTimeout:
                logger.warning("La evaluación del turno %s tardó demasiado", tid)
            except Exception:
                pass
        evaluate_and_store(tid)  # sin tarea (reinicio) o tarea fallida: calcular ya


def question_wait_seconds(first: bool) -> float:
    return settings.FIRST_QUESTION_WAIT_SECONDS if first else settings.NEXT_QUESTION_WAIT_SECONDS
