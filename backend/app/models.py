import uuid
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    SmallInteger,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from app.database import Base


class RbacRole(Base):
    __tablename__ = "rbac_roles"
    role_id = Column(Integer, primary_key=True, index=True)
    role_code = Column(String(50), unique=True, nullable=False)
    role_name = Column(String(100), nullable=False)
    permissions = Column(JSONB, nullable=False, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    google_sub = Column(String(255), unique=True, nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    auth_provider = Column(String(50), nullable=False, default="local")
    email_verified = Column(Boolean, nullable=False, default=True)
    full_name = Column(String(255), nullable=False)
    avatar_url = Column(Text, nullable=True)
    university = Column(String(255), default="Tecnológico de Monterrey")
    career_code = Column(String(50), nullable=True)
    role_code = Column(
        String(50), ForeignKey("rbac_roles.role_code"), nullable=False, default="student"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login_at = Column(DateTime(timezone=True), server_default=func.now())


class Career(Base):
    __tablename__ = "careers"
    career_code = Column(String(50), primary_key=True)
    career_name = Column(String(150), nullable=False)
    faculty = Column(String(150), nullable=False)
    default_target_roles = Column(JSONB, nullable=False, default=list)
    active = Column(Boolean, default=True)


class QuestionBank(Base):
    __tablename__ = "question_bank"
    question_id = Column(Integer, primary_key=True, index=True)
    career_code = Column(
        String(50), ForeignKey("careers.career_code", ondelete="CASCADE"), nullable=False
    )
    category = Column(String(80), nullable=False)
    seniority_level = Column(String(50), nullable=False, default="Junior / Intern")
    competency = Column(String(120), nullable=False)
    question_text = Column(Text, nullable=False)
    expected_star_focus = Column(Text, nullable=False)
    active = Column(Boolean, default=True)


class StudyResource(Base):
    __tablename__ = "study_resources"
    resource_id = Column(Integer, primary_key=True, index=True)
    career_code = Column(
        String(50), ForeignKey("careers.career_code", ondelete="CASCADE"), nullable=True
    )
    dimension_target = Column(String(50), nullable=False)
    title = Column(String(200), nullable=False)
    provider = Column(String(100), nullable=False)
    url = Column(Text, nullable=False)
    description = Column(Text, nullable=False)


class InterviewSession(Base):
    __tablename__ = "interview_sessions"
    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    career_code = Column(
        String(50), ForeignKey("careers.career_code"), nullable=False
    )
    university = Column(String(255), nullable=False, default="Tecnológico de Monterrey")
    target_role = Column(String(150), nullable=False)
    seniority_level = Column(String(50), nullable=False, default="Junior / Intern")
    anonymized_cv_text = Column(Text, nullable=False)
    job_description_text = Column(Text, nullable=False)
    selected_question_ids = Column(JSONB, nullable=False, default=list)
    total_questions = Column(Integer, nullable=False, default=16)
    current_question_index = Column(Integer, nullable=False, default=0)
    session_state = Column(
        String(50), nullable=False, default="pasar_a_siguiente_tema"
    )
    overall_score = Column(Numeric(4, 2), nullable=True)
    score_evolution_rate = Column(Numeric(6, 2), default=0.00)
    final_report_json = Column(JSONB, nullable=True)
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)


class MessageTurn(Base):
    __tablename__ = "message_turns"
    turn_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    question_number = Column(Integer, nullable=False)
    question_id = Column(Integer, ForeignKey("question_bank.question_id"), nullable=True)
    is_followup = Column(Boolean, nullable=False, default=False)
    interviewer_question = Column(Text, nullable=False)
    candidate_response = Column(Text, nullable=False)
    response_length_chars = Column(Integer, nullable=False, default=0)
    response_word_count = Column(Integer, nullable=False, default=0)
    has_quantitative_metrics = Column(Boolean, nullable=False, default=False)
    quantitative_metrics_count = Column(Integer, nullable=False, default=0)
    detected_metrics_list = Column(JSONB, nullable=False, default=list)
    response_time_seconds = Column(Numeric(6, 2), default=0.00)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelEvaluation(Base):
    __tablename__ = "model_evaluations"
    evaluation_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    turn_id = Column(
        UUID(as_uuid=True),
        ForeignKey("message_turns.turn_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.session_id", ondelete="CASCADE"),
        nullable=False,
    )
    star_situation = Column(SmallInteger, nullable=False)
    star_task = Column(SmallInteger, nullable=False)
    star_action = Column(SmallInteger, nullable=False)
    star_result = Column(SmallInteger, nullable=False)
    technical_clarity = Column(SmallInteger, nullable=False)
    relevance = Column(SmallInteger, nullable=False)
    turn_average_score = Column(Numeric(4, 2), nullable=False)
    strengths = Column(Text, nullable=False)
    improvement_areas = Column(Text, nullable=False)
    is_weakest_response = Column(Boolean, nullable=False, default=False)
    improved_example_star = Column(Text, nullable=True)
    recommended_resources = Column(JSONB, default=list)
    evaluation_latency_ms = Column(Integer, default=0)
    json_format_valid = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class UserFeedback(Base):
    __tablename__ = "user_feedback"
    feedback_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interview_sessions.session_id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False
    )
    csat_score = Column(SmallInteger, nullable=True)
    perceived_utility = Column(Boolean, default=True)
    student_comment = Column(Text, nullable=True)
    abandonment_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class GoldenDataset(Base):
    """Respuestas de referencia para medir al Agente Evaluador (RN-07)."""
    __tablename__ = "golden_dataset"
    golden_id = Column(Integer, primary_key=True)
    career_code = Column(String(50), ForeignKey("careers.career_code"), nullable=False)
    competency_rubric = Column(String(150), nullable=False)
    sample_question = Column(Text, nullable=False)
    sample_response = Column(Text, nullable=False)
    human_expert_score = Column(Numeric(4, 2), nullable=False)
    model_score = Column(Numeric(4, 2), nullable=True)
    hitl_review_status = Column(String(50), nullable=False, default="approved")
    reviewer_notes = Column(Text, nullable=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now())
