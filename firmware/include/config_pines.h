// =====================================================================================
//  config_pines.h  ·  EL ÚNICO ARCHIVO QUE HAY QUE EDITAR PARA TU MONTAJE
// =====================================================================================
//  Aquí se dice qué sensores tiene tu matera y en qué pines están conectados.
//  Si no sabes algo, sube primero el firmware "diagnostico" (ver firmware/README.md):
//  imprime por el puerto serie los dispositivos I2C, los DHT que encuentra y el valor
//  de cada pin analógico, y con eso llenas este archivo.
//
//  Regla de oro de los pines analógicos: con WiFi encendido solo funcionan los pines ADC1
//  (GPIO 32, 33, 34, 35, 36, 39). Los ADC2 (0, 2, 4, 12, 13, 14, 15, 25, 26, 27) dan lecturas
//  inválidas mientras el WiFi está activo. Los GPIO 34, 35, 36 y 39 solo sirven de entrada.
// =====================================================================================
#pragma once

// -------------------------------------------------------------------------------------
//  1. SERVIDOR (el portátil que corre app.py)
// -------------------------------------------------------------------------------------
// Valor que aparece por defecto en el portal de configuración WiFi (se puede cambiar ahí).
// Formato "equipo:puerto". Usa el nombre que imprime scripts/iniciar_demo.sh (<hostname>.local)
// o, si el .local no resuelve, la IP del portátil en la red del hotspot (ej. "192.168.43.10:5000").
// TODO: cambia "mi-portatil" por el nombre real de tu portátil.
#define SERVIDOR_POR_DEFECTO "mi-portatil.local:5000"

// -------------------------------------------------------------------------------------
//  2. PANTALLA OLED SSD1306 (I2C, 128x64)
// -------------------------------------------------------------------------------------
#define OLED_SDA        21
#define OLED_SCL        22
#define OLED_DIRECCION  0x3C     // la mayoría usa 0x3C; algunas 0x3D (el diagnóstico la muestra)
#define OLED_ANCHO      128
#define OLED_ALTO       64

// -------------------------------------------------------------------------------------
//  3. SENSOR DE TEMPERATURA
// -------------------------------------------------------------------------------------
#define TEMP_DHT11        1   // sensor digital DHT11 (azul, mide temperatura y humedad del aire)
#define TEMP_DHT22        2   // sensor digital DHT22 / AM2302 (blanco, más preciso)
#define TEMP_ANALOGICO    3   // sensor analógico lineal: LM35, TMP36, etc.

#define TEMP_TIPO         TEMP_DHT22
#define TEMP_PIN          4

// Solo si TEMP_TIPO es TEMP_ANALOGICO:  grados = (milivoltios - OFFSET) / MV_POR_GRADO
//   LM35  -> OFFSET 0   y 10 mV por grado
//   TMP36 -> OFFSET 500 y 10 mV por grado
// (usar un pin ADC1: 32, 33, 34, 35, 36 o 39)
#define TEMP_ANALOGICO_OFFSET_MV     0.0f
#define TEMP_ANALOGICO_MV_POR_GRADO  10.0f

// -------------------------------------------------------------------------------------
//  4. SENSOR DE HUMEDAD
// -------------------------------------------------------------------------------------
#define HUM_DHT11         1   // humedad del AIRE con un DHT11
#define HUM_DHT22         2   // humedad del AIRE con un DHT22
#define HUM_SUELO         3   // sonda analógica de humedad del SUELO (capacitiva o resistiva)

// Si el sensor de temperatura y el de humedad son el mismo DHT, pon el mismo pin en TEMP_PIN y
// HUM_PIN y el mismo tipo en los dos: el firmware lo lee una sola vez.
// OJO: un DHT mide humedad del aire, no de la tierra. Para la demo sirve, pero para una matera
// de verdad lo correcto es una sonda de suelo (HUM_SUELO).
#define HUM_TIPO          HUM_SUELO
#define HUM_PIN           34

// Calibración de la sonda de suelo (solo si HUM_TIPO es HUM_SUELO). Son valores crudos del ADC
// (0-4095). Mide con la sonda al aire (seca) y metida en un vaso de agua (mojada) usando la
// lectura del firmware "diagnostico". Casi todas las sondas dan MÁS valor cuando están secas.
#define HUM_SUELO_ADC_SECO     3000
#define HUM_SUELO_ADC_MOJADO   1300

// -------------------------------------------------------------------------------------
//  5. POTENCIÓMETRO (perilla) · como no hay sensor de luz, la perilla hace de sensor
// -------------------------------------------------------------------------------------
#define ROL_NINGUNO    0   // no hay potenciómetro (o no se usa)
#define ROL_LUZ        1   // la perilla simula la luz: de 0 a POT_LUZ_MAXIMA_LUX
#define ROL_HUMEDAD    2   // la perilla simula la humedad (0-100 %): girarla "riega" la planta

#define POT_ROL            ROL_LUZ
#define POT_PIN            35        // pin ADC1 (32, 33, 34, 35, 36 o 39)
#define POT_INVERTIR       0         // pon 1 si al girar a la derecha el valor baja

// Calibración del recorrido del potenciómetro (valores crudos del ADC)
#define POT_ADC_MIN        0
#define POT_ADC_MAX        4095

// Con ROL_LUZ: luz en lux cuando la perilla está al máximo (rangos de las especies: ~150 a 5000)
#define POT_LUZ_MAXIMA_LUX 3000.0f

// Si la perilla NO es la luz, el backend igual exige un valor de luz: se manda este fijo.
#define LUZ_FIJA_LUX       800.0f

// -------------------------------------------------------------------------------------
//  6. COMPORTAMIENTO
// -------------------------------------------------------------------------------------
#define INTERVALO_LECTURA_MS   10000   // cada cuánto se mide y se envía (10 s)
#define CAMBIO_PANTALLA_MS     4000    // cada cuánto alterna Gotchi <-> lecturas en la OLED

#define BOTON_RESET_PIN        0       // botón BOOT de la placa
#define BOTON_RESET_MS         5000    // mantenerlo 5 s = borrar WiFi y vinculación (restablecer)

// Nombre de la red WiFi que crea el ESP32 para configurarlo (portal cautivo)
#define PORTAL_NOMBRE_AP       "MateraGotchi-Setup"
