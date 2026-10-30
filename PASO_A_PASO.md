# Paso a Paso: lo que tienes que hacer tú — InterviewAI (`v0.4.0`)

Todo lo que se podía resolver en código ya está en el repositorio. Esta lista es lo que **solo tú** puedes hacer porque requiere tus cuentas. Hazlo en orden.

---

## Paso 0 — URGENTE: proteger tus cuentas (10 min)

El `.zip` del proyecto incluía tu archivo `.env` con llaves reales.

1. **Revoca el token de GitHub.** En `GEMINI_API_KEY` tenías un token que empieza con `ghp_`: eso es un *Personal Access Token* de GitHub, no una llave de Gemini, y da acceso a tu cuenta. Entra a GitHub → *Settings → Developer settings → Personal access tokens*, bórralo y crea otro solo si lo necesitas.
2. **Rota tu llave de OpenAI.** En https://platform.openai.com/api-keys elimina la llave actual y crea una nueva (la anterior viajó dentro del `.zip`).
3. **No vuelvas a compartir el `.env`.** Si subes el proyecto como `.zip` a un chat o a un proyecto, bórralo antes o comprime solo lo que está en Git (`git archive -o proyecto.zip HEAD`). El `.zip` que está en los archivos del proyecto de Claude todavía contiene el `.env`: reemplázalo.

## Paso 1 — Crear la llave correcta de Gemini

1. ✅ **Hecho (29/10/2026):** ya tienes una llave nueva con formato `AQ.` y quedó en tu `.env`. Google cambió el formato de `AIza…` a `AQ.…`; el backend acepta ambos.
2. **OpenAI:** lo que mandaste (`key_…`) es el **ID** de la llave, no la llave secreta. En https://platform.openai.com/api-keys crea una nueva y copia el valor que empieza con `sk-` (solo se muestra una vez). Mientras tanto, tu `.env` conserva la `sk-proj-…` anterior para que la app funcione; cámbiala en cuanto tengas la nueva.
3. Recomendado para privacidad: activa facturación en ese proyecto. En la capa gratuita Google puede usar las entradas para mejorar sus productos (ver `SEGURIDAD.md`).

## Paso 2 — Llenar `.env`

✅ **Hecho:** te entregué un `.env` listo con contraseña de PostgreSQL y `SECRET_KEY` generadas al azar, tu llave de Gemini y tu Client ID. Cópialo a la raíz del proyecto (reemplaza el tuyo), corre `chmod 600 .env` y `bash scripts/install_git_hooks.sh`. Si lo quieres hacer a mano:

```bash
cp .env.example .env
python -c "import secrets;print(secrets.token_urlsafe(48))"   # cópialo en SECRET_KEY
python -c "import secrets;print(secrets.token_urlsafe(24))"   # cópialo en POSTGRES_PASSWORD
```

Llena en `.env`: `OPENAI_API_KEY` (nueva, `sk-…`), `GEMINI_API_KEY` (`AIza…`), `GOOGLE_CLIENT_ID`, `SECRET_KEY` y `POSTGRES_PASSWORD`.

> Si ya habías levantado Docker antes, PostgreSQL conserva la contraseña vieja en su volumen. Para empezar limpio: `docker compose down -v` (borra los datos locales de prueba).

## Paso 3 — Arreglar "Iniciar sesión con Google"

Estas eran las causas del error. Revisa todas:

1. **Orígenes autorizados.** Google Cloud Console → *APIs y servicios → Credenciales* → tu cliente OAuth tipo **Aplicación web** → *Orígenes autorizados de JavaScript*. Agrega **los tres**:
   - `http://localhost`
   - `http://localhost:3000`
   - `https://marcoflesh.github.io`

   Google exige `http://localhost` **además** del que lleva puerto. Los cambios tardan de 5 minutos a unas horas.
2. **Abre la página siempre en `http://localhost:3000`.** No funciona con doble clic sobre `index.html` (`file://`), ni con Live Server de VS Code (`:5500`), ni con `127.0.0.1` (salvo que también lo agregues).
3. **Pantalla de consentimiento.** Si la app está en modo *Prueba*, agrega tu correo en *Usuarios de prueba* o publícala.
4. **Mismo Client ID en todos lados.** El `GOOGLE_CLIENT_ID` de `.env` es el que usa el backend para validar y el que recibe el frontend. Si cambias de cliente, reinicia Docker.
5. **Reloj sincronizado.** Si el error dice "hora desfasada", sincroniza la hora de Windows/Mac y reinicia Docker Desktop.

El mensaje de error exacto ahora aparece debajo del botón, ya no se pierde en silencio.

## Paso 4 — Verificar las llaves (sin gastar saldo)

```bash
python scripts/check_apis.py
```

Debe terminar en **TODO LISTO ✓**. Consulta los modelos sin generar tokens y nunca imprime tus llaves.

## Paso 5 — Levantar en localhost con Docker

```bash
docker compose up --build -d
docker compose ps          # db, backend y frontend en "healthy"/"running"
```

- App: http://localhost:3000
- Estado del backend: http://localhost:8000/api/health (dice qué llaves están configuradas, sin mostrarlas)
- Documentación de la API: http://localhost:8000/docs
- Logs de los agentes: `docker compose logs -f backend` (verás `llm provider=gemini model=gemini-3.8-flash status=200 latency_ms=…`)

Ollama ya no se levanta por defecto (pesa ~2 GB y no se usaba). Si lo quieres como respaldo sin internet:
`docker compose --profile local-llm up -d`, luego `docker compose exec ollama ollama pull llama3.2:3b` y `OLLAMA_ENABLED=true` en `.env`.

## Paso 6 — Prueba de estrés REAL de los agentes

```bash
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
python scripts/stress_test_agents.py                    # ~126 llamadas, centavos de dólar
python scripts/load_test_backend.py --users 20 --turns 5   # con Docker encendido
```

Copia la salida en `PRUEBAS.md` (sección 5) y compárala con los criterios de viabilidad que están ahí.

## Paso 7 — Publicar en GitHub Pages

1. En GitHub → repositorio → *Settings → Pages → Source:* **GitHub Actions**.
2. *Settings → Secrets and variables → Actions → Variables*: crea `GOOGLE_CLIENT_ID` (es público). **Nunca** pongas ahí las llaves de OpenAI o Gemini.
3. Haz un push a `main` (o corre el workflow manualmente). La página queda en `https://marcoflesh.github.io/InterviewAI-page/`.

**Importante:** GitHub Pages solo sirve archivos estáticos; no puede ejecutar el backend ni guardar llaves. Sin backend, la página funciona en **Modo demo** (evaluación local, datos solo en el navegador). Para tener los agentes de IA en la versión pública:

1. Despliega el backend (`Dockerfile.backend`) en un servicio con contenedores, por ejemplo Render o Google Cloud Run, con un PostgreSQL administrado (por ejemplo Neon o Supabase) cargado con `database/init.sql`.
2. Pon tus llaves como variables de entorno **de ese servicio** y `ALLOWED_ORIGINS=https://marcoflesh.github.io`.
3. En GitHub crea la variable `API_BASE_URL` con la URL `https://…` de tu backend y vuelve a desplegar Pages.

## Paso 8 — Antes del 14 de enero de 2027

OpenAI anunció el retiro de `gpt-4o-mini` en su API para esa fecha y recomienda `gpt-6-luna` como reemplazo ([deprecaciones de OpenAI](https://developers.openai.com/api/docs/deprecations)). Solo cambia `OPENAI_CHAT_MODEL` en `.env` y corre de nuevo el Paso 6.

## Paso 9 — Trabajar con el repositorio

```bash
git clone https://github.com/Marcoflesh/InterviewAI-page.git
cd InterviewAI-page
cp /ruta/a/tu/.env .      # tu .env NUNCA se sube (está en .gitignore)
```

Antes de cada push, `git status` no debe mostrar `.env`. El CI corre las pruebas y un escáner de secretos en cada push.
