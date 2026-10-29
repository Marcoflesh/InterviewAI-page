# Roadmap de Desarrollo — InterviewAI

Este documento registra la evolución iterativa de **InterviewAI**, diferenciando los hitos completados (Pasado), los componentes implementados en la iteración actual (`v0.3.0`) y las funcionalidades programadas para las siguientes iteraciones.

---

## 1. Hitos Pasados (Fase 0, `v0.1.0` y `v0.2.0`)

- [x] **Diagnóstico Institucional y Levantamiento de Necesidades**: Análisis del problema de ansiedad en entrevistas (74.2% de los estudiantes) y desconocimiento del método STAR (65.5%).
- [x] **Especificación de Requisitos de Software (SRS bajo ISO/IEC/IEEE 29148-2018)**: Definición formal de Reglas de Negocio (`RN-01` a `RN-12`), Requisitos Funcionales (`RF-01` a `RF-15`), No Funcionales (`RNF-01` a `RNF-09`), de Información (`RIF-01` a `RIF-05`) e Interfaz (`RIN-01` a `RIN-04`).
- [x] **Infraestructura Docker, Esquema PostgreSQL con 176 Preguntas y Descarga PDF con `jsPDF` (`v0.1.0` – `v0.2.0`)**.

---

## 2. Estado Actual (Iteración `v0.3.0` — Evaluación Crítica 0–5, Agentes `gpt-4o-mini` + `gemini-3.8-flash`, Validador de Correo Real MX, Google SDK Oficial y Aislamiento por Usuario)

- [x] **Evaluación Crítica y Objetiva en Escala `0 a 5` (Cero Complacencia)**:
  - Se amplió la escala a **`[0, 5]`** en PostgreSQL (`database/init.sql`), esquemas Pydantic (`schemas.py`), Agente Evaluador (`evaluator.py`) y Frontend (`js/app.js`).
  - Respuestas sin sentido, evasivas (`"no sé"`, `"nada"`), vacías o habilidades no demostradas reciben **`0/5` (`0.0 / 5.0`)** con diagnóstico crítico directo.
  - Ampliación del analizador de raíces semánticas y léxicas para reconocer respuestas bien estructuradas en lenguaje natural profesional y premiarlas justamente entre `4/5` y `5/5` sin penalizaciones artificiales.
- [x] **Integración y Documentación de Agentes `gpt-4o-mini` y `gemini-3.8-flash` (`GUIA_CONFIGURACION_APIS.md`)**:
  - Configuración directa en `.env.example`, `docker-compose.yml`, `backend/app/config.py`, `evaluator.py`, `interviewer.py`, `synthesizer.py` y `frontend/js/app.js` con comentarios explícitos (`# >>> AQUÍ COLOCA TU API KEY ... <<<`) y guía paso a paso en `GUIA_CONFIGURACION_APIS.md`.
  - Eliminación del botón y modal de configuración de API de la interfaz gráfica para mantener toda la configuración limpia en `.env`.
- [x] **Validador de Correos Reales con Verificación DNS MX en Vivo (`backend/app/auth.py`, `frontend/js/app.js`)**:
  - Bloqueo de dominios ficticios, de prueba o temporales (`ejemplo.com`, `test.com`, `tempmail.com`, `mailinator.com`, etc.) y consulta en tiempo real a `https://dns.google/resolve?name=<dominio>&type=MX` para comprobar que el dominio del correo tenga servidores de correo reales antes de registrar una cuenta.
- [x] **Verificador Oficial de Google Identity Services (`accounts.google.com/gsi/client`)**:
  - Eliminación del modal simulado y conexión directa con el SDK oficial de Google Identity Services y validación criptográfica JWT en `backend/app/auth.py`.
- [x] **Vinculación del "Contexto de la vacante" con las Preguntas y Limpieza de Interfaz**:
  - Selección y adaptación de las 15–20 preguntas de la carrera en función de la afinidad semántica con el **Contexto de la vacante** y el **Puesto objetivo**.
  - Eliminación de textos autorrellenados en todos los campos, eliminación de la ventana de conteo de preguntas en configuración, eliminación del subtítulo en login y ajuste del placeholder del chat únicamente a `"Escribe tu respuesta"`.
- [x] **Aislamiento Total de Perfil, Historial y Formulario por Usuario**:
  - Cada cuenta almacena y consulta exclusivamente su propio historial (`historiesByUser[email]`), y al cerrar sesión o cambiar de usuario se reinician por completo los campos de **Nueva práctica** y la sesión activa.

---

## 3. Siguientes Funcionalidades (Fase 2 y Fase 3)

- [ ] **Extracción directa de archivos PDF/DOCX en carga de CV**: Integrar parser (`pypdf` / `python-docx`) para adjuntar archivo además de escribir el resumen.
- [ ] **Panel de Administración para Product Owner y MLOps (`/admin`)**: CRUD protegido por RBAC para gestionar el Golden Dataset y ejecutar auditorías estadísticas (`>= 0.75`).
