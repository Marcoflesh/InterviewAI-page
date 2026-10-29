import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "InterviewAI API"
    APP_VERSION: str = "0.3.0"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://interviewai:interviewai_secret@db:5432/interviewai",
    )

    # =========================================================================
    # >>> CONFIGURACIÓN DE AGENTES DE IA (GPT-4o mini y Gemini 3.8 Flash) <<<
    # Puedes colocar tus llaves directamente en el archivo `.env` (recomendado)
    # o reemplazar el segundo argumento de os.getenv(...) aquí abajo:
    # =========================================================================
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")  # <-- PON AQUÍ TU API KEY DE OPENAI EN .env
    OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")

    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")  # <-- PON AQUÍ TU API KEY DE GEMINI EN .env
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

    # Proveedores por defecto para cada agente en LangGraph:
    EVALUATOR_PROVIDER: str = os.getenv("EVALUATOR_PROVIDER", "gemini")
    INTERVIEWER_PROVIDER: str = os.getenv("INTERVIEWER_PROVIDER", "openai")

    # =========================================================================
    # >>> VERIFICADOR OFICIAL DE GOOGLE OAUTH 2.0 <<<
    # Coloca tu Client ID de Google Cloud Console en `.env` (GOOGLE_CLIENT_ID)
    # =========================================================================
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")

    # Respaldo con Ollama local
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

    ENABLE_FOLLOWUP_QUESTIONS: bool = (
        os.getenv("ENABLE_FOLLOWUP_QUESTIONS", "false").lower() == "true"
    )
    FOLLOWUP_STAR_THRESHOLD: int = int(os.getenv("FOLLOWUP_STAR_THRESHOLD", "3"))

    class Config:
        env_file = ".env"


settings = Settings()
