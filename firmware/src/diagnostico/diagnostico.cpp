// Firmware de diagnóstico: sirve para descubrir qué hay conectado y en qué pin, sin tocar el
// firmware principal. Todo sale por el puerto serie a 115200 (pio device monitor).
//
//   1. Escanea el bus I2C buscando la pantalla OLED (suele aparecer como 0x3C).
//   2. Prueba DHT11 y DHT22 en los pines más comunes.
//   3. Cada segundo imprime el valor (0-4095) de todos los pines ADC1: gira el potenciómetro o
//      moja la sonda y mira qué GPIO cambia.
//
// Pulsa el botón BOOT para repetir el escaneo I2C y la búsqueda de DHT.
#include <Arduino.h>
#include <Wire.h>
#include <DHT.h>
#include "config_pines.h"

static const int PINES_DHT[] = {2, 4, 5, 12, 13, 14, 15, 16, 17, 18, 19, 23, 25, 26, 27, 32, 33};
// ADC1: los únicos analógicos que funcionan con WiFi
static const int PINES_ADC1[] = {32, 33, 34, 35, 36, 39};

// Prueba TODAS las parejas de pines (SDA, SCL) entre los GPIO usables, buscando la OLED en 0x3C/0x3D.
static const int PINES_I2C[] = {2, 4, 5, 13, 14, 15, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33};

static void escanearI2C() {
    Serial.println("\n=== Escaneo I2C (todas las parejas de pines) ===");
    int sdaConRespuesta = 0;
    for (int sda : PINES_I2C) {
        Serial.printf("  SDA=GPIO%d...\n", sda); Serial.flush();
        int aciertos = 0;                       // con cuántos SCL distintos "contesta" esta SDA
        int primerScl = -1; uint8_t primeraDir = 0;
        for (int scl : PINES_I2C) {
            if (sda == scl) continue;
            pinMode(sda, INPUT_PULLUP); pinMode(scl, INPUT_PULLUP); delay(1);
            if (!digitalRead(sda) || !digitalRead(scl)) continue;   // línea en bajo: no es I2C libre
            if (!Wire.begin(sda, scl, 100000)) continue;
            Wire.setTimeOut(20);
            for (uint8_t dir : {(uint8_t)0x3C, (uint8_t)0x3D}) {
                Wire.beginTransmission(dir);
                unsigned long t0 = millis();
                uint8_t r = Wire.endTransmission();
                if (millis() - t0 > 500) Serial.printf("    (SDA=%d SCL=%d 0x%02X: timeout, algo hay en esos pines)\n", sda, scl, dir);
                if (r == 0) {
                    aciertos++;
                    if (primerScl < 0) { primerScl = scl; primeraDir = dir; }
                }
            }
            Wire.end();
        }
        if (aciertos == 0) continue;
        if (aciertos > 2) {
            // Un I2C real solo contesta con SU pin SCL. Si contesta con muchos, la línea SDA está
            // pegada a bajo y el "ACK" es falso.
            Serial.printf("  AVISO: GPIO%d contesta con %d combinaciones de SCL: falso positivo. La línea SDA está retenida en bajo: la OLED probablemente no tiene alimentación (VCC/GND) o hay un cable flojo.\n", sda, aciertos);
        } else {
            Serial.printf("  OLED en 0x%02X con SDA=GPIO%d y SCL=GPIO%d\n", primeraDir, sda, primerScl);
            sdaConRespuesta++;
        }
    }
    if (sdaConRespuesta == 0) Serial.println("  Ninguna pareja respondió de forma creíble: revisa la alimentación (VCC a 3V3, GND) y que los cables de SDA/SCL lleguen al ESP32.");
}

static void buscarDHT() {
    // Un módulo DHT alimentado mantiene su pin "out" en alto (tiene pull-up propio):
    // con pull-down interno, el pin que siga en 1 es candidato.
    Serial.println("\n=== Pines en alto con pull-down (candidatos a DHT out) ===");
    for (int pin : PINES_DHT) {
        pinMode(pin, INPUT_PULLDOWN); delay(2);
        if (digitalRead(pin)) {
            Serial.printf("  GPIO%d en ALTO -> prueba lenta como DHT22 y DHT11\n", pin);
            for (int tipo : {DHT22, DHT11}) {
                DHT dht(pin, tipo);
                dht.begin();
                for (int i = 0; i < 3; i++) {
                    delay(2500);
                    float t = dht.readTemperature(), h = dht.readHumidity();
                    Serial.printf("    DHT%d intento %d: temp %.1f C, humedad %.1f %%\n", tipo, i + 1, t, h);
                }
            }
        }
    }
    Serial.println("\n=== Búsqueda de DHT (DHT11 y DHT22 en pines comunes) ===");
    Serial.println("  Un DHT22 da temperatura con decimales; un DHT11 la da entera (23.0, 24.0...).");
    bool encontrado = false;
    for (int pin : PINES_DHT) {
        for (int tipo : {DHT22, DHT11}) {
            DHT dht(pin, tipo);
            dht.begin();
            delay(30);
            float t = dht.readTemperature(false, true);   // force = true: no esperar los 2 s entre lecturas
            float h = dht.readHumidity(true);
            if (!isnan(t) && !isnan(h)) {
                Serial.printf("  GPIO%-2d responde como DHT%d: temperatura %.1f C, humedad %.1f %%\n", pin, tipo, t, h);
                encontrado = true;
            }
        }
    }
    if (!encontrado) Serial.println("  Ningún DHT respondió. Revisa la resistencia pull-up (4.7k a 3.3V) y la alimentación.");
}

static void escaneoCompleto() {
    escanearI2C();
    buscarDHT();
    Serial.println("\n=== Pines analógicos ADC1 (cada segundo) · gira el potenciómetro y mira cuál cambia ===");
}

void setup() {
    Serial.begin(115200);
    delay(1500);
    pinMode(0, INPUT_PULLUP);
    analogReadResolution(12);
    for (int pin : PINES_ADC1) analogSetPinAttenuation(pin, ADC_11db);
    Serial.println("\n##### DIAGNOSTICO Matera-Gotchi #####");
    Serial.println("Botón BOOT = repetir el escaneo de I2C y DHT.");
    escaneoCompleto();
}

void loop() {
    static unsigned long ultimo = 0;
    if (digitalRead(0) == LOW) {
        delay(300);
        escaneoCompleto();
    }
    if (millis() - ultimo >= 1000) {
        ultimo = millis();
        for (int pin : PINES_ADC1) Serial.printf("GPIO%-2d=%4d  ", pin, analogRead(pin));
        Serial.println();
    }
}
