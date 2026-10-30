# InterviewAI - arranque "plug and play" (Windows)
#   Doble clic en iniciar.bat   (o:  powershell -ExecutionPolicy Bypass -File iniciar.ps1 [-Reset])
param([switch]$Reset)
$ErrorActionPreference = "Stop"
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

if ($Reset) { docker compose down -v }

Write-Host "-> Construyendo y levantando contenedores (la primera vez tarda unos minutos)..."
docker compose up --build -d
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host -NoNewline "-> Esperando al backend"
for ($i = 0; $i -lt 60; $i++) {
  try {
    $h = Invoke-RestMethod -Uri "http://localhost:8000/api/health" -TimeoutSec 3
    Write-Host " OK" -ForegroundColor Green
    $c = $h.configured
    Write-Host ("  OpenAI {0} | Gemini {1} | Google Sign-In {2}" -f `
      ($(if ($c.openai_key) {"OK"} else {"X"})), ($(if ($c.gemini_key) {"OK"} else {"X"})), ($(if ($c.google_sign_in) {"OK"} else {"X"})))
    Write-Host "Listo: http://localhost:3000" -ForegroundColor Green
    Start-Process "http://localhost:3000"
    exit 0
  } catch { Write-Host -NoNewline "."; Start-Sleep -Seconds 3 }
}
Write-Host " X El backend no respondio. Ultimos logs:" -ForegroundColor Red
docker compose logs backend --tail 25
if ((docker compose logs backend 2>&1 | Out-String) -match "password authentication failed") {
  Write-Host "-> La base de datos tiene una contrasena vieja. Ejecuta: powershell -ExecutionPolicy Bypass -File iniciar.ps1 -Reset" -ForegroundColor Yellow
}
exit 1
