from typing import Optional
from fastapi import HTTPException, status
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from app.config import settings


def verify_google_token(credential: Optional[str], fallback_email: str, fallback_name: str, fallback_sub: str) -> dict:
    """
    Verifica un token JWT de Google Sign-In si GOOGLE_CLIENT_ID está configurado y se provee credential.
    En modo desarrollo local (sin GOOGLE_CLIENT_ID), permite autenticación limpia con perfil simulado de Google.
    """
    if credential and settings.GOOGLE_CLIENT_ID:
        try:
            idinfo = id_token.verify_oauth2_token(
                credential, google_requests.Request(), settings.GOOGLE_CLIENT_ID
            )
            return {
                "google_sub": idinfo["sub"],
                "email": idinfo.get("email", fallback_email),
                "full_name": idinfo.get("name", fallback_name),
                "avatar_url": idinfo.get("picture"),
            }
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token de Google inválido: {str(exc)}",
            ) from exc

    return {
        "google_sub": fallback_sub or f"google-sub-{fallback_email}",
        "email": fallback_email,
        "full_name": fallback_name,
        "avatar_url": None,
    }
