import random
from datetime import datetime, timezone
from typing import List
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
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
    validate_email_format,
    verify_google_token,
    verify_password,
)
from app.services.anonymizer import anonymize_pii, extract_auxiliary_features
from app.services.question_selector import select_randomized_questions_for_career
from app.agents.graph import interview_graph
from app.agents.synthesizer import synthesize_final_report

app = FastAPI(title=settings.APP_NAME, version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": "0.2.0",
        "ollama_model": settings.OLLAMA_MODEL,
        "followups_enabled_by_default": settings.ENABLE_FOLLOWUP_QUESTIONS,
    }


@app.post("/api/auth/register", response_model=UserProfileResponse)
def register_local_user(payload: LocalRegisterRequest, db: Session = Depends(get_db)):
    clean_email = validate_email_format(payload.email)
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
        university=payload.university.strip() or "Tecnológico de Monterrey",
        role_code="student",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return UserProfileResponse(
        user_id=str(user.user_id),
        email=user.email,
        full_name=user.full_name,
        university=user.university,
        auth_provider=user.auth_provider,
        avatar_url=user.avatar_url,
        career_code=user.career_code,
        role_code=user.role_code,
    )


@app.post("/api/auth/login", response_model=UserProfileResponse)
def login_local_user(payload: LocalLoginRequest, db: Session = Depends(get_db)):
    clean_email = validate_email_format(payload.email)
    user = db.query(User).filter(User.email == clean_email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No encontramos una cuenta con ese correo electrónico. Regístrate primero o usa Google.",
        )
    if user.auth_provider == "google" and not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta cuenta fue creada con Google. Usa el botón 'Iniciar Sesión con Google'.",
        )
    if not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Contraseña incorrecta. Verifica tus datos e intenta nuevamente.",
        )

    user.last_login_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(user)

    return UserProfileResponse(
        user_id=str(user.user_id),
        email=user.email,
        full_name=user.full_name,
        university=user.university,
        auth_provider=user.auth_provider,
        avatar_url=user.avatar_url,
        career_code=user.career_code,
        role_code=user.role_code,
    )


@app.post("/api/auth/google", response_model=UserProfileResponse)
def google_login(payload: GoogleLoginRequest, db: Session = Depends(get_db)):
    verified = verify_google_token(
        credential=payload.credential,
        fallback_email=payload.email,
        fallback_name=payload.full_name,
        fallback_sub=payload.google_sub,
        fallback_avatar=payload.avatar_url,
    )
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

    return UserProfileResponse(
        user_id=str(user.user_id),
        email=user.email,
        full_name=user.full_name,
        university=user.university,
        auth_provider=user.auth_provider,
        avatar_url=user.avatar_url,
        career_code=user.career_code,
        role_code=user.role_code,
    )


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
    payload: StartSessionRequest, db: Session = Depends(get_db)
):
    anonymized_cv = anonymize_pii(payload.cv_text)
    anonymized_jd = anonymize_pii(payload.job_description_text)

    # Número aleatorio realista de preguntas entre 15 y 20
    random_count = payload.total_questions or random.randint(15, 20)
    random_count = max(15, min(20, random_count))

    selected_questions = select_randomized_questions_for_career(
        db=db, career_code=payload.career_code, count=random_count
    )
    if not selected_questions:
        raise HTTPException(
            status_code=400,
            detail="No se encontraron preguntas activas para la carrera seleccionada.",
        )

    q_ids = [q.question_id for q in selected_questions]
    first_question = selected_questions[0]

    session_obj = InterviewSession(
        user_id=payload.user_id,
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
        "question_text": first_question.question_text,
        "competency": first_question.competency,
        "anonymized_cv_preview": anonymized_cv[:200],
    }


@app.post("/api/sessions/turn")
def submit_interview_turn(
    payload: SubmitTurnRequest, db: Session = Depends(get_db)
):
    session_obj = (
        db.query(InterviewSession)
        .filter(InterviewSession.session_id == payload.session_id)
        .first()
    )
    if not session_obj:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

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
    anonymized_response = anonymize_pii(payload.candidate_response)

    graph_output = interview_graph.invoke(
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
            "llm_provider": payload.llm_provider,
            "llm_api_key": payload.llm_api_key,
            "llm_model": payload.llm_model,
            "evaluation_result": {},
            "session_state": session_obj.session_state,
            "next_question_bank_text": next_q_text,
            "next_interviewer_message": "",
            "evaluation_latency_ms": 0,
            "json_format_valid": True,
        }
    )

    eval_res = graph_output["evaluation_result"]
    new_state = graph_output["session_state"]

    turn_obj = MessageTurn(
        session_id=session_obj.session_id,
        question_number=min(session_obj.total_questions, idx + 1),
        question_id=current_q_id,
        is_followup=(session_obj.session_state == "profundizar_pregunta"),
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
    }


@app.get("/api/sessions/{session_id}/report")
def get_final_report(session_id: str, db: Session = Depends(get_db)):
    session_obj = (
        db.query(InterviewSession)
        .filter(InterviewSession.session_id == session_id)
        .first()
    )
    if not session_obj:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")

    if session_obj.final_report_json:
        return session_obj.final_report_json

    turns = (
        db.query(MessageTurn, ModelEvaluation)
        .join(ModelEvaluation, MessageTurn.turn_id == ModelEvaluation.turn_id)
        .filter(MessageTurn.session_id == session_id)
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

    report = synthesize_final_report(
        turns_with_evals=turns_data,
        study_resources=resources_list,
        target_role=session_obj.target_role,
        career_code=session_obj.career_code,
        evolution_rate=0.0,
    )

    if prev_sessions and prev_sessions[0].overall_score:
        prev_score = float(prev_sessions[0].overall_score)
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
def submit_csat(payload: SubmitCsatRequest, db: Session = Depends(get_db)):
    existing = (
        db.query(UserFeedback)
        .filter(UserFeedback.session_id == payload.session_id)
        .first()
    )
    if existing:
        existing.csat_score = payload.csat_score
        existing.perceived_utility = payload.perceived_utility
        existing.student_comment = payload.student_comment
    else:
        fb = UserFeedback(
            session_id=payload.session_id,
            user_id=payload.user_id,
            csat_score=payload.csat_score,
            perceived_utility=payload.perceived_utility,
            student_comment=payload.student_comment,
        )
        db.add(fb)
    db.commit()
    return {"status": "saved"}


@app.get("/api/users/{user_id}/history")
def get_user_history(user_id: str, db: Session = Depends(get_db)):
    sessions = (
        db.query(InterviewSession)
        .filter(InterviewSession.user_id == user_id)
        .order_by(InterviewSession.started_at.desc())
        .all()
    )
    return [
        {
            "session_id": str(s.session_id),
            "career_code": s.career_code,
            "target_role": s.target_role,
            "overall_score": float(s.overall_score) if s.overall_score else None,
            "score_evolution_rate": float(s.score_evolution_rate or 0.0),
            "session_state": s.session_state,
            "started_at": s.started_at.isoformat() if s.started_at else None,
        }
        for s in sessions
    ]
