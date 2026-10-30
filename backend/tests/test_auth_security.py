import pytest
from fastapi import HTTPException

from app.auth import validate_real_email, suggest_typo
from app.security import create_access_token, decode_access_token

LEGIT = ["ana.lopez@gmail.com", "ana.lopez@me.com", "ana.lopez@uam.mx", "ana.lopez@msn.com",
         "ana.lopez@up.edu.mx", "ana.lopez@uaq.mx", "ana.lopez@mail.com", "ana.lopez@outlook.es",
         "ana.lopez@hotmail.es", "ana.lopez@itam.mx", "ana.lopez@unal.edu.co", "a01709802@tec.mx"]
TYPOS = ["x.y@gnial.com", "x.y@gmal.com", "x.y@hotmial.com", "x.y@outlok.com", "x.y@gmail.co", "x.y@yahooo.com"]


@pytest.mark.parametrize("email", LEGIT)
def test_correos_reales_no_se_bloquean(email):
    assert validate_real_email(email, verify_dns_mx=False) == email


@pytest.mark.parametrize("email", TYPOS)
def test_errores_de_dedo_se_bloquean(email):
    with pytest.raises(HTTPException):
        validate_real_email(email, verify_dns_mx=False)


def test_sugerencia_de_typo():
    assert suggest_typo("gnial.com") == "gmail.com"
    assert suggest_typo("ibm.com") is None


def test_token_firmado_y_manipulado():
    tok = create_access_token("abc")
    assert decode_access_token(tok) == "abc"
    body, sig = tok.split(".")
    assert decode_access_token(body + "." + sig[:-2] + "AA") is None
    assert decode_access_token("basura") is None


def test_endpoints_protegidos_sin_token(client):
    assert client.get("/api/users/me/history").status_code == 401
    assert client.post("/api/sessions/start", json={}).status_code in (401, 422)
    r = client.post("/api/sessions/start", headers={"Authorization": "Bearer falso.token"},
                    json={"career_code": "ITC", "target_role": "Backend", "cv_text": "x", "job_description_text": "y"})
    assert r.status_code == 401


def test_health_no_expone_llaves(client):
    body = client.get("/api/health").text
    assert "sk-" not in body and "AIza" not in body and "ghp_" not in body


def test_google_rechaza_token_invalido(client):
    r = client.post("/api/auth/google", json={"credential": "aaa.bbb.ccc"})
    assert r.status_code == 401


def test_login_no_revela_si_existe_la_cuenta(client, make_user):
    user, _ = make_user()
    r1 = client.post("/api/auth/login", json={"email": user["email"], "password": "incorrecta"})
    r2 = client.post("/api/auth/login", json={"email": "nadie.aqui@gmail.com", "password": "incorrecta"})
    assert r1.status_code == r2.status_code == 401
    assert r1.json()["detail"] == r2.json()["detail"]


def test_password_corta_rechazada(client):
    r = client.post("/api/auth/register", json={"full_name": "Ana Lopez", "email": "ana.corta@gmail.com",
                                                "password": "123", "university": "Tec"})
    assert r.status_code == 422


def test_cors_restringido(client):
    r = client.options("/api/health", headers={"Origin": "https://sitio-malicioso.com",
                                                "Access-Control-Request-Method": "GET"})
    assert r.headers.get("access-control-allow-origin") != "https://sitio-malicioso.com"
    r = client.options("/api/health", headers={"Origin": "https://marcoflesh.github.io",
                                                "Access-Control-Request-Method": "GET"})
    assert r.headers.get("access-control-allow-origin") == "https://marcoflesh.github.io"
