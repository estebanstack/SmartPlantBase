# Instala todo lo necesario en Windows: entorno virtual, dependencias, PlatformIO y .env.
# Se ejecuta con doble clic en instalar.bat
$ErrorActionPreference = "Stop"
$raiz = Split-Path -Parent $PSScriptRoot
Set-Location $raiz

# --- 1. Python ---------------------------------------------------------------------------
$py = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $py = "py" }
elseif (Get-Command python -ErrorAction SilentlyContinue) { $py = "python" }
if (-not $py) {
    Write-Host "No encuentro Python." -ForegroundColor Red
    Write-Host "1. Descárgalo de https://www.python.org/downloads/"
    Write-Host "2. En el instalador marca la casilla 'Add python.exe to PATH' (abajo, antes de instalar)."
    Write-Host "3. Cierra esta ventana y vuelve a ejecutar instalar.bat."
    exit 1
}
& $py --version

# --- 2. Entorno virtual dentro del repo ---------------------------------------------------
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "Creando el entorno virtual (venv)..."
    & $py -m venv venv
    if ($LASTEXITCODE -ne 0) { Write-Host "No se pudo crear el venv." -ForegroundColor Red; exit 1 }
}

# --- 3. Dependencias ---------------------------------------------------------------------
Write-Host "Instalando dependencias (puede tardar unos minutos)..."
& venv\Scripts\python.exe -m pip install --upgrade pip
& venv\Scripts\python.exe -m pip install -r requirements.txt platformio pyserial
if ($LASTEXITCODE -ne 0) { Write-Host "Falló pip install." -ForegroundColor Red; exit 1 }

# --- 4. .env con JWT_SECRET aleatoria (no se imprime) --------------------------------------
if (-not (Test-Path ".env")) { Copy-Item ".env.example" ".env" }
$lineas = Get-Content ".env"
$tieneClave = $lineas | Where-Object { $_ -match '^JWT_SECRET=.+' -and $_ -notmatch '^JWT_SECRET=cambie-esta' }
if (-not $tieneClave) {
    $clave = & venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
    $lineas = $lineas | Where-Object { $_ -notmatch '^JWT_SECRET=' }
    $lineas = @("JWT_SECRET=$clave") + $lineas
    Set-Content -Path ".env" -Value $lineas -Encoding ASCII
    Write-Host "Se creó JWT_SECRET en .env."
}

Write-Host ""
Write-Host "Listo. Siguiente paso: iniciar_demo.bat" -ForegroundColor Green
