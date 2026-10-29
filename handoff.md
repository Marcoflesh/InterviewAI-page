# Documento de Handoff y Continuidad Técnica — InterviewAI (`v0.3.0`)

**Fecha de actualización:** 29 de octubre de 2026  
**Repositorio objetivo:** `https://github.com/Marcoflesh/InterviewAI-page.git`  
**Propósito:** Garantizar la continuidad inmediata del desarrollo en caso de agotamiento de tokens o cambio de sesión, documentando la arquitectura y todas las decisiones de la iteración `v0.3.0`.

---

## 1. Cambios Implementados en la Iteración `v0.3.0`

1. **Agentes Configurados para `gpt-4o-mini` y `gemini-3.8-flash` por `.env` (`GUIA_CONFIGURACION_APIS.md`)**:
   - Se eliminó de la interfaz web el botón/modal de configuración de API para que toda la configuración resida limpiamente en `.env`.
   - Se configuró `gpt-4o-mini` (`OPENAI_API_KEY`, `OPENAI_CHAT_MODEL`) como modelo principal del **Agente Entrevistador** y `gemini-3.8-flash` (`GEMINI_API_KEY`, `GEMINI_MODEL`) como modelo principal del **Agente Evaluador Crítico**.
   - Se agregaron comentarios explícitos en `.env.example`, `docker-compose.yml`, `backend/app/config.py`, `evaluator.py`, `interviewer.py`, `synthesizer.py`, `auth.py` y `frontend/js/app.js`, además del documento dedicado **`GUIA_CONFIGURACION_APIS.md`**.
2. **Evaluación Crítica en Escala `0 a 5` (`[0, 5]`) con Espectro Amplio y Cero Complacencia**:
   - Se modificaron las restricciones `CHECK` en PostgreSQL (`database/init.sql`), los esquemas Pydantic (`schemas.py`) y la lógica de evaluación (`evaluator.py` y `frontend/js/app.js`) para permitir calificaciones desde **`0`** hasta **`5`**.
   - Si el usuario escribe respuestas sin sentido, bromas, texto repetitivo, respuestas evasivas (`"no sé"`, `"nada"`) o no demuestra una dimensión STAR en absoluto, la calificación baja a **`0/5`**.
   - Al mismo tiempo, se amplió el diccionario de raíces verbales y sustantivas en español + extracción dinámica de palabras clave del **Contexto de la vacante** y del **CV** para que las respuestas bien elaboradas obtengan entre `4/5` y `5/5` sin sufrir bajas de puntos injustificadas por usar sinónimos.
3. **Validador de Correos Reales en Registro (`validate_real_email` / `validateRealEmailAccount`)**:
   - Verifica sintaxis estricta RFC 5322, bloquea usuarios de prueba y dominios ficticios o desechables (`ejemplo.com`, `test.com`, `tempmail.com`, `mailinator.com`, etc.) y consulta en tiempo real los registros `MX` del dominio mediante Google DNS-over-HTTPS (`https://dns.google/resolve?name=<dominio>&type=MX`).
4. **Verificador Oficial de Google Identity Services (`accounts.google.com/gsi/client`)**:
   - Se eliminó el modal personalizado de selección de cuentas y se integró el SDK oficial de Google Identity Services en `frontend/index.html` y `frontend/js/app.js` junto con el endpoint `/api/auth/google-config` y la verificación criptográfica JWT en `backend/app/auth.py`.
5. **Adaptación de Preguntas al "Contexto de la vacante" y Limpieza de Campos**:
   - Se eliminó la ventana de conteo de preguntas en la vista de configuración (las preguntas se muestran directamente en el chat).
   - Se vaciaron todos los campos de entrada (`value=""`) en Login, Registro y Configuración para que ningún campo aparezca autorrellenado.
   - Se quitó el subtítulo en la pantalla de Login y se dejó únicamente `"Escribe tu respuesta"` como placeholder del cuadro del chatbot.
   - El selector de preguntas (`question_selector.py` y `buildVacancyTailoredQuestions`) ordena y adapta las preguntas de la carrera según su afinidad semántica con el **Contexto de la vacante** y el **Puesto objetivo**.
6. **Aislamiento Total entre Usuarios (Historial y Nueva Práctica)**:
   - El historial de sesiones se almacena indexado exclusivamente por el correo electrónico de cada cuenta (`historiesByUser[email]`).
   - Cada vez que un usuario cierra sesión o inicia sesión con otra cuenta (`resetPracticeFormAndSession`), se limpian por completo los campos de **Nueva práctica**, el chat y las barras de evaluación.

---

## 2. Cómo Subir a GitHub y Desplegar

```bash
cd InterviewAI-page
cp .env.example .env
# Coloca tus llaves OPENAI_API_KEY, GEMINI_API_KEY y GOOGLE_CLIENT_ID en .env (ver GUIA_CONFIGURACION_APIS.md)
./push_to_github.sh
docker compose up --build -d
```

---

## 3. Próximos Pasos (Next Steps)

1. Colocar tus llaves `OPENAI_API_KEY`, `GEMINI_API_KEY` y `GOOGLE_CLIENT_ID` siguiendo **`GUIA_CONFIGURACION_APIS.md`**.
2. Probar el flujo completo en `http://localhost:3000` con tus modelos `gpt-4o-mini` y `gemini-3.8-flash`.
