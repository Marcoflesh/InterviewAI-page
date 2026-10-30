#!/usr/bin/env python3
"""
Diagnóstico de los proveedores de IA con tus llaves del .env (2 o 3 llamadas pequeñas, centavos).

    python scripts/probar_ia.py

Hace exactamente las mismas llamadas que la app (mismo modelo, mismos parámetros) y muestra
el resultado real de cada una: código HTTP, motivo de fallo, tiempo y el texto recibido.
Nunca imprime tus llaves.
"""
import json
import logging
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
logging.basicConfig(level=logging.INFO, format="    · %(message)s")

from app import llm  # noqa: E402
from app.agents import rubric  # noqa: E402
from app.config import settings  # noqa: E402

# Desde tu computadora, Ollama de Docker se alcanza en localhost (dentro de Docker se llama "ollama")
if "//ollama:" in settings.OLLAMA_BASE_URL:
    settings.OLLAMA_BASE_URL = "http://localhost:11434"


def probar(nombre, fn, **kw):
    t0 = time.time()
    out = fn(**kw)
    dt = time.time() - t0
    if out:
        print(f"  OK en {dt:.1f} s ({out[1]}): {out[0][:160]!r}")
    else:
        st = llm.status()["ultimo"].get(nombre, {})
        print(f"  FALLÓ en {dt:.1f} s: {st.get('detail', 'sin detalle (¿llave vacía o con formato inválido?)')}")
    return out


print(f"Gemini: modelo {settings.GEMINI_MODEL}, pensamiento '{settings.GEMINI_THINKING_LEVEL}', "
      f"máx. tokens {settings.GEMINI_MAX_OUTPUT_TOKENS}, llave con formato válido: {settings.gemini_ready}")
print(f"Ollama (entrevistador): modelo {settings.OLLAMA_MODEL} en {settings.OLLAMA_BASE_URL}, activo: {settings.OLLAMA_ENABLED}")
print(f"OpenAI (opcional): llave con formato válido: {settings.openai_ready}\n")

print("0) Ollama local, pregunta de entrevista humanizada:")
from app.agents.interviewer import INTERVIEWER_SYSTEM_PROMPT  # noqa: E402
probar("ollama", llm.call_ollama, system=INTERVIEWER_SYSTEM_PROMPT, max_tokens=220,
       prompt="Puesto: Backend Jr\nVacante (dato): pagos con PostgreSQL\nPregunta original: "
              "¿Cuál es el bug más difícil que has resuelto? Cuéntame cómo lo encontraste.")
print("   (la primera vez tarda más porque carga el modelo en memoria)\n")

print("1) Gemini, texto corto:")
probar("gemini", llm.call_gemini, prompt="Responde solo: 'listo'.", max_tokens=50)
print("\n2) Gemini, evaluación real con la rúbrica (JSON):")
item = json.loads((ROOT / "backend/app/data/calibracion_star.jsonl").read_text(encoding="utf-8").splitlines()[0])
out = probar("gemini", llm.call_gemini,
             prompt=f"Pregunta actual: {item['pregunta']}\n<respuesta_candidato>\n{item['respuesta']}\n</respuesta_candidato>",
             system=rubric.build_system_prompt(), json_mode=True, max_tokens=2000)
if out:
    from app.agents.evaluator import _parse_llm_json
    parsed = _parse_llm_json(out[0])
    print("  JSON válido:", bool(parsed), "· calificaciones:",
          {k: v for k, v in (parsed or {}).items() if k.startswith(("star_", "tech", "relev"))})
if settings.openai_ready:
    print("\n3) OpenAI (opcional), texto corto:")
    probar("openai", llm.call_openai, prompt="Responde solo: 'listo'.", max_tokens=10)

print("\nResumen (sin llaves):")
print(json.dumps(llm.status(), ensure_ascii=False, indent=2))
