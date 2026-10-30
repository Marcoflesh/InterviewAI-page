import logging
import random
import uuid
from datetime import datetime, timezone
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import (
    Career,
    InterviewSession,
    MessageTurn,
    ModelEvaluation,
    QuestionBank,
    StudyResource,
    User,
    UserFeedback,
)
from app.schemas import (
    GoogleLoginRequest,
    LocalLoginRequest,
    LocalRegisterRequest,
    StartSessionRequest,
    SubmitCsatRequest,
    SubmitTurnRequest,
    UserProfileResponse,
)
from app.auth import (
    hash_password,
    validate_real_email,
    verify_google_token,
    verify_password,
)
from app.security import create_access_token, get_current_user_id, rate_limit
from app.services.anonymizer import anonymize_pii, extract_auxiliary_features
from app.services.question_selector import select_randomized_questions_for_career
from app.agents.graph import interview_graph
from app.agents.interviewer import contextualize_question_with_vacancy
from app.agents.synthesizer import synthesize_final_report

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("interviewai.api")

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# CORS: solo los orígenes de ALLOWED_ORIGINS (localhost y GitHub Pages). Sin cookies.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

auth_limit = Depends(rate_limit(settings.RATE_LIMIT_AUTH_PER_MINUTE))
turn_limit = Depends(rate_limit(settings.RATE_LIMIT_TURN_PER_MINUTE))


@app.on_event("startup")
def _more_worker_threads() -> None:
    # Las llamadas a los agentes de IA bloquean un hilo varios segundos: más hilos = más usuarios.
    import anyio.to_thread
    anyio.to_thread.current_default_thread_limiter().total_tokens = 100


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(Exception)
async def unhandled_error(request: Request, exc: Exception):
    logger.exception("Error no controlado en %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Error interno del servidor."})


def _profile(user: User) -> UserProfileResponse:
    return UserProfileResponse(
        user_id=str(user.user_id),
        email=user.email,
        full_name=user.full_name,
        university=user.university or "",
        auth_provider=user.auth_provider,
        avatar_url=user.avatar_url,
        career_code=user.career_code,
        role_code=user.role_code,
        access_token=create_access_token(str(user.user_id)),
    )


def _parse_uuid(value: str, label: str = "Sesión") -> uuid.UUID:
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError):
        raise HTTPException(status_code=404, detail=f"{label} no encontrada.")


def _get_owned_session(db: Session, session_id: str, user_id: str) -> InterviewSession:
    session_obj = (
        db.query(InterviewSession)
        .filter(InterviewSession.session_id == _parse_uuid(session_id))
        .first()
    )
    # Mismo 404 si no existe o si es de otra persona: no revela sesiones ajenas.
    if not session_obj or str(session_obj.user_id) != str(user_id):
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")
    return session_obj


def _get_user(db: Session, user_id: str) -> User:
    user = db.query(User).filter(User.user_id == _parse_uuid(user_id, "Cuenta")).first()
    if not user:
        raise HTTPException(status_code=401, detail="Tu cuenta ya no existe. Inicia sesión de nuevo.")
    return user


@app.get("/api/health")
def health_check():
    # Solo booleanos: nunca se devuelve ninguna llave.
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "interviewer": {"provider": settings.INTERVIEWER_PROVIDER, "model": settings.OPENAI_CHAT_MODEL},
        "evaluator": {"provider": settings.EVALUATOR_PROVIDER, "model": settings.GEMINI_MODEL},
        "configured": {
            "openai_key": settings.openai_ready,
            "gemini_key": settings.gemini_ready,
            "google_sign_in": settings.google_signin_ready,
            "ollama": settings.OLLAMA_ENABLED,
        },
    }


@app.get("/api/auth/google-config")
def get_google_oauth_config():
    """
    Entrega al frontend el GOOGLE_CLIENT_ID configurado en `.env` para inicializar
    el botón verificador oficial de Google Identity Services (`accounts.google.com/gsi/client`).
    """
    is_configured = settings.google_signin_ready
    return {
        "google_client_id": settings.GOOGLE_CLIENT_ID if is_configured else "",
        "is_configured": is_configured,
    }


@app.post("/api/auth/register", response_model=UserProfileResponse, dependencies=[auth_limit])
def register_local_user(payload: LocalRegisterRequest, db: Session = Depends(get_db)):
    clean_email = validate_real_email(payload.email, verify_dns_mx=True)
    existing = db.query(User).filter(User.email == clean_email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una cuenta registrada con este correo electrónico. Por favor inicia sesión.",
        )

    user = User(
        email=clean_email,
        password_hash=hash_password(payload.password),
        auth_provider="local",
        email_verified=True,
        full_name=payload.full_name.strip(),
        university=payload.university.strip(),
        role_code="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return _profile(user)


@app.post("/api/auth/login", response_model=UserProfileResponse, dependencies=[auth_limit])
def login_local_user(payload: LocalLoginRequest, db: Session = Depends(get_db)):
    clean_email = validate_real_email(payload.email, verify_dns_mx=False)
    user = db.query(User).filter(User.email == clean_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
        )
    if user.auth_provider == "google" and not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta cuenta está vinculada con Google. Usa el botón 'Iniciar sesión con Google'.",
        )
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    return _profile(user)


@app.post("/api/auth/google", response_model=UserProfileResponse, dependencies=[auth_limit])
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    verified = verify_google_token(payload.credential)
    user = db.query(User).filter(User.email == verified["email"]).first()
    if not user:
        user = User(
            google_sub=verified["google_sub"],
            email=verified["email"],
            auth_provider="google",
            email_verified=True,
            full_name=verified["full_name"],
            avatar_url=verified.get("avatar_url"),
            role_code="student",
        )
        db.add(user)
    else:
        user.last_login_at = datetime.now(timezone.utc)
        user.full_name = verified["full_name"]
        if verified.get("avatar_url"):
            user.avatar_url = verified["avatar_url"]
        if verified.get("google_sub") and not user.google_sub:
            user.google_sub = verified["google_sub"]
    db.commit()
    db.refresh(user)

    return _profile(user)


@app.get("/api/careers")
def list_careers(db: Session = Depends(get_db)):
    careers = db.query(Career).filter(Career.active.is_(True)).all()
    return [
        {
            "career_code": c.career_code,
            "career_name": c.career_name,
            "faculty": c.faculty,
            "default_target_roles": c.default_target_roles,
        }
        for c in careers
    ]


@app.post("/api/sessions/start")
def start_interview_session(
    payload: StartSessionRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    user = _get_user(db, current_user_id)
    if not db.query(Career).filter(Career.career_code == payload.career_code).first():
        raise HTTPException(status_code=400, detail="Carrera no válida.")
    anonymized_cv = anonymize_pii(payload.cv_text, [user.full_name])
    anonymized_jd = anonymize_pii(payload.job_description_text, [user.full_name])

    random_count = payload.total_questions or random.randint(15, 20)
    random_count = max(15, min(20, random_count))

    selected_questions = select_randomized_questions_for_career(
        db=db,
        career_code=payload.career_code,
        count=random_count,
        vacancy_context=anonymized_jd,
        cv_text=anonymized_cv,
        target_role=payload.target_role,
    )
    if not selected_questions:
        raise HTTPException(
            status_code=400,
            detail="No se encontraron preguntas activas para la carrera seleccionada.",
        )

    q_ids = [q.question_id for q in selected_questions]
    first_question_raw = selected_questions[0].question_text
    first_competency = selected_questions[0].competency
    db.commit()  # libera la conexión a la BD mientras responde el agente de IA
    first_question_adapted = contextualize_question_with_vacancy(
        base_question=first_question_raw,
        target_role=payload.target_role,
        vacancy_context=anonymized_jd,
        cv_summary=anonymized_cv,
    )

    session_obj = InterviewSession(
        user_id=user.user_id,
        career_code=payload.career_code,
        target_role=payload.target_role,
        seniority_level=payload.seniority_level,
        anonymized_cv_text=anonymized_cv,
        job_description_text=anonymized_jd,
        selected_question_ids=q_ids,
        total_questions=len(q_ids),
        current_question_index=0,
        session_state="pasar_a_siguiente_tema",
    )
    db.add(session_obj)
    db.commit()
    db.refresh(session_obj)

    return {
        "session_id": str(session_obj.session_id),
        "career_code": session_obj.career_code,
        "target_role": session_obj.target_role,
        "total_questions": session_obj.total_questions,
        "current_question_number": 1,
        "question_text": first_question_adapted,
        "competency": first_competency,
        "anonymized_cv_preview": anonymized_cv[:200],
    }


@app.post("/api/sessions/turn", dependencies=[turn_limit])
def submit_interview_turn(
    payload: SubmitTurnRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    session_obj = _get_owned_session(db, payload.session_id, current_user_id)
    if session_obj.session_state == "finalizar_entrevista":
        raise HTTPException(status_code=409, detail="Esta entrevista ya terminó.")
    user = _get_user(db, current_user_id)

    q_ids: List[int] = list(session_obj.selected_question_ids or [])
    idx = session_obj.current_question_index
    current_q_id = q_ids[idx] if idx < len(q_ids) else None
    current_q = (
        db.query(QuestionBank).filter(QuestionBank.question_id == current_q_id).first()
        if current_q_id
        else None
    )
    current_q_text = (
        current_q.question_text
        if current_q
        else "Cuéntame sobre un proyecto relevante de tu carrera y los resultados obtenidos."
    )

    next_q_text = None
    if idx + 1 < len(q_ids):
        next_q_obj = (
            db.query(QuestionBank)
            .filter(QuestionBank.question_id == q_ids[idx + 1])
            .first()
        )
        if next_q_obj:
            next_q_text = next_q_obj.question_text

    aux_features = extract_auxiliary_features(payload.candidate_response)
    anonymized_response = anonymize_pii(payload.candidate_response, [user.full_name])

    graph_input = (
        {
            "session_id": str(session_obj.session_id),
            "career_code": session_obj.career_code,
            "target_role": session_obj.target_role,
            "seniority_level": session_obj.seniority_level,
            "anonymized_cv_text": session_obj.anonymized_cv_text,
            "job_description_text": session_obj.job_description_text,
            "current_question_index": idx,
            "total_questions": session_obj.total_questions,
            "current_question_text": current_q_text,
            "candidate_response": anonymized_response,
            "auxiliary_features": aux_features,
            "allow_followups": payload.allow_followups,
            "is_followup_turn": session_obj.session_state == "profundizar_pregunta",
            "llm_provider": None,
            "llm_api_key": None,
            "llm_model": None,
            "evaluation_result": {},
            "session_state": session_obj.session_state,
            "next_question_bank_text": next_q_text,
            "next_interviewer_message": "",
            "evaluation_latency_ms": 0,
            "json_format_valid": True,
        }
    )
    session_pk = session_obj.session_id
    state_before = session_obj.session_state
    was_followup = state_before == "profundizar_pregunta"
    db.commit()  # libera la conexión a la BD mientras evalúan los agentes de IA
    graph_output = interview_graph.invoke(graph_input)
    session_obj = (
        db.query(InterviewSession)
        .filter(InterviewSession.session_id == session_pk)
        .with_for_update()
        .first()
    )
    # Evita turnos duplicados si el usuario envía dos veces la misma respuesta
    if session_obj.current_question_index != idx or session_obj.session_state != state_before:
        db.rollback()
        raise HTTPException(status_code=409, detail="Esa respuesta ya fue registrada.")

    eval_res = graph_output["evaluation_result"]
    new_state = graph_output["session_state"]

    turn_obj = MessageTurn(
        session_id=session_obj.session_id,
        question_number=min(session_obj.total_questions, idx + 1),
        question_id=current_q_id,
        is_followup=was_followup,
        interviewer_question=current_q_text,
        candidate_response=anonymized_response,
        response_length_chars=aux_features["response_length_chars"],
        response_word_count=aux_features["response_word_count"],
        has_quantitative_metrics=aux_features["has_quantitative_metrics"],
        quantitative_metrics_count=aux_features["quantitative_metrics_count"],
        detected_metrics_list=aux_features["detected_metrics_list"],
        response_time_seconds=payload.response_time_seconds,
    )
    db.add(turn_obj)
    db.flush()

    model_eval = ModelEvaluation(
        turn_id=turn_obj.turn_id,
        session_id=session_obj.session_id,
        star_situation=eval_res["star_situation"],
        star_task=eval_res["star_task"],
        star_action=eval_res["star_action"],
        star_result=eval_res["star_result"],
        technical_clarity=eval_res["technical_clarity"],
        relevance=eval_res["relevance"],
        turn_average_score=eval_res["turn_average_score"],
        strengths=eval_res["strengths"],
        improvement_areas=eval_res["improvement_areas"],
        evaluation_latency_ms=graph_output["evaluation_latency_ms"],
        json_format_valid=graph_output["json_format_valid"],
    )
    db.add(model_eval)

    session_obj.session_state = new_state
    if new_state == "pasar_a_siguiente_tema":
        session_obj.current_question_index = idx + 1
    elif new_state == "finalizar_entrevista":
        session_obj.current_question_index = session_obj.total_questions
        session_obj.completed_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "session_id": str(session_obj.session_id),
        "session_state": new_state,
        "question_number": turn_obj.question_number,
        "total_questions": session_obj.total_questions,
        "evaluation": eval_res,
        "auxiliary_features": aux_features,
        "next_interviewer_message": graph_output["next_interviewer_message"],
        "is_completed": new_state == "finalizar_entrevista",
        "evaluator_source": eval_res.get("evaluator_source"),
    }


@app.get("/api/sessions/{session_id}/report", dependencies=[turn_limit])
def get_final_report(
    session_id: str,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    session_obj = _get_owned_session(db, session_id, current_user_id)

    if session_obj.final_report_json:
        return session_obj.final_report_json

    turns = (
        db.query(MessageTurn, ModelEvaluation)
        .join(ModelEvaluation, MessageTurn.turn_id == ModelEvaluation.turn_id)
        .filter(MessageTurn.session_id == session_obj.session_id)
        .order_by(MessageTurn.question_number.asc())
        .all()
    )

    turns_data = []
    for t, e in turns:
        turns_data.append(
            {
                "turn_id": t.turn_id,
                "question_number": t.question_number,
                "interviewer_question": t.interviewer_question,
                "candidate_response": t.candidate_response,
                "star_situation": e.star_situation,
                "star_task": e.star_task,
                "star_action": e.star_action,
                "star_result": e.star_result,
                "technical_clarity": e.technical_clarity,
                "relevance": e.relevance,
                "turn_average_score": float(e.turn_average_score),
                "strengths": e.strengths,
                "improvement_areas": e.improvement_areas,
            }
        )

    resources = (
        db.query(StudyResource)
        .filter(StudyResource.career_code == session_obj.career_code)
        .all()
    )
    resources_list = [
        {
            "title": r.title,
            "provider": r.provider,
            "url": r.url,
            "dimension_target": r.dimension_target,
            "description": r.description,
        }
        for r in resources
    ]

    prev_sessions = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.user_id == session_obj.user_id,
            InterviewSession.session_id != session_obj.session_id,
            InterviewSession.overall_score.isnot(None),
        )
        .order_by(InterviewSession.started_at.desc())
        .all()
    )

    prev_score_val = (
        float(prev_sessions[0].overall_score)
        if prev_sessions and prev_sessions[0].overall_score is not None
        else None
    )
    db.commit()  # libera la conexión mientras el agente redacta los ejemplos STAR
    report = synthesize_final_report(
        turns_with_evals=turns_data,
        study_resources=resources_list,
        target_role=session_obj.target_role,
        career_code=session_obj.career_code,
        evolution_rate=0.0,
    )

    if prev_score_val is not None:
        prev_score = prev_score_val
        if prev_score > 0:
            evolution = round(
                ((report["overall_score"] - prev_score) / prev_score) * 100.0, 2
            )
            report["score_evolution_rate"] = evolution

    session_obj.overall_score = report["overall_score"]
    session_obj.score_evolution_rate = report["score_evolution_rate"]
    session_obj.final_report_json = report
    db.commit()

    return report


@app.post("/api/sessions/csat")
def submit_csat(
    payload: SubmitCsatRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    session_obj = _get_owned_session(db, payload.session_id, current_user_id)
    existing = (
        db.query(UserFeedback)
        .filter(UserFeedback.session_id == session_obj.session_id)
        .first()
    )
    if existing:
        existing.csat_score = payload.csat_score
        existing.perceived_utility = payload.perceived_utility
        existing.student_comment = payload.student_comment
    else:
        fb = UserFeedback(
            session_id=session_obj.session_id,
            user_id=session_obj.user_id,
            csat_score=payload.csat_score,
            perceived_utility=payload.perceived_utility,
            student_comment=payload.student_comment,
        )
        db.add(fb)
    db.commit()
    return {"status": "saved"}


@app.get("/api/users/me/history")
def get_my_history(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == _parse_uuid(current_user_id, "Cuenta"))
        .order_by(InterviewSession.started_at.desc())
        .all()
    )
    return [
        {
            "session_id": str(s.session_id),
            "career_code": s.career_code,
            "target_role": s.target_role,
            "overall_score": float(s.overall_score) if s.overall_score is not None else None,
            "score_evolution_rate": float(s.score_evolution_rate or 0.0),
            "session_state": s.session_state,
            "started_at": s.started_at.isoformat() if s.started_at else None,
        }
        for s in sessions
    ]


@app.delete("/api/users/me")
def delete_my_account(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id),
):
    """Derecho al olvido: borra la cuenta y, por cascada, sesiones, turnos, evaluaciones y CSAT."""
    user = _get_user(db, current_user_id)
    db.execute(delete(User).where(User.user_id == user.user_id))
    db.commit()
    return {"status": "deleted"}
