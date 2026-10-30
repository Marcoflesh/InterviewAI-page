#!/usr/bin/env python3
"""
Servidor FALSO de OpenAI + Gemini para probar el backend bajo carga sin gastar saldo.
Simula latencias realistas, errores 429/503 y un modelo que a veces "cae" en la
inyección de prompt (para comprobar el guardrail).

    python scripts/mock_llm_server.py --port 9999
    OPENAI_BASE_URL=http://127.0.0.1:9999/v1 GEMINI_BASE_URL=http://127.0.0.1:9999/v1beta ...

Los resultados obtenidos con este servidor miden al BACKEND, no la calidad real de los modelos.
"""
import argparse
import asyncio
import json
import random
import re

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()
CFG = {"err429": 0.03, "err503": 0.01, "median_openai": 1.4, "median_gemini": 2.0}


def fake_eval(text: str) -> dict:
    m = re.search(r"<respuesta_candidato>\s*(.*?)\s*</respuesta_candidato>", text, re.S)
    resp = (m.group(1) if m else text).lower()
    if "ignora" in resp or "system:" in resp:
        base = 5 if random.random() < 0.5 else 0  # a veces el modelo "obedece" la inyección
    else:
        words = len(resp.split())
        nums = len(re.findall(r"\d+", resp))
        base = min(5, words // 15 + (1 if nums else 0))
    j = lambda: max(0, min(5, base + random.choice([-1, 0, 0, 1])))  # noqa: E731
    return {"star_situation": j(), "star_task": j(), "star_action": j(), "star_result": j(),
            "technical_clarity": j(), "relevance": j(), "strengths": "Simulado.", "improvement_areas": "Simulado."}


async def maybe_fail(median: float):
    await asyncio.sleep(random.lognormvariate(0, 0.45) * median)
    r = random.random()
    if r < CFG["err429"]:
        return JSONResponse({"error": {"message": "rate limit (simulado)"}}, status_code=429)
    if r < CFG["err429"] + CFG["err503"]:
        return JSONResponse({"error": {"message": "overloaded (simulado)"}}, status_code=503)
    return None


@app.post("/v1/chat/completions")
async def openai(req: Request):
    body = await req.json()
    if fail := await maybe_fail(CFG["median_openai"]):
        return fail
    text = body["messages"][-1]["content"]
    content = json.dumps(fake_eval(text)) if body.get("response_format") else \
        "Adapta tu experiencia: ¿cómo aplicarías esto en la plataforma de pagos de la vacante con PostgreSQL y Docker?"
    return {"choices": [{"message": {"content": content}}]}


@app.post("/v1beta/models/{model}:generateContent")
async def gemini(model: str, req: Request):
    body = await req.json()
    if fail := await maybe_fail(CFG["median_gemini"]):
        return fail
    text = body["contents"][-1]["parts"][0]["text"]
    is_json = body.get("generationConfig", {}).get("responseMimeType") == "application/json"
    out = json.dumps(fake_eval(text)) if is_json else \
        "En un proyecto de [contexto] identifiqué [problema]; mi meta era [objetivo]. Implementé [acciones] y logré [X %] de mejora."
    return {"candidates": [{"content": {"parts": [{"text": out}]}}]}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=9999)
    a = ap.parse_args()
    uvicorn.run(app, host="127.0.0.1", port=a.port, log_level="warning")
