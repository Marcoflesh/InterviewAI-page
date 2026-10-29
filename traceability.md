# Matriz de Trazabilidad y Bitácora de Cambios — InterviewAI

Este archivo funciona como registro de cambios (changelog) y matriz de trazabilidad entre la Especificación de Requisitos de Software (SRS), los ajustes solicitados por el usuario y los archivos implementados en el repositorio.

## 1. Bitácora de Cambios (Changelog)

### `[v0.3.0] - 2026-10-29 — Evaluación Crítica (0 a 5), Agentes gpt-4o-mini y gemini-3.8-flash en .env, Validador DNS MX de Correos Reales, Google Identity Services Oficial y Aislamiento por Usuario`

* **Creado `GUIA_CONFIGURACION_APIS.md`**: Documento detallado con la ruta exacta de cada archivo, número de línea y pasos para colocar `OPENAI_API_KEY` (`gpt-4o-mini`), `GEMINI_API_KEY` (`gemini-3.8-flash`) y `GOOGLE_CLIENT_ID`.

* **Actualizado `.env.example`, `docker-compose.yml` y `backend/app/config.py`**: Configuración directa de los agentes **`gpt-4o-mini`** y **`gemini-3.8-flash`** con comentarios explícitos (`# >>> AQUÍ COLOCA TU API KEY ... <<<`).

* **Actualizado `database/init.sql`, `backend/app/schemas.py`, `backend/app/agents/evaluator.py` y `frontend/js/app.js`**:
  * Ampliación de la escala de evaluación a **`[0, 5]`** para permitir calificación de **`0/5`** cuando el usuario no demuestra la habilidad o ingresa respuestas evasivas/sin sentido, manteniendo cero complacencia y un amplio espectro léxico para calificar justamente entre `4/5` y `5/5` las respuestas bien fundamentadas.
  * Vinculación semántica del **Contexto de la vacante** y el **Puesto objetivo** con la selección y adaptación de las preguntas de la entrevista (`question_selector.py`, `interviewer.py` y `buildVacancyTailoredQuestions`).

* **Actualizado `backend/app/auth.py` y `frontend/js/app.js`**:
  * Implementación de validador de correos reales (`validate_real_email` / `validateRealEmailAccount`) con bloqueo de dominios ficticios/desechables y verificación en vivo de registros `MX` mediante Google Public DNS (`dns.google`).
  * Integración del verificador oficial de **Google Identity Services (`accounts.google.com/gsi/client`)** y eliminación del modal simulado.
  * Aislamiento estricto del historial por cuenta (`historiesByUser[email]`) y reinicio total del formulario de **Nueva práctica** al cambiar de usuario o cerrar sesión.

* **Actualizado `frontend/index.html`**: Eliminación de la ventana de conteo de preguntas en configuración, eliminación del botón/modal de configuración de API en la barra superior, eliminación de valores autorrellenados en todos los campos, eliminación del subtítulo de login y simplificación del placeholder del chat a `"Escribe tu respuesta"`.

### `[v0.2.0] - 2026-10-29 — Autenticación Triple Verificada, Descarga Real de PDF, Evaluador Semántico STAR + Llaves API y 15–20 Preguntas Aleatorias`

* **Actualizado `database/init.sql`**: Ampliación del banco de preguntas de 120 a **176 preguntas autocontenidas (22 por carrera en las 8 carreras)**, actualización de la restricción `total_questions` al rango aleatorio de **15 a 20 preguntas por sesión**, y adición de columnas `password_hash`, `auth_provider` y `email_verified` en la tabla `users`.

* **Actualizado `backend/app/auth.py`, `models.py`, `schemas.py` y `main.py`**: Implementación de tres flujos de acceso verificados (`POST /api/auth/login`, `POST /api/auth/register` y `POST /api/auth/google`) y generación aleatoria de 15 a 20 preguntas en `POST /api/sessions/start`.

* **Actualizado `frontend/index.html`, `frontend/css/styles.css` y `frontend/js/app.js`**: Cambio de etiqueta a **"Contexto de la vacante"** e integración de `jsPDF` (`2.5.1`) y generador binario PDF 1.4 para descarga directa del reporte `.pdf`.

### `[v0.1.0] - 2026-10-29 — Construcción del Esqueleto Completo del Proyecto`

* **Creado `database/init.sql`, `backend/`, `frontend/`, `Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.yml`, `roadmap.md`, `handoff.md`, `traceability.md`, `README.md`, `push_to_github.sh`**.

## 2. Trazabilidad de Reglas de Negocio (`RN-01` a `RN-12`)

| ID en SRS | Descripción Resumida | Estado | Archivo(s) / Componente(s) que lo Implementan | 
| ----- | ----- | ----- | ----- | 
| **RN-01** | Sesión de 15 a 20 preguntas aleatorias adaptadas a carrera, rol, CV y contexto de la vacante. | Implementado | `database/init.sql`, `backend/app/services/question_selector.py`, `backend/app/agents/interviewer.py`, `frontend/js/app.js` | 
| **RN-02** | Vector de puntuación crítica `[0, 5]` en estructura STAR (S, T, A, R), claridad técnica y pertinencia. | Implementado | `backend/app/agents/evaluator.py`, `database/init.sql` (`model_evaluations`), `frontend/js/app.js` | 
| **RN-03** | Aristas condicionales en LangGraph para evaluar puntajes STAR (evitando repreguntas innecesarias por defecto). | Implementado | `backend/app/agents/graph.py` (`route_after_evaluation`), `backend/app/config.py` (`ENABLE_FOLLOWUP_QUESTIONS`) | 
| **RN-04** | Extracción de longitud de respuesta y detección Regex de métricas cuantitativas. | Implementado | `backend/app/services/anonymizer.py` (`extract_auxiliary_features`, `QUANTITATIVE_METRICS_REGEX`) | 
| **RN-05** | Transición a `pasar_a_siguiente_tema` o al nodo terminal `finalizar_entrevista`. | Implementado | `backend/app/agents/graph.py`, `backend/app/agents/interviewer.py`, `backend/app/main.py` | 
| **RN-06** | Identificación automática de las 2 respuestas más débiles, ejemplos de mejora y Plan de Acción. | Implementado | `backend/app/agents/synthesizer.py` (`synthesize_final_report`), `frontend/js/app.js` | 
| **RN-07** | Estructura de tabla `golden_dataset` para validación estadística (`>= 0.75`). | Base Creada | `database/init.sql` (`golden_dataset` con calificaciones humanas y del modelo) | 
| **RN-08** | Evaluación crítica, objetiva, invariante y libre de sesgos demográficos o complacencia. | Implementado | `backend/app/agents/evaluator.py` (`EVALUATOR_SYSTEM_PROMPT` y `_critical_star_analyzer`) | 
| **RN-09** | Registro de satisfacción CSAT y validación estricta de salidas JSON con reintento/fallback (`< 0.5%` error). | Implementado | `backend/app/agents/evaluator.py`, `backend/app/main.py` (`/api/sessions/csat`) | 
| **RN-10** | Pipeline automatizado de anonimización de datos personales antes de guardar en BD. | Implementado | `backend/app/services/anonymizer.py` (`anonymize_pii`), invocado en `/api/sessions/start` y `/api/sessions/turn` | 
| **RN-11** | Arquitectura modular de prompts y monitoreo de latencia/validez JSON en BD. | Implementado | `database/init.sql` (`evaluation_latency_ms`, `json_format_valid` en `model_evaluations`) | 
| **RN-12** | Ejecución en contenedores Docker con versión fija y estandarizada de Python. | Implementado | `Dockerfile.backend` (`python:3.11.11-slim`), `docker-compose.yml`, `backend/requirements.txt` | 

## 3. Trazabilidad de Requisitos Funcionales (`RF-01` a `RF-15`)

| ID en SRS | Requisito Funcional | Estado | Implementación en el Proyecto | 
| ----- | ----- | ----- | ----- | 
| **RF-01** | Carga de currículum vitae y contexto de la vacante objetivo (campos limpios por usuario). | Implementado | Vista de Configuración en `frontend/index.html` y endpoint `POST /api/sessions/start` en `backend/app/main.py`. | 
| **RF-02** | Inicio de sesión de entrevista simulada en el chat interactivo (solo texto, con 15–20 preguntas adaptadas al contexto de la vacante). | Implementado | `backend/app/services/question_selector.py`, `database/init.sql` (176 preguntas en 8 carreras) y vista de Chat en `frontend/index.html`. | 
| **RF-03** | Evaluación crítica en tiempo real (0 a 5) con método STAR y decisión de estado mediante LangGraph (`gemini-3.8-flash` y `gpt-4o-mini`). | Implementado | `backend/app/agents/graph.py`, `backend/app/agents/evaluator.py` y `POST /api/sessions/turn`. | 
| **RF-04** | Panel lateral de métricas STAR en vivo estilizado con CSS responsivo. | Implementado | `frontend/index.html` y `frontend/css/styles.css`. | 
| **RF-05** | Reporte final descargable en PDF con las 2 respuestas más débiles y Plan de Acción Personalizado. | Implementado | `backend/app/agents/synthesizer.py`, `GET /api/sessions/{session_id}/report` y descarga directa `.pdf` con `jsPDF` en `frontend/js/app.js`. | 
| **RF-06** | Registro de calificación de satisfacción (CSAT). | Implementado | `POST /api/sessions/csat` en `backend/app/main.py` y selector 1–5 en vista de Resultados. | 
| **RF-07** | Consulta de historial personal aislado por usuario y Tasa de Evolución de Puntaje. | Implementado | `GET /api/users/{user_id}/history` en `backend/app/main.py` y `historiesByUser[email]` en `frontend/js/app.js`. | 
| **RF-08 a RF-10** | Catálogo de rúbricas, recursos de estudio, Golden Dataset y flujo Human-in-the-loop (Product Owner). | Esquema SQL y Semilla Listos | Tablas `study_resources` y `golden_dataset` creadas y pobladas en `database/init.sql`. | 
| **RF-11 a RF-15** | Orquestación LangGraph, validación estadística, anonimización en PostgreSQL y contenedores Docker (MLOps). | Implementado en Backend/Docker | `backend/app/agents/graph.py`, `backend/app/services/anonymizer.py`, `database/init.sql`, `Dockerfile.backend` y `docker-compose.yml`. | 

## 4. Trazabilidad de Requisitos de Información (`RIF-01` a `RIF-05`) e Interfaz (`RIN-01` a `RIN-04`)

* **RIF-01 (`interview_sessions`)**: Implementada en `database/init.sql` y `backend/app/models.py` (`InterviewSession`).

* **RIF-02 (`message_turns`)**: Implementada en `database/init.sql` y `backend/app/models.py` (`MessageTurn`).

* **RIF-03 (`model_evaluations`)**: Implementada en `database/init.sql` y `backend/app/models.py` (`ModelEvaluation` en escala 0 a 5).

* **RIF-04 (`user_feedback` y `golden_dataset`)**: Implementadas en `database/init.sql` y `backend/app/models.py` (`UserFeedback`).

* **RIF-05 (`rbac_roles` y `users`)**: Implementadas en `database/init.sql` con validación de correos reales (DNS MX) y verificador oficial de Google Identity Services.

* **RIN-01 a RIN-04**: Implementados mediante `docker-compose.yml` conectando `frontend`, `backend` (`gpt-4o-mini` + `gemini-3.8-flash` + LangGraph), `ollama` y `db` (PostgreSQL).