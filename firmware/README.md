# Firmware del Matera-Gotchi (ESP32)

Firmware para el ESP32 de la matera: lee los sensores, los manda al backend de SmartPlantBase y dibuja en la pantalla OLED la carita del Matera-Gotchi que responde el servidor.

> Estado: compila y está probado contra el backend con el simulador. **No se ha probado con la placa real** (las dependencias de pines y modelos se confirman con el montaje en mano). Los pasos de abajo están pensados para hacer eso.

## Qué hay aquí

```
firmware/
├── platformio.ini                # dos entornos: esp32dev (principal) y diagnostico
├── include/
│   ├── config_pines.h            # LO ÚNICO QUE SE EDITA: pines, modelos de sensor, calibración
│   └── tipos.h
└── src/
    ├── main.cpp                  # flujo: WiFi -> hora -> vinculación QR -> ciclo de lectura
    ├── sensores.cpp / .h         # lectura de DHT, sondas y potenciómetro
    ├── pantalla.cpp / .h         # OLED: splash, QR, Gotchi, lecturas
    ├── red.cpp / .h              # portal WiFi, mDNS, hora y llamadas HTTP al backend
    └── diagnostico/diagnostico.cpp   # entorno "diagnostico": descubre pines y modelos
```

## Mañana, paso a paso

### 0. Una sola vez en el portátil

1. Permiso para usar el puerto USB (hay que cerrar sesión y volver a entrar después):
   ```bash
   sudo usermod -aG dialout $USER
   ```
2. PlatformIO ya está instalado en `~/.platformio-venv`. Para escribir menos:
   ```bash
   alias pio=~/.platformio-venv/bin/pio
   ```
3. Revisa que `JWT_SECRET` esté en `.env` (si no, `scripts/iniciar_demo.sh` te dice cómo crearla). Sin ella, cada reinicio del backend invalida el token del ESP32.

### 1. Red y backend

1. Activa el **hotspot del celular** y conecta el portátil a él.
2. En el portátil:
   ```bash
   cd 2026-2/ARQUIT/SmartPlantBase
   ./scripts/iniciar_demo.sh
   ```
   Imprime las IPs del portátil (usa la de la red del hotspot) y `<hostname>.local`. Si `ufw` está activo, te avisa que abras el puerto: `sudo ufw allow 5000/tcp`.
3. Desde el celular, abre `http://<ip-del-portátil>:5000`. Si carga el panel, la red está bien. Crea tu cuenta y registra una planta (el id de dispositivo puede ser cualquiera, se reemplaza al vincular).

### 2. Descubrir pines y modelos (firmware `diagnostico`)

1. Conecta la placa por USB y sube el diagnóstico:
   ```bash
   cd firmware
   pio run -e diagnostico -t upload
   pio device monitor
   ```
   Si no encuentra el puerto, mira la sección de problemas. Si el upload se queda en `Connecting...`, mantén pulsado BOOT hasta que empiece a escribir.
2. En el monitor serie (115200) verás:
   - **Escaneo I2C:** `Dispositivo en 0x3C (SDA=21, SCL=22)` es la OLED. Si sale en otros pines, apúntalos.
   - **Búsqueda de DHT:** `GPIO4 responde como DHT22: temperatura 24.1 C ...`. Si la temperatura trae decimales es DHT22; si siempre es entera, DHT11.
   - **Pines analógicos:** una línea por segundo con `GPIO32=… GPIO33=… GPIO34=…`. Gira el potenciómetro y mira cuál GPIO cambia entre 0 y 4095. Moja la sonda de suelo y mira cuál baja (o sube). Los pines sin nada conectado dan números que bailan solos.
   - Pulsa BOOT para repetir el escaneo de I2C y DHT.
3. Apunta en la tabla de cableado (más abajo) qué es cada cosa.

### 3. Configurar y subir el firmware principal

1. Edita **solo** `firmware/include/config_pines.h`:
   - `SERVIDOR_POR_DEFECTO`: pon el nombre real de tu portátil (el que imprimió el script) o su IP.
   - Pines y tipo de la OLED, temperatura y humedad (`DHT11`, `DHT22` o sonda de suelo).
   - Potenciómetro: `POT_PIN` y `POT_ROL`. Con `ROL_LUZ` la perilla hace de sensor de luz; con `ROL_HUMEDAD`, girarla "riega" la planta y el Gotchi se pone agradecido.
   - Si usas sonda de suelo, `HUM_SUELO_ADC_SECO` y `HUM_SUELO_ADC_MOJADO` con los valores que viste en el diagnóstico (sonda al aire y sonda en agua).
2. Sube:
   ```bash
   pio run -e esp32dev -t upload
   pio device monitor
   ```

### 4. Primer arranque

1. La OLED muestra el splash y luego **"Configura el WiFi"**. Con el celular conéctate a la red `MateraGotchi-Setup`; el portal se abre solo (si no, ve a `192.168.4.1`).
2. Elige la red del hotspot y escribe su clave. En **Servidor** deja `equipo:puerto` (por ejemplo `192.168.43.10:5000`). Guarda.
3. El ESP32 se conecta, ajusta la hora y dibuja un **QR** en la pantalla.
4. Escanéalo con el celular (debe estar en la misma red del hotspot). Se abre el panel con **"Vincular este dispositivo a…"**: inicia sesión, elige la planta y pulsa **Vincular**.
5. La OLED dice "Vinculado!" y desde ahí empieza a mandar lecturas cada 10 s. En el panel aparece el Gotchi de la planta y se actualiza solo.

### Restablecer

Mantén **BOOT** (GPIO0) 5 segundos con el firmware corriendo: borra el WiFi y la vinculación y vuelve al portal. También sirve si cambió el servidor, porque la dirección solo se pide cuando se abre el portal.

## Cableado (plantilla)

Llénala con lo que salga del diagnóstico.

| Componente | Señal | Pin del ESP32 | Notas |
|---|---|---|---|
| OLED SSD1306 | VCC | 3V3 | |
| | GND | GND | |
| | SDA | GPIO ___ (por defecto 21) | dirección I2C: 0x___ |
| | SCL | GPIO ___ (por defecto 22) | |
| Temperatura (modelo: ______) | VCC / GND | 3V3 / GND | un DHT necesita pull-up de 4.7 kΩ entre DATA y 3V3 (muchos módulos ya la traen) |
| | DATA | GPIO ___ | |
| Humedad (modelo: ______) | VCC / GND | 3V3 / GND | |
| | DATA / AO | GPIO ___ | analógico: usar ADC1 (32, 33, 34, 35, 36, 39) |
| Potenciómetro | extremos | 3V3 y GND | |
| | cursor (el del medio) | GPIO ___ | ADC1; rol: ☐ luz ☐ humedad |
| Botón BOOT | — | GPIO0 | ya viene en la placa |

## Problemas frecuentes

- **El puerto serie no aparece o da `Permission denied`.** Falta el grupo `dialout` (`sudo usermod -aG dialout $USER` y reiniciar sesión). Revisa también el cable USB: muchos solo cargan y no llevan datos. Comprueba con `ls /dev/ttyUSB* /dev/ttyACM*`.
- **El upload se queda en `Connecting......`.** Mantén pulsado BOOT mientras empieza, o prueba otro cable.
- **El ESP32 no encuentra al servidor.** La pantalla dice "No encuentro al servidor". Casi siempre es una de estas:
  - El hotspot del celular aísla a los clientes entre sí (*client isolation*) o tiene activa alguna opción tipo "solo internet". Prueba con otro celular, o con el portátil conectado por el mismo hotspot y haz `ping` a la IP del ESP32.
  - El nombre `<hostname>.local` no se resuelve. mDNS no siempre funciona en un hotspot: usa directamente la IP del portátil (`192.168.x.x:5000`). Al reconfigurar con BOOT 5 s puedes cambiarla.
  - `ufw` bloquea el puerto: `sudo ufw allow 5000/tcp`.
  - El portátil cambió de IP: vuelve a mirar la que imprime `iniciar_demo.sh`.
- **El celular no abre el QR.** Debe estar en la misma red que el portátil. Si el QR no cabe en la pantalla (servidor con nombre largo), la OLED muestra la URL escrita: puedes teclearla.
- **La lectura analógica sale 0 o fija al encender el WiFi.** Estás en un pin ADC2 (0, 2, 4, 12, 13, 14, 15, 25, 26, 27): no funcionan con WiFi activo. El firmware lo avisa al arrancar. Cambia a un pin ADC1 (32, 33, 34, 35, 36, 39).
- **Los GPIO 34, 35, 36 y 39 no sirven para un DHT.** Solo son entrada. Pon el DHT en uno como el 4, 5, 18 o 19.
- **Sensores a 3.3 V.** El ESP32 usa 3.3 V en sus pines: alimenta los sensores con 3V3 salvo que su módulo diga expresamente que soporta 5 V en la señal. Una sonda a 5 V puede dañar la entrada analógica.
- **"Error de sensor: temperatura" (o humedad).** El DHT no responde: revisa cableado, pull-up y el modelo (`DHT11` vs `DHT22`) en `config_pines.h`.
- **La OLED no enciende.** Mira en el diagnóstico si el I2C aparece en `0x3C` o `0x3D` y ajusta `OLED_DIRECCION`. El firmware sigue funcionando por serie aunque no haya pantalla.
- **El servidor no tiene internet (hotspot sin datos).** La hora se toma de la cabecera `Date` del propio backend si NTP falla.
- **Cada reinicio del backend pide vincular otra vez.** Pasa si falta `JWT_SECRET` en `.env`: el token que tenía el ESP32 deja de valer (401) y el firmware vuelve a mostrar el QR.

## Detalles que conviene saber

- El `dispositivo_id` sale de la MAC del chip (`esp32-A1B2C3`). Al vincular, la planta que elijas pasa a usar ese id. Si otra planta tuya lo tenía, esa queda como `libre-<id>`; si lo tenía una planta de otro usuario, el backend responde 409.
- El id de la sesión QR lo elige el ESP32 (12 caracteres hex aleatorios) y no el servidor (32), para que el QR sea de versión 3 y se lea bien en una pantalla de 128x64. Vale 5 minutos y quien conozca el id puede leer el token de esa sesión una vez autorizada, así que está pensado para una demo en red local, no para producción.
- Cada lectura se recorta a los límites físicos del backend (humedad 0-100, luz 0-150000, temperatura -50 a 80) para que un sensor ruidoso no provoque un 400.
- Si el servidor no responde, reintenta con espera creciente (5, 10, 20, 40 y 60 s) y muestra una X en la esquina de la pantalla.
