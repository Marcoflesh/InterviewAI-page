# Guía de Configuración de API Keys y Agentes de IA (`v0.4.0`)

**Regla única:** las llaves secretas viven **solo** en `.env` (raíz del proyecto). Nunca en el código, nunca en el frontend, nunca en GitHub. El paso a paso completo está en [`PASO_A_PASO.md`](./PASO_A_PASO.md).

## ¿Qué modelo usa cada agente?

| Agente | Modelo por defecto | Variables en `.env` | Formato de la llave |
| :--- | :--- | :--- | :--- |
| **Entrevistador** (adapta las preguntas a la vacante) | `gpt-4o-mini` | `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL`, `INTERVIEWER_PROVIDER=openai` | empieza con `sk-` |
| **Evaluador crítico** (califica 0–5) y **Sintetizador** (ejemplos STAR del reporte) | `gemini-3.8-flash` (respaldo `gemini-2.5-flash`) | `GEMINI_API_KEY`, `GEMINI_MODEL`, `EVALUATOR_PROVIDER=gemini` | empieza con `AIza` |
| **Google Sign-In** | Google Identity Services | `GOOGLE_CLIENT_ID` | termina en `.apps.googleusercontent.com` (es público) |

Si el proveedor principal falla (error, límite de uso o llave inválida), el backend reintenta una vez y luego usa el otro proveedor. Si ninguno responde, usa el analizador determinista local. La respuesta de cada turno indica quién evaluó (`evaluator_source`).

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

## Comprobar que todo está bien

```bash
python scripts/check_apis.py                   # valida llaves sin gastar saldo
curl http://localhost:8000/api/health          # con Docker encendido: qué está configurado
docker compose logs -f backend | grep llm      # proveedor, modelo, código HTTP y latencia de cada llamada
```

## Cambiar de modelo

Solo edita `.env` y reinicia (`docker compose up -d`):

```ini
OPENAI_CHAT_MODEL=gpt-6-luna        # reemplazo recomendado por OpenAI antes del 14/01/2027
GEMINI_MODEL=gemini-3.8-flash
EVALUATOR_PROVIDER=openai           # para que gpt evalúe en lugar de Gemini
```
