from typing import List, Optional
from pydantic import BaseModel, Field


class GoogleLoginRequest(BaseModel):
    credential: Optional[str] = None
    email: str = "estudiante@tec.mx"
    full_name: str = "Candidato Demo"
    google_sub: str = "google-oauth-demo-sub"
    avatar_url: Optional[str] = None


class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    university: str
    career_code: Optional[str] = None
    role_code: str


class StartSessionRequest(BaseModel):
    user_id: str
    career_code: str = Field(..., description="Código de carrera (ej. ITC, ISD, IIS, IMT, LAF, LMC, IBT, ARQ)")
    target_role: str = Field(..., description="Puesto objetivo")
    seniority_level: str = Field(default="Junior / Intern")
    cv_text: str = Field(..., description="Texto del currículum (será anonimizado antes de guardarse)")
    job_description_text: str = Field(..., description="Descripción de la vacante objetivo")
    total_questions: int = Field(default=5, ge=5, le=10)
    allow_followups: bool = Field(default=False, description="Desactivado por defecto para priorizar preguntas aleatorias sin repreguntas innecesarias")


class StarEvaluationSchema(BaseModel):
    star_situation: int = Field(..., ge=1, le=5)
    star_task: int = Field(..., ge=1, le=5)
    star_action: int = Field(..., ge=1, le=5)
    star_result: int = Field(..., ge=1, le=5)
    technical_clarity: int = Field(..., ge=1, le=5)
    relevance: int = Field(..., ge=1, le=5)
    strengths: str
    improvement_areas: str


class SubmitTurnRequest(BaseModel):
    session_id: str
    candidate_response: str = Field(..., min_length=5)
    response_time_seconds: float = Field(default=30.0, ge=0.0)
    allow_followups: bool = Field(default=False)


class SubmitCsatRequest(BaseModel):
    session_id: str
    user_id: str
    csat_score: int = Field(..., ge=1, le=5)
    perceived_utility: bool = True
    student_comment: Optional[str] = None
