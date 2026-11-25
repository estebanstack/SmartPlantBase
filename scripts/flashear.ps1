# Compila y sube el firmware al ESP32 (puerto detectado automáticamente).
# Uso:  flashear.bat diagnostico    o    flashear.bat esp32dev
param([string]$Entorno)
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz
if ($Entorno -ne "diagnostico" -and $Entorno -ne "esp32dev") {
    Write-Host "Uso: flashear.bat diagnostico   o   flashear.bat esp32dev" -ForegroundColor Yellow
    exit 1
}
$pio = Join-Path $raiz "venv\Scripts\pio.exe"
if (-not (Test-Path $pio)) { Write-Host "No encuentro PlatformIO. Ejecuta primero instalar.bat" -ForegroundColor Red; exit 1 }
Write-Host "La primera vez PlatformIO descarga varios cientos de MB; puede tardar varios minutos."
Write-Host "Si se queda en 'Connecting......', mantén pulsado el botón BOOT del ESP32."
& $pio run -d firmware -e $Entorno -t upload
