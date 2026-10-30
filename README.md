# InterviewAI — Simulador Inteligente de Entrevistas Laborales

Plataforma web minimalista para practicar entrevistas laborales por escrito, con evaluación crítica en tiempo real (escala **0 a 5**) bajo el método **STAR**, preguntas adaptadas a la carrera y al contexto de la vacante, y reporte final descargable en PDF.

- **Agentes de IA (LangGraph):** Entrevistador local `qwen3.5:4b` con Ollama (gratis), Evaluador y Sintetizador `gemini-3.8-flash`, con respaldo automático entre proveedores y analizador determinista local.
- **Stack:** FastAPI + PostgreSQL 16 + nginx en Docker. Frontend HTML/CSS/JS sin frameworks.
- **Privacidad:** anonimización de datos personales (incluido tu nombre) antes de guardar o enviar a la IA, sesiones con token firmado y borrado de cuenta.

## Inicio rápido (localhost, plug & play)

1. Abre Docker Desktop y pon tu `.env` en la raíz (plantilla: `.env.example`).
2. **Windows:** doble clic en `iniciar.bat` · **macOS/Linux:** `./iniciar.sh`

O a mano: `python scripts/check_apis.py` y `docker compose up --build -d`.

Abre **http://localhost:3000** · API: http://localhost:8000/docs

## GitHub Pages

El workflow `.github/workflows/pages.yml` publica `frontend/` en `https://marcoflesh.github.io/InterviewAI-page/`. Sin un backend desplegado la página funciona en **Modo demo** (evaluación local). Detalles en [`PASO_A_PASO.md`](./PASO_A_PASO.md#paso-7--publicar-en-github-pages).

## Documentación

| Archivo | Contenido |
| :--- | :--- |
| [`PASO_A_PASO.md`](./PASO_A_PASO.md) | Lo que tienes que hacer tú: llaves, Google Sign-In, Docker, pruebas y Pages. |
| [`GUIA_CONFIGURACION_APIS.md`](./GUIA_CONFIGURACION_APIS.md) | Qué modelo usa cada agente y dónde se configura. |
| [`SEGURIDAD.md`](./SEGURIDAD.md) | Auditoría de seguridad y anonimato. |
| [`research/metodo_star.md`](./research/metodo_star.md) | Investigación del método STAR, banco de preguntas y cómo se calibra a los agentes. |
| [`PRUEBAS.md`](./PRUEBAS.md) | Resultados de pruebas automáticas, de navegador, de carga y de los agentes. |
| [`roadmap.md`](./roadmap.md) · [`handoff.md`](./handoff.md) · [`traceability.md`](./traceability.md) | Evolución, continuidad técnica y trazabilidad con el SRS. |

## Pruebas

```bash
cd backend && TEST_DATABASE_URL=postgresql://usuario:pass@localhost:5432/interviewai_test python -m pytest -q
python scripts/stress_test_agents.py        # agentes reales con tus llaves
python scripts/load_test_backend.py         # carga sobre el backend en Docker
```
