#!/usr/bin/env python3
"""
Simulador de Dispositivo Sensor ESP32 (R3).
Script independiente que genera y transmite telemetría ambiental periódica
al backend HTTP (POST /api/dispositivos/{id}/lecturas).

Genera:
1. Lecturas óptimas (SALUDABLE - 201 Created)
2. Lecturas con alertas botánicas (EN_RIESGO / CRITICO - 201 Created)
3. Lecturas corruptas o fuera de límites físicos (400 Bad Request - PARAMETRO_INVALIDO)
"""
import argparse
from datetime import datetime, timezone
import json
import os
import sys
import time
import urllib.error
import urllib.request


def generar_token_dispositivo_demo(dispositivo_id: str, planta_id: str = "planta-01") -> str:
    """Genera un token JWT de dispositivo usando la misma clave de configuración para pruebas."""
    try:
        from matera.adaptadores.salida.emisor_jwt import JwtEmisorTokenAdapter
        clave = os.getenv("JWT_SECRET", "matera-secret-key-arquitectura-2026-segura")
        emisor = JwtEmisorTokenAdapter(secret_key=clave)
        return emisor.emitir_token_dispositivo(dispositivo_id=dispositivo_id, planta_id=planta_id)
    except Exception:
        return ""


def main():
    parser = argparse.ArgumentParser(description="Simulador de Sensor ESP32 para SmartPlantBase")
    parser.add_argument("--url", default=os.getenv("BACKEND_URL", "http://localhost:5000"), help="URL base del backend")
    parser.add_argument("--dispositivo-id", default="esp32-01", help="ID del dispositivo ESP32")
    parser.add_argument("--intervalo", type=float, default=3.0, help="Intervalo en segundos entre envíos")
    parser.add_argument("--iteraciones", type=int, default=0, help="Número de lecturas a enviar (0 = infinito)")
    parser.add_argument("--token", default="", help="Token JWT de dispositivo con scope='dispositivo'")

    args = parser.parse_args()

    token = args.token or generar_token_dispositivo_demo(args.dispositivo_id)
    endpoint = f"{args.url.rstrip('/')}/api/dispositivos/{args.dispositivo_id}/lecturas"

    print("=" * 70)
    print("🌱 SIMULADOR DEL DISPOSITIVO SENSOR ESP32 · SMARTPLANTBASE")
    print(f"📡 Endpoint:       {endpoint}")
    print(f"📟 Dispositivo ID: {args.dispositivo_id}")
    print(f"⏱️  Intervalo:      {args.intervalo} s")
    print(f"🔁 Iteraciones:    {'Infinitas' if args.iteraciones == 0 else args.iteraciones}")
    print(f"🔑 Token cargado:  {token[:25]}..." if token else "⚠️  Sin token suministrado")
    print("=" * 70)

    # Secuencia de patrones botánicos de prueba
    patrones = [
        # 1. Rango Óptimo para Sansevieria (humedad 20-45%, luz 200-1500 lux, temp 15-29°C)
        {"humedad": 35.0, "luz": 600.0, "temperatura": 22.0, "desc": "Lectura óptima (SALUDABLE)"},
        {"humedad": 30.0, "luz": 850.0, "temperatura": 21.0, "desc": "Lectura óptima (SALUDABLE)"},
        # 2. Desviación Botánica (Sequía -> EN_RIESGO)
        {"humedad": 12.0, "luz": 900.0, "temperatura": 23.0, "desc": "Alerta botánica: sequía (EN_RIESGO)"},
        # 3. Múltiples Desviaciones (Calor excesivo + sequía -> CRITICO)
        {"humedad": 10.0, "luz": 2500.0, "temperatura": 36.0, "desc": "Alerta crítica: calor y sol (CRITICO)"},
        # 4. Sensor con Lectura Corrupta / Físicamente Imposible -> 400 PARAMETRO_INVALIDO
        {"humedad": 150.0, "luz": 500.0, "temperatura": 22.0, "desc": "Sensor corrupto: humedad > 100% (400)"},
        {"humedad": 25.0, "luz": 700.0, "temperatura": -99.0, "desc": "Sensor corrupto: temp < -50°C (400)"},
    ]

    enviados = 0
    while True:
        patron = patrones[enviados % len(patrones)]
        marca = datetime.now(timezone.utc).isoformat()
        payload = {
            "humedad": patron["humedad"],
            "luz": patron["luz"],
            "temperatura": patron["temperatura"],
            "marca_tiempo": marca,
        }

        print(f"\n[{enviados + 1}] Enviando {patron['desc']}...")
        print(f"    Valores: Humedad={patron['humedad']}% | Luz={patron['luz']} lux | Temp={patron['temperatura']}°C")

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            endpoint,
            data=data,
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}",
            },
            method="POST",
        )

        try:
            with urllib.request.urlopen(req, timeout=5) as response:
                resp_json = json.loads(response.read().decode("utf-8"))
                estado = resp_json.get("estado", "OK")
                print(f"    ✅ Respuesta {response.status}: Estado={estado}")
        except urllib.error.HTTPError as he:
            cuerpo = he.read().decode("utf-8")
            try:
                err_json = json.loads(cuerpo)
                print(f"    ⚠️  Respuesta {he.code}: {err_json.get('error')} - {err_json.get('mensaje')}")
            except Exception:
                print(f"    ⚠️  Respuesta {he.code}: {cuerpo}")
        except urllib.error.URLError as ue:
            print(f"    ❌ Error de conexión: {ue.reason}. ¿Está el backend ejecutándose?")

        enviados += 1
        if args.iteraciones > 0 and enviados >= args.iteraciones:
            print(f"\nFinalizadas {enviados} iteraciones.")
            break

        time.sleep(args.intervalo)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Simulador detenido por el usuario.")
        sys.exit(0)
