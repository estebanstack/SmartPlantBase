# Arranca el backend de la demo y muestra las direcciones para el ESP32 y el celular.
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz
$python = Join-Path $raiz "venv\Scripts\python.exe"

if (-not (Test-Path $python)) {
    Write-Host "No encuentro venv. Ejecuta primero instalar.bat" -ForegroundColor Red
    exit 1
}

# --- JWT_SECRET (sin imprimirla) -----------------------------------------------------------
$ok = (Test-Path ".env") -and (Select-String -Path ".env" -Pattern '^JWT_SECRET=.+' -Quiet) `
      -and -not (Select-String -Path ".env" -Pattern '^JWT_SECRET=cambie-esta' -Quiet)
if (-not $ok) {
    Write-Host "Falta JWT_SECRET en .env (o sigue la de ejemplo). Ejecuta instalar.bat para crearla." -ForegroundColor Red
    exit 1
}

$puerto = "5000"
$lineaPuerto = Select-String -Path ".env" -Pattern '^PORT=(\d+)' | Select-Object -Last 1
if ($lineaPuerto) { $puerto = $lineaPuerto.Matches[0].Groups[1].Value }

Write-Host "=============================================================="
Write-Host " Matera-Gotchi - servidor de la demo (puerto $puerto)"
Write-Host "=============================================================="
Write-Host "Direcciones de este PC (usa la de la red del hotspot en el celular y en el portal del ESP32):"
Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" } |
    ForEach-Object { Write-Host ("  {0,-24} http://{1}:{2}" -f $_.InterfaceAlias, $_.IPAddress, $puerto) }
Write-Host ""
Write-Host "AVISO: la primera vez Windows pregunta por el Firewall. Marca 'Redes privadas' y 'Permitir acceso'."
Write-Host "Si el celular o el ESP32 no conectan, abre el puerto desde un PowerShell como administrador:"
Write-Host "  netsh advfirewall firewall add rule name=`"Matera 5000`" dir=in action=allow protocol=TCP localport=5000"
Write-Host ""

& $python app.py
