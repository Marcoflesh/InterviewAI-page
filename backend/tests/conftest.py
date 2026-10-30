"""
Pruebas del backend contra un PostgreSQL REAL (el mismo init.sql que usa Docker).

    TEST_DATABASE_URL=postgresql://interviewai:<pass>@127.0.0.1:5432/interviewai_test pytest -q

Las llamadas a OpenAI/Gemini se simulan aquí; para probar las APIs reales usa
scripts/stress_test_agents.py (consume tu saldo).
"""
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

TEST_DB = os.getenv("TEST_DATABASE_URL")
if not TEST_DB:
    pytest.skip("Define TEST_DATABASE_URL para correr las pruebas de integración.", allow_module_level=True)

os.environ.update({
    "DATABASE_URL": TEST_DB,
    "OPENAI_API_KEY": "",
    "GEMINI_API_KEY": "",
    "GOOGLE_CLIENT_ID": "123-test.apps.googleusercontent.com",
    "SECRET_KEY": "test-secret-key-solo-para-pruebas",
    "EMAIL_MX_CHECK": "off",
    "RATE_LIMIT_AUTH_PER_MINUTE": "1000",
    "RATE_LIMIT_TURN_PER_MINUTE": "1000",
})


@pytest.fixture(scope="session")
def client():
    from fastapi.testclient import TestClient
    from app.main import app
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture
def make_user(client):
    import uuid

    def _make(name="Ana Prueba Lopez"):
        email = f"ana.{uuid.uuid4().hex[:10]}@gmail.com"
        r = client.post("/api/auth/register", json={
            "full_name": name, "email": email, "password": "Contrasena123", "university": "Tec"})
        assert r.status_code == 200, r.text
        data = r.json()
        return data, {"Authorization": f"Bearer {data['access_token']}"}

    return _make
