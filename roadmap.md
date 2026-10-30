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
- [ ] **Pendiente del usuario**: revocar el token `ghp_`, crear una llave secreta de OpenAI `sk-…` (se recibió el ID `key_…`), configurar orígenes de Google y correr `check_apis.py` y `stress_test_agents.py` en su computadora (ver `PASO_A_PASO.md`).

---

## 3. Siguientes Funcionalidades (Fase 2 y Fase 3)

- [ ] **Backend público para GitHub Pages**: desplegar `Dockerfile.backend` (Render / Cloud Run) con PostgreSQL administrado y configurar `API_BASE_URL`.
- [ ] **Migrar `OPENAI_CHAT_MODEL`** antes del 14/01/2027 (retiro de `gpt-4o-mini`) y repetir la prueba de estrés.
- [ ] **Extracción directa de archivos PDF/DOCX en carga de CV** (`pypdf` / `python-docx`).
- [ ] **Panel de Administración `/admin`** con RBAC para Product Owner y MLOps (Golden Dataset y auditoría estadística `>= 0.75`).
- [ ] **Verificación de correo por enlace**, sesión en cookie `HttpOnly` y limitador en Redis.
- [ ] **Backend asíncrono** (`httpx.AsyncClient`) para escalar más allá de ~100 usuarios simultáneos.
