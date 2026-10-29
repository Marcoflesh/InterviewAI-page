import hashlib
import hmac
import os
import re
from typing import Optional
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.config import settings

EMAIL_FORMAT_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def validate_email_format(email: str) -> str:
    clean = (email or "").strip().lower()
    if not EMAIL_FORMAT_REGEX.match(clean):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El formato del correo electrónico no es válido.",
        )
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
    fallback_email: str,
    fallback_name: str,
    fallback_sub: str,
    fallback_avatar: Optional[str] = None,
) -> dict:
    """
    Verifica un token JWT real de Google Identity Services si se envía `credential`,
    o valida los datos de perfil de Google OAuth verificando el formato real del correo.
    """
    if credential and settings.GOOGLE_CLIENT_ID:
        try:
            idinfo = id_token.verify_oauth2_token(
                credential, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )
            if not idinfo.get("email_verified", True):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="La cuenta de Google no tiene el correo verificado.",
                )
            return {
                "google_sub": idinfo["sub"],
                "email": validate_email_format(idinfo.get("email", fallback_email)),
                "full_name": idinfo.get("name", fallback_name),
                "avatar_url": idinfo.get("picture", fallback_avatar),
            }
        except HTTPException:
            raise
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token de Google inválido: {str(exc)}",
            ) from exc

    clean_email = validate_email_format(fallback_email)
    if not fallback_name or len(fallback_name.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El perfil de Google debe incluir un nombre válido.",
        )

    return {
        "google_sub": fallback_sub or f"google-sub-{clean_email}",
        "email": clean_email,
        "full_name": fallback_name.strip(),
        "avatar_url": fallback_avatar,
    }
