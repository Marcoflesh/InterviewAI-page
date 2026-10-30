"""
Tokens de sesión firmados (HMAC-SHA256) y limitador de peticiones en memoria.

- El frontend recibe `access_token` al iniciar sesión y lo envía en
  `Authorization: Bearer <token>`.
- El backend ya NO confía en el `user_id` que manda el navegador: lo toma del token.
"""
import base64
import hashlib
import hmac
import json
import threading
import time
from collections import defaultdict, deque
from typing import Deque, Dict, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings

_bearer = HTTPBearer(auto_error=False)


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64d(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def create_access_token(user_id: str) -> str:
    now = int(time.time())
    payload = {"sub": str(user_id), "iat": now, "exp": now + settings.ACCESS_TOKEN_TTL_MINUTES * 60}
    body = _b64(json.dumps(payload, separators=(",", ":")).encode())
    sig = hmac.new(settings.SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest()
    return f"{body}.{_b64(sig)}"


def decode_access_token(token: str) -> Optional[str]:
    try:
        body, sig = token.split(".", 1)
        expected = hmac.new(settings.SECRET_KEY.encode(), body.encode(), hashlib.sha256).digest()
        if not hmac.compare_digest(expected, _b64d(sig)):
            return None
        payload = json.loads(_b64d(body))
        if int(payload.get("exp", 0)) < int(time.time()):
            return None
        return str(payload["sub"])
    except Exception:
        return None


def get_current_user_id(
    creds: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
) -> str:
    if not creds or creds.scheme.lower() != "bearer":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Inicia sesión para continuar.")
    user_id = decode_access_token(creds.credentials)
    if not user_id:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Tu sesión expiró. Inicia sesión de nuevo.")
    return user_id


# ---------------------------------------------------------------------------
# Limitador de peticiones (ventana deslizante de 60 s por IP y por ruta).
# Suficiente para un solo contenedor; en producción con varias réplicas usar Redis.
# ---------------------------------------------------------------------------
_hits: Dict[str, Deque[float]] = defaultdict(deque)
_lock = threading.Lock()


def _client_ip(request: Request) -> str:
    fwd = request.headers.get("x-real-ip") or request.headers.get("x-forwarded-for", "")
    if fwd:
        return fwd.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def rate_limit(limit_per_minute: int):
    def dependency(request: Request) -> None:
        key = f"{_client_ip(request)}:{request.url.path}"
        now = time.monotonic()
        with _lock:
            q = _hits[key]
            while q and now - q[0] > 60:
                q.popleft()
            if len(q) >= limit_per_minute:
                raise HTTPException(
                    status.HTTP_429_TOO_MANY_REQUESTS,
                    "Demasiadas solicitudes. Espera un minuto e intenta de nuevo.",
                )
            q.append(now)

    return dependency


def reset_rate_limits() -> None:
    with _lock:
        _hits.clear()
