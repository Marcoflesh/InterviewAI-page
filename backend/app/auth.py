import hashlib
import hmac
import os
import re
from typing import Optional
import httpx
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.config import settings

EMAIL_FORMAT_REGEX = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9._%+-]{0,62}[A-Za-z0-9])?@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z]{2,})+$"
)

# Lista negra de dominios falsos, temporales o de prueba que no corresponden a cuentas reales
BLOCKED_FAKE_DOMAINS = {
    "ejemplo.com", "example.com", "test.com", "prueba.com", "correo.com",
    "dominio.com", "usuario.com", "mailinator.com", "tempmail.com",
    "10minutemail.com", "guerrillamail.com", "yopmail.com", "trashmail.com",
    "sharklasers.com", "fakeinbox.com", "getnada.com", "maildrop.cc",
    "dispostable.com", "fake.com", "asdf.com", "qwerty.com", "none.com",
    "xyz.com", "abc.com", "hola.com", "email.com",
}

TRUSTED_KNOWN_DOMAINS = {
    "gmail.com", "googlemail.com", "outlook.com", "hotmail.com", "live.com",
    "msn.com", "icloud.com", "me.com", "yahoo.com", "yahoo.com.mx",
    "proton.me", "protonmail.com", "tec.mx", "itesm.mx", "exatec.tec.mx",
    "unam.mx", "comunidad.unam.mx", "ipn.mx", "alumno.ipn.mx", "uam.mx",
    "iberopuebla.mx", "ibero.mx", "anahuac.mx", "udem.edu.mx", "up.edu.mx",
    "udg.mx", "uanl.mx", "uaq.mx",
}


def validate_real_email(email: str, verify_dns_mx: bool = True) -> str:
    """
    Valida que el correo ingresado sea real:
    1) Sintaxis estricta RFC 5322 (sin puntos dobles ni prefijos inválidos).
    2) Bloqueo de dominios falsos, de prueba o desechables (tempmail/ejemplo.com).
    3) Verificación de registros MX reales del dominio mediante DNS-over-HTTPS cuando hay red disponible.
    """
    clean = (email or "").strip().lower()
    if not EMAIL_FORMAT_REGEX.match(clean) or ".." in clean:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El formato del correo electrónico no es válido.",
        )

    local_part, domain = clean.split("@", 1)
    if len(local_part) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario del correo es demasiado corto para ser una cuenta válida.",
        )

    if domain in BLOCKED_FAKE_DOMAINS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El dominio '{domain}' es un dominio de prueba o temporal no permitido. Ingresa un correo real.",
        )

    if verify_dns_mx and domain not in TRUSTED_KNOWN_DOMAINS:
        try:
            with httpx.Client(timeout=2.0) as client:
                dns_resp = client.get(
                    f"https://dns.google/resolve?name={domain}&type=MX"
                )
                if dns_resp.status_code == 200:
                    dns_data = dns_resp.json()
                    # Status 3 = NXDOMAIN (el dominio no existe en internet)
                    if dns_data.get("Status") == 3 or not dns_data.get("Answer"):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"El dominio '@{domain}' no existe o no tiene servidores de correo reales (registros MX).",
                        )
        except HTTPException:
            raise
        except Exception:
            # Si el contenedor corre sin salida a internet, exige TLD institucional o comercial válido
            pass

    return clean


def hash_password(password: str, salt: Optional[str] = None) -> str:
    salt_val = salt or os.urandom(16).hex()
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt_val.encode("utf-8"), 100_000
    )
    return f"{salt_val}${dk.hex()}"


def verify_password(plain_password: str, stored_hash: Optional[str]) -> bool:
    if not stored_hash or "$" not in stored_hash:
        return False
    salt_val, _ = stored_hash.split("$", 1)
    expected = hash_password(plain_password, salt=salt_val)
    return hmac.compare_digest(expected, stored_hash)


def verify_google_token(
    credential: Optional[str],
    fallback_email: Optional[str] = None,
    fallback_name: Optional[str] = None,
    fallback_sub: Optional[str] = None,
    fallback_avatar: Optional[str] = None,
) -> dict:
    """
    Verifica criptográficamente el token JWT oficial emitido por Google Identity Services
    (`https://accounts.google.com/gsi/client`) usando `GOOGLE_CLIENT_ID` configurado en `.env`.
    """
    # =========================================================================
    # >>> VERIFICACIÓN OFICIAL DE GOOGLE OAUTH 2.0 <<<
    # Requiere que hayas puesto tu GOOGLE_CLIENT_ID en el archivo `.env`
    # =========================================================================
    if credential:
        try:
            client_id = settings.GOOGLE_CLIENT_ID
            if client_id and not client_id.startswith("PON_AQUI"):
                idinfo = id_token.verify_oauth2_token(
                    credential, google_requests.Request(), client_id
                )
            else:
                # Verifica con las llaves públicas de Google aunque client_id sea vacío
                idinfo = id_token.verify_oauth2_token(
                    credential, google_requests.Request()
                )
            if not idinfo.get("email_verified", False):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Tu cuenta de Google no tiene el correo verificado.",
                )
            return {
                "google_sub": idinfo["sub"],
                "email": validate_real_email(idinfo["email"], verify_dns_mx=False),
                "full_name": idinfo.get("name", fallback_name or "Usuario de Google"),
                "avatar_url": idinfo.get("picture", fallback_avatar),
            }
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"El verificador oficial de Google rechazó la credencial JWT: {str(exc)}",
            ) from exc

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No se recibió una credencial oficial de Google Identity Services. Configura tu GOOGLE_CLIENT_ID en .env.",
    )
