#!/usr/bin/env python3
"""
Verifica tus llaves SIN gastar tokens y SIN imprimirlas.

    python scripts/check_apis.py            (lee el .env de la raíz)

- OpenAI: consulta GET /v1/models/<modelo>  (gratis)
- Gemini: consulta GET /v1beta/models/<modelo> (gratis)
- Google Sign-In: revisa el formato del Client ID
"""
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

ENV = Path(__file__).resolve().parents[1] / ".env"


def load_env(path: Path) -> dict:
    data = {}
    if not path.exists():
        sys.exit(f"No existe {path}. Crea uno con: cp .env.example .env")
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            data[k.strip()] = v.strip().strip('"').strip("'")
    return data


def mask(v: str) -> str:
    return f"{v[:4]}…{v[-4:]} ({len(v)} caracteres)" if len(v) > 10 else "(vacía)"


def err_text(body) -> str:
    if isinstance(body, dict) and "Tunnel" in str(body.get("error", "")) or "urlopen error" in str(body):
        return "sin conexión a internet desde esta máquina (córrelo en tu computadora)"
    if isinstance(body, dict):
        e = body.get("error", body)
        return e.get("message", str(e)) if isinstance(e, dict) else str(e)
    return str(body)


def get(url: str, headers: dict) -> tuple:
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b"{}")
        except Exception:
            return e.code, {}
    except Exception as e:
        return 0, {"error": str(e)}


def main() -> int:
    env = load_env(ENV)
    ok = True

    model = env.get("OLLAMA_MODEL", "qwen3.5:4b")
    print(f"\n[Ollama local] modelo {model}")
    st, body = get("http://localhost:11434/api/tags", {})
    if st == 200:
        names = [m.get("name", "") for m in body.get("models", [])]
        if any(n in (model, f"{model}:latest") for n in names):
            print("  ✓ Ollama encendido y el modelo ya está descargado.")
        else:
            print(f"  … Ollama encendido pero el modelo aún no está (se descarga solo; mira: docker compose logs -f ollama-init). Modelos: {names}")
    else:
        print("  ✗ Ollama no responde en localhost:11434. ¿Ya corriste iniciar / docker compose up -d?"); ok = False

    key = env.get("OPENAI_API_KEY", "")
    model = env.get("OPENAI_CHAT_MODEL", "gpt-4o-mini")
    print(f"\n[OpenAI, opcional] llave {mask(key)} · modelo {model}")
    if not key:
        print("  – Sin llave: no se usa (el entrevistador es Ollama).")
    elif key.startswith("key_"):
        print("  ✗ Pegaste el ID de la llave ('key_…'), no la llave secreta. En https://platform.openai.com/api-keys")
        print("    crea una nueva y copia el valor que empieza con 'sk-' (solo se muestra una vez)."); ok = False
    elif not key.startswith("sk-"):
        print("  ✗ La llave de OpenAI debe empezar con 'sk-'."); ok = False
    else:
        st, body = get(f"https://api.openai.com/v1/models/{model}", {"Authorization": f"Bearer {key}"})
        if st == 200:
            print("  ✓ Llave válida y modelo disponible.")
        else:
            print(f"  ✗ HTTP {st}: {err_text(body)[:200]}"); ok = False

    key = env.get("GEMINI_API_KEY", "")
    model = env.get("GEMINI_MODEL", "gemini-3.8-flash")
    print(f"\n[Gemini] llave {mask(key)} · modelo {model}")
    if key.startswith("ghp_") or key.startswith("github_pat_"):
        print("  ✗ ¡Eso es un token de GitHub, no una llave de Gemini! Revócalo en GitHub y crea una llave en https://aistudio.google.com/apikey")
        ok = False
    elif not key.startswith(("AIza", "AQ.")):
        print("  ✗ La llave de Gemini debe empezar con 'AIza' o 'AQ.'."); ok = False
    else:
        st, body = get(f"https://generativelanguage.googleapis.com/v1beta/models/{model}", {"x-goog-api-key": key})
        if st == 200:
            print("  ✓ Llave válida y modelo disponible.")
        else:
            print(f"  ✗ HTTP {st}: {err_text(body)[:200]}"); ok = False

    cid = env.get("GOOGLE_CLIENT_ID", "")
    print(f"\n[Google Sign-In] Client ID: {cid or '(vacío)'}")
    if cid.endswith(".apps.googleusercontent.com"):
        print("  ✓ Formato correcto. En Google Cloud > Credenciales > tu cliente web agrega en")
        print("    'Orígenes autorizados de JavaScript':  http://localhost  y  http://localhost:3000")
        print("    (y https://marcoflesh.github.io si usarás GitHub Pages).")
    else:
        print("  ✗ Debe terminar en .apps.googleusercontent.com"); ok = False

    if not env.get("SECRET_KEY"):
        print("\n[SECRET_KEY] ✗ vacía: genera una con  python -c \"import secrets;print(secrets.token_urlsafe(48))\""); ok = False
    if env.get("POSTGRES_PASSWORD", "") in ("", "interviewai_secret", "CAMBIA_ESTA_CONTRASENA"):
        print("[POSTGRES_PASSWORD] ✗ usa una contraseña propia (la de ejemplo es pública)."); ok = False

    print("\nResultado:", "TODO LISTO ✓" if ok else "Hay pendientes ✗ (ver arriba)")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
