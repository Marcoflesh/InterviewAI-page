# Documento de Handoff y Continuidad Técnica — InterviewAI (`v0.8.0`)

**Fecha de actualización:** 29 de octubre de 2026
**Repositorio:** `https://github.com/Marcoflesh/InterviewAI-page.git`
**Propósito:** Garantizar la continuidad inmediata del desarrollo en caso de agotamiento de tokens o cambio de sesión, documentando la arquitectura y las decisiones de la iteración `v0.4.0`.

---

## 1. Diagnóstico con el que se inició `v0.4.0`

1. **Google Sign-In "no funcionaba"**: combinación de (a) orígenes de JavaScript sin `http://localhost` en Google Cloud, (b) abrir la página fuera de `http://localhost:3000`, (c) errores del backend que el frontend ocultaba y (d) un *fallback* que iniciaba sesión sin verificar y generaba un `user_id` no UUID que hacía fallar `/api/sessions/start` con 500.
2. **`GEMINI_API_KEY` contenía un token de GitHub (`ghp_…`)**: el evaluador nunca usó Gemini; todo caía a OpenAI o al analizador local sin avisar (los errores se tragaban sin log).
3. **IDOR, CORS `*`, llaves posibles en el navegador, contraseñas en texto plano en `localStorage` y XSS** en el reporte (detalle en `SEGURIDAD.md`).
4. **El repositorio remoto estaba vacío**: los commits locales nunca se habían subido.
5. **El reporte del frontend no usaba al Agente Sintetizador** y el CSAT no se enviaba al backend.

## 2. Decisiones de arquitectura de `v0.4.0`

| Decisión | Motivo |
|---|---|
| Las llaves de IA solo existen en el backend (`.env`); `frontend/js/config.js` contiene solo `API_BASE_URL` y `GOOGLE_CLIENT_ID` | GitHub Pages es público: cualquier llave en el navegador queda expuesta. |
| Modo demo automático si `/api/health` no responde | Permite publicar en GitHub Pages sin backend sin romper la página. |
| Tokens HMAC propios en `backend/app/security.py` (sin dependencia extra) | Suficiente para un solo servicio; el `user_id` ya no viene del navegador. |
| `backend/app/llm.py` como único punto de salida a proveedores | Un solo lugar para llaves, reintentos, respaldo, logs y URL base configurable (pruebas con `mock_llm_server.py`). |
| Guardrail determinista sobre la nota del LLM | El analizador local ya existía; ahora calibra al LLM y bloquea inyecciones. |
| Liberar la conexión a BD durante las llamadas al LLM | Era el cuello de botella real bajo carga. |
| Ollama como perfil opcional | Pesaba ~2 GB, el modelo no se descargaba solo y sumaba timeouts inútiles. |
| UI sin rediseño | Requisito del proyecto: mantener la página simple y minimalista. Solo se agregó el indicador discreto "Modo demo". |

## 3. Mapa de archivos nuevos o reescritos

- `backend/app/security.py`, `backend/app/llm.py` — nuevos.
- `backend/app/auth.py`, `config.py`, `schemas.py`, `main.py`, `database.py`, `agents/evaluator.py`, `agents/interviewer.py`, `agents/synthesizer.py`, `services/anonymizer.py` — modificados.
- `frontend/js/config.js`, `frontend/vendor/jspdf.umd.min.js` — nuevos; `frontend/js/app.js`, `index.html`, `nginx.conf`, `css/styles.css` — modificados.
- `docker-compose.yml`, `Dockerfile.backend`, `.dockerignore`, `.gitignore`, `.env.example` — endurecidos.
- `.github/workflows/pages.yml`, `.github/workflows/ci.yml` — nuevos.
- `backend/tests/` y `scripts/` — nuevos.
- `PASO_A_PASO.md`, `SEGURIDAD.md`, `PRUEBAS.md` — nuevos.

## 4. Cómo continuar

```bash
git clone https://github.com/Marcoflesh/InterviewAI-page.git && cd InterviewAI-page
cp .env.example .env                 # llenar según PASO_A_PASO.md
python scripts/check_apis.py
docker compose up --build -d          # http://localhost:3000
```

Pruebas: `backend/tests` (pytest con `TEST_DATABASE_URL`), `scripts/load_test_backend.py`, `scripts/stress_test_agents.py`.

## 5. Actualización `v0.4.1` (misma fecha)

- El usuario entregó una llave nueva de Gemini con formato `AQ.` (Google cambió el formato en 2026; solo funciona por header `x-goog-api-key`, que `llm.py` ya usa). Se agregó soporte en `config.py` y `check_apis.py`.
- Para OpenAI entregó `key_…`, que es el **ID** de la llave, no el secreto; el `.env` conserva la `sk-proj-…` anterior hasta que cree una nueva.
- Se le entregó un `.env` completo (no versionado) con secretos aleatorios para PostgreSQL y `SECRET_KEY`. Si ya había un volumen `pgdata` con la contraseña vieja, debe correr `docker compose down -v`.
- Nuevos guardas: `scripts/install_git_hooks.sh`, regla gitleaks `AQ.`, patrones ampliados en `push_to_github.sh`.

## 6. Actualización `v0.4.2` (plug & play)

- `.env` completo: OpenAI `sk-svcacct-…`, Gemini `AQ.…`, Client ID, secretos aleatorios. Entregado al usuario, nunca versionado.
- Arranque en un paso: `iniciar.bat` (Windows) / `iniciar.sh` (macOS/Linux).
- GitHub Pages: el workflow falla en `configure-pages` hasta que el dueño active *Settings → Pages → Source: GitHub Actions*; la API de GitHub para activarlo no está disponible desde esta sesión.

## 7. Incidente 30/10/2026: "Error interno del servidor" al iniciar sesión (`v0.4.3`)

- **Causa raíz**: volumen `pgdata` creado antes del `.env` nuevo → contraseña desalineada (`password authentication failed`) y/o esquema viejo (sin `users.password_hash`). Reproducido con PostgreSQL 16 en modo scram.
- **Corrección**: `check_database()` + `/api/health` 503 con diagnóstico + manejador `DBAPIError` + autorreparación en `iniciar.*` vía `scripts/db_sync_password.sh`.
- **Lección**: el healthcheck debe tocar la base de datos; los errores de BD necesitan un manejador específico para no perder CORS.

## 8. `v0.4.4` (30/10/2026)

- Texto del campo de contraseña en el registro corregido de 6 a 8 caracteres para coincidir con la validación (`app.js` y `schemas.py` ya exigían 8).

## 9. Consulta 30/10/2026: calidad y "entrenamiento" de los agentes (sin código)

- Respuesta: los agentes no están entrenados ni medidos contra humanos; el camino recomendado es rúbrica con anclas → golden dataset → arnés de evaluación → mejoras de prompt → ciclo con usuarios → fine-tuning solo si hace falta. Plan en `roadmap.md` §3.
- Pendiente de decisión del usuario: quién califica el golden dataset y cuántas respuestas reunir.

## 10. `v0.5.0` — Velocidad y tono del entrevistador (30/10/2026)

- **Arquitectura del turno**: `POST /turn` ya no espera a la IA. Guarda la respuesta, toma la siguiente pregunta de `pipeline` (preparada por adelantado) y encola la evaluación. El frontend consulta `GET /turns/{turn_id}/evaluation` hasta que llega y actualiza el panel.
- **Limitación conocida**: el caché de preguntas vive en memoria de un solo proceso (Docker usa uno). Con varias réplicas habría que moverlo a Redis; si se pierde, todo se recalcula bajo demanda sin romper la entrevista.
- **Parámetros** (`.env` opcional): `QUESTION_PREFETCH_AHEAD=2`, `FIRST_QUESTION_WAIT_SECONDS=4`, `NEXT_QUESTION_WAIT_SECONDS=2`, `REPORT_EVALUATION_WAIT_SECONDS=30`.
- **Repreguntas** (`allow_followups`): siguen por el grafo de LangGraph de forma síncrona porque dependen de la evaluación.

## 11. `v0.6.0` — Investigación y calibración de agentes (30/10/2026)

- **Investigación**: `research/metodo_star.md`. Reddit, Stack Exchange, Hacker News y el sitio original del Tech Interview Handbook estaban bloqueados desde el entorno; se usaron compilaciones citadas.
- **Datos** (en `backend/app/data/`, entran a la imagen de Docker): `preguntas_software.json` (58), `rubrica_star.json` (30 indicadores), `ejemplos_fewshot.json` (3), `calibracion_star.jsonl` (24, sintético).
- **Evaluador**: modo `indicadores` por defecto; acepta también el JSON anterior (`star_*`). En modo indicadores el tope "analizador + 2" está desactivado porque el analizador subestima respuestas excelentes; el bloqueo de inyección sigue activo.
- **Siguiente paso de mayor impacto**: golden dataset humano (`datos/golden/LEEME.md`) y correr el arnés con IA real.

## 12. `v0.6.1` — Por qué la IA no calificaba (30/10/2026)

- Gemini 3.x consume tokens de salida al "pensar": con `maxOutputTokens` bajo responde 200 vacío (`finishReason=MAX_TOKENS`). Ahora se usa `GEMINI_MAX_OUTPUT_TOKENS=8192` y `thinkingLevel=low`.
- `gemini-2.5-flash` responde 404 para cuentas nuevas: se eliminó como respaldo.
- La cuenta de OpenAI del usuario no tiene saldo: el cortacircuitos la pausa 10 min y todo usa Gemini.
- Diagnóstico: `python scripts/probar_ia.py` y el campo `ia` de `/api/health`.
- Pendiente: confirmar con las llaves reales (este entorno no tiene salida a Google ni a OpenAI).

## 13. `v0.7.0` — Ollama, base de datos llena y prueba con internet (30/10/2026)

- **Entrevistador**: Ollama local `qwen3.5:4b` (gratis). Servicios `ollama` + `ollama-init` en Compose; la primera vez descarga ~3.4 GB (`docker compose logs -f ollama-init`). Mientras no está listo, el backend usa las preguntas del banco sin esperar. GPU NVIDIA: `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d`.
- **Gemini** sigue como Evaluador y Sintetizador. OpenAI solo como respaldo si alguien vuelve a poner llave con saldo.
- **Datos**: `golden_dataset` se llena solo al arrancar (26 web + 24 calibración); `reviewer_notes` guarda fuente, URL y etiqueta original. Puntajes web representativos (4.0/1.0) y en `pending_review`: no son calificaciones humanas reales.
- **Medición**: `scripts/evaluar_evaluador.py --conjunto web|bd`. Analizador local: AUC 0.93 / exactitud 81 %. Falta la medición con Gemini (este entorno no tiene salida a Google ni a Ollama).
- **Elección de modelo**: `qwen3.5:4b` sobre `ministral-3:3b` (español) y Gemma 4 (razonamiento no desactivable, más lento). Alternativa si hay ≥ 16 GB de RAM o GPU: `OLLAMA_MODEL=qwen3.5:9b`.

## 14. `v0.7.1` — `.env` claro y scripts dentro de Docker (30/10/2026)

- El usuario no veía en el `.env` quién hacía cada rol: la sección 2 ahora lo dice explícitamente. `/api/health` → `agentes` y `iniciar` lo imprimen.
- `probar_ia.py` y `evaluar_evaluador.py` viven también en la imagen del backend (`/app/scripts`); dentro del contenedor usan `ollama:11434` y `db:5432`, fuera usan `localhost`.
- Guía de actualización: `PASO_A_PASO.md` → "Actualizar a la versión con Ollama + Gemini".

## 15. `v0.8.0` — Entrevistas pasadas y arranque visible (30/10/2026)

- Historial: fuente de verdad = BD (`/api/users/me/history`, solo terminadas). Detalle con `/api/sessions/{id}/detail`. En el navegador solo resumen; en modo demo se guarda la conversación local para poder verla.
- `renderReport(data)` es la única función que pinta el reporte (nuevo o pasado) y deja `appState.reportData` para el PDF.
- Incidente del usuario: Ctrl+C durante `docker compose up --build` dejó el backend viejo (`Entrevistador: None`). `iniciar` ahora enseña el progreso y se auto-repara.
- GitHub Pages sigue fallando con "Get Pages site failed": falta activar Settings → Pages → Source: GitHub Actions (solo el dueño puede).

## 16. `v0.8.1` — Arranque robusto (30/10/2026)

- `backend` ya no tiene `depends_on: ollama`; un fallo de Ollama (imagen sin descargar, puerto 11434 ocupado por un Ollama nativo) impedía crear el backend (`sin_backend`, logs vacíos).
- `iniciar` actualiza el repo solo (`git pull --ff-only`) y muestra `docker compose ps -a` al fallar.

## 17. `v0.8.2` — Puerto de Ollama (30/10/2026)

- El usuario tiene un Ollama nativo en el 11434. El contenedor `ollama` ya no publica puertos; todo lo que lo usa corre dentro de Docker (`docker compose exec backend python scripts/...`).

## 18. Próximos pasos inmediatos

1. Usuario: seguir "Actualizar a la versión con Ollama + Gemini" de `PASO_A_PASO.md` y pegar la salida de `docker compose exec backend python scripts/evaluar_evaluador.py --modo llm --conjunto web`.
2. Usuario: Pasos 0 a 6 de `PASO_A_PASO.md` (revocar token de GitHub, rotar llave de OpenAI, llave real de Gemini, orígenes de Google, prueba de estrés real).
3. Pegar los resultados reales de `stress_test_agents.py` en `PRUEBAS.md` §5 y decidir viabilidad con los criterios ahí definidos.
4. Elegir hosting del backend para la versión pública en GitHub Pages.
