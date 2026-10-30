#!/usr/bin/env bash
# InterviewAI — arranque "plug and play" (macOS / Linux)
#   ./iniciar.sh            levanta todo, repara la base de datos si hace falta y abre http://localhost:3000
#   ./iniciar.sh --reset    borra la base de datos local y empieza limpio
set -uo pipefail
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

HEALTH=/tmp/interviewai_health.json

# Traer la última versión del repositorio (solo avanza, nunca borra cambios tuyos).
if [ -d .git ]; then
  if git pull --ff-only -q 2>/tmp/interviewai_pull.txt; then
    echo "✓ Versión: $(git log --oneline -1)"
  else
    echo "✗ No se pudo actualizar con git pull:"; sed 's/^/    /' /tmp/interviewai_pull.txt
    echo "  Si dice que tienes cambios locales: git stash && git pull   (y vuelve a correr ./iniciar.sh)"
  fi
fi


levantar() {
  echo "→ Construyendo y levantando contenedores. La primera vez tarda 2-5 min: NO presiones Ctrl+C."
  docker compose pull -q ollama ollama-init 2>/dev/null || true   # Ollama al día (los modelos nuevos lo exigen)
  docker compose up --build -d || true   # si la BD falla, se diagnostica abajo
}

# Si el backend no reporta "agentes", quedó una imagen anterior (p. ej. se interrumpió la construcción).
backend_actualizado() {
  python3 -c "import json,sys;sys.exit(0 if json.load(open('$HEALTH')).get('agentes',{}).get('entrevistador') else 1)" 2>/dev/null \
    || grep -q '"entrevistador"' "$HEALTH"
}

# Devuelve el código de estado de la base de datos: ok | contrasena | esquema_desactualizado | sin_tablas | sin_conexion | sin_backend
estado_bd() {
  for _ in $(seq 1 40); do
    if curl -s -m 5 http://localhost:8000/api/health -o "$HEALTH" 2>/dev/null && [ -s "$HEALTH" ]; then
      python3 -c "import json;print(json.load(open('$HEALTH')).get('database',{}).get('code','ok'))" 2>/dev/null \
        || sed -n 's/.*"code":"\([a-z_]*\)".*/\1/p' "$HEALTH"
      return
    fi
    sleep 3
  done
  echo "sin_backend"
}

if [ "${1:-}" = "--reset" ]; then docker compose down -v; fi
levantar

for intento in 1 2 3; do
  echo -n "→ Revisando el backend y la base de datos… "
  codigo="$(estado_bd)"
  echo "$codigo"
  case "$codigo" in
    ok)
      if ! backend_actualizado; then
        echo "→ El backend sigue con la versión anterior. Reconstruyéndolo (no presiones Ctrl+C)…"
        docker compose up --build -d backend && sleep 5 && estado_bd >/dev/null
      fi
      docker compose up -d >/dev/null 2>&1   # asegura que el frontend también esté arriba
      python3 - "$HEALTH" <<'PY' 2>/dev/null || true
import json, sys
c = json.load(open(sys.argv[1]))["configured"]
m = lambda b: "✓" if b else "✗"
h = json.load(open(sys.argv[1])); a = h.get("agentes", {})
print(f"  Entrevistador: {a.get('entrevistador')} ({a.get('modelo_ollama')}) · Evaluador: {a.get('evaluador')} ({a.get('modelo_gemini')})")
print(f"  Gemini {m(c['gemini_key'])} · Google Sign-In {m(c['google_sign_in'])} · OpenAI (opcional) {'✓' if c['openai_key'] else '-'}")
PY
      modelo="$(grep -E '^OLLAMA_MODEL=' .env | cut -d= -f2)"; modelo="${modelo:-qwen3.5:4b}"
      echo "✓ Página lista: http://localhost:3000"
      (open http://localhost:3000 || xdg-open http://localhost:3000) >/dev/null 2>&1 || true
      if docker compose exec -T ollama ollama list 2>/dev/null | grep -q "^${modelo}"; then
        echo "✓ Entrevistador local (Ollama ${modelo}): listo"
      else
        echo "→ Descargando el entrevistador local (Ollama ${modelo}, ~3.4 GB, solo la primera vez)."
        echo "  Ya puedes usar la página: mientras tanto usa las preguntas del banco."
        echo "  Versión de Ollama en Docker: $(docker compose exec -T ollama ollama --version 2>/dev/null | tail -1)"
        bajar_modelo() { docker compose exec ollama ollama pull "$modelo" 2>&1 | tee /tmp/interviewai_ollama.txt; ! grep -q "Error" /tmp/interviewai_ollama.txt; }
        if ! bajar_modelo && grep -q "newer version" /tmp/interviewai_ollama.txt; then
          echo "→ La imagen de Ollama es vieja para ${modelo}. Bajando la versión más nueva de Ollama y reintentando…"
          grep -q '^OLLAMA_IMAGE=' .env && sed -i.bak 's#^OLLAMA_IMAGE=.*#OLLAMA_IMAGE=ollama/ollama:latest#' .env
          OLLAMA_IMAGE=ollama/ollama:latest docker compose pull ollama ollama-init
          OLLAMA_IMAGE=ollama/ollama:latest docker compose up -d --force-recreate ollama
          sleep 8
          echo "  Versión de Ollama en Docker: $(docker compose exec -T ollama ollama --version 2>/dev/null | tail -1)"
          bajar_modelo
        fi
        if ! grep -q "Error" /tmp/interviewai_ollama.txt; then
          echo "✓ Entrevistador local (Ollama ${modelo}): listo. Las siguientes entrevistas ya lo usan."
        else
          echo "✗ No se pudo descargar ${modelo}. Copia el error de arriba y compártelo."
          echo "  Mientras tanto la página funciona con las preguntas del banco."
        fi
      fi
      exit 0 ;;
    contrasena)
      echo "→ La base de datos guarda una contraseña anterior. Sincronizándola con tu .env (sin borrar datos)…"
      docker compose exec -T db sh -s < scripts/db_sync_password.sh && docker compose up -d >/dev/null 2>&1 ;;
    esquema_desactualizado|sin_tablas)
      echo "→ La base de datos local se creó con una versión anterior de InterviewAI."
      read -r -p "  ¿Reiniciarla? Se borran solo las cuentas y entrevistas de prueba locales (s/n): " r
      if [[ "$r" =~ ^[sSyY] ]]; then docker compose down -v && levantar; else echo "Sin reiniciar no puede funcionar. Saliendo."; exit 1; fi ;;
    *)
      echo "✗ El backend no respondió. Estado de los contenedores:"
      docker compose ps -a
      if [ -z "$(docker compose ps -a -q backend 2>/dev/null)" ]; then
        echo "  El contenedor del backend ni siquiera se creó. Causas comunes:"
        echo "   - Falló la construcción: corre  docker compose up --build -d  y lee el error en rojo."
        echo "   - Disco lleno: docker system df   (libera con  docker system prune)"
        echo "   - Un puerto ocupado (5432, 8000 o 3000) por otro programa."
      else
        echo "  Últimos logs del backend:"
        docker compose logs backend --tail 40
      fi
      echo "  Copia todo esto y compártelo."
      exit 1 ;;
  esac
done
echo "✗ No se pudo dejar lista la base de datos. Prueba: ./iniciar.sh --reset"
exit 1
