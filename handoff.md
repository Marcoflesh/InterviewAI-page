# Documento de Handoff y Continuidad Técnica — InterviewAI (`v0.4.0`)

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

## 12. Próximos pasos inmediatos

1. Usuario: Pasos 0 a 6 de `PASO_A_PASO.md` (revocar token de GitHub, rotar llave de OpenAI, llave real de Gemini, orígenes de Google, prueba de estrés real).
2. Pegar los resultados reales de `stress_test_agents.py` en `PRUEBAS.md` §5 y decidir viabilidad con los criterios ahí definidos.
3. Elegir hosting del backend para la versión pública en GitHub Pages.
