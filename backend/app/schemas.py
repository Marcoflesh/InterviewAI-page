from typing import Optional
from pydantic import BaseModel, Field


class LocalRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=3, max_length=120, description="Nombre completo del usuario")
    email: str = Field(..., max_length=254, description="Correo electrónico real y verificable")
    password: str = Field(..., min_length=8, max_length=128, description="Contraseña (mínimo 8 caracteres)")
    university: str = Field(..., min_length=2, max_length=160, description="Universidad o institución")


class LocalLoginRequest(BaseModel):
    email: str = Field(..., max_length=254)
    password: str = Field(..., min_length=1, max_length=128)


class GoogleLoginRequest(BaseModel):
    credential: str = Field(..., max_length=4096, description="JWT emitido por Google Identity Services")


class UserProfileResponse(BaseModel):
    user_id: str
    email: str
    full_name: str
    university: Optional[str] = ""
    auth_provider: str = "local"
    avatar_url: Optional[str] = None
    career_code: Optional[str] = None
    role_code: str
    access_token: Optional[str] = None
    token_type: str = "bearer"


class StartSessionRequest(BaseModel):
    # user_id se ignora: el backend lo toma del token de sesión.
    user_id: Optional[str] = None
    career_code: str = Field(..., max_length=10)
    target_role: str = Field(..., min_length=2, max_length=150)
    seniority_level: str = Field(default="Junior / Intern", max_length=50)
    cv_text: str = Field(..., min_length=1, max_length=6000)
    job_description_text: str = Field(..., min_length=1, max_length=6000)
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
    session_id: str = Field(..., max_length=64)
    candidate_response: str = Field(..., min_length=1, max_length=4000)
    response_time_seconds: float = Field(default=30.0, ge=0.0, le=86400)
    allow_followups: bool = Field(default=False)


class SubmitCsatRequest(BaseModel):
    session_id: str = Field(..., max_length=64)
    user_id: Optional[str] = None  # se ignora: se toma del token
    csat_score: int = Field(..., ge=1, le=5)
    perceived_utility: bool = True
    student_comment: Optional[str] = Field(default=None, max_length=1000)
