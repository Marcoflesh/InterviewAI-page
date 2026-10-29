# Roadmap de Desarrollo — InterviewAI

Este documento registra la evolución iterativa de **InterviewAI**, diferenciando los hitos completados (Pasado), los componentes implementados en la iteración actual (`v0.2.0`) y las funcionalidades programadas para las siguientes iteraciones.

---

## 1. Hitos Pasados (Fase 0 y Iteración `v0.1.0`)

- [x] **Diagnóstico Institucional y Levantamiento de Necesidades**: Análisis del problema de ansiedad en entrevistas (74.2% de los estudiantes) y desconocimiento del método STAR (65.5%).
- [x] **Especificación de Requisitos de Software (SRS bajo ISO/IEC/IEEE 29148-2018)**: Definición formal de 12 Reglas de Negocio (`RN-01` a `RN-12`), 15 Requisitos Funcionales (`RF-01` a `RF-15`), 9 Requisitos No Funcionales (`RNF-01` a `RNF-09`), 5 Requisitos de Información (`RIF-01` a `RIF-05`) y 4 Requisitos de Interfaz (`RIN-01` a `RIN-04`).
- [x] **Esqueleto Inicial Full-Stack (`v0.1.0`)**: Configuración base de contenedores Docker (`python:3.11.11-slim`, `postgres:16.6-alpine`, `ollama/ollama:0.5.7`, `nginx:1.27.3-alpine`), esquema inicial en PostgreSQL y grafo base en LangGraph.

---

## 2. Estado Actual (Iteración `v0.2.0` — Autenticación Triple, Evaluación Semántica STAR, Descarga PDF Real y 15–20 Preguntas Aleatorias)

- [x] **Autenticación Triple Verificada (`Iniciar sesión`, `Registrar` y `Continuar con Google`)**:
  - **Iniciar sesión (Cuentas existentes)**: Verifica formato de correo electrónico, existencia de la cuenta registrada en PostgreSQL (`/api/auth/login`) / almacenamiento local y validación de contraseña con hash PBKDF2-HMAC-SHA256 (`backend/app/auth.py`).
  - **Registrar (Nuevas cuentas)**: Permite dar de alta nuevas cuentas verificando correo único, institución y contraseña mínima de 6 caracteres (`/api/auth/register`).
  - **Iniciar sesión con Google**: Selector y verificador OAuth de cuenta de Google (`/api/auth/google`) que valida el correo y carga los datos reales del perfil del usuario (nombre completo, correo verificado e iniciales/avatar en la barra superior).
- [x] **Generación Aleatoria Realista de 15 a 20 Preguntas por Sesión (`database/init.sql`, `backend/app/main.py`, `frontend/js/app.js`)**:
  - Expansión del banco de preguntas a **176 preguntas autocontenidas (22 por cada una de las 8 carreras)**.
  - Cada sesión genera automáticamente un número aleatorio entre **15 y 20 preguntas** sin repetición, e incluye un botón de corte voluntario (`Finalizar y ver reporte`) durante el chat para pruebas rápidas.
  - Cambio de etiqueta en configuración a **"Contexto de la vacante"**.
- [x] **Motor de Evaluación STAR Semántico y Léxico + Conector de Llaves API (`backend/app/agents/evaluator.py`, `frontend/js/app.js`)**:
  - Penalización inmediata (`1/5`) para respuestas cortas (`< 8` palabras), evasivas (`"no sé"`, `"hola"`) o sin relación con la pregunta.
  - Evaluación independiente de **Situación**, **Tarea**, **Acción (verbos en 1ra persona)**, **Resultado (conectores de logro + métricas Regex)**, **Claridad Técnica** (diccionario de 30+ términos técnicos por cada una de las 8 carreras) y **Pertinencia** (cruce léxico con la pregunta actual y el contexto de la vacante).
  - Visualización en vivo de las métricas cuantitativas y conceptos técnicos detectados en cada turno.
  - Modal **"Configurar API / IA"** en la barra superior para conectar llaves API propias (Google Gemini, OpenAI, Groq) o usar Ollama local.
- [x] **Descarga Directa de Archivo PDF (`jsPDF` + Generador Binario PDF 1.4)**:
  - Reemplazo de `window.print()` por generación y descarga real de documento `.pdf` (`Reporte_InterviewAI_<Candidato>.pdf`) mediante `jsPDF` con respaldo binario PDF 1.4 nativo para funcionar dentro de iframes/Canvas y cualquier navegador.

---

## 3. Siguientes Funcionalidades (Fase 2 y Fase 3)

- [ ] **Pruebas en Vivo con las Llaves API del Usuario**: Conectar las llaves API definitivas en el archivo `.env` / modal de configuración para comparar latencia y correlación entre `llama3.2:3b` (Ollama), `gemini-2.5-flash` y `gpt-4o-mini`.
- [ ] **Extracción directa de archivos PDF/DOCX en carga de CV**: Integrar parser (`pypdf` / `python-docx`) además del campo de texto en la pantalla de configuración.
- [ ] **Panel de Administración para Product Owner y MLOps (`/admin`)**: CRUD protegido por RBAC para gestionar el Golden Dataset y visualizar la correlación estadística (`>= 0.75`).
