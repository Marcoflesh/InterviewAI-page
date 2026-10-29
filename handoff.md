# Documento de Handoff y Continuidad Técnica — InterviewAI

**Fecha de corte:** 29 de octubre de 2026  
**Repositorio objetivo:** `https://github.com/Marcoflesh/InterviewAI-page.git`  
**Propósito:** Garantizar la continuidad inmediata del desarrollo en caso de agotamiento de tokens o cambio de sesión/desarrollador, registrando la arquitectura construida, las decisiones técnicas tomadas y los pasos exactos para continuar.

---

## 1. Resumen del Estado Actual

Se construyó desde cero el esqueleto completo y funcional de la plataforma **InterviewAI** siguiendo la Especificación de Requisitos de Software (SRS) y las directrices explícitas del usuario:

1. **Base de Datos SQL (`database/init.sql`)**: Esquema relacional completo en PostgreSQL con 10 tablas normalizadas, índices de rendimiento y una semilla de **120 preguntas de entrevista distribuidas en 8 carreras universitarias** (15 por carrera) más recursos de estudio curados y registros base del Golden Dataset.
2. **Backend en Python con FastAPI, LangGraph y Ollama (`backend/app/`)**:
   - Orquestación cíclica/condicional en `backend/app/agents/graph.py` usando `StateGraph` de LangGraph.
   - Integración con **Ollama** (`backend/app/agents/evaluator.py`, `interviewer.py`, `synthesizer.py`) empleando salidas JSON estructuradas y un mecanismo de *fallback* determinista para que la evaluación nunca falle ni supere el umbral de 2.5 segundos por turno, incluso mientras Ollama descarga el modelo local.
   - Pipeline de anonimización de datos personales (PII) y extractor Regex de métricas cuantitativas en `backend/app/services/anonymizer.py`.
   - Selector aleatorio de preguntas por carrera sin repetición en `backend/app/services/question_selector.py`.
3. **Frontend Minimalista (`frontend/index.html`, `frontend/css/styles.css`, `frontend/js/app.js`)**:
   - Diseño limpio y minimalista en CSS puro (Grid/Flexbox), sin saturación de elementos.
   - Pantalla inicial con autenticación mediante Google (`Continuar con Google`).
   - **Cero etiquetas de requerimientos (`RF-XX`, `RN-XX`, etc.) visibles en la interfaz**.
   - **Cero controles de grabación o uso de voz**: interacción 100% por texto en el chatbot.
   - Panel lateral limpio de indicadores STAR en vivo y vista de Reporte Final con las 2 respuestas más débiles, ejemplos redactados de mejora, Plan de Acción Personalizado, exportación a PDF y encuesta CSAT.
4. **Contenedorización con Docker (`docker-compose.yml`, `Dockerfile.backend`, `Dockerfile.frontend`)**:
   - Versiones fijadas para evitar conflictos entre entornos (`python:3.11.11-slim`, `postgres:16.6-alpine`, `ollama/ollama:0.5.7`, `nginx:1.27.3-alpine`).

---

## 2. Decisiones Arquitectónicas y de Producto Tomadas

| Tema | Decisión Tomada | Justificación |
| :--- | :--- | :--- |
| **Motor de IA Local (Ollama vs. API Cloud)** | Se configuró **Ollama** (`http://ollama:11434`, modelo por defecto `llama3.2:3b` configurable vía `.env`) en lugar de Gemini/OpenAI mencionadas en el SRS original. | Solicitud explícita del usuario: *"Use ollama for the AI, Langraph for the manage of the AI agents, Docker for the versions and SQL for the database."* |
| **Política de Preguntas de Seguimiento (`profundizar_pregunta`)** | En `backend/app/config.py` y `graph.py`, el parámetro `ENABLE_FOLLOWUP_QUESTIONS` está configurado en `false` por defecto. Cada turno avanza directamente a la siguiente pregunta aleatoria de la carrera (`pasar_a_siguiente_tema`), pero el nodo `profundizar_pregunta` permanece programado en el grafo y puede activarse cambiando `ENABLE_FOLLOWUP_QUESTIONS=true`. | Solicitud explícita del usuario: *"Create a whole bunch of questions for the careers so the questions can be randomized for every user depending on their career and avoid follow-up questions if not needed."* |
| **Interfaz Limpia sin Códigos del SRS ni Voz** | Se eliminó cualquier referencia visual a códigos `RF-XX`/`RN-XX`/`RIF-XX` en las pantallas y se omitió cualquier botón de micrófono o API de voz (Web Speech API). | Solicitud explícita del usuario: *"Don't show were are the RF or any of the requirements being used in the page. Keep it all simple. Don't use any voice record or usage, just texting the chatbot."* |
| **Autenticación con Google en Desarrollo vs. Producción** | `backend/app/auth.py` verifica tokens JWT reales de Google OAuth 2.0 cuando `GOOGLE_CLIENT_ID` está definido en `.env`, y ofrece un flujo inmediato de desarrollo local cuando no se ha configurado aún la credencial de Google Cloud. | Permite probar todo el flujo extremo a extremo desde el primer `docker compose up` sin bloquear al desarrollador por credenciales externas pendientes. |
| **Resiliencia del Frontend (Modo Conectado + Modo Autónomo)** | `frontend/js/app.js` consume los endpoints REST de FastAPI (`/api/...`) y cuenta con respaldo local en memoria con las 120 preguntas por carrera. | Garantiza que la interfaz sea 100% funcional tanto dentro del stack Docker como en previsualizaciones estáticas (Canvas). |

---

## 3. Estructura del Proyecto

```text
InterviewAI-page/
├── .env.example                  # Variables de entorno de referencia
├── .gitignore                    # Archivos ignorados por Git
├── Dockerfile.backend            # Imagen Python 3.11.11-slim para FastAPI + LangGraph
├── Dockerfile.frontend           # Imagen Nginx 1.27.3-alpine con proxy inverso a /api/
├── docker-compose.yml            # Orquestación de db, ollama, backend y frontend
├── push_to_github.sh             # Script listo para subir los commits a GitHub
├── README.md                     # Guía de instalación y levantamiento con Docker
├── roadmap.md                    # Estado de features pasadas, actuales y siguientes
├── handoff.md                    # Este documento de continuidad técnica
├── traceability.md               # Bitácora de cambios y matriz de trazabilidad contra el SRS
├── database/
│   └── init.sql                  # Esquema PostgreSQL + 120 preguntas aleatorias en 8 carreras
├── backend/
│   ├── requirements.txt          # Dependencias Python con versiones fijas
│   └── app/
│       ├── main.py               # Endpoints FastAPI (/api/auth/google, /api/sessions/start, /turn, /report, /csat)
│       ├── config.py             # Configuración centralizada con Pydantic Settings
│       ├── database.py           # Conexión SQLAlchemy a PostgreSQL
│       ├── models.py             # Modelos ORM (Users, Careers, QuestionBank, Sessions, Turns, Evaluations, Feedback)
│       ├── schemas.py            # Esquemas Pydantic de entrada/salida
│       ├── auth.py               # Verificación de Google Sign-In y RBAC
│       ├── services/
│       │   ├── anonymizer.py     # Anonimización de PII en CV y extracción Regex de métricas cuantitativas
│       │   └── question_selector.py # Muestreo aleatorio sin reemplazo por carrera
│       └── agents/
│           ├── state.py          # Definición de InterviewGraphState para LangGraph
│           ├── evaluator.py      # Nodo Agente Evaluador (Ollama JSON + fallback heurístico)
│           ├── interviewer.py    # Nodos Agente Entrevistador (avance aleatorio, seguimiento opcional y cierre)
│           ├── synthesizer.py    # Síntesis de las 2 respuestas más débiles y Plan de Acción
│           └── graph.py          # Compilación del StateGraph de LangGraph
└── frontend/
    ├── nginx.conf                # Configuración Nginx para SPA y proxy /api/
    ├── index.html                # Estructura HTML5 minimalista en 5 vistas limpias
    ├── css/
    │   └── styles.css            # Hoja de estilos minimalista y responsiva
    └── js/
        └── app.js                # Lógica de cliente, Google login, chat por texto y reporte PDF
```

---

## 4. Cómo Levantar el Proyecto y Subirlo a GitHub

### 4.1 Subir al repositorio `https://github.com/Marcoflesh/InterviewAI-page.git`
Debido a que el entorno sandbox de generación no tiene salida de red hacia GitHub ni acceso a tus llaves privadas/tokens de GitHub, el repositorio Git ya fue inicializado localmente con todos los commits listos. Solo descarga y descomprime `InterviewAI-page.zip` y ejecuta:

```bash
cd InterviewAI-page
chmod +x push_to_github.sh
./push_to_github.sh
```
*(O manualmente: `git push -u origin main`)*.

### 4.2 Levantar con Docker y Descargar el Modelo en Ollama
```bash
cp .env.example .env
docker compose up --build -d
# Descargar el modelo ligero en el contenedor de Ollama (solo la primera vez):
docker exec -it interviewai-ollama ollama pull llama3.2:3b
```
- **Frontend**: `http://localhost:3000`
- **Backend API & Swagger Docs**: `http://localhost:8000/docs`

---

## 5. Próximos Pasos Exactos para la Siguiente Sesión (Next Steps)

1. **Confirmar decisiones abiertas con el usuario** (listadas en la respuesta de entrega):
   - Modelo exacto de Ollama preferido según la RAM/VRAM disponible (`llama3.2:3b`, `llama3.1:8b` o `qwen2.5:7b`).
   - Política de repreguntas: mantener desactivadas las preguntas de seguimiento (`ENABLE_FOLLOWUP_QUESTIONS=false`) en todos los casos o activarlas únicamente cuando el puntaje de Resultado sea crítico (`1/5`).
   - Vistas de administración (Product Owner y MLOps): definir si se mantienen como rutas separadas (`/admin`) para no ensuciar la interfaz minimalista del estudiante.
2. **Integrar Google Identity Services SDK real en el cliente**:
   - Una vez que el usuario genere su `GOOGLE_CLIENT_ID` en Google Cloud Console, colocarlo en `.env` y en el botón de Google Identity Services en `frontend/index.html`.
3. **Implementar cargador de archivos PDF para el CV**:
   - Agregar endpoint `POST /api/sessions/upload-cv` con `pypdf` que extraiga el texto del PDF y lo pase automáticamente por `anonymize_pii()`.
4. **Construir el notebook/script de validación estadística (`scripts/evaluate_golden_dataset.py`)**:
   - Conectar a la tabla `golden_dataset` en PostgreSQL y calcular la correlación frente a las calificaciones humanas (`>= 0.75`).
