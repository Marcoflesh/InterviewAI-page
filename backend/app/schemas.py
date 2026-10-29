from typing import Optional
from pydantic import BaseModel, Field


class LocalRegisterRequest(BaseModel):
    full_name: str = Field(..., min_length=2, description="Nombre completo del usuario")
    email: str = Field(..., description="Correo electrónico válido")
    password: str = Field(..., min_length=6, description="Contraseña (mínimo 6 caracteres)")
    university: str = Field(default="Tecnológico de Monterrey")


class LocalLoginRequest(BaseModel):
    email: str = Field(..., description="Correo registrado")
    password: str = Field(..., min_length=1, description="Contraseña")


class GoogleLoginRequest(BaseModel):
    credential: Optional[str] = None
    email: str
    full_name: str
    google_sub: str
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
    total_questions: Optional[int] = Field(default=None, ge=15, le=20, description="Si se omite, el servidor asigna un número aleatorio entre 15 y 20 preguntas")
    allow_followups: bool = Field(default=False)


class SubmitTurnRequest(BaseModel):
    session_id: str
    candidate_response: str = Field(..., min_length=1)
    response_time_seconds: float = Field(default=30.0, ge=0.0)
    allow_followups: bool = Field(default=False)
    llm_provider: Optional[str] = Field(default=None, description="'ollama' | 'gemini' | 'openai'")
    llm_api_key: Optional[str] = Field(default=None, description="Llave API opcional provista por el usuario para los agentes")
    llm_model: Optional[str] = Field(default=None, description="Modelo específico opcional")


class SubmitCsatRequest(BaseModel):
    session_id: str
    user_id: str
    csat_score: int = Field(..., ge=1, le=5)
    perceived_utility: bool = True
    student_comment: Optional[str] = None
