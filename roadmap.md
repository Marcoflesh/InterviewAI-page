# Roadmap de Desarrollo — InterviewAI

Este documento registra la evolución iterativa de **InterviewAI**, diferenciando los hitos completados (Pasado), los componentes implementados en la iteración actual (`v0.4.0`) y las funcionalidades programadas para las siguientes iteraciones.

---

## 1. Hitos Pasados (Fase 0 a `v0.3.0`)

- [x] **Diagnóstico Institucional y SRS (ISO/IEC/IEEE 29148-2018)**: RN-01 a RN-12, RF-01 a RF-15, RNF-01 a RNF-09, RIF-01 a RIF-05 y RIN-01 a RIN-04.
- [x] **`v0.1.0` – `v0.2.0`**: Infraestructura Docker, esquema PostgreSQL con 176 preguntas (22 por carrera), autenticación triple y descarga PDF con jsPDF.
- [x] **`v0.3.0`**: Escala crítica 0–5, agentes `gpt-4o-mini` + `gemini-3.8-flash` configurados por `.env`, validador de correos con MX, Google Identity Services, preguntas adaptadas al Contexto de la vacante y aislamiento por usuario.

---

## 2. Estado Actual (Iteración `v0.4.0` — Auditoría, Seguridad, Anonimato, Docker, GitHub Pages y Pruebas de Estrés)

- [x] **Auditoría completa del código** y corrección del inicio de sesión con Google (audiencia obligatoria, errores accionables, `Referrer-Policy` compatible, sin *bypass* en el navegador).
- [x] **Seguridad**: tokens de sesión, cierre de IDOR, CORS restringido, límites de peticiones, XSS escapado + CSP, contraseñas con hash también en modo demo, llaves fuera del navegador, defensa contra inyección de prompt (ver `SEGURIDAD.md`).
- [x] **Anonimato**: anonimización del nombre del usuario y redes sociales, borrado de cuenta en cascada, aviso sobre la capa gratuita de Gemini.
- [x] **Agentes de IA robustos**: cliente único `llm.py` con reintento y respaldo entre proveedores, logs de latencia, `evaluator_source` visible, ejemplos STAR sin cifras inventadas, reporte del Agente Sintetizador conectado al frontend, CSAT persistido.
- [x] **Docker endurecido** (puertos internos en `127.0.0.1`, backend sin root, healthchecks, Ollama opcional) y rendimiento ×2.6 bajo carga.
- [x] **GitHub**: repositorio publicado, workflow de GitHub Pages (con Modo demo sin backend) y CI con pytest + gitleaks.
- [x] **Pruebas**: 32 pytest con PostgreSQL real, 17 E2E en Chromium, carga hasta 100 usuarios simultáneos, scripts de estrés para las APIs reales.
- [x] **`v0.4.1`**: llave de Gemini `AQ.` y Client ID configurados en `.env` seguro; soporte del formato `AQ.`; pre-commit anti-secretos.
- [x] **`v0.4.2`**: llave de OpenAI `sk-svcacct-…` en `.env`; scripts plug & play `iniciar.bat` / `iniciar.sh`.
- [x] **`v0.4.3`**: "Error interno" al iniciar sesión corregido (diagnóstico de base de datos + autorreparación en `iniciar`).
- [x] **`v0.4.4`**: el registro ya indica "mínimo 8 caracteres" (coincide con la validación real).
- [x] **`v0.5.0`**: el entrevistador responde al instante (preguntas preparadas por adelantado y evaluación en segundo plano), sin emojis y con preguntas humanizadas.
- [x] **`v0.6.0`**: investigación STAR, 58 preguntas nuevas con fuentes, rúbrica de 30 indicadores, set de calibración y arnés de medición.
- [x] **`v0.6.1`**: la IA ya califica en el arnés (margen de tokens para Gemini 3.x, diagnóstico de fallas, pausa a proveedores sin saldo).
- [ ] **Pendiente del usuario**: agregar saldo en OpenAI o usar `INTERVIEWER_PROVIDER=gemini`; correr `scripts/probar_ia.py` y `scripts/evaluar_evaluador.py --modo llm` con sus llaves y conseguir 2–3 calificadores humanos; activar GitHub Pages (Settings → Pages → GitHub Actions), agregar orígenes en Google Cloud, revocar el token `ghp_` y la llave `sk-proj-` vieja, y correr `stress_test_agents.py` en su computadora.

---

## 3. Plan de Calidad de los Agentes de IA (propuesto 30/10/2026, sin código aún)

Estado actual: los agentes **no están entrenados**; son modelos generales (`gpt-4o-mini`, `gemini-3.8-flash`) guiados por prompts, más un analizador determinista y un *guardrail*. Aún no hay medición contra calificaciones humanas (`golden_dataset` vacío, RN-07).

- [x] **Fase A — Rúbrica con anclas** (v0.6.0: 30 indicadores en `backend/app/data/rubrica_star.json`): definir qué significa 0, 1, 2, 3, 4 y 5 en cada dimensión STAR, con un ejemplo real por nivel y ajustes por carrera.
- [ ] **Fase B — Golden dataset** (v0.6.0: plantilla y guía en `datos/golden/`; faltan calificadores humanos): 150–200 respuestas reales anonimizadas y con consentimiento, calificadas por 2–3 personas (profesores/reclutadores). Medir el acuerdo entre humanos primero.
- [x] **Fase C — Arnés de evaluación** (v0.6.0: `scripts/evaluar_evaluador.py`): comparar modelo vs. humanos (kappa ponderado, error medio, % de coincidencia ±1) en cada cambio de prompt, como pruebas automáticas.
- [x] **Fase D — Mejoras de prompt** (v0.6.0: rúbrica, evidencia antes de calificar y 3 ejemplos resueltos; falta mediana de varias evaluaciones): rúbrica con anclas, ejemplos *few-shot* del golden set, citar evidencia antes de calificar, salida con esquema JSON, mediana de 3 evaluaciones o de ambos modelos.
- [ ] **Fase E — Ciclo con usuarios**: botón "esta retroalimentación no me sirvió", revisión humana y alimentación del golden set; pruebas de sesgo (misma respuesta, distinto perfil).
- [ ] **Fase F — Fine-tuning (opcional)**: solo con 500–1000 ejemplos de calidad y si el prompt ya no mejora; no sobre `gpt-4o-mini` (se retira el 14/01/2027 junto con sus versiones afinadas).

## 4. Siguientes Funcionalidades (Fase 2 y Fase 3)

- [ ] **Backend público para GitHub Pages**: desplegar `Dockerfile.backend` (Render / Cloud Run) con PostgreSQL administrado y configurar `API_BASE_URL`.
- [ ] **Migrar `OPENAI_CHAT_MODEL`** antes del 14/01/2027 (retiro de `gpt-4o-mini`) y repetir la prueba de estrés.
- [ ] **Extracción directa de archivos PDF/DOCX en carga de CV** (`pypdf` / `python-docx`).
- [ ] **Panel de Administración `/admin`** con RBAC para Product Owner y MLOps (Golden Dataset y auditoría estadística `>= 0.75`).
- [ ] **Verificación de correo por enlace**, sesión en cookie `HttpOnly` y limitador en Redis.
- [ ] **Backend asíncrono** (`httpx.AsyncClient`) para escalar más allá de ~100 usuarios simultáneos.
