"""
Cliente único para los proveedores de IA (Gemini, OpenAI y Ollama).

- La llave de Gemini viaja en el header `x-goog-api-key` (no en la URL), así no
  queda registrada en logs de proxies.
- Cada llamada registra proveedor, modelo, código HTTP y latencia. Nunca la llave.
- Si un proveedor falla, se devuelve None y el llamador usa el siguiente.
"""
import logging
import time
from typing import Iterable, List, Optional, Tuple

import httpx

from app.config import settings

logger = logging.getLogger("interviewai.llm")

GEMINI_URL = settings.GEMINI_BASE_URL.rstrip("/") + "/models/{model}:generateContent"
OPENAI_URL = settings.OPENAI_BASE_URL.rstrip("/") + "/chat/completions"

_client = httpx.Client(
    timeout=httpx.Timeout(settings.LLM_TIMEOUT_SECONDS, connect=5.0),
    limits=httpx.Limits(max_connections=50, max_keepalive_connections=20),
)


def _post(url: str, provider: str, model: str, **kwargs) -> httpx.Response:
    """POST con un reintento si el proveedor responde 429/5xx (respeta Retry-After hasta 3 s)."""
    for attempt in range(2):
        started = time.perf_counter()
        resp = _client.post(url, **kwargs)
        _log(provider, model, resp.status_code, started)
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


def call_gemini(prompt: str, system: Optional[str] = None, json_mode: bool = False,
                max_tokens: int = 800) -> Optional[Tuple[str, str]]:
    if not settings.gemini_ready:
        return None
    models: List[str] = [settings.GEMINI_MODEL]
    if settings.GEMINI_FALLBACK_MODEL and settings.GEMINI_FALLBACK_MODEL not in models:
        models.append(settings.GEMINI_FALLBACK_MODEL)
    for model in models:
        body = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": max_tokens},
        }
        if model.startswith("gemini-3"):
            # Respuestas rápidas: razonamiento bajo (familia Gemini 3.x).
            body["generationConfig"]["thinkingConfig"] = {"thinkingLevel": "low"}
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        if json_mode:
            body["generationConfig"]["responseMimeType"] = "application/json"
        started = time.perf_counter()
        try:
            resp = _post(GEMINI_URL.format(model=model), "gemini", model, json=body,
                         headers={"x-goog-api-key": settings.GEMINI_API_KEY})
            if resp.status_code != 200:
                logger.warning("gemini error %s: %s", resp.status_code, resp.text[:300])
                # 400/401/403 = llave o petición inválida -> no tiene caso probar otro modelo
                if resp.status_code in (400, 401, 403):
                    return None
                continue
            parts = resp.json()["candidates"][0]["content"]["parts"]
            text = "".join(p.get("text", "") for p in parts if not p.get("thought")).strip()
            if text:
                return text, f"gemini:{model}"
        except Exception as exc:  # timeout, red, JSON inesperado
            _log("gemini", model, type(exc).__name__, started)
    return None


def call_openai(prompt: str, system: Optional[str] = None, json_mode: bool = False,
                max_tokens: int = 800, temperature: float = 0.2) -> Optional[Tuple[str, str]]:
    if not settings.openai_ready:
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
            logger.warning("openai error %s: %s", resp.status_code, resp.text[:300])
            return None
        text = (resp.json()["choices"][0]["message"]["content"] or "").strip()
        return (text, f"openai:{model}") if text else None
    except Exception as exc:
        _log("openai", model, type(exc).__name__, started)
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
            return result
    return None
