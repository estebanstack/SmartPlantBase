# Guía para Windows

Cómo dejar la demo andando en un PC con Windows: backend, firmware y ESP32. Todo se hace con doble clic en los `.bat` de la carpeta `scripts\`.

## 1. Preparar el PC (una sola vez)

1. **Python.** Instala la versión 3.10 o superior desde https://www.python.org/downloads/. En la primera pantalla del instalador marca **"Add python.exe to PATH"** antes de pulsar Install.
2. **Driver del ESP32.** Normalmente no hace falta. Conecta la placa con un cable USB de datos (muchos cables solo cargan). Abre el Administrador de dispositivos y mira en "Puertos (COM y LPT)": si aparece algo como `USB-SERIAL CH340 (COM5)`, ya está. Si en cambio sale un dispositivo desconocido, instala el driver CH340 (busca "CH340 driver" del fabricante WCH) y vuelve a conectar la placa.
3. **El código.** Con git:
   ```
   git clone -b feature/esp32-producto https://github.com/estebanstack/SmartPlantBase.git
   ```
   o descarga el ZIP de esa rama desde GitHub (botón Code, Download ZIP, con la rama `feature/esp32-producto` elegida) y descomprímelo.
4. **Instalar.** Entra a la carpeta `scripts` y haz doble clic en `instalar.bat`. Crea el entorno `venv`, instala las dependencias y PlatformIO, y genera el archivo `.env` con una clave aleatoria. Si Python no está bien instalado, el script lo dice.

## 2. Probar el backend

1. Activa el **hotspot del celular** y conecta el PC a esa red.
2. Doble clic en `scripts\iniciar_demo.bat`. Anota la dirección que muestra en la red del hotspot, algo como `http://192.168.43.10:5000`.
3. La primera vez, Windows pregunta por el Firewall: marca **Redes privadas** y Permitir.
4. En el celular (misma red) abre esa dirección. Crea una cuenta y registra una planta. El id de dispositivo puede ser cualquiera: se reemplaza al vincular.

Deja esa ventana abierta mientras dura la demo.

## 3. Revisar el montaje con el diagnóstico

1. Conecta el ESP32. `flashear.bat` necesita saber qué firmware subir, así que se usa desde una ventana de CMD abierta en la carpeta `scripts`:
   ```
   flashear.bat diagnostico
   ```
   La primera vez PlatformIO descarga varios cientos de MB y tarda varios minutos.
2. Cuando termine, ejecuta:
   ```
   monitor.bat
   ```
   Muestra 30 segundos de lo que imprime la placa (`monitor.bat --segundos 0` no se detiene hasta Ctrl+C). Verás el escaneo I2C (la OLED debería salir en `0x3C`), la búsqueda del DHT22 y los valores de los pines analógicos. Gira la perilla y mira que GPIO34 cambie.
3. Si algo no coincide con tu cableado, edita `firmware\include\config_pines.h` (es el único archivo de configuración) y vuelve a empezar.

## 4. Subir el firmware final

1. Con el ESP32 conectado, en CMD dentro de `scripts`:
   ```
   flashear.bat esp32dev
   ```
2. En el celular, conéctate a la red **MateraGotchi-Setup**. Se abre un portal (si no, entra a `192.168.4.1`).
3. Elige la red del hotspot, escribe su clave y, en **Servidor**, la dirección del PC sin `http://`, por ejemplo `192.168.43.10:5000`.
4. El ESP32 se conecta y dibuja un **QR** en la OLED. Escanéalo con el celular, inicia sesión y elige la planta.
5. La OLED dice "Vinculado!" y desde ahí manda lecturas cada 10 s.

Para empezar de cero (cambió el WiFi o la dirección del PC): mantén el botón **BOOT** 5 segundos con el firmware corriendo.

## Cableado recomendado

| Pieza | Conexión |
|---|---|
| OLED 1.3" | VCC a 3V3, GND a GND, SCK a D22, SDA a D21 |
| Perilla (potenciómetro) | extremos a 3V3 y GND, pata del medio a GPIO34 |
| Sensor de humedad de suelo | AOUT a GPIO35 |
| DHT22 (módulo `+ out -`) | + a 3V3, - a GND, out a D4 (GPIO4) |

Si el `out` del DHT22 va a otro pin, cámbialo en `TEMP_PIN` de `config_pines.h`.

## Problemas frecuentes

- **No aparece ningún puerto COM.** Prueba otro cable (de datos) y otro puerto USB, y mira el Administrador de dispositivos. Si sale como dispositivo desconocido, instala el driver CH340.
- **`flashear.bat` se queda en `Connecting......`.** Mantén pulsado BOOT en la placa hasta que empiece a escribir.
- **El celular o el ESP32 no llegan al PC.** Casi siempre es el Firewall. Abre PowerShell como administrador y ejecuta:
  ```
  netsh advfirewall firewall add rule name="Matera 5000" dir=in action=allow protocol=TCP localport=5000
  ```
  Comprueba también que el PC y el celular estén en el mismo hotspot y que la IP no haya cambiado.
- **La OLED no enciende.** Lo más probable es alimentación o cables flojos. Revisa que VCC y GND lleguen de verdad al módulo (en las protoboards grandes los rieles de alimentación a veces vienen partidos por la mitad) y que el conector de la OLED esté bien metido. Si el diagnóstico la ve pero no dibuja, prueba el otro controlador: en `config_pines.h` cambia `OLED_CONTROLADOR` entre `OLED_SH1106` y `OLED_SSD1306`. Si la OLED no contesta, el firmware sigue funcionando solo por serie.
- **El diagnóstico avisa "falso positivo" en I2C.** La línea SDA está pegada a bajo: la OLED no tiene alimentación o un cable no hace contacto.
- **El DHT22 da `nan` o "Error de sensor".** El pin `out` no es el que está en `TEMP_PIN`, o el módulo no está alimentado. Corre el diagnóstico: la prueba lenta del DHT dice en qué GPIO responde.
- **La primera compilación es lenta.** PlatformIO baja la plataforma ESP32 y las librerías; son varios cientos de MB y tarda minutos. Las siguientes son rápidas.
- **Cada vez que reinicio el backend hay que vincular otra vez.** Falta `JWT_SECRET` en `.env`. Ejecuta `instalar.bat` de nuevo.
