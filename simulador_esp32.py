#!/usr/bin/env python3
"""
Simulador del ESP32 de la matera (R3).

Hace lo mismo que haría el dispositivo real: "lee" sus sensores cada cierto tiempo
y envía la lectura por HTTP al backend con su token de dispositivo.

Es un script independiente: solo usa la librería estándar de Python y no importa
nada del proyecto. Lo único que conoce del backend es la URL y el token que el
backend le entregó al registrar la planta (igual que el token que se grabaría
en el firmware de un ESP32 de verdad).

Qué genera:
  1. Lecturas realistas: la tierra se va secando y de vez en cuando "riegan";
     la luz sigue el ciclo del día; la temperatura sube de día y baja de noche.
  2. Valores fuera de rango para la planta: salen solos cuando la tierra se seca
     o hay demasiado sol (el backend responde 201 con EN_RIESGO o CRITICO).
  3. Datos inválidos, como un sensor dañado (el backend debe responder 400 o 401):
       - imposible:      un valor físicamente imposible (humedad 150 %, temperatura -99 °C)
       - no_numerico:    el sensor devuelve texto ("ERR") en vez de un número
       - campo_faltante: la lectura llega sin uno de los tres valores
       - sin_token:      la petición sale sin el token del dispositivo

Uso típico:
  python simulador_esp32.py --dispositivo-id esp32-01 --token <TOKEN> --intervalo 3
"""
import argparse
import json
import math
import os
import random
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

TIPOS_DE_ERROR = ("imposible", "no_numerico", "campo_faltante", "sin_token")


class MateraSimulada:
    """
    Modelo sencillo del ambiente de una matera.
    Cada llamada a `leer()` avanza el reloj simulado y devuelve lo que medirían los sensores.
    """

    def __init__(self, rng: random.Random, minutos_por_lectura: float, luz_maxima: float,
                 humedad_inicial: float = 45.0, umbral_riego: float = 12.0):
        self._rng = rng
        self._minutos_por_lectura = minutos_por_lectura
        self._paso = timedelta(minutes=minutos_por_lectura)
        self._luz_maxima = luz_maxima
        self._umbral_riego = umbral_riego
        self.humedad = humedad_inicial
        # El reloj simulado arranca a las 7:00 (hora Colombia, 12:00 UTC) para que la demo empiece de día.
        self.reloj = datetime.now(timezone.utc).replace(hour=12, minute=0, second=0, microsecond=0)
        self.regada = False

    def _hora_local(self) -> float:
        # Colombia es UTC-5; solo se usa para el ciclo de luz y temperatura.
        local = self.reloj - timedelta(hours=5)
        return local.hour + local.minute / 60

    def _luz(self) -> float:
        hora = self._hora_local()
        if hora < 6 or hora > 18:
            return round(self._rng.uniform(0, 5), 1)  # de noche casi no hay luz
        sol = math.sin(math.pi * (hora - 6) / 12)  # 0 al amanecer, 1 al mediodía
        nubes = self._rng.uniform(0.6, 1.05)
        return round(max(0.0, self._luz_maxima * sol * nubes), 1)

    def _temperatura(self) -> float:
        hora = self._hora_local()
        # Mínima ~16 °C de madrugada, máxima ~26 °C a media tarde, más un poco de ruido.
        ciclo = math.sin(math.pi * (hora - 9) / 12)
        return round(21 + 5 * ciclo + self._rng.uniform(-0.6, 0.6), 1)

    def _actualizar_humedad(self, luz: float, temperatura: float) -> None:
        self.regada = False
        if self.humedad <= self._umbral_riego and self._rng.random() < 0.5:
            # Alguien riega: la humedad sube de golpe.
            self.humedad = self._rng.uniform(60, 72)
            self.regada = True
            return
        # La tierra se seca más rápido con sol y calor.
        secado = (0.6 + luz / 3000 + max(0.0, temperatura - 20) * 0.08) * self._minutos_por_lectura / 30
        self.humedad = max(3.0, self.humedad - secado * self._rng.uniform(0.7, 1.3))

    def leer(self) -> dict:
        self.reloj += self._paso
        luz = self._luz()
        temperatura = self._temperatura()
        self._actualizar_humedad(luz, temperatura)
        return {
            "humedad": round(self.humedad + self._rng.uniform(-0.5, 0.5), 1),
            "luz": luz,
            "temperatura": temperatura,
        }


def danar_lectura(lectura: dict, tipo: str, rng: random.Random) -> dict:
    """Devuelve una copia de la lectura con el defecto pedido (ver TIPOS_DE_ERROR)."""
    danada = dict(lectura)
    if tipo == "imposible":
        if rng.random() < 0.5:
            danada["humedad"] = 150.0
        else:
            danada["temperatura"] = -99.0
    elif tipo == "no_numerico":
        danada[rng.choice(["humedad", "luz", "temperatura"])] = "ERR"
    elif tipo == "campo_faltante":
        danada.pop(rng.choice(["humedad", "luz", "temperatura"]))
    # "sin_token" no cambia los valores: se resuelve al armar la petición.
    return danada


def enviar(url: str, cuerpo: dict, token: str, timeout: float = 5.0):
    """Hace el POST. Devuelve (código HTTP, JSON de respuesta o texto)."""
    cabeceras = {"Content-Type": "application/json"}
    if token:
        cabeceras["Authorization"] = f"Bearer {token}"
    peticion = urllib.request.Request(
        url, data=json.dumps(cuerpo).encode("utf-8"), headers=cabeceras, method="POST"
    )
    try:
        with urllib.request.urlopen(peticion, timeout=timeout) as respuesta:
            return respuesta.status, json.loads(respuesta.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        texto = error.read().decode("utf-8")
        try:
            return error.code, json.loads(texto)
        except ValueError:
            return error.code, texto


def describir_respuesta(codigo: int, datos) -> str:
    if isinstance(datos, dict):
        if 200 <= codigo < 300:
            return f"{codigo} · estado {datos.get('estado', '?')}"
        return f"{codigo} · {datos.get('error', 'ERROR')}: {datos.get('mensaje', '')}"
    return f"{codigo} · {datos}"


def leer_argumentos(argv=None):
    parser = argparse.ArgumentParser(description="Simulador del ESP32 de la matera inteligente")
    parser.add_argument("--url", default=os.getenv("BACKEND_URL", "http://localhost:5000"),
                        help="URL base del backend (por defecto http://localhost:5000)")
    parser.add_argument("--dispositivo-id", default=os.getenv("DISPOSITIVO_ID", "esp32-01"),
                        help="Id del dispositivo, el mismo con que se registró la planta")
    parser.add_argument("--token", default=os.getenv("TOKEN_DISPOSITIVO", ""),
                        help="Token del dispositivo que entregó el backend al registrar la planta")
    parser.add_argument("--intervalo", type=float, default=3.0,
                        help="Segundos entre lecturas (por defecto 3)")
    parser.add_argument("--iteraciones", type=int, default=0,
                        help="Cuántas lecturas enviar; 0 = sin fin")
    parser.add_argument("--prob-error", type=float, default=0.15,
                        help="Probabilidad de enviar un dato inválido en cada lectura (0 a 1)")
    parser.add_argument("--minutos-por-lectura", type=float, default=30.0,
                        help="Cuánto avanza el reloj simulado en cada lectura (acelera el día)")
    parser.add_argument("--humedad-inicial", type=float, default=45.0,
                        help="Humedad del sustrato al arrancar, en %% (por defecto 45)")
    parser.add_argument("--luz-maxima", type=float, default=1800.0,
                        help="Luz al mediodía en lux (junto a una ventana ~1500-2500)")
    parser.add_argument("--semilla", type=int, default=None,
                        help="Semilla aleatoria para repetir exactamente la misma secuencia")
    args = parser.parse_args(argv)
    if not args.token:
        parser.error("falta el token del dispositivo: use --token o la variable TOKEN_DISPOSITIVO")
    if not 0 <= args.prob_error <= 1:
        parser.error("--prob-error debe estar entre 0 y 1")
    return args


def main(argv=None) -> None:
    args = leer_argumentos(argv)
    rng = random.Random(args.semilla)
    matera = MateraSimulada(rng, args.minutos_por_lectura, args.luz_maxima, args.humedad_inicial)
    endpoint = f"{args.url.rstrip('/')}/api/dispositivos/{args.dispositivo_id}/lecturas"

    print("=" * 72)
    print(f"Simulador ESP32 · dispositivo {args.dispositivo_id}")
    print(f"Endpoint:  {endpoint}")
    print(f"Intervalo: {args.intervalo} s · reloj simulado +{args.minutos_por_lectura:g} min por lectura")
    print(f"Datos inválidos: {args.prob_error:.0%} de las lecturas")
    print("=" * 72)

    enviadas = 0
    while args.iteraciones == 0 or enviadas < args.iteraciones:
        lectura = matera.leer()
        tipo_error = rng.choice(TIPOS_DE_ERROR) if rng.random() < args.prob_error else None

        cuerpo = danar_lectura(lectura, tipo_error, rng) if tipo_error else dict(lectura)
        cuerpo["dispositivo_id"] = args.dispositivo_id
        cuerpo["marca_tiempo"] = datetime.now(timezone.utc).isoformat()
        token = "" if tipo_error == "sin_token" else args.token

        hora = (matera.reloj - timedelta(hours=5)).strftime("%H:%M")
        etiqueta = f"[inválida: {tipo_error}]" if tipo_error else ("[riego]" if matera.regada else "")
        valores = " ".join(f"{k}={cuerpo.get(k, '—')}" for k in ("humedad", "luz", "temperatura"))
        print(f"#{enviadas + 1:<4} {hora} {valores} {etiqueta}")

        try:
            codigo, datos = enviar(endpoint, cuerpo, token)
            print(f"       -> {describir_respuesta(codigo, datos)}")
        except urllib.error.URLError as error:
            print(f"       -> sin conexión ({error.reason}). ¿Está corriendo el backend en {args.url}?")

        enviadas += 1
        if args.iteraciones == 0 or enviadas < args.iteraciones:
            time.sleep(args.intervalo)

    print(f"\nListo: {enviadas} lecturas enviadas.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSimulador detenido.")
        sys.exit(0)
