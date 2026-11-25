# Contexto del proyecto (para Claude)

Lee este archivo primero. Resume qué es el proyecto, dónde está cada cosa y cómo trabajar con la dueña del repositorio.

## Qué es

SmartPlantBase es una **matera inteligente** (curso de Arquitectura de Software, Universidad Sergio Arboleda). Un ESP32 lee temperatura, humedad y luz de una planta y las manda a un backend Flask. El backend compara las lecturas con los rangos de la especie y calcula el estado (`SALUDABLE`, `EN_RIESGO`, `CRITICO`). Encima hay una capa de gamificación, el **Matera-Gotchi**: una carita que cambia de ánimo según el estado de la planta, con XP, niveles y racha. El ESP32 la dibuja en una pantalla OLED.

- **Backend:** Python, Flask, SQLite, PyJWT, arquitectura **hexagonal** (puertos y adaptadores). El dominio no importa Flask, SQL ni JWT.
- **Frontend:** HTML, CSS y JavaScript estáticos en `frontend/`, servidos por el mismo Flask.
- **Firmware:** C++ con Arduino sobre PlatformIO, en `firmware/`.
- **Vinculación por QR:** el ESP32 crea una sesión, dibuja en la OLED un QR con `http://<servidor>/?vincular=<sesión>`; al escanearlo con el celular, el usuario elige su planta y el dispositivo recibe su token.

## Mapa del repositorio

| Ruta | Qué hay |
|---|---|
| `app.py` | Arranque del backend |
| `matera/dominio/` | Reglas, modelo, casos de uso y puertos (`gamificacion.py`, `validador.py`, `modelo.py`) |
| `matera/adaptadores/entrada/` | API para el front y para el dispositivo, seguridad JWT |
| `matera/adaptadores/salida/` | CSV, SQLite, JWT, hasher |
| `matera/app.py` | Único sitio donde se conectan adaptadores con puertos |
| `frontend/` | Interfaz web |
| `tests/` | Pruebas (pytest) y dobles en `fakes.py` |
| `firmware/include/config_pines.h` | **Lo único que se edita** para pines, modelos de sensor y calibración |
| `firmware/src/` | `main.cpp`, `sensores.cpp`, `pantalla.cpp`, `red.cpp`; `diagnostico/` es el otro firmware (descubre pines) |
| `scripts/` | `instalar.bat`, `iniciar_demo.bat`, `flashear.bat`, `monitor.bat`, `monitor_serie.py` (y `iniciar_demo.sh` para Linux) |
| `simulador_esp32.py` | Imita al ESP32 sin hardware |
| `GUIA_WINDOWS.md` | Pasos para Windows |
| `firmware/README.md` | Guía detallada del firmware |
| `docs/` | Documento de arquitectura, propuesta del Gotchi, enunciados |

## Comandos (Windows, desde la raíz del repo)

```
scripts\instalar.bat                     instala todo (una vez)
scripts\iniciar_demo.bat                 arranca el backend y muestra la IP
venv\Scripts\python.exe -m pytest -q     pruebas (se esperan 146 en verde)
venv\Scripts\pio.exe run -d firmware -e esp32dev          compilar el firmware principal
venv\Scripts\pio.exe run -d firmware -e diagnostico       compilar el diagnóstico
scripts\flashear.bat diagnostico         subir el diagnóstico al ESP32
scripts\flashear.bat esp32dev            subir el firmware principal
scripts\monitor.bat                      ver lo que imprime la placa (30 s; --segundos 0 = sin límite)
```

## Estado del hardware

Placa: ESP32 DevKit de 38 pines (WROOM-32, USB con chip CH340). Id visto: `esp32-CD75D0`.

| Pieza | Conexión | Estado |
|---|---|---|
| Perilla B10K (potenciómetro), pata del medio | GPIO34 | Verificada |
| Sensor capacitivo de humedad de suelo v1.2, AOUT | GPIO35 | Verificada, lee ~2400-3000 al aire; a veces 4095 (suele ser cableado) |
| OLED 1.3", pines `VCC GND SCK SDA`, controlador **SH1106**, dirección `0x3C` | SDA=GPIO21, SCL=GPIO22 | Respondió una vez y luego dejó de hacerlo. **No verificada** |
| DHT22 (módulo blanco `+ out -`) | recomendado: + a 3V3, - a GND, out a D4 (GPIO4); `TEMP_PIN 4` es provisional | Nunca respondió. **Sin confirmar** el pin `out` |

Sospechas sobre la OLED y el DHT (no confirmadas):
- Jumpers flojos o el conector de la OLED a medio meter.
- Los rieles de alimentación de la protoboard están partidos por la mitad y los módulos no recibían corriente.
- Un escaneo mostró la OLED "respondiendo" en SDA=21 con todos los SCL: es un falso positivo, la línea SDA quedó pegada a bajo porque el chip no tenía alimentación. El diagnóstico ya lo detecta y lo avisa.

El firmware principal ya no se cuelga si la OLED no contesta: comprueba el bus antes de iniciarla y, si no hay ACK, sigue solo por serie.

## Hecho y pendiente

Hecho:
- Backend hexagonal con JWT, plantas, historial, diagnóstico, Gotchi y WebSocket; 146 pruebas.
- Frontend, simulador y vinculación por QR iniciada por el dispositivo.
- Firmware que compila (`esp32dev` y `diagnostico`), con portal WiFi, QR, OLED SSD1306/SH1106 y guarda del bus I2C.
- Scripts y guía para Windows.

Pendiente:
- Confirmar con el diagnóstico que la OLED y el DHT22 responden con la alimentación bien hecha.
- Fijar `TEMP_PIN` con el pin real del DHT22.
- Calibrar `HUM_SUELO_ADC_SECO` y `HUM_SUELO_ADC_MOJADO` (sonda al aire y en agua).
- Prueba de punta a punta con la placa real: portal WiFi, QR, vinculación y lecturas.

## Reglas de trabajo

- Nombres de código, comentarios y documentos **en español**, como el resto del repo.
- Respeta la arquitectura hexagonal: el dominio no importa Flask, SQL, HTTP ni PyJWT; todo pasa por puertos y adaptadores, y la composición se hace solo en `matera/app.py`.
- Las pruebas deben seguir en verde (146). Si agregas lógica, agrega su prueba.
- Nunca subas `.env`, claves ni tokens a git.
- Del firmware, solo `firmware/include/config_pines.h` es configuración de montaje.
- **Claude web no puede ejecutar comandos ni ver la placa.** Cuando necesites información, dale a la usuaria el comando exacto para pegar en CMD y pídele que te pegue la salida completa. Lo más útil es la salida de `scripts\monitor.bat` después de `flashear.bat diagnostico`. No supongas el resultado de algo que no has visto.
- Dile qué está verificado y qué no, sin rodeos.

## Cómo conectarlo a Claude web

1. Entra a claude.ai, Projects, **New project**.
2. En **Add content**, elige **GitHub** y el repositorio `estebanstack/SmartPlantBase` (público).
3. Elige la rama `feature/esp32-producto` (o `main` si ya se fusionó).
4. Selecciona estos archivos y carpetas: `CONTEXTO_CLAUDE.md`, `GUIA_WINDOWS.md`, `firmware/`, `matera/`, `frontend/`, `scripts/`.
5. En las instrucciones del proyecto (Set project instructions) pega este texto:

```
Eres mi ayudante técnico para el proyecto SmartPlantBase (matera inteligente con ESP32, backend Flask hexagonal, curso de Arquitectura de Software). Antes de responder, lee CONTEXTO_CLAUDE.md y GUIA_WINDOWS.md del proyecto.
Trabajo en Windows. No puedes ejecutar comandos ni ver mi placa: cuando necesites datos, dame el comando exacto para pegar en CMD y pídeme que te pegue la salida completa (sobre todo la de scripts\monitor.bat).
Responde en español, claro y corto. Dime siempre qué está verificado y qué es suposición.
Si me propones cambios de código, dime el archivo y el fragmento exacto. Respeta la arquitectura hexagonal (el dominio no importa Flask, SQL ni JWT), no rompas las 146 pruebas y nunca me pidas subir .env ni claves a git.
Para el hardware, el único archivo de configuración es firmware/include/config_pines.h.
```
