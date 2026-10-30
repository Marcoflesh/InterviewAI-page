"""
Autenticación: contraseñas (PBKDF2-HMAC-SHA256), validador de correos reales y
verificación criptográfica del token de Google Identity Services.
"""
import hashlib
import hmac
import logging
import os
import re
from typing import Optional

import httpx
import requests
from fastapi import HTTPException, status
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token

from app.config import settings

logger = logging.getLogger("interviewai.auth")

EMAIL_FORMAT_REGEX = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9._%+-]{0,62}[A-Za-z0-9])?@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9-]{2,})*\.[A-Za-z]{2,}$"
)

# Dominios de prueba, desechables o con errores de dedo frecuentes
BLOCKED_FAKE_DOMAINS = {
    "ejemplo.com", "example.com", "test.com", "prueba.com", "correo.com",
    "dominio.com", "usuario.com", "mailinator.com", "tempmail.com",
    "10minutemail.com", "guerrillamail.com", "yopmail.com", "trashmail.com",
    "sharklasers.com", "fakeinbox.com", "getnada.com", "maildrop.cc",
    "dispostable.com", "fake.com", "asdf.com", "qwerty.com", "none.com",
    "gnial.com", "gmal.com", "gmial.com", "gamil.com", "gmai.com", "gmail.co",
    "hotmial.com", "hotmal.com", "outlok.com", "outllok.com", "yaho.com",
}

# Proveedores contra los que se buscan errores de dedo (solo dominios largos y muy usados)
TYPO_TARGETS = ["gmail.com", "hotmail.com", "outlook.com", "yahoo.com", "icloud.com"]

TRUSTED_KNOWN_DOMAINS = {
    "gmail.com", "googlemail.com", "outlook.com", "outlook.es", "hotmail.com",
    "hotmail.es", "live.com", "live.com.mx", "msn.com", "icloud.com", "me.com",
    "mac.com", "yahoo.com", "yahoo.com.mx", "yahoo.es", "aol.com", "mail.com",
    "gmx.com", "proton.me", "protonmail.com", "pm.me", "zoho.com",
    "tec.mx", "itesm.mx", "exatec.tec.mx", "unam.mx", "comunidad.unam.mx",
    "ipn.mx", "alumno.ipn.mx", "uam.mx", "ibero.mx", "iberopuebla.mx",
    "anahuac.mx", "udem.edu.mx", "up.edu.mx", "udg.mx", "uanl.mx", "uaq.mx", "itam.mx",
}

ACADEMIC_SUFFIX = re.compile(r"\.(edu|edu\.[a-z]{2}|ac\.[a-z]{2}|gob\.[a-z]{2})$")


def _edit_distance(a: str, b: str) -> int:
    """Distancia Damerau-Levenshtein (una letra intercambiada cuenta como 1 error)."""
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        d[i][0] = i
    for j in range(len(b) + 1):
        d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[len(a)][len(b)]


def suggest_typo(domain: str) -> Optional[str]:
    """Devuelve el proveedor correcto si `domain` parece un error de dedo (p. ej. gnial.com)."""
    if domain in TRUSTED_KNOWN_DOMAINS or ACADEMIC_SUFFIX.search(domain):
        return None
    for target in TYPO_TARGETS:
        if 0 < _edit_distance(domain, target) <= 2:
            return target
    return None


def _domain_has_mx(domain: str) -> Optional[bool]:
    """True/False si se pudo consultar DNS; None si no hubo forma de verificar."""
    try:
        import dns.resolver  # dnspython (resolver del sistema)

        try:
            answers = dns.resolver.resolve(domain, "MX", lifetime=3.0)
            return any(str(r.exchange).strip(".") for r in answers)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return False
    except Exception:
        pass
    try:  # Respaldo: Google DNS-over-HTTPS
        resp = httpx.get("https://dns.google/resolve", params={"name": domain, "type": "MX"}, timeout=3.0)
        if resp.status_code == 200:
            data = resp.json()
            return data.get("Status") == 0 and bool(data.get("Answer"))
    except Exception:
        pass
    return None


def validate_real_email(email: str, verify_dns_mx: bool = True) -> str:
    """
    1) Sintaxis estricta. 2) Bloqueo de dominios falsos/desechables y errores de dedo.
    3) Verificación de registros MX (EMAIL_MX_CHECK=strict rechaza si no se puede verificar).
    """
    clean = (email or "").strip().lower()
    if len(clean) > 254 or not EMAIL_FORMAT_REGEX.match(clean) or ".." in clean:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El formato del correo electrónico no es válido.")

    local_part, domain = clean.split("@", 1)
    if len(local_part) < 2:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "El usuario del correo es demasiado corto.")

    if domain in BLOCKED_FAKE_DOMAINS:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, f"El dominio '@{domain}' no es un proveedor de correo válido.")

    typo = suggest_typo(domain)
    if typo:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"El dominio '@{domain}' parece mal escrito (¿quisiste escribir '@{typo}'?).",
        )

    mode = (settings.EMAIL_MX_CHECK or "strict").lower()
    if verify_dns_mx and mode != "off" and domain not in TRUSTED_KNOWN_DOMAINS:
        has_mx = _domain_has_mx(domain)
        if has_mx is False or (has_mx is None and mode == "strict"):
            raise HTTPException(
                status.HTTP_400_BAD_REQUEST,
                f"No pudimos confirmar que '@{domain}' reciba correos (registros MX). Usa un correo real.",
            )
    return clean


def hash_password(password: str, salt: Optional[str] = None) -> str:
    salt_val = salt or os.urandom(16).hex()
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_val.encode("utf-8"), 310_000)
    return f"{salt_val}${dk.hex()}"


def _legacy_hash(password: str, salt_val: str) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt_val.encode("utf-8"), 100_000)
    return f"{salt_val}${dk.hex()}"


def verify_password(plain_password: str, stored_hash: Optional[str]) -> bool:
    if not stored_hash or "$" not in stored_hash:
        return False
    salt_val, _ = stored_hash.split("$", 1)
    if hmac.compare_digest(hash_password(plain_password, salt=salt_val), stored_hash):
        return True
    # Cuentas creadas con v0.3.0 (100k iteraciones)
    return hmac.compare_digest(_legacy_hash(plain_password, salt_val), stored_hash)


# Sesión HTTP reutilizable para descargar (y cachear por conexión) las llaves públicas de Google
_google_session = requests.Session()


def _google_error_message(exc: Exception) -> str:
    msg = str(exc)
    if "Token used too early" in msg or "Token expired" in msg:
        return ("La hora de tu computadora o del contenedor está desfasada. Sincroniza el reloj "
                "(Windows: Configuración > Hora > Sincronizar ahora) y reinicia Docker.")
    if "audience" in msg.lower() or "Wrong recipient" in msg:
        return ("El token pertenece a otro Client ID. El GOOGLE_CLIENT_ID del backend (.env) debe ser "
                "exactamente el mismo que usa el frontend.")
    if "certs" in msg or "Max retries" in msg or "connect" in msg.lower():
        return "El backend no pudo contactar a Google para validar el token. Revisa la conexión a internet del contenedor."
    return "Google rechazó la credencial. Vuelve a intentarlo."


def verify_google_token(credential: Optional[str]) -> dict:
    """
    Verifica la firma, emisor, expiración y AUDIENCIA (GOOGLE_CLIENT_ID) del JWT de Google.
    Sin GOOGLE_CLIENT_ID no se acepta ningún token (antes se aceptaban tokens de cualquier app).
    """
    if not settings.google_signin_ready:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            "El inicio con Google no está configurado en el servidor (GOOGLE_CLIENT_ID en .env).",
        )
    if not credential or credential.count(".") != 2:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No se recibió una credencial válida de Google.")
    try:
        idinfo = id_token.verify_oauth2_token(
            credential,
            google_requests.Request(session=_google_session),
            settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=settings.GOOGLE_CLOCK_SKEW_SECONDS,
        )
    except Exception as exc:
        logger.warning("Google token rechazado: %s", exc)
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, _google_error_message(exc)) from exc

    if not idinfo.get("email_verified", False):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Tu cuenta de Google no tiene el correo verificado.")
    email = str(idinfo.get("email", "")).strip().lower()
    if not EMAIL_FORMAT_REGEX.match(email):
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Google no entregó un correo válido.")
    return {
        "google_sub": idinfo["sub"],
        "email": email,  # Google ya verificó el correo: no se aplica el filtro de dominios
        "full_name": idinfo.get("name") or email.split("@")[0],
        "avatar_url": idinfo.get("picture"),
    }
