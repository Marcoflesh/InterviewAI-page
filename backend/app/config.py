import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "InterviewAI API"
    APP_VERSION: str = "0.1.0"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://interviewai:interviewai_secret@db:5432/interviewai",
    )
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    # By default, avoid follow-up questions so each turn draws a fresh randomized career question
    ENABLE_FOLLOWUP_QUESTIONS: bool = (
        os.getenv("ENABLE_FOLLOWUP_QUESTIONS", "false").lower() == "true"
    )
    FOLLOWUP_STAR_THRESHOLD: int = int(os.getenv("FOLLOWUP_STAR_THRESHOLD", "3"))
    DEFAULT_QUESTIONS_PER_SESSION: int = int(
        os.getenv("DEFAULT_QUESTIONS_PER_SESSION", "5")
    )

    class Config:
        env_file = ".env"


settings = Settings()
