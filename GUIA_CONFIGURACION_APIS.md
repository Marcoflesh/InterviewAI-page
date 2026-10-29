# Guía Exacta de Configuración de API Keys y Agentes de IA (`gpt-4o-mini`, `gemini-3.8-flash` y Google OAuth)

Este documento detalla **la ruta exacta de cada archivo, el número de línea y los pasos** donde debes colocar tus llaves API para cargar tus agentes de IA (**`gpt-4o-mini`** para el Agente Entrevistador/Chat y **`gemini-3.8-flash`** para el Agente Evaluador Crítico) y el verificador oficial de **Google Sign-In**.

## Resumen Rápido: ¿Qué modelo usa cada Agente?

| Agente en LangGraph | Modelo Configurado | Variable de Entorno | Función Principal | 
| ----- | ----- | ----- | ----- | 
| **Agente Entrevistador (Chat)** | `gpt-4o-mini` | `OPENAI_API_KEY` | Contextualiza las preguntas aleatorias de la carrera según el **Contexto de la vacante** y el currículum del candidato. | 
| **Agente Evaluador Crítico (LLM-as-a-Judge)** | `gemini-3.8-flash` | `GEMINI_API_KEY` | Evalúa de forma crítica y objetiva cada respuesta en escala **0 a 5** (`Situación`, `Tarea`, `Acción`, `Resultado`, `Claridad técnica`, `Pertinencia`) y redacta los ejemplos de mejora del reporte final. | 
| **Verificador Oficial Google Sign-In** | Google Identity Services | `GOOGLE_CLIENT_ID` | Carga el botón y popup oficial de `accounts.google.com/gsi/client` y verifica criptográficamente el token JWT del usuario. | 

## Paso 1 (Principal y Recomendado): Configurar el archivo `.env` en la raíz

Cuando trabajas con Docker (`docker compose up --build`), **solo necesitas poner tus llaves en un único archivo (`.env`)** y Docker las inyecta automáticamente a todos los módulos del backend.

1. **Ruta del archivo**:

   * Plantilla base: `InterviewAI-page/.env.example`

   * Archivo activo a crear en la raíz: `InterviewAI-page/.env`

2. **Comando para crearlo**:

   ```
   cp .env.example .env
   
   ```

3. **Líneas exactas donde debes pegar tus llaves en `.env`** (Líneas **19 a 36**):

```
# [Línea 19-20] Pega aquí tu llave de OpenAI (sk-...) para cargar gpt-4o-mini:
OPENAI_API_KEY=sk-proj-TU_LLAVE_REAL_DE_OPENAI_AQUI
OPENAI_CHAT_MODEL=gpt-4o-mini

# [Línea 23-24] Pega aquí tu llave de Google AI Studio (AIza...) para cargar gemini-3.8-flash:
GEMINI_API_KEY=AIzaSyTU_LLAVE_REAL_DE_GEMINI_AQUI
GEMINI_MODEL=gemini-3.8-flash

# [Línea 27 y 30] Proveedores activos para cada agente:
EVALUATOR_PROVIDER=gemini
INTERVIEWER_PROVIDER=openai

# [Línea 36] Pega aquí tu Client ID de Google Cloud Console para el login oficial de Google:
GOOGLE_CLIENT_ID=1234567890-abcdefg.apps.googleusercontent.com

```

## Paso 2: Archivos del Backend donde se leen y ejecutan tus API Keys

Todos los archivos de código ya tienen comentarios marcados con `# >>> ... <<<` indicando dónde se leen y utilizan tus llaves:

### 1. Configuración Central del Backend

* **Ruta del archivo**: `InterviewAI-page/backend/app/config.py`

* **Líneas exactas**: **Líneas 18 a 33**

* **Qué hace**: Lee `OPENAI_API_KEY`, `OPENAI_CHAT_MODEL` (`gpt-4o-mini`), `GEMINI_API_KEY`, `GEMINI_MODEL` (`gemini-3.8-flash`) y `GOOGLE_CLIENT_ID` desde `.env`. Si no usas `.env`, puedes pegar tus llaves en el segundo parámetro de `os.getenv(...)` en esas líneas:

  ```
  # Línea 18 de backend/app/config.py:
  OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")  # <-- PON AQUÍ TU API KEY DE OPENAI EN .env
  OPENAI_CHAT_MODEL: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4o-mini")
  
  # Línea 21 de backend/app/config.py:
  GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")  # <-- PON AQUÍ TU API KEY DE GEMINI EN .env
  GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
  
  ```

### 2. Agente Evaluador Crítico (`gemini-3.8-flash` y `gpt-4o-mini`)

* **Ruta del archivo**: `InterviewAI-page/backend/app/agents/evaluator.py`

* **Líneas exactas**:

  * **Líneas 332 a 361**: Bloque `# >>> OPCIÓN 1: AGENTE EVALUADOR CON GEMINI 3.8 FLASH (GEMINI_API_KEY EN .env) <<<` que llama a `https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent`.

  * **Líneas 363 a 390**: Bloque `# >>> OPCIÓN 2: AGENTE EVALUADOR CON GPT-4o MINI (OPENAI_API_KEY EN .env) <<<` que llama a `https://api.openai.com/v1/chat/completions`.

### 3. Agente Entrevistador y Contextualizador de la Vacante (`gpt-4o-mini` y `gemini-3.8-flash`)

* **Ruta del archivo**: `InterviewAI-page/backend/app/agents/interviewer.py`

* **Líneas exactas**:

  * **Líneas 29 a 52**: Bloque `# >>> AGENTE ENTREVISTADOR CON GPT-4o MINI (OPENAI_API_KEY EN .env) <<<` que adapta cada pregunta aleatoria de la carrera al **Contexto de la vacante** y al **Puesto objetivo**.

  * **Líneas 54 a 78**: Bloque `# >>> AGENTE ENTREVISTADOR CON GEMINI 3.8 FLASH (GEMINI_API_KEY EN .env) <<<`.

### 4. Sintetizador del Reporte Final y Ejemplos STAR (`gemini-3.8-flash` y `gpt-4o-mini`)

* **Ruta del archivo**: `InterviewAI-page/backend/app/agents/synthesizer.py`

* **Líneas exactas**:

  * **Líneas 25 a 49**: Bloque `# >>> SÍNTESIS DE REPORTE CON GEMINI 3.8 FLASH (GEMINI_API_KEY EN .env) <<<`.

  * **Líneas 51 a 74**: Bloque `# >>> SÍNTESIS DE REPORTE CON GPT-4o MINI (OPENAI_API_KEY EN .env) <<<`.

### 5. Verificador Oficial de Google Sign-In (`GOOGLE_CLIENT_ID`)

* **Ruta en Backend**: `InterviewAI-page/backend/app/auth.py` (**Líneas 99 a 132**) — Verifica criptográficamente el token JWT emitido por Google usando `google.oauth2.id_token.verify_oauth2_token`.

* **Ruta en Frontend**: `InterviewAI-page/frontend/js/app.js` (**Líneas 16 a 29**) — Objeto `AGENT_CONFIG`:

  ```
  // Líneas 16 a 29 de frontend/js/app.js:
  const AGENT_CONFIG = {
    GOOGLE_CLIENT_ID: "", // <-- PON AQUÍ TU GOOGLE_CLIENT_ID.apps.googleusercontent.com (o en .env)
    OPENAI_API_KEY: "",   // <-- PON AQUÍ TU OPENAI_API_KEY EN .env (o aquí si abres el HTML sin backend)
    OPENAI_CHAT_MODEL: "gpt-4o-mini",
    GEMINI_API_KEY: "",   // <-- PON AQUÍ TU GEMINI_API_KEY EN .env (o aquí si abres el HTML sin backend)
    GEMINI_MODEL: "gemini-3.8-flash"
  };
  
  ```

## Paso 3: Cómo obtener el `GOOGLE_CLIENT_ID` oficial en 2 minutos

1. Entra a [Google Cloud Console — Credentials](https://www.google.com/search?q=https://console.cloud.google.com/apis/credentials).

2. Haz clic en **Create Credentials** -> **OAuth client ID**.

3. En **Application type**, elige **Web application**.

4. En **Authorized JavaScript origins**, agrega:

   * `http://localhost:3000`

   * `http://localhost:8000`

5. Copia el **Client ID** generado (`xxxx.apps.googleusercontent.com`) y pégalo en la variable `GOOGLE_CLIENT_ID` de tu archivo `.env` (y/o en la línea 19 de `frontend/js/app.js`).

6. Reinicia los contenedores:

   ```
   docker compose up --build -d
   
   ```