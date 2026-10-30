"""Cliente de IA: respuestas vacías de Gemini 3.x, 404 de modelo retirado y OpenAI sin saldo (30/10/2026)."""
import json

import httpx
import pytest

from app import llm
from app.config import settings


@pytest.fixture
def fake_api(monkeypatch):
    calls = []

    def install(handler):
        def wrapped(request):
            calls.append(request)
            return handler(request)
        monkeypatch.setattr(llm, "_client", httpx.Client(transport=httpx.MockTransport(wrapped)))
        return calls

    monkeypatch.setattr(settings, "GEMINI_API_KEY", "AQ.falsa.solo.pruebas")
    monkeypatch.setattr(settings, "OPENAI_API_KEY", "sk-svcacct-prueba")
    monkeypatch.setattr(settings, "GEMINI_MODEL", "gemini-3.8-flash")
    monkeypatch.setattr(settings, "GEMINI_FALLBACK_MODEL", "")
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    llm.reset_status()
    yield install
    llm.reset_status()


def test_gemini_respuesta_vacia_por_pensamiento_se_reporta(fake_api):
    calls = fake_api(lambda r: httpx.Response(200, json={
        "candidates": [{"content": {"role": "model"}, "finishReason": "MAX_TOKENS"}],
        "usageMetadata": {"thoughtsTokenCount": 1990, "candidatesTokenCount": 0}}))
    assert llm.call_gemini("hola", json_mode=True, max_tokens=1200) is None
    detail = llm.status()["ultimo"]["gemini"]["detail"]
    assert "MAX_TOKENS" in detail and "1990" in detail
    body = json.loads(calls[0].content)
    assert body["generationConfig"]["maxOutputTokens"] >= 8192
    assert body["generationConfig"]["thinkingConfig"] == {"thinkingLevel": "low"}
    assert "temperature" not in body["generationConfig"]
    assert calls[0].headers["x-goog-api-key"].startswith("AQ.") and "key=" not in str(calls[0].url)


def test_gemini_ignora_pensamientos_y_devuelve_texto(fake_api):
    fake_api(lambda r: httpx.Response(200, json={"candidates": [{"content": {"parts": [
        {"text": "razonando...", "thought": True}, {"text": "{\"ok\": true}"}]}}]}))
    assert llm.call_gemini("hola") == ('{"ok": true}', "gemini:gemini-3.8-flash")
    assert llm.status()["ultimo"]["gemini"]["ok"] is True


def test_modelo_retirado_se_pausa(fake_api, monkeypatch):
    monkeypatch.setattr(settings, "GEMINI_FALLBACK_MODEL", "gemini-2.5-flash")

    def handler(r):
        if "gemini-2.5-flash" in str(r.url):
            return httpx.Response(404, json={"error": {"message": "no longer available to new users"}})
        return httpx.Response(503, json={"error": {"message": "overloaded"}})
    calls = fake_api(handler)
    llm.call_gemini("hola")
    n = len(calls)
    llm.call_gemini("hola")
    assert not any("gemini-2.5-flash" in str(c.url) for c in calls[n:])  # ya no se vuelve a intentar
    assert "gemini:gemini-2.5-flash" in llm.status()["en_pausa"]


def test_openai_sin_saldo_no_reintenta_y_se_pausa(fake_api):
    calls = fake_api(lambda r: httpx.Response(429, json={"error": {
        "message": "You have no credits remaining.", "type": "insufficient_quota", "code": "credit_balance_exhausted"}}))
    assert llm.call_openai("hola") is None
    assert len(calls) == 1  # sin reintento inútil
    assert llm.call_openai("hola") is None
    assert len(calls) == 1  # en pausa: ni siquiera se llama
    assert "saldo" in llm.status()["en_pausa"]["openai"]["motivo"]


def test_complete_usa_gemini_si_openai_no_tiene_saldo(fake_api):
    def handler(r):
        if "openai" in str(r.url):
            return httpx.Response(429, json={"error": {"code": "credit_balance_exhausted"}})
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "¿Me cuentas de un proyecto?"}]}}]})
    fake_api(handler)
    text, source = llm.complete("x", preferred="openai")
    assert source.startswith("gemini") and text.startswith("¿Me cuentas")


def test_ollama_desactiva_pensamiento_y_mantiene_modelo(fake_api, monkeypatch):
    monkeypatch.setattr(settings, "OLLAMA_ENABLED", True)
    monkeypatch.setattr(settings, "OLLAMA_MODEL", "qwen3.5:4b")
    calls = fake_api(lambda r: httpx.Response(200, json={"message": {"content": "¿Me cuentas del bug más difícil?"}}))
    text, src = llm.call_ollama("hola", system="sistema")
    body = json.loads(calls[0].content)
    assert src == "ollama:qwen3.5:4b" and text.startswith("¿Me cuentas")
    assert body["think"] is False and body["stream"] is False and body["keep_alive"]
    assert "think" not in body["options"]  # dentro de options Ollama lo ignora


def test_ollama_modelo_no_descargado_se_pausa(fake_api, monkeypatch):
    monkeypatch.setattr(settings, "OLLAMA_ENABLED", True)
    calls = fake_api(lambda r: httpx.Response(404, json={"error": "model 'qwen3.5:4b' not found"}))
    assert llm.call_ollama("hola") is None
    assert llm.call_ollama("hola") is None
    assert len(calls) == 1
    assert "descargado" in llm.status()["en_pausa"]["ollama"]["motivo"]


def test_entrevistador_prefiere_ollama_y_cae_a_gemini(fake_api, monkeypatch):
    monkeypatch.setattr(settings, "OLLAMA_ENABLED", True)

    def handler(r):
        if "/api/chat" in str(r.url):
            raise httpx.ConnectError("sin servidor")
        return httpx.Response(200, json={"candidates": [{"content": {"parts": [{"text": "¿Qué hiciste tú?"}]}}]})
    fake_api(handler)
    assert llm.provider_order("ollama")[:2] == ["ollama", "gemini"]
    text, src = llm.complete("x", preferred="ollama")
    assert src.startswith("gemini")
