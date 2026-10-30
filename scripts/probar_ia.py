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
print(f"OpenAI: modelo {settings.OPENAI_CHAT_MODEL}, llave con formato válido: {settings.openai_ready}\n")

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
print("\n3) OpenAI, texto corto:")
probar("openai", llm.call_openai, prompt="Responde solo: 'listo'.", max_tokens=10)

print("\nResumen (sin llaves):")
print(json.dumps(llm.status(), ensure_ascii=False, indent=2))
