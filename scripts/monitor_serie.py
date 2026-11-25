#!/usr/bin/env python3
"""Lector del puerto serie del ESP32 (Linux y Windows).

Busca la placa por el VID del chip USB (CH340, CP210x o USB nativo de Espressif), la reinicia
con DTR/RTS y muestra lo que imprime.

Uso:
    python scripts/monitor_serie.py                    # 30 s
    python scripts/monitor_serie.py --segundos 0       # hasta Ctrl+C
    python scripts/monitor_serie.py --puerto COM5
"""
import argparse
import sys
import time

import serial
from serial.tools import list_ports

VIDS = {0x1A86: "CH340", 0x10C4: "CP210x", 0x303A: "Espressif"}


def buscar_puerto():
    for p in list_ports.comports():
        if p.vid in VIDS:
            return p.device, VIDS[p.vid]
    return None, None


def reiniciar(ser):
    # EN y GPIO0 van por DTR/RTS: dejar GPIO0 en alto y pulsar EN reinicia al programa normal.
    try:
        ser.dtr = False
        ser.rts = True
        time.sleep(0.1)
        ser.rts = False
    except OSError:
        print("(este puerto no permite reiniciar la placa; púlsale EN a mano)")


def main():
    ap = argparse.ArgumentParser(description="Lee el puerto serie del ESP32")
    ap.add_argument("--puerto", help="ej. COM5 o /dev/ttyUSB0 (por defecto se detecta)")
    ap.add_argument("--segundos", type=float, default=30, help="duración; 0 = hasta Ctrl+C")
    ap.add_argument("--baudios", type=int, default=115200)
    args = ap.parse_args()

    puerto, chip = args.puerto, "indicado a mano"
    if not puerto:
        puerto, chip = buscar_puerto()
    if not puerto:
        print("No encuentro el ESP32. Revisa el cable USB (que sea de datos) y el driver CH340.")
        print("Puertos vistos:", [p.device for p in list_ports.comports()] or "ninguno")
        return 1

    print(f"Puerto: {puerto} ({chip}), {args.baudios} baudios. Ctrl+C para salir.", flush=True)
    try:
        ser = serial.Serial(puerto, args.baudios, timeout=0.5)
    except serial.SerialException as e:
        print(f"No pude abrir {puerto}: {e}")
        print("¿Otro programa lo está usando? En Linux, ¿estás en el grupo dialout?")
        return 1

    with ser:
        reiniciar(ser)
        fin = time.time() + args.segundos if args.segundos > 0 else None
        try:
            while fin is None or time.time() < fin:
                linea = ser.readline()
                if linea:
                    print(linea.decode("utf-8", errors="replace").rstrip(), flush=True)
        except KeyboardInterrupt:
            pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
