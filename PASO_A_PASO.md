# Paso a Paso — InterviewAI (`v0.11.0`)

## Ver tus entrevistas pasadas (v0.8.0)

Arriba a la derecha, **Historial** → botón **Ver** en la entrevista que quieras. Ves el reporte, la **Conversación completa** y puedes **Descargar PDF** otra vez. Solo aparecen las entrevistas que terminaste (con reporte), una vez cada una.

## Actualizar a la versión con Ollama + Gemini (v0.7.1)

Quién hace qué: **Entrevistador = Ollama** (`qwen3.5:4b`, local y gratis) · **Evaluador y Sintetizador = Gemini** (`gemini-3.8-flash`) · OpenAI apagado.

1. **Abre Docker Desktop** y espera a que diga *Engine running*. Deja libres ~6 GB de disco para el modelo.
2. **Baja el código nuevo.** En la carpeta `InterviewAI-page/`:
   ```bash
   git pull
   ```
   (Si la descargaste como ZIP, vuelve a descargarla de GitHub y copia ahí tu `.env`.)
3. **Pon el `.env` nuevo** en `InterviewAI-page/`, reemplazando el anterior. Si el navegador lo guardó como `env` o `env.txt`, renómbralo exactamente a `.env`. Para revisarlo, en la sección 2 deben aparecer estas líneas:
   ```ini
   INTERVIEWER_PROVIDER=ollama
   EVALUATOR_PROVIDER=gemini
   GEMINI_API_KEY=AQ.…        # tu llave, sin espacios
   OPENAI_API_KEY=            # vacío
   ```
   y en la sección 5: `OLLAMA_ENABLED=true` y `OLLAMA_MODEL=qwen3.5:4b`.
4. **Arranca y reconstruye** (hace falta porque el backend cambió):
   - Windows: doble clic en `iniciar.bat`
   - macOS/Linux: `./iniciar.sh`
   - A mano: `docker compose up --build -d`

   **No presiones Ctrl+C mientras construye** (ahora ves el avance). Debe imprimir: `Entrevistador: ollama (qwen3.5:4b) | Evaluador: gemini (gemini-3.8-flash)`. Si sale `None`, el mismo script reconstruye el backend.
5. **Espera la descarga del modelo** (solo la primera vez, 5–20 min según tu internet). El script la muestra con una barra de progreso y termina con `✓ Entrevistador local (Ollama qwen3.5:4b): listo`. Mientras tanto ya puedes usar la página (usa preguntas del banco). Para revisarlo después: `docker compose exec ollama ollama list` debe mostrar `qwen3.5:4b`.
6. **Comprueba que ambas IAs responden** (no necesitas instalar Python, corre dentro de Docker):
   ```bash
   docker compose exec backend python scripts/probar_ia.py
   ```
   Debe salir ✓ en Ollama y en Gemini. También puedes abrir http://localhost:8000/api/health y buscar `"agentes"`.
7. **Abre http://localhost:3000** y haz una entrevista de prueba.
8. **Mide al evaluador con las respuestas de internet** y guarda la calificación en la base de datos:
   ```bash
   docker compose exec backend python scripts/evaluar_evaluador.py --modo llm --conjunto web
   docker compose exec backend python scripts/evaluar_evaluador.py --modo llm --conjunto bd --guardar-en-bd
   ```
   Copia lo que imprima y compártelo.

| Si ves esto | Haz esto |
|---|---|
| `Entrevistador: openai` o `gemini` | Tu `.env` sigue siendo el viejo o el backend no se reconstruyó: repite los pasos 3 y 4. |
| Ollama ✗ "modelo no descargado" | Espera el paso 5, o fuerza la descarga: `docker compose exec ollama ollama pull qwen3.5:4b` |
| Gemini ✗ 401/403 | La llave está mal copiada o restringida a otra API: revísala en https://aistudio.google.com/apikey |
| Las preguntas tardan mucho | Sin tarjeta de video el modelo corre en CPU. Cierra programas pesados o usa GPU NVIDIA: `docker compose -f docker-compose.yml -f docker-compose.gpu.yml up -d` |
| "contraseña anterior" de la base de datos | Vuelve a correr `iniciar`: la corrige sola sin borrar datos. |

## Plug & Play (lo único que necesitas para verlo funcionando)

1. Instala y abre **Docker Desktop**.
2. `git clone https://github.com/Marcoflesh/InterviewAI-page.git` y copia tu `.env` (el que te entregué) a la carpeta `InterviewAI-page/`.
3. **Windows:** doble clic en `iniciar.bat`. **macOS/Linux:** `./iniciar.sh`.

El script levanta todo, instala la protección anti-secretos de git, te dice qué llaves están activas y abre http://localhost:3000. Si la base de datos tenía una contraseña vieja, te pedirá correrlo con `-Reset` / `--reset`.

## Estado de la configuración (29/10/2026)

| Pieza | Estado |
|---|---|
| Entrevistador local (Ollama `qwen3.5:4b`) | ✅ Se descarga solo la primera vez que corres `iniciar` (~3.4 GB) |
| Llave de OpenAI | ➖ Ya no se usa (vacía en tu `.env`; revócala si no la ocupas) |
| Llave de Gemini (`AQ.…`, formato nuevo) | ✅ En tu `.env` |
| Google Sign-In Client ID | ✅ En tu `.env` y en `frontend/js/config.js` (es público) |
| Contraseña de PostgreSQL y `SECRET_KEY` | ✅ Generadas al azar en tu `.env` |
| Repositorio, CI y escáner de secretos | ✅ En verde en GitHub |
| **Orígenes de Google** (Paso 3) | ⏳ Tú, en Google Cloud Console |
| **Activar GitHub Pages** (Paso 7) | ⏳ Tú, un clic (GitHub no deja que una herramienta externa lo active) |
| **Revocar el token `ghp_…`** (Paso 0) | ⏳ Tú, en GitHub |

---

## Probar con respuestas reales de internet (v0.7.0)

Con Docker encendido (`iniciar` ya llenó la base de datos):

```bash
docker compose exec backend python scripts/probar_ia.py                 # Ollama y Gemini responden
docker compose exec backend python scripts/evaluar_evaluador.py --modo llm --conjunto web   # 26 respuestas fuertes/débiles de 7 sitios
docker compose exec backend python scripts/evaluar_evaluador.py --modo llm --conjunto bd --guardar-en-bd   # todo golden_dataset; guarda model_score
```

Para revisar preguntas que piden solo una parte (cómo, plan, rol): `--conjunto enfoque`.

La meta propuesta es AUC ≥ 0.90 y exactitud ≥ 85 %. El script lista las respuestas mal clasificadas para revisarlas a mano. El analizador local (sin IA) saca AUC 0.93 y 81 %.

## Entrenar y medir a los agentes (v0.6.0)

Lee primero `research/metodo_star.md`. Luego:

0. **Confirma que la IA responde** (3 llamadas pequeñas): `python scripts/probar_ia.py`. Si Ollama dice que el modelo no está descargado, espera a `docker compose logs -f ollama-init`.

1. **Mide al agente real con tus llaves** (≈ 24 llamadas, centavos):
   ```bash
   python scripts/evaluar_evaluador.py --modo llm --rubrica indicadores
   python scripts/evaluar_evaluador.py --modo llm --rubrica holistico   # para comparar con el método anterior
   ```
2. **Consigue calificaciones humanas:** sigue `datos/golden/LEEME.md` (2 o 3 personas calificando con la misma rúbrica).
3. **Vuelve a medir** con `--golden tu_archivo.csv`. La meta (RN-07) es kappa ≥ 0.75.
4. Revisa las respuestas con más diferencia (el script las lista) y ajusta la rúbrica o los ejemplos de `backend/app/data/`. Repite.

## Si algo falla

| Lo que ves | Qué hacer |
|---|---|
| "La base de datos de Docker guarda una contraseña anterior…" | Vuelve a abrir `iniciar.bat` / `./iniciar.sh`: la sincroniza sola sin borrar datos. |
| "La base de datos se creó con una versión anterior…" | Abre `iniciar` y responde `s` cuando pregunte si reiniciarla. |
| Cualquier otro error | `docker compose logs backend --tail 50` y mándame lo que salga. |

## Paso 0 — Proteger tus cuentas

1. **Revoca el token de GitHub `ghp_…`** que estaba en `GEMINI_API_KEY` del `.env` viejo: GitHub → *Settings → Developer settings → Personal access tokens* → bórralo.
2. **Borra la llave `sk-proj-…` vieja** en https://platform.openai.com/api-keys (ya la reemplazamos por la nueva `sk-svcacct-…`).
3. **No compartas el `.env`.** El `.zip` en los archivos del proyecto de Claude todavía trae el `.env` viejo: reemplázalo por uno hecho con `git archive -o proyecto.zip HEAD`.
4. En Google Cloud **restringe** la llave de Gemini a *Generative Language API* y en OpenAI ponle **límite de gasto mensual** al proyecto.

## Paso 1 y 2 — Llaves y `.env` ✅ (ya hechos)

Si algún día necesitas rehacer el `.env` a mano:

```bash
cp .env.example .env
python -c "import secrets;print(secrets.token_urlsafe(48))"   # SECRET_KEY
python -c "import secrets;print(secrets.token_urlsafe(24))"   # POSTGRES_PASSWORD
```

Formatos: OpenAI `sk-…` (no `key_…`, que es solo el ID), Gemini `AQ.…` o `AIza…`, Client ID `….apps.googleusercontent.com`.

## Paso 3 — Arreglar "Iniciar sesión con Google"

Estas eran las causas del error. Revisa todas. **No se puede hacer desde Cloud Shell ni `gcloud`**: Google solo deja editar los orígenes de un cliente OAuth web desde la consola.

1. **Orígenes autorizados** (corrige `Error 400: origin_mismatch`). https://console.cloud.google.com/auth/clients → elige el proyecto → clic en el cliente que termina en `…avobo5kt8llvuo7tsopufgn27ejfunb9.apps.googleusercontent.com` → *Orígenes autorizados de JavaScript* → **Agregar URI**. Agrega **los tres**, sin `/` al final y sin `/InterviewAI-page`:
   - `http://localhost`
   - `http://localhost:3000`
   - `https://marcoflesh.github.io`

   Google exige `http://localhost` **además** del que lleva puerto. Los cambios tardan de 5 minutos a unas horas.
2. **Abre la página siempre en `http://localhost:3000`.** No funciona con doble clic sobre `index.html` (`file://`), ni con Live Server de VS Code (`:5500`), ni con `127.0.0.1` (salvo que también lo agregues).
3. **Pantalla de consentimiento.** https://console.cloud.google.com/auth/audience → si dice *Prueba*, solo entran los correos de *Usuarios de prueba*. Para que entre cualquiera, **Publicar app** (con permisos básicos de nombre y correo no requiere verificación de Google). Las cuentas `@tec.mx` dependen además de lo que permita el administrador del Tec; si las bloquea, usa una cuenta Gmail.
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

## Si Chrome dice "Dangerous site" / "Sitio peligroso" (v0.11.0)

Google Safe Browsing marcó la página como posible phishing: era un sitio `github.io` nuevo que pedía correo, contraseña y tenía un botón de Google dibujado a mano. Desde `v0.11.0` la versión pública **no pide contraseñas** (se entra solo con el nombre) y solo usa el botón oficial de Google cuando hay servidor. Falta que Google lo revise:

1. **Reporte rápido (sin cuenta extra):** https://safebrowsing.google.com/safebrowsing/report_error/?hl=es → URL `https://marcoflesh.github.io/InterviewAI-page/` → explica: *"Proyecto escolar de código abierto (github.com/Marcoflesh/InterviewAI-page). Simulador de entrevistas; no pide contraseñas ni datos de pago. Se quitó el formulario de acceso de la versión pública."*
2. **Revisión oficial (recomendada):** https://search.google.com/search-console → *Agregar propiedad* → **Prefijo de URL** `https://marcoflesh.github.io/InterviewAI-page/` → método **Etiqueta HTML** → copia solo el código de `content="…"` → en GitHub: *Settings → Secrets and variables → Actions → Variables → New variable* `GOOGLE_SITE_VERIFICATION` = ese código → *Actions → Deploy frontend to GitHub Pages → Run workflow* → en Search Console **Verificar** → *Seguridad y acciones manuales → Problemas de seguridad* → **Solicitar una revisión**.
3. Google tarda alrededor de un día en revisar phishing y hasta 72 h en quitar la alerta.

## Paso 7 — Publicar en GitHub Pages

**Una sola vez (solo tú puedes, GitHub no deja hacerlo desde fuera):**

1. https://github.com/Marcoflesh/InterviewAI-page/settings/pages → *Build and deployment → Source:* **GitHub Actions**.
2. https://github.com/Marcoflesh/InterviewAI-page/actions/workflows/pages.yml → **Run workflow** → *main* → **Run workflow**. En 1–2 minutos queda en verde.
3. Abre **https://marcoflesh.github.io/InterviewAI-page/**.
4. Para Google Sign-In con `?local=1`: en Google Cloud Console (Paso 3) agrega el origen `https://marcoflesh.github.io`. Si no, Google responde **Error 400: origin_mismatch**. En la versión pública sin servidor no aparece el botón de Google (se entra como invitado).

Desde ahí, cada push que cambie `frontend/` vuelve a publicar solo.

**Cómo funciona la página publicada:**

| Quién la abre | Qué pasa |
|---|---|
| Cualquier persona | **Modo demo**: entrevista completa con el banco de preguntas, calificación en el navegador (misma regla de enfoque), reporte, historial y PDF. Los datos se quedan en su navegador. |
| Tú, con Docker encendido (`./iniciar.sh`) | Abre **https://marcoflesh.github.io/InterviewAI-page/?local=1** (o el enlace "usar mi computadora" junto a "Modo demo"). La página usa tu backend: Ollama, Gemini y la base de datos. Chrome/Edge preguntan una vez si permites acceso a la red local: acepta. Se recuerda; `?local=0` lo quita. |

Nota: `?local=1` solo puede conectarse a `http://localhost:8000` de la misma computadora, así que un enlace no puede mandar datos a otro servidor. Funciona en Chrome, Edge y Firefox; Safari bloquea esa conexión.

**Versión pública con IA para todos (después):** desplegar `Dockerfile.backend` en Render o Cloud Run con PostgreSQL administrado, llaves como variables de ese servicio, `ALLOWED_ORIGINS=https://marcoflesh.github.io` y la variable de GitHub `API_BASE_URL` con su URL. Ollama necesita una máquina con mucha memoria; en la nube conviene que el entrevistador sea Gemini (`INTERVIEWER_PROVIDER=gemini`).

## Paso 8 — Antes del 14 de enero de 2027

OpenAI anunció el retiro de `gpt-4o-mini` en su API para esa fecha y recomienda `gpt-6-luna` como reemplazo ([deprecaciones de OpenAI](https://developers.openai.com/api/docs/deprecations)). Solo cambia `OPENAI_CHAT_MODEL` en `.env` y corre de nuevo el Paso 6.

## Paso 9 — Trabajar con el repositorio

```bash
git clone https://github.com/Marcoflesh/InterviewAI-page.git
cd InterviewAI-page
cp /ruta/a/tu/.env .      # tu .env NUNCA se sube (está en .gitignore)
```

Antes de cada push, `git status` no debe mostrar `.env`. El CI corre las pruebas y un escáner de secretos en cada push.
