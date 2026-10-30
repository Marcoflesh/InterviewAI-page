"""
Configuración central del backend.

Todas las llaves se leen del archivo `.env` (raíz del proyecto) o de variables
de entorno. NUNCA escribas llaves reales en este archivo ni en el frontend.
Guía completa: GUIA_CONFIGURACION_APIS.md
"""
import logging
import secrets
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger("interviewai.config")

# Busca `.env` en la raíz del proyecto aunque el backend se ejecute desde backend/
_ROOT_ENV = Path(__file__).resolve().parents[2] / ".env"
_LOCAL_ENV = Path(".env")

GEMINI_KEY_PREFIXES = ("AIza", "AQ.")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(_ROOT_ENV), str(_LOCAL_ENV)),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "InterviewAI API"
    APP_VERSION: str = "0.4.0"
    DATABASE_URL: str = "postgresql://interviewai:interviewai_secret@db:5432/interviewai"

    # --- Agentes de IA (las llaves viven SOLO en .env) ---------------------
    OPENAI_API_KEY: str = ""
    OPENAI_CHAT_MODEL: str = "gpt-4o-mini"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.8-flash"
    GEMINI_FALLBACK_MODEL: str = "gemini-2.5-flash"
    EVALUATOR_PROVIDER: str = "gemini"      # gemini | openai | ollama
    INTERVIEWER_PROVIDER: str = "openai"    # openai | gemini | ollama
    LLM_TIMEOUT_SECONDS: float = 20.0
    # indicadores = rúbrica analítica de 30 criterios (recomendado) | holistico = 0-5 directo (v0.4)
    EVALUATOR_RUBRIC_MODE: str = "indicadores"
    # Cuánto esperar a que el Agente Entrevistador termine de redactar una pregunta
    # antes de mostrar la del banco (que ya está bien escrita).
    FIRST_QUESTION_WAIT_SECONDS: float = 4.0
    NEXT_QUESTION_WAIT_SECONDS: float = 2.0
    QUESTION_PREFETCH_AHEAD: int = 2   # preguntas que se preparan por adelantado
    # Cuánto espera el reporte final a las evaluaciones que aún corren en segundo plano.
    REPORT_EVALUATION_WAIT_SECONDS: float = 30.0
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"

    # --- Google Sign-In (el Client ID es público; no es un secreto) --------
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLOCK_SKEW_SECONDS: int = 30

    # --- Respaldo local con Ollama -----------------------------------------
    OLLAMA_BASE_URL: str = "http://ollama:11434"
    OLLAMA_MODEL: str = "llama3.2:3b"
    OLLAMA_ENABLED: bool = False

    # --- Sesión de usuario y seguridad -------------------------------------
    SECRET_KEY: str = ""                    # firma de tokens de sesión
    ACCESS_TOKEN_TTL_MINUTES: int = 720
    ALLOWED_ORIGINS: str = (
        "http://localhost:3000,http://127.0.0.1:3000,"
        "http://localhost:8000,https://marcoflesh.github.io"
    )
    RATE_LIMIT_AUTH_PER_MINUTE: int = 10
    RATE_LIMIT_TURN_PER_MINUTE: int = 30
    MAX_RESPONSE_CHARS: int = 4000
    MAX_CONTEXT_CHARS: int = 6000
    EMAIL_MX_CHECK: str = "strict"          # strict | lenient | off

    # --- Reglas de sesión en LangGraph -------------------------------------
    ENABLE_FOLLOWUP_QUESTIONS: bool = False
    FOLLOWUP_STAR_THRESHOLD: int = 3

    @property
    def allowed_origins_list(self) -> List[str]:
        return [o.strip().rstrip("/") for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

    @property
    def openai_ready(self) -> bool:
        return bool(self.OPENAI_API_KEY) and self.OPENAI_API_KEY.startswith("sk-")

    @property
    def gemini_ready(self) -> bool:
        # Google AI Studio: formato clásico "AIza…" o el nuevo "AQ.…" (2026)
        return bool(self.GEMINI_API_KEY) and self.GEMINI_API_KEY.startswith(GEMINI_KEY_PREFIXES)

    @property
    def google_signin_ready(self) -> bool:
        cid = self.GOOGLE_CLIENT_ID or ""
        return cid.endswith(".apps.googleusercontent.com") and not cid.startswith("PON_AQUI")


settings = Settings()

if not settings.SECRET_KEY:
    # Sin SECRET_KEY las sesiones se invalidan en cada reinicio. Úsalo solo en desarrollo.
    settings.SECRET_KEY = secrets.token_urlsafe(48)
    logger.warning("SECRET_KEY no está definida en .env: se generó una temporal (las sesiones se cerrarán al reiniciar).")

if settings.GEMINI_API_KEY and not settings.gemini_ready:
    logger.error(
        "GEMINI_API_KEY no tiene formato de llave de Google AI Studio (debe empezar con 'AIza' o 'AQ.'). "
        "El evaluador usará el siguiente proveedor disponible."
    )
if settings.OPENAI_API_KEY and not settings.openai_ready:
    if settings.OPENAI_API_KEY.startswith("key_"):
        logger.error("OPENAI_API_KEY contiene el ID de la llave ('key_…'), no la llave secreta ('sk-…').")
    else:
        logger.error("OPENAI_API_KEY no tiene formato válido (debe empezar con 'sk-').")
