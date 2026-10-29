# Matriz de Trazabilidad y Bitácora de Cambios — InterviewAI

Este archivo funciona como registro de cambios (changelog) y matriz de trazabilidad entre la Especificación de Requisitos de Software (SRS), los ajustes solicitados por el usuario y los archivos implementados en el repositorio.

---

## 1. Bitácora de Cambios (Changelog)

### `[v0.1.0] - 2026-10-29 — Construcción del Esqueleto Completo del Proyecto`
- **Creado `database/init.sql`**: Esquema PostgreSQL para sesiones, turnos, evaluaciones STAR, retroalimentación CSAT, Golden Dataset, RBAC, catálogo de 8 carreras y banco de **120 preguntas aleatorias autocontenidas** (15 por carrera) más recursos de estudio curados.
- **Creado `backend/app/services/anonymizer.py`**: Pipeline de anonimización de datos personales (correos, teléfonos, matrículas, CURP/RFC y perfiles) y detector Regex de métricas cuantitativas.
- **Creado `backend/app/services/question_selector.py`**: Selector aleatorio sin repetición de preguntas filtradas por la carrera profesional del estudiante.
- **Creado `backend/app/agents/` (`state.py`, `evaluator.py`, `interviewer.py`, `synthesizer.py`, `graph.py`)**: Orquestación de agentes con **LangGraph** conectada a **Ollama**, con evaluación STAR en tiempo real (`[1, 5]`), desactivación por defecto de repreguntas innecesarias para priorizar el banco aleatorio por carrera, y síntesis de las 2 respuestas más débiles con Plan de Acción.
- **Creado `backend/app/main.py`, `models.py`, `schemas.py`, `auth.py`, `config.py`, `database.py`**: Servidor REST en FastAPI con soporte para inicio de sesión con Google, sesiones de entrevista, evaluación por turno, generación de reporte final, registro de CSAT e historial de sesiones.
- **Creado `frontend/` (`index.html`, `css/styles.css`, `js/app.js`, `nginx.conf`)**: Interfaz web minimalista, limpia, con inicio de sesión de Google al entrar, chatbot exclusivamente de texto (sin voz), sin etiquetas de requisitos (`RF-XX`) visibles en pantalla, indicadores STAR en vivo y exportación de reporte en PDF.
- **Creado `Dockerfile.backend`, `Dockerfile.frontend`, `docker-compose.yml`, `.env.example`**: Infraestructura contenedorizada con versiones fijas de Python (`3.11.11`), PostgreSQL (`16.6`), Ollama (`0.5.7`) y Nginx (`1.27.3`).
- **Creado `roadmap.md`, `handoff.md`, `traceability.md`, `README.md`, `push_to_github.sh`**: Documentación iterativa de continuidad y script de despliegue al repositorio de GitHub.

---

## 2. Trazabilidad de Reglas de Negocio (`RN-01` a `RN-12`)

| ID en SRS | Descripción Resumida | Estado | Archivo(s) / Componente(s) que lo Implementan |
| :--- | :--- | :--- | :--- |
| **RN-01** | Sesión de entre 5 y 10 respuestas adaptadas a carrera, rol y seniority. | Implementado | `database/init.sql` (`CHECK (total_questions BETWEEN 5 AND 10)`), `backend/app/schemas.py`, `frontend/index.html` |
| **RN-02** | Vector de puntuación `[1, 5]` en estructura STAR (S, T, A, R), claridad técnica y pertinencia. | Implementado | `backend/app/agents/evaluator.py`, `database/init.sql` (`model_evaluations`), `frontend/js/app.js` |
| **RN-03** | Aristas condicionales en LangGraph para evaluar puntajes STAR (con ajuste del usuario para evitar repreguntas innecesarias). | Implementado | `backend/app/agents/graph.py` (`route_after_evaluation`), `backend/app/config.py` (`ENABLE_FOLLOWUP_QUESTIONS`) |
| **RN-04** | Extracción de longitud de respuesta y detección Regex de métricas cuantitativas. | Implementado | `backend/app/services/anonymizer.py` (`extract_auxiliary_features`, `QUANTITATIVE_METRICS_REGEX`) |
| **RN-05** | Transición a `pasar_a_siguiente_tema` o al nodo terminal `finalizar_entrevista`. | Implementado | `backend/app/agents/graph.py`, `backend/app/agents/interviewer.py`, `backend/app/main.py` |
| **RN-06** | Identificación automática de las 2 respuestas más débiles, ejemplos de mejora y Plan de Acción. | Implementado | `backend/app/agents/synthesizer.py` (`synthesize_final_report`), `frontend/js/app.js` |
| **RN-07** | Estructura de tabla `golden_dataset` para validación estadística (`>= 0.75`). | Base Creada | `database/init.sql` (`golden_dataset` con calificaciones humanas y del modelo) |
| **RN-08** | Evaluación invariante y libre de sesgos demográficos o modismos regionales. | Implementado | `backend/app/agents/evaluator.py` (`EVALUATOR_SYSTEM_PROMPT` con instrucción de invariancia) |
| **RN-09** | Registro de satisfacción CSAT y validación estricta de salidas JSON con reintento/fallback (`< 0.5%` error). | Implementado | `backend/app/agents/evaluator.py` (reintento automático + fallback determinista), `backend/app/main.py` (`/api/sessions/csat`) |
| **RN-10** | Pipeline automatizado de anonimización de datos personales antes de guardar en BD. | Implementado | `backend/app/services/anonymizer.py` (`anonymize_pii`), invocado en `/api/sessions/start` y `/api/sessions/turn` |
| **RN-11** | Arquitectura modular de prompts y monitoreo de latencia/validez JSON en BD. | Implementado | `database/init.sql` (`evaluation_latency_ms`, `json_format_valid` en `model_evaluations`) |
| **RN-12** | Ejecución en contenedores Docker con versión fija y estandarizada de Python. | Implementado | `Dockerfile.backend` (`python:3.11.11-slim`), `docker-compose.yml`, `backend/requirements.txt` |

---

## 3. Trazabilidad de Requisitos Funcionales (`RF-01` a `RF-15`)

| ID en SRS | Requisito Funcional | Estado | Implementación en el Proyecto |
| :--- | :--- | :--- | :--- |
| **RF-01** | Carga de currículum vitae y descripción de oferta laboral objetivo. | Implementado | Vista de Configuración en `frontend/index.html` y endpoint `POST /api/sessions/start` en `backend/app/main.py`. |
| **RF-02** | Inicio de sesión de entrevista simulada en el chat interactivo (solo texto, con preguntas aleatorias por carrera). | Implementado | `backend/app/services/question_selector.py`, `database/init.sql` (120 preguntas en 8 carreras) y vista de Chat en `frontend/index.html`. |
| **RF-03** | Evaluación en tiempo real con método STAR y decisión de estado mediante LangGraph. | Implementado | `backend/app/agents/graph.py`, `backend/app/agents/evaluator.py` y `POST /api/sessions/turn`. |
| **RF-04** | Panel lateral de métricas STAR en vivo estilizado con CSS responsivo. | Implementado | `frontend/index.html` (`aside` de desempeño del turno) y `frontend/css/styles.css`. |
| **RF-05** | Reporte final descargable con las 2 respuestas más débiles y Plan de Acción Personalizado. | Implementado | `backend/app/agents/synthesizer.py`, `GET /api/sessions/{session_id}/report` y vista de Resultados con impresión PDF en `frontend/index.html`. |
| **RF-06** | Registro de calificación de satisfacción (CSAT). | Implementado | `POST /api/sessions/csat` en `backend/app/main.py` y selector 1–5 en vista de Resultados. |
| **RF-07** | Consulta de historial de sesiones y Tasa de Evolución de Puntaje. | Implementado | `GET /api/users/{user_id}/history` en `backend/app/main.py` y vista de Historial en `frontend/index.html`. |
| **RF-08 a RF-10** | Catálogo de rúbricas, recursos de estudio, Golden Dataset y flujo Human-in-the-loop (Product Owner). | Esquema SQL y Semilla Listos | Tablas `study_resources` y `golden_dataset` creadas y pobladas en `database/init.sql` (UI administrativa programada para Fase 2 en `roadmap.md`). |
| **RF-11 a RF-15** | Orquestación LangGraph, validación estadística, anonimización en PostgreSQL y contenedores Docker (MLOps). | Implementado en Backend/Docker | `backend/app/agents/graph.py`, `backend/app/services/anonymizer.py`, `database/init.sql`, `Dockerfile.backend` y `docker-compose.yml`. |

---

## 4. Trazabilidad de Requisitos de Información (`RIF-01` a `RIF-05`) e Interfaz (`RIN-01` a `RIN-04`)

- **RIF-01 (`interview_sessions`)**: Implementada en `database/init.sql` y `backend/app/models.py` (`InterviewSession`).
- **RIF-02 (`message_turns`)**: Implementada en `database/init.sql` y `backend/app/models.py` (`MessageTurn`).
- **RIF-03 (`model_evaluations`)**: Implementada en `database/init.sql` y `backend/app/models.py` (`ModelEvaluation`).
- **RIF-04 (`user_feedback` y `golden_dataset`)**: Implementadas en `database/init.sql` y `backend/app/models.py` (`UserFeedback`).
- **RIF-05 (`rbac_roles` y `users`)**: Implementadas en `database/init.sql` con los 3 roles (`student`, `product_owner`, `mlops_admin`) y login con Google OAuth.
- **RIN-01 a RIN-04**: Implementados mediante la comunicación interna en `docker-compose.yml` entre `frontend` (Nginx), `backend` (FastAPI + LangGraph), `ollama` (LLM local) y `db` (PostgreSQL).
