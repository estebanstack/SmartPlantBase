#!/usr/bin/env bash
# Arranca el backend para la demo con el ESP32.
#
# - Usa el entorno virtual compartido (../venv).
# - Comprueba que JWT_SECRET esté en .env (sin imprimirlo).
# - Muestra las direcciones por las que el ESP32 y el celular pueden llegar al portátil.
# - Avisa si el firewall (ufw) está activo.
#
# Uso:  ./scripts/iniciar_demo.sh
set -u

RAIZ="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$RAIZ" || exit 1
PYTHON="$RAIZ/../venv/bin/python"

if [ ! -x "$PYTHON" ]; then
    echo "No encuentro el entorno virtual en $PYTHON"
    echo "Créalo con:  python3 -m venv ../venv && ../venv/bin/pip install -r requirements.txt"
    exit 1
fi

# --- JWT_SECRET: sin ella los tokens se pierden cada vez que se reinicia el servidor ---------
if [ ! -f .env ] || ! grep -q '^JWT_SECRET=.\+' .env || grep -q '^JWT_SECRET=cambie-esta' .env; then
    echo "Falta JWT_SECRET en .env. Sin ella, cada reinicio invalida el token del ESP32 y hay que volver a vincular."
    echo "Genera una y agrégala (no se imprime en pantalla):"
    echo "  [ -f .env ] || cp .env.example .env"
    echo "  echo \"JWT_SECRET=\$(python3 -c 'import secrets; print(secrets.token_urlsafe(48))')\" >> .env"
    echo "Si .env ya tiene una línea JWT_SECRET= (vacía o la de ejemplo), bórrala antes de ejecutar el echo."
    exit 1
fi

PUERTO="$(grep -E '^PORT=' .env 2>/dev/null | tail -n1 | cut -d= -f2 | tr -d '[:space:]')"
PUERTO="${PUERTO:-5000}"

# --- Direcciones para llegar al portátil -------------------------------------------------------
echo "=============================================================="
echo " Matera-Gotchi · servidor de la demo (puerto $PUERTO)"
echo "=============================================================="
echo "Direcciones del portátil (usa la de la red del hotspot en el firmware y en el celular):"
ip -4 -o addr show scope global 2>/dev/null | awk '{split($4, a, "/"); printf "  %-12s http://%s:'"$PUERTO"'\n", $2, a[1]}'
echo "  por nombre   http://$(hostname).local:$PUERTO   (puede no resolver en el celular; si falla, usa la IP)"
echo

# --- Firewall ------------------------------------------------------------------------------------
if command -v ufw >/dev/null 2>&1 && systemctl is-active --quiet ufw 2>/dev/null; then
    echo "AVISO: ufw está activo. Si el ESP32 o el celular no conectan, abre el puerto:"
    echo "  sudo ufw allow $PUERTO/tcp"
    echo "(sin sudo no puedo ver si ya hay una regla para $PUERTO)"
    echo
fi

exec "$PYTHON" app.py
