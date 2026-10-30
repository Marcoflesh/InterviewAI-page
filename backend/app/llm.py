"""
Cliente único para los proveedores de IA (Gemini, OpenAI y Ollama).

- La llave de Gemini viaja en el header `x-goog-api-key` (no en la URL), así no
  queda registrada en logs de proxies.
- Cada llamada registra proveedor, modelo, código HTTP y latencia. Nunca la llave.
- Si un proveedor falla, se devuelve None y el llamador usa el siguiente.
- Cortacircuitos: si un proveedor no tiene saldo, la llave es inválida o el modelo no
  existe, se deja de intentar por un tiempo (no se pierden segundos en cada llamada).
- `status()` resume el último resultado de cada proveedor (lo muestra /api/health).
"""
import logging
import re
import threading
import time
from typing import Dict, Iterable, List, Optional, Tuple

import httpx

from app.config import settings

logger = logging.getLogger("interviewai.llm")

GEMINI_URL = settings.GEMINI_BASE_URL.rstrip("/") + "/models/{model}:generateContent"
OPENAI_URL = settings.OPENAI_BASE_URL.rstrip("/") + "/chat/completions"

_client = httpx.Client(
    timeout=httpx.Timeout(settings.LLM_TIMEOUT_SECONDS, connect=5.0),
    limits=httpx.Limits(max_connections=120, max_keepalive_connections=40),
)


# ---------------------------------------------------------------------------
# Estado y cortacircuitos por proveedor/modelo
# ---------------------------------------------------------------------------
_state_lock = threading.Lock()
_disabled: Dict[str, Tuple[float, str]] = {}   # clave -> (hasta_cuando, motivo)
_last: Dict[str, Dict[str, object]] = {}       # proveedor -> último resultado

_NO_CREDIT = re.compile(r"insufficient_quota|credit_balance_exhausted|billing|no credits", re.I)


def _record(provider: str, ok: bool, detail: str, model: str = "") -> None:
    with _state_lock:
        _last[provider] = {"ok": ok, "model": model, "detail": detail[:240], "at": int(time.time())}


def _disable(key: str, seconds: float, reason: str) -> None:
    with _state_lock:
        already = key in _disabled and _disabled[key][0] > time.time()
        _disabled[key] = (time.time() + seconds, reason)
    if not already:
        logger.warning("IA desactivada temporalmente: %s (%d min) -> %s", key, seconds // 60, reason)


def _is_disabled(key: str) -> bool:
    with _state_lock:
        until = _disabled.get(key)
        if until and until[0] > time.time():
            return True
        _disabled.pop(key, None)
        return False


def status() -> Dict[str, object]:
    """Resumen sin secretos: último resultado y proveedores en pausa."""
    now = time.time()
    with _state_lock:
        paused = {k: {"motivo": r, "segundos_restantes": int(t - now)} for k, (t, r) in _disabled.items() if t > now}
        return {"ultimo": dict(_last), "en_pausa": paused}


def reset_status() -> None:
    with _state_lock:
        _disabled.clear()
        _last.clear()


def _post(url: str, provider: str, model: str, **kwargs) -> httpx.Response:
    """POST con un reintento si el proveedor responde 429/5xx (respeta Retry-After hasta 3 s).
    No reintenta si el 429 es por falta de saldo (no se va a arreglar solo)."""
    for attempt in range(2):
        started = time.perf_counter()
        resp = _client.post(url, **kwargs)
        _log(provider, model, resp.status_code, started)
        if resp.status_code == 429 and _NO_CREDIT.search(resp.text or ""):
            return resp
        if resp.status_code in (429, 500, 502, 503, 504) and attempt == 0:
            try:
                wait = min(3.0, float(resp.headers.get("retry-after", "1")))
            except ValueError:
                wait = 1.0
            time.sleep(wait)
            continue
        return resp
    return resp


def _log(provider: str, model: str, status: object, started: float) -> None:
    logger.info("llm provider=%s model=%s status=%s latency_ms=%d",
                provider, model, status, int((time.perf_counter() - started) * 1000))


def _gemini_text(data: dict) -> Tuple[str, str]:
    """Extrae el texto final (sin 'pensamientos'). Devuelve (texto, motivo_si_vacío)."""
    candidates = data.get("candidates") or []
    if not candidates:
        fb = data.get("promptFeedback") or {}
        return "", f"sin candidatos (bloqueo: {fb.get('blockReason', 'desconocido')})"
    cand = candidates[0]
    parts = (cand.get("content") or {}).get("parts") or []
    text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
    if text:
        return text, ""
    usage = data.get("usageMetadata") or {}
    return "", (f"respuesta vacía (finishReason={cand.get('finishReason')}, "
                f"tokens de pensamiento={usage.get('thoughtsTokenCount')}, "
                f"tokens de salida={usage.get('candidatesTokenCount')})")


def call_gemini(prompt: str, system: Optional[str] = None, json_mode: bool = False,
                max_tokens: int = 800) -> Optional[Tuple[str, str]]:
    if not settings.gemini_ready or _is_disabled("gemini"):
        return None
    models: List[str] = [settings.GEMINI_MODEL]
    if settings.GEMINI_FALLBACK_MODEL and settings.GEMINI_FALLBACK_MODEL not in models:
        models.append(settings.GEMINI_FALLBACK_MODEL)
    for model in models:
        if _is_disabled(f"gemini:{model}"):
            continue
        # Los modelos Gemini 3.x "piensan" antes de responder y ese razonamiento también
        # consume tokens de salida: con poco margen la respuesta llega vacía.
        out_tokens = max(max_tokens, settings.GEMINI_MAX_OUTPUT_TOKENS) if model.startswith("gemini-3") else max_tokens
        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": out_tokens},
        }
        if model.startswith("gemini-3"):
            body["generationConfig"]["thinkingConfig"] = {"thinkingLevel": settings.GEMINI_THINKING_LEVEL}
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        if json_mode:
            body["generationConfig"]["responseMimeType"] = "application/json"
        started = time.perf_counter()
        try:
            resp = _post(GEMINI_URL.format(model=model), "gemini", model, json=body,
                         headers={"x-goog-api-key": settings.GEMINI_API_KEY})
            if resp.status_code != 200:
                detail = f"HTTP {resp.status_code}: {resp.text[:300]}"
                logger.warning("gemini %s error %s", model, detail)
                _record("gemini", False, detail, model)
                if resp.status_code == 404:
                    _disable(f"gemini:{model}", 24 * 3600, "el modelo no existe o no está disponible para esta cuenta")
                    continue
                if resp.status_code in (401, 403):
                    _disable("gemini", 600, "llave inválida o sin permiso")
                    return None
                if resp.status_code == 400:
                    return None  # petición inválida: otro modelo no lo arregla
                continue
            text, why = _gemini_text(resp.json())
            if text:
                _record("gemini", True, f"{int((time.perf_counter() - started) * 1000)} ms", model)
                return text, f"gemini:{model}"
            logger.warning("gemini %s: %s", model, why)
            _record("gemini", False, why, model)
        except Exception as exc:  # timeout, red, JSON inesperado
            detail = f"{type(exc).__name__}: {str(exc)[:160]}"
            logger.warning("gemini %s falló: %s", model, detail)
            _record("gemini", False, detail, model)
    return None


def call_openai(prompt: str, system: Optional[str] = None, json_mode: bool = False,
                max_tokens: int = 800, temperature: float = 0.2) -> Optional[Tuple[str, str]]:
    if not settings.openai_ready or _is_disabled("openai"):
        return None
    model = settings.OPENAI_CHAT_MODEL
    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": prompt}
    ]
    body = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    if json_mode:
        body["response_format"] = {"type": "json_object"}
    started = time.perf_counter()
    try:
        resp = _post(OPENAI_URL, "openai", model, json=body,
                     headers={"Authorization": f"Bearer {settings.OPENAI_API_KEY}"})
        if resp.status_code != 200:
            detail = f"HTTP {resp.status_code}: {resp.text[:300]}"
            logger.warning("openai error %s", detail)
            _record("openai", False, detail, model)
            if resp.status_code == 429 and _NO_CREDIT.search(resp.text or ""):
                _disable("openai", 600, "la cuenta de OpenAI no tiene saldo (agrega créditos en Billing)")
            elif resp.status_code in (401, 403):
                _disable("openai", 600, "llave inválida o sin permiso")
            elif resp.status_code == 404:
                _disable("openai", 3600, f"el modelo {model} no existe para esta cuenta")
            return None
        text = (resp.json()["choices"][0]["message"]["content"] or "").strip()
        _record("openai", bool(text), f"{int((time.perf_counter() - started) * 1000)} ms", model)
        return (text, f"openai:{model}") if text else None
    except Exception as exc:
        detail = f"{type(exc).__name__}: {str(exc)[:160]}"
        logger.warning("openai falló: %s", detail)
        _record("openai", False, detail, model)
        return None


def call_ollama(prompt: str, system: Optional[str] = None, json_mode: bool = False,
                max_tokens: int = 800) -> Optional[Tuple[str, str]]:
    if not settings.OLLAMA_ENABLED:
        return None
    model = settings.OLLAMA_MODEL
    messages = ([{"role": "system", "content": system}] if system else []) + [
        {"role": "user", "content": prompt}
    ]
    body = {"model": model, "messages": messages, "stream": False,
            "options": {"temperature": 0.1, "num_predict": max_tokens}}
    if json_mode:
        body["format"] = "json"
    started = time.perf_counter()
    try:
        resp = _client.post(f"{settings.OLLAMA_BASE_URL}/api/chat", json=body)
        _log("ollama", model, resp.status_code, started)
        if resp.status_code != 200:
            return None
        text = (resp.json().get("message", {}).get("content") or "").strip()
        return (text, f"ollama:{model}") if text else None
    except Exception as exc:
        _log("ollama", model, type(exc).__name__, started)
        return None


_PROVIDERS = {"gemini": call_gemini, "openai": call_openai, "ollama": call_ollama}


# Emojis y pictogramas (no toca letras con acento ni signos del español)
_EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF\U0001F1E6-\U0001F1FF\u2600-\u27BF\u2B00-\u2BFF"
    "\u2300-\u23FF\uFE0E\uFE0F\u200D\u20E3]"
)


def strip_emojis(text: str) -> str:
    return re.sub(r"[ \t]{2,}", " ", _EMOJI.sub("", text or "")).strip()


def provider_order(preferred: str) -> List[str]:
    preferred = (preferred or "").lower()
    order = [preferred] if preferred in _PROVIDERS else []
    return order + [p for p in ("gemini", "openai", "ollama") if p not in order]


def complete(prompt: str, preferred: str, system: Optional[str] = None,
             json_mode: bool = False, max_tokens: int = 800,
             order: Optional[Iterable[str]] = None) -> Optional[Tuple[str, str]]:
    """Intenta el proveedor preferido y luego los demás. Devuelve (texto, 'proveedor:modelo')."""
    for name in order or provider_order(preferred):
        result = _PROVIDERS[name](prompt, system=system, json_mode=json_mode, max_tokens=max_tokens)
        if result:
            return strip_emojis(result[0]), result[1]  # la app nunca muestra emojis
    return None
