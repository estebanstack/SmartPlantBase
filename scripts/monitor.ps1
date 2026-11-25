# Muestra lo que el ESP32 imprime por USB (reinicia la placa al abrir).
param([string[]]$Argumentos)
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz
$python = Join-Path $raiz "venv\Scripts\python.exe"
if (-not (Test-Path $python)) { Write-Host "No encuentro venv. Ejecuta primero instalar.bat" -ForegroundColor Red; exit 1 }
& $python scripts\monitor_serie.py @Argumentos
