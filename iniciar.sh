#!/usr/bin/env bash
# InterviewAI — arranque "plug and play" (macOS / Linux)
#   ./iniciar.sh            levanta todo y abre http://localhost:3000
#   ./iniciar.sh --reset    borra la base de datos local y empieza limpio
set -euo pipefail
cd "$(dirname "$0")"

command -v docker >/dev/null || { echo "✗ Instala Docker Desktop: https://docs.docker.com/get-docker/"; exit 1; }
docker info >/dev/null 2>&1 || { echo "✗ Abre Docker Desktop y espera a que diga 'running'."; exit 1; }

if [ ! -f .env ]; then
  cp .env.example .env
  echo "✗ Se creó .env desde la plantilla. Llena tus llaves (ver PASO_A_PASO.md) y vuelve a correr ./iniciar.sh"
  exit 1
fi
chmod 600 .env 2>/dev/null || true
[ -d .git ] && [ ! -f .git/hooks/pre-commit ] && bash scripts/install_git_hooks.sh >/dev/null && echo "✓ Protección anti-secretos para git instalada"

if [ "${1:-}" = "--reset" ]; then docker compose down -v; fi

echo "→ Construyendo y levantando contenedores (la primera vez tarda unos minutos)…"
docker compose up --build -d

echo -n "→ Esperando al backend"
for _ in $(seq 1 60); do
  if curl -fsS http://localhost:8000/api/health >/tmp/interviewai_health.json 2>/dev/null; then
    echo " ✓"
    python3 - <<'PY' 2>/dev/null || cat /tmp/interviewai_health.json
import json
c = json.load(open("/tmp/interviewai_health.json"))["configured"]
m = lambda b: "✓" if b else "✗"
print(f"  OpenAI {m(c['openai_key'])} · Gemini {m(c['gemini_key'])} · Google Sign-In {m(c['google_sign_in'])}")
PY
    echo "✓ Listo: http://localhost:3000"
    (open http://localhost:3000 || xdg-open http://localhost:3000) >/dev/null 2>&1 || true
    exit 0
  fi
  echo -n "."; sleep 3
done

echo " ✗ El backend no respondió. Últimos logs:"
docker compose logs backend --tail 25
if docker compose logs backend 2>&1 | grep -q "password authentication failed"; then
  echo "→ La base de datos tiene una contraseña vieja. Corre: ./iniciar.sh --reset"
fi
exit 1
