# Roadmap de Desarrollo — InterviewAI

Este documento registra la evolución iterativa de **InterviewAI**, diferenciando los hitos completados (Pasado), los componentes implementados en esta entrega base (Actual) y las funcionalidades programadas para las siguientes iteraciones (Siguiente).

---

## 1. Hitos Pasados (Fase 0 — Especificación y Diagnóstico)

- [x] **Diagnóstico Institucional y Levantamiento de Necesidades**: Análisis del problema de ansiedad en entrevistas (74.2% de los estudiantes) y desconocimiento del método STAR (65.5%).
- [x] **Especificación de Requisitos de Software (SRS bajo ISO/IEC/IEEE 29148-2018)**: Definición formal de 12 Reglas de Negocio (`RN-01` a `RN-12`), 15 Requisitos Funcionales (`RF-01` a `RF-15`), 9 Requisitos No Funcionales (`RNF-01` a `RNF-09`), 5 Requisitos de Información (`RIF-01` a `RIF-05`) y 4 Requisitos de Interfaz (`RIN-01` a `RIN-04`).
- [x] **Creación del Repositorio Remoto**: Inicialización del repositorio en GitHub (`https://github.com/Marcoflesh/InterviewAI-page.git`).

---

## 2. Estado Actual (Fase 1 — Esqueleto Funcional Full-Stack y Orquestación Base)

- [x] **Infraestructura Contenedorizada con Docker (`docker-compose.yml`, `Dockerfile.backend`, `Dockerfile.frontend`)**:
  - Entorno reproducible con versiones fijas: Python `3.11.11-slim`, PostgreSQL `16.6-alpine`, Ollama `0.5.7` y Nginx `1.27.3-alpine`.
- [x] **Base de Datos Relacional en PostgreSQL (`database/init.sql`)**:
  - Implementación completa de las tablas `rbac_roles`, `users`, `careers`, `question_bank`, `study_resources`, `interview_sessions`, `message_turns`, `model_evaluations`, `user_feedback` y `golden_dataset`.
  - Semilla inicial de **120 preguntas autocontenidas distribuidas en 8 carreras profesionales** (15 preguntas por carrera: `ITC`, `ISD`, `IIS`, `IMT`, `LAF`, `LMC`, `IBT`, `ARQ`) para garantizar selección aleatoria sin repetición por usuario.
- [x] **Orquestación de Agentes con LangGraph y Ollama (`backend/app/agents/`)**:
  - Grafo de estados (`StateGraph`) que coordina al **Agente Evaluador** (LLM-as-a-Judge con salida JSON validada y respaldo heurístico para asegurar `< 0.5%` de fallos de formato) y al **Agente Entrevistador**.
  - Configuración por defecto (`ENABLE_FOLLOWUP_QUESTIONS=false`) para avanzar directamente a la siguiente pregunta aleatoria de la carrera del candidato sin generar repreguntas innecesarias, conservando soporte opcional para profundización (`profundizar_pregunta`) si se activa por variable de entorno.
- [x] **Anonimización de Datos Personales y Extracción Regex (`backend/app/services/anonymizer.py`)**:
  - Sanitización automática de correos electrónicos, teléfonos, matrículas/CURP/RFC y enlaces personales antes de almacenar currículums o respuestas en PostgreSQL.
  - Detección mediante expresiones regulares de métricas cuantitativas (`%`, `ms`, `$`, tiempos, volúmenes) para respaldar la dimensión de Resultado del método STAR.
- [x] **Interfaz Web Minimalista y Limpia (`frontend/` e `interviewai.html`)**:
  - Pantalla de acceso inicial con inicio de sesión de Google (`Continuar con Google`).
  - Flujo limpio en 4 vistas sin saturación visual, **sin etiquetas de requerimientos (`RF-XX`) visibles para el usuario** y **100% basado en texto (sin grabación ni uso de voz)**.
  - Panel lateral minimalista con barras de progreso STAR en vivo y vista de Reporte Final con las 2 respuestas más débiles, ejemplos de mejora redactados, Plan de Acción Personalizado, exportación a PDF y calificación CSAT.

---

## 3. Siguientes Funcionalidades (Fase 2 y Fase 3 — Expansión y MLOps)

### Fase 2 — Experiencia de Estudiante y Product Owner (Corto Plazo)
- [ ] **Extracción directa de archivos PDF/DOCX en carga de CV**: Integrar parser ligero (`pypdf` / `python-docx`) además del pegado directo de texto en la pantalla de configuración.
- [ ] **Panel de Administración para Product Owner / Evaluador Experto**:
  - CRUD minimalista protegido por rol (`product_owner`) para agregar nuevas preguntas al banco por carrera, actualizar recursos de estudio y etiquetar pares pregunta-respuesta en la tabla `golden_dataset` (flujo Human-in-the-loop).
- [ ] **Credenciales OAuth 2.0 de Producción en Google Cloud Console**: Conectar el `GOOGLE_CLIENT_ID` oficial del dominio desplegado para reemplazar el modo híbrido de desarrollo.

### Fase 3 — Validación Estadística MLOps y Analítica Institucional (Mediano Plazo)
- [ ] **Script Automatizado de Validación contra Golden Dataset (`scripts/validate_golden_dataset.py` / Google Colab)**:
  - Calcular automáticamente el coeficiente de correlación de Pearson / Spearman y Kappa de Cohen entre el Agente Evaluador (Ollama) y las calificaciones humanas (`>= 0.75`) antes de cada despliegue.
- [ ] **Auditoría Automatizada de Invariancia y Ausencia de Sesgos**:
  - Pruebas de perturbación demográfica (género, edad, nacionalidad y modismos regionales) verificando varianza nula en el vector `[1, 5]`.
- [ ] **Tablero Analítico MLOps**:
  - Vista exclusiva para el rol `mlops_admin` con métricas agregadas por carrera, tasa de evolución de puntaje, CSAT promedio (`> 80%`) y análisis de motivos de abandono.
