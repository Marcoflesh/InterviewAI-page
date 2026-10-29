# Documento de Handoff y Continuidad Técnica — InterviewAI (`v0.2.0`)

**Fecha de actualización:** 29 de octubre de 2026  
**Repositorio objetivo:** `https://github.com/Marcoflesh/InterviewAI-page.git`  
**Propósito:** Garantizar la continuidad inmediata del desarrollo en caso de agotamiento de tokens o cambio de sesión, documentando todos los ajustes de la iteración `v0.2.0`, las decisiones tomadas y los siguientes pasos.

---

## 1. Cambios Implementados en la Iteración `v0.2.0`

En respuesta a la revisión funcional del usuario se corrigieron y evolucionaron 5 áreas críticas tanto en el backend (`backend/app/`) como en el frontend (`frontend/`) y en la aplicación interactiva (`interviewai.html`):

1. **Botón "Descargar PDF" 100% Funcional (`frontend/js/app.js`, `frontend/index.html`)**:
   - **Problema previo**: `window.print()` es bloqueado por los iframes con sandbox (como Canvas) y no descargaba un archivo directo.
   - **Solución implementada**: Se integró `jsPDF` (`2.5.1`) junto con un generador binario nativo PDF 1.4 de respaldo (`buildMinimalPdfBinary`). Al hacer clic en **Descargar PDF**, se construye y descarga directamente el archivo `Reporte_InterviewAI_<Nombre>.pdf` con el puntaje global, evolución, desglose de las 2 respuestas más débiles, ejemplos STAR recomendados y el Plan de Acción.
2. **Sistema de Evaluación STAR Sensible, Diferenciado y Conectado a Llaves API (`backend/app/agents/evaluator.py`, `frontend/js/app.js`)**:
   - **Problema previo**: El evaluador heurístico de respaldo otorgaba calificaciones muy similares (`3/5` o `4/5`) basándose casi únicamente en el conteo de palabras.
   - **Solución implementada**:
     - Se programó un motor de análisis semántico y léxico (`_deep_star_analyzer` / `evaluateResponseLocal`) con diccionarios técnicos específicos por carrera (`ITC`, `ISD`, `IIS`, `IMT`, `LAF`, `LMC`, `IBT`, `ARQ` — más de 30 términos por carrera), cruce de palabras clave contra la pregunta específica y el **Contexto de la vacante**, detección de verbos de acción en primera persona y extracción Regex de métricas cuantitativas.
     - Si el usuario escribe una respuesta corta (`< 8` palabras), evasiva (`"no sé"`, `"hola"`) o ajena a la pregunta, recibe `1/5` y retroalimentación específica sobre qué le faltó.
     - El panel lateral ahora muestra en vivo las **Métricas detectadas** y los **Conceptos clave** identificados en ese turno, además de ejemplos de mejora redactados específicamente para la pregunta evaluada.
     - Se añadió el botón y modal **"Configurar API / IA"** en la barra superior (y soporte en `POST /api/sessions/turn`) para usar llaves API de **Google Gemini**, **OpenAI**, **Groq** o **Ollama**.
3. **Autenticación Completa en 3 Modalidades (`Iniciar sesión`, `Registrar` e `Iniciar sesión con Google`)**:
   - **Iniciar sesión (`POST /api/auth/login`)**: Para cuentas ya existentes; valida formato de correo, verifica que el correo exista en la base de datos de usuarios registrados y comprueba la contraseña (hash PBKDF2-SHA256 en backend). Incluye cuenta demo verificada (`a01709802@tec.mx` / `Interview2026!`) para pruebas inmediatas.
   - **Registrar (`POST /api/auth/register`)**: Para cuentas nuevas; valida nombre completo, formato real de correo electrónico, universidad y contraseña de al menos 6 caracteres, impidiendo correos duplicados.
   - **Continuar con Google (`POST /api/auth/google`)**: Abre el selector y verificador de cuentas de Google que valida el correo (`@gmail.com` / cuenta institucional) y carga los datos reales del usuario (nombre completo, correo e iniciales/avatar) en la sesión activa.
4. **Cambio de Etiqueta a "Contexto de la vacante"**:
   - En la vista de configuración (`view-setup`) y en los esquemas del backend (`schemas.py`, `evaluator.py`), se reemplazó `"Descripción de la vacante"` por **"Contexto de la vacante"**.
5. **Cantidad Aleatoria Realista de 15 a 20 Preguntas por Sesión**:
   - Se eliminó el selector fijo de 5–10 preguntas. Ahora cada entrevista genera automáticamente un valor aleatorio entre **15 y 20 preguntas** (`random.randint(15, 20)` en Python y `Math.floor(Math.random() * 6) + 15` en JS).
   - Se amplió el banco de preguntas en `database/init.sql` y `frontend/js/app.js` de 120 a **176 preguntas únicas (22 por cada una de las 8 carreras)** para garantizar que ninguna sesión de 15 a 20 preguntas repita temas.
   - Se añadió el botón **"Finalizar y ver reporte"** en el encabezado del chat para permitir evaluar y descargar el reporte en cualquier momento después de responder al menos 1 pregunta.

---

## 2. Cómo Subir los Cambios a GitHub y Ejecutar con Docker

### 2.1 Subir a `https://github.com/Marcoflesh/InterviewAI-page.git`
```bash
cd InterviewAI-page
./push_to_github.sh
```

### 2.2 Levantar el Stack Docker
```bash
cp .env.example .env
docker compose up --build -d
docker exec -it interviewai-ollama ollama pull llama3.2:3b
```

---

## 3. Próximos Pasos (Next Steps)

1. **Configuración de Llaves API de los Agentes**: Probar las llaves API disponibles del usuario (Gemini, OpenAI, Groq u Ollama) desde el botón **"Configurar API / IA"** en la barra superior o inyectándolas en `.env`.
2. **Carga de Archivo PDF en CV**: Añadir extracción automática de texto desde archivos `.pdf` en el formulario de configuración.
3. **Vistas de Product Owner y MLOps**: Conectar las tablas `golden_dataset` y `study_resources` a una ruta `/admin` separada.
