import logging
from typing import Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DBAPIError, OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

logger = logging.getLogger("interviewai.database")

engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=20,
    max_overflow=20,
    pool_timeout=30,
    connect_args={"connect_timeout": 5},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Diagnóstico de la base de datos (lo usan /api/health, el manejador de errores
# y los scripts iniciar.*). Detecta los dos problemas típicos de Docker:
#  1) el volumen pgdata guarda una contraseña anterior a la del .env
#  2) el volumen se creó con un init.sql de una versión anterior
# ---------------------------------------------------------------------------
HINTS = {
    "ok": "Base de datos lista.",
    "contrasena": (
        "La base de datos de Docker guarda una contraseña anterior a la de tu .env. "
        "Vuelve a ejecutar iniciar.bat / ./iniciar.sh (la corrige sola) "
        "o ejecuta: docker compose down -v"
    ),
    "esquema_desactualizado": (
        "La base de datos se creó con una versión anterior de InterviewAI. "
        "Ejecuta iniciar.bat / ./iniciar.sh y acepta reiniciarla "
        "(o: docker compose down -v). Se borran solo los datos locales de prueba."
    ),
    "sin_tablas": (
        "La base de datos existe pero no tiene las tablas. "
        "Ejecuta: docker compose down -v y vuelve a iniciar."
    ),
    "sin_conexion": "No se pudo conectar a PostgreSQL. Revisa que el contenedor 'db' esté encendido.",
}

REQUIRED_USER_COLUMNS = {"password_hash", "auth_provider", "email_verified"}
MIN_QUESTIONS_PER_CAREER = 20


def _result(code: str, extra: str = "") -> dict:
    return {"ok": code == "ok", "code": code, "detail": HINTS[code] + (f" ({extra})" if extra else "")}


def classify_db_error(exc: BaseException) -> str:
    msg = str(getattr(exc, "orig", exc)).lower()
    if "password authentication failed" in msg:
        return "contrasena"
    if "does not exist" in msg and ("relation" in msg or "column" in msg):
        return "esquema_desactualizado"
    if "violates check constraint" in msg:
        return "esquema_desactualizado"
    return "sin_conexion"


def check_database(eng: Optional[Engine] = None) -> dict:
    eng = eng or engine
    try:
        with eng.connect() as conn:
            cols = {
                r[0]
                for r in conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_schema = current_schema() AND table_name = 'users'"
                ))
            }
            if not cols:
                return _result("sin_tablas")
            missing = REQUIRED_USER_COLUMNS - cols
            if missing:
                return _result("esquema_desactualizado", "faltan columnas: " + ", ".join(sorted(missing)))
            check_def = conn.execute(text(
                "SELECT pg_get_constraintdef(c.oid) FROM pg_constraint c "
                "JOIN pg_namespace n ON n.oid = c.connamespace "
                "WHERE n.nspname = current_schema() AND c.conname = 'model_evaluations_star_situation_check'"
            )).scalar()
            if check_def and ">= 0" not in check_def:
                return _result("esquema_desactualizado", "la escala de evaluación aún es 1-5")
            min_q = conn.execute(text(
                "SELECT COALESCE(MIN(c), 0) FROM (SELECT COUNT(*) AS c FROM question_bank "
                "WHERE active GROUP BY career_code) t"
            )).scalar()
            if int(min_q or 0) < MIN_QUESTIONS_PER_CAREER:
                return _result("esquema_desactualizado", "banco de preguntas incompleto")
            return _result("ok")
    except OperationalError as exc:
        code = classify_db_error(exc)
        logger.error("Base de datos: %s", HINTS[code])
        return _result(code)
    except DBAPIError as exc:
        logger.error("Base de datos: %s", exc)
        return _result(classify_db_error(exc))
