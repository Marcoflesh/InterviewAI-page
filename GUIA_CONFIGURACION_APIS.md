# Guía de Configuración de API Keys y Agentes de IA (`v0.7.1`)

**Regla única:** las llaves secretas viven **solo** en `.env` (raíz del proyecto). Nunca en el código, nunca en el frontend, nunca en GitHub. El paso a paso completo está en [`PASO_A_PASO.md`](./PASO_A_PASO.md).

## ¿Qué modelo usa cada agente?

| Agente | Modelo por defecto | Variables en `.env` | Formato de la llave |
| :--- | :--- | :--- | :--- |
| **Entrevistador** (adapta las preguntas a la vacante) | Ollama local `qwen3.5:4b` (gratis, corre en tu computadora dentro de Docker) | `INTERVIEWER_PROVIDER=ollama`, `OLLAMA_ENABLED=true`, `OLLAMA_MODEL` | no necesita llave |
| Respaldo opcional del Entrevistador | `gpt-4o-mini` | `OPENAI_API_KEY` (vacía por defecto) | empieza con `sk-` |
| **Evaluador crítico** (califica 0–5) y **Sintetizador** (ejemplos STAR del reporte) | `gemini-3.8-flash` (sin respaldo: `gemini-2.5-flash` ya no está disponible para cuentas nuevas) | `GEMINI_API_KEY`, `GEMINI_MODEL`, `EVALUATOR_PROVIDER=gemini` | empieza con `AQ.` (formato nuevo) o `AIza` |
| **Google Sign-In** | Google Identity Services | `GOOGLE_CLIENT_ID` | termina en `.apps.googleusercontent.com` (es público) |

La primera vez, el contenedor `ollama-init` descarga el modelo (~3.4 GB; avance con `docker compose logs -f ollama-init`). Mientras tanto, la entrevista usa las preguntas del banco sin esperar. Con tarjeta NVIDIA: `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d`.

Si el proveedor principal falla (error, límite de uso o llave inválida), el backend reintenta una vez y luego usa el otro proveedor. Si un proveedor **no tiene saldo**, la llave es inválida o el modelo no existe, se pone **en pausa** unos minutos para no perder tiempo en cada llamada; `/api/health` muestra el último resultado de cada IA en el campo `ia`.

**Gemini 3.x "piensa" antes de responder** y ese razonamiento consume tokens de salida: por eso el backend le da hasta `GEMINI_MAX_OUTPUT_TOKENS=8192` (solo se cobra lo usado) con `GEMINI_THINKING_LEVEL=low`. Con menos margen, la respuesta llega vacía (`finishReason=MAX_TOKENS`). Si ninguno responde, usa el analizador determinista local. La respuesta de cada turno indica quién evaluó (`evaluator_source`).

## Dónde se leen las llaves (no necesitas editar estos archivos)

| Archivo | Qué hace |
| :--- | :--- |
| `.env` | Tus valores reales (en `.gitignore` y `.dockerignore`). |
| `docker-compose.yml` | Pasa las variables de `.env` al contenedor `backend`. |
| `backend/app/config.py` | Lee y valida el formato de las llaves (avisa en los logs si una no tiene el formato correcto). |
| `backend/app/llm.py` | Único cliente de Gemini/OpenAI/Ollama: llave en *header*, reintento y logs sin secretos. |
| `backend/app/agents/evaluator.py`, `interviewer.py`, `synthesizer.py` | Prompts de cada agente; llaman a `llm.py`. |
| `backend/app/auth.py` | Verifica el JWT de Google con `GOOGLE_CLIENT_ID`. |
| `frontend/js/config.js` | Solo datos públicos: `API_BASE_URL` y `GOOGLE_CLIENT_ID`. **Sin llaves.** |

## Proteger tus llaves

- `chmod 600 .env` (macOS/Linux) para que solo tu usuario lo lea.
- `bash scripts/install_git_hooks.sh` instala un *pre-commit* que bloquea commits con `.env` o con llaves (`sk-`, `AIza`, `AQ.`, `ghp_`).
- En Google Cloud, **restringe** la llave de Gemini a *Generative Language API*. En OpenAI, ponle **límite de gasto mensual** al proyecto.
- Las llaves `AQ.` solo funcionan en el header `x-goog-api-key`; el backend ya las envía así (con `?key=` en la URL fallan con 404).

## Comprobar que todo está bien

```bash
docker compose exec backend python scripts/probar_ia.py   # llamada real a cada IA (Ollama gratis, Gemini centavos)
python scripts/check_apis.py                   # valida llaves sin gastar saldo
curl http://localhost:8000/api/health          # "agentes": quién es Entrevistador y Evaluador
docker compose logs -f backend | grep llm      # proveedor, modelo, código HTTP y latencia de cada llamada
```

## Cambiar de modelo

Solo edita `.env` y reinicia (`docker compose up -d`):

```ini
OLLAMA_MODEL=qwen3.5:9b             # más fino; necesita ~8 GB libres de RAM o GPU
OPENAI_CHAT_MODEL=gpt-6-luna        # solo si vuelves a usar OpenAI (gpt-4o-mini se retira el 14/01/2027)
GEMINI_MODEL=gemini-3.8-flash
EVALUATOR_PROVIDER=openai           # para que gpt evalúe en lugar de Gemini
```
