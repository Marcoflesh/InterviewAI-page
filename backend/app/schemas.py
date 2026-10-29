from typing import Optional
from pydantic import BaseModel, Field


class LocalRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, description="Nombre completo del usuario")
    email: str = Field(..., description="Correo electrónico real y verificable")
    password: str = Field(..., min_length=6, description="Contraseña (mínimo 6 caracteres)")
    university: str = Field(..., min_length=2, description="Universidad o institución")


class LocalLoginRequest(BaseModel):
    email: str = Field(..., description="Correo registrado")
    password: str = Field(..., min_length=1, description="Contraseña")


class GoogleLoginRequest(BaseModel):
    credential: str = Field(..., description="Token JWT oficial emitido por Google Identity Services")
    email: Optional[str] = None
    full_name: Optional[str] = None
    google_sub: Optional[str] = None
    avatar_url: Optional[str] = None


class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    university: str
    auth_provider: str = "local"
    avatar_url: Optional[str] = None
    career_code: Optional[str] = None
    role_code: str


class StartSessionRequest(BaseModel):
    user_id: str
    career_code: str = Field(..., description="Código de carrera (ITC, ISD, IIS, IMT, LAF, LMC, IBT, ARQ)")
    target_role: str = Field(..., description="Puesto objetivo")
    seniority_level: str = Field(default="Junior / Intern")
    cv_text: str = Field(..., description="Resumen del currículum (será anonimizado antes de guardarse)")
    job_description_text: str = Field(..., description="Contexto de la vacante objetivo")
    total_questions: Optional[int] = Field(default=None, ge=15, le=20)
    allow_followups: bool = Field(default=False)


class StarEvaluationSchema(BaseModel):
    star_situation: int = Field(..., ge=0, le=5)
    star_task: int = Field(..., ge=0, le=5)
    star_action: int = Field(..., ge=0, le=5)
    star_result: int = Field(..., ge=0, le=5)
    technical_clarity: int = Field(..., ge=0, le=5)
    relevance: int = Field(..., ge=0, le=5)
    strengths: str
    improvement_areas: str


class SubmitTurnRequest(BaseModel):
    session_id: str
    candidate_response: str = Field(..., min_length=1)
    response_time_seconds: float = Field(default=30.0, ge=0.0)
    allow_followups: bool = Field(default=False)


class SubmitCsatRequest(BaseModel):
    session_id: str
    user_id: str
    csat_score: int = Field(..., ge=1, le=5)
    perceived_utility: bool = True
    student_comment: Optional[str] = None
