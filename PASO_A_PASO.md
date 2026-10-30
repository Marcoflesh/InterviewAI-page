# Paso a Paso — InterviewAI (`v0.7.0`)

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
python scripts/probar_ia.py                                            # Ollama y Gemini responden
python scripts/evaluar_evaluador.py --modo llm --conjunto web          # 26 respuestas fuertes/débiles de 7 sitios
python scripts/evaluar_evaluador.py --modo llm --conjunto bd --guardar-en-bd   # todo golden_dataset; guarda model_score
```

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

1. En GitHub → repositorio → *Settings → Pages → Build and deployment → Source:* **GitHub Actions**. (El workflow ya existe; solo falta este clic. Después avísame o haz cualquier push y se publica.)
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
