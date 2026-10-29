# InterviewAI — Simulador Inteligente de Entrevistas Laborales

Plataforma web minimalista de práctica de entrevistas laborales por escrito con evaluación en tiempo real bajo la metodología **STAR** (Situación, Tarea, Acción y Resultado), preguntas aleatorias por carrera profesional, orquestación de agentes con **LangGraph**, inferencia local con **Ollama**, persistencia en **PostgreSQL** y despliegue reproducible en **Docker**.

## Características Principales

- **Inicio de Sesión con Google**: Pantalla de bienvenida limpia centrada en autenticación con Google.
- **Interfaz Minimalista y 100% Basada en Texto**: Sin saturación visual, sin etiquetas técnicas de requerimientos en pantalla y sin grabación de voz.
- **Banco de 120 Preguntas Aleatorias en 8 Carreras**: Selección aleatoria sin repetición para Ingeniería de Software (`ITC`), Ciencia de Datos e IA (`ISD`), Ingeniería Industrial (`IIS`), Mecatrónica (`IMT`), Finanzas y Consultoría (`LAF`), Marketing y Producto (`LMC`), Biomédica y Biotecnología (`IBT`) y Arquitectura/Diseño/UX (`ARQ`).
- **Orquestación con LangGraph + Ollama**: Evaluación automática de cada respuesta calificando de 1 a 5 Situación, Tarea, Acción, Resultado, Claridad Técnica y Pertinencia, avanzando de forma fluida entre preguntas sin repreguntas innecesarias.
- **Privacidad y Anonimización**: Sanitización automática de datos personales (correos, teléfonos, matrículas, identificadores) antes de guardar en PostgreSQL.
- **Reporte Final y Plan de Acción**: Identificación de las 2 respuestas más débiles con ejemplos redactados de mejora, recursos de estudio por carrera y descarga en PDF.

## Requisitos Previos

- [Docker](https://docs.docker.com/get-docker/) y Docker Compose instalados.

## Ejecución Rápida con Docker

1. Copia el archivo de variables de entorno:
   ```bash
   cp .env.example .env
   ```
2. Levanta los contenedores (PostgreSQL, Ollama, Backend FastAPI/LangGraph y Frontend Nginx):
   ```bash
   docker compose up --build -d
   ```
3. Descarga el modelo en el contenedor de Ollama (solo la primera vez):
   ```bash
   docker exec -it interviewai-ollama ollama pull llama3.2:3b
   ```
4. Abre la aplicación en tu navegador:
   - **Aplicación Web**: `http://localhost:3000`
   - **Documentación API (Swagger)**: `http://localhost:8000/docs`

## Documentación del Proyecto

- [`roadmap.md`](./roadmap.md): Estado de las funcionalidades pasadas, actuales y siguientes iteraciones.
- [`handoff.md`](./handoff.md): Documento de continuidad técnica, arquitectura y decisiones tomadas.
- [`traceability.md`](./traceability.md): Bitácora de cambios y matriz de trazabilidad frente al SRS.
