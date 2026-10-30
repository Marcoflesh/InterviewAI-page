"""
Regresión del error "Error interno del servidor" al iniciar sesión (30/10/2026):
la base de datos de Docker tenía (A) una contraseña anterior o (B) un esquema viejo.
"""
import os
import uuid
from urllib.parse import urlparse, urlunparse

import pytest
from sqlalchemy import create_engine, text

from app import database
from app.database import check_database

TEST_DB = os.environ["TEST_DATABASE_URL"]


def _with_password(url: str, pw: str) -> str:
    u = urlparse(url)
    netloc = f"{u.username}:{pw}@{u.hostname}:{u.port or 5432}"
    return urlunparse(u._replace(netloc=netloc))


def test_base_actual_esta_ok():
    assert check_database()["code"] == "ok"


def test_contrasena_vieja_se_detecta():
    eng = create_engine(_with_password(TEST_DB, "contrasena-vieja-del-volumen"))
    state = check_database(eng)
    if state["code"] == "ok":
        pytest.skip("Este PostgreSQL acepta cualquier contraseña (trust); en Docker sí se valida.")
    assert state["code"] == "contrasena"
    assert "docker compose down -v" in state["detail"]


def test_esquema_viejo_se_detecta():
    schema = "legacy_" + uuid.uuid4().hex[:8]
    eng = create_engine(TEST_DB, connect_args={"options": f"-csearch_path={schema}"})
    with eng.begin() as conn:
        conn.execute(text(f"CREATE SCHEMA {schema}"))
        conn.execute(text(f"CREATE TABLE {schema}.users (user_id uuid, google_sub varchar NOT NULL, email varchar)"))
    try:
        state = check_database(eng)
        assert state["code"] == "esquema_desactualizado"
        assert "password_hash" in state["detail"]
    finally:
        with eng.begin() as conn:
            conn.execute(text(f"DROP SCHEMA {schema} CASCADE"))
        eng.dispose()


def test_login_con_bd_rota_explica_la_causa(client, monkeypatch):
    """Antes: 500 'Error interno del servidor'. Ahora: 503 con la causa y cómo arreglarla."""
    from sqlalchemy.exc import OperationalError
    from app.models import User
    from sqlalchemy.orm import Query

    def boom(*a, **k):
        raise OperationalError("SELECT", {}, Exception('password authentication failed for user "interviewai"'))

    monkeypatch.setattr(Query, "first", boom)
    r = client.post("/api/auth/login", json={"email": "marco.prueba@gmail.com", "password": "Contrasena123"})
    assert r.status_code == 503
    assert r.json()["code"] == "contrasena"
    assert "iniciar" in r.json()["detail"]


def test_health_reporta_bd(client, monkeypatch):
    monkeypatch.setattr(
        "app.main.check_database",
        lambda: {"ok": False, "code": "esquema_desactualizado", "detail": database.HINTS["esquema_desactualizado"]},
    )
    r = client.get("/api/health")
    assert r.status_code == 503
    assert r.json()["database"]["code"] == "esquema_desactualizado"
    assert "sk-" not in r.text and "AQ." not in r.text
