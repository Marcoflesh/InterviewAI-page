# InterviewAI - arranque "plug and play" (Windows)
#   Doble clic en iniciar.bat   (o:  powershell -ExecutionPolicy Bypass -File iniciar.ps1 [-Reset])
param([switch]$Reset)
$ErrorActionPreference = "Continue"
Set-Location $PSScriptRoot

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
  Write-Host "X Instala Docker Desktop: https://docs.docker.com/get-docker/" -ForegroundColor Red; exit 1 }
docker info *> $null
if ($LASTEXITCODE -ne 0) { Write-Host "X Abre Docker Desktop y espera a que diga 'running'." -ForegroundColor Red; exit 1 }

if (-not (Test-Path .env)) {
  Copy-Item .env.example .env
  Write-Host "X Se creo .env desde la plantilla. Llena tus llaves (ver PASO_A_PASO.md) y vuelve a ejecutar." -ForegroundColor Yellow
  exit 1
}
# Solo tu usuario de Windows puede leer .env
try { icacls .env /inheritance:r /grant:r "$($env:USERNAME):(R,W)" *> $null } catch {}
if ((Test-Path .git) -and -not (Test-Path .git\hooks\pre-commit) -and (Get-Command bash -ErrorAction SilentlyContinue)) {
  bash scripts/install_git_hooks.sh *> $null; Write-Host "OK Proteccion anti-secretos para git instalada" }

function Levantar {
  Write-Host "-> Construyendo y levantando contenedores (la primera vez tarda unos minutos)..."
  docker compose up --build -d *> $null   # si la BD falla, se diagnostica abajo
}

# Devuelve: ok | contrasena | esquema_desactualizado | sin_tablas | sin_conexion | sin_backend  (y el JSON de salud)
function Estado-BD {
  for ($i = 0; $i -lt 40; $i++) {
    try {
      $resp = Invoke-WebRequest -Uri "http://localhost:8000/api/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
      $json = $resp.Content | ConvertFrom-Json
    } catch {
      $json = $null
      # 503 = backend vivo pero con problema en la BD: leer el cuerpo (PowerShell 5.1 y 7)
      $body = $_.ErrorDetails.Message
      if (-not $body -and $_.Exception.Response -and ($_.Exception.Response | Get-Member -Name GetResponseStream)) {
        try { $body = (New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())).ReadToEnd() } catch {}
      }
      if ($body) { try { $json = $body | ConvertFrom-Json } catch {} }
    }
    if ($json) {
      $code = "ok"; if ($json.database) { $code = $json.database.code }
      return @($code, $json)
    }
    Start-Sleep -Seconds 3
  }
  return @("sin_backend", $null)
}

if ($Reset) { docker compose down -v }
Levantar

for ($intento = 1; $intento -le 3; $intento++) {
  Write-Host -NoNewline "-> Revisando el backend y la base de datos... "
  $r = Estado-BD; $code = $r[0]; $health = $r[1]
  Write-Host $code
  switch ($code) {
    "ok" {
      docker compose up -d *> $null   # asegura que el frontend tambien este arriba
      $c = $health.configured
      $a = $health.agentes
      if ($a) { Write-Host ("  Entrevistador: {0} ({1}) | Evaluador: {2} ({3})" -f $a.entrevistador, $a.modelo_ollama, $a.evaluador, $a.modelo_gemini) }
      Write-Host ("  Gemini {0} | Google Sign-In {1} | OpenAI (opcional) {2}" -f `
        ($(if ($c.gemini_key) {"OK"} else {"X"})), ($(if ($c.google_sign_in) {"OK"} else {"X"})), ($(if ($c.openai_key) {"OK"} else {"-"})))
      $modelo = (Select-String -Path .env -Pattern '^OLLAMA_MODEL=(.+)$' | Select-Object -First 1).Matches.Groups[1].Value
      if (-not $modelo) { $modelo = "qwen3.5:4b" }
      $lista = docker compose exec -T ollama ollama list 2>$null | Out-String
      if ($lista -match [regex]::Escape($modelo)) {
        Write-Host "  Entrevistador local (Ollama $modelo): listo" -ForegroundColor Green
      } else {
        Write-Host "  Entrevistador local (Ollama $modelo): descargandose la primera vez (~3-7 GB)." -ForegroundColor Yellow
        Write-Host "  Mientras tanto se usan las preguntas del banco. Avance: docker compose logs -f ollama-init"
      }
      Write-Host "Listo: http://localhost:3000" -ForegroundColor Green
      Start-Process "http://localhost:3000"
      exit 0
    }
    "contrasena" {
      Write-Host "-> La base de datos guarda una contrasena anterior. Sincronizandola con tu .env (sin borrar datos)..." -ForegroundColor Yellow
      ((Get-Content scripts\db_sync_password.sh -Raw) -replace "`r", "") | docker compose exec -T db sh -s
      docker compose up -d *> $null
    }
    { $_ -in @("esquema_desactualizado", "sin_tablas") } {
      Write-Host "-> La base de datos local se creo con una version anterior de InterviewAI." -ForegroundColor Yellow
      $ans = Read-Host "   Reiniciarla? Se borran solo las cuentas y entrevistas de prueba locales (s/n)"
      if ($ans -match '^[sSyY]') { docker compose down -v; Levantar }
      else { Write-Host "Sin reiniciar no puede funcionar. Saliendo." -ForegroundColor Red; exit 1 }
    }
    default {
      Write-Host "X El backend no respondio. Ultimos logs:" -ForegroundColor Red
      docker compose logs backend --tail 30
      exit 1
    }
  }
}
Write-Host "X No se pudo dejar lista la base de datos. Prueba: iniciar.bat -Reset" -ForegroundColor Red
exit 1
