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

struct ParI2C { int sda, scl; };
static const ParI2C PARES_I2C[] = {
    {OLED_SDA, OLED_SCL},          // lo que dice config_pines.h
    {21, 22}, {22, 21}, {5, 4}, {4, 5}, {16, 17}, {17, 16},
    {26, 25}, {25, 26}, {19, 18}, {18, 19}, {33, 32}, {32, 33}, {27, 14}, {14, 27},
};

static const int PINES_DHT[] = {4, 5, 13, 14, 15, 16, 17, 18, 19, 23, 25, 26, 27, 32, 33};
// ADC1: los únicos analógicos que funcionan con WiFi
static const int PINES_ADC1[] = {32, 33, 34, 35, 36, 39};

static void escanearI2C() {
    Serial.println("\n=== Escaneo I2C ===");
    bool encontrado = false;
    for (const ParI2C& par : PARES_I2C) {
        if (!Wire.begin(par.sda, par.scl)) continue;
        Wire.setTimeOut(20);
        for (uint8_t dir = 1; dir < 127; dir++) {
            Wire.beginTransmission(dir);
            if (Wire.endTransmission() == 0) {
                Serial.printf("  Dispositivo en 0x%02X  (SDA=%d, SCL=%d)%s\n", dir, par.sda, par.scl,
                              (dir == 0x3C || dir == 0x3D) ? "  <- parece la OLED SSD1306" : "");
                encontrado = true;
            }
        }
        Wire.end();
    }
    if (!encontrado) Serial.println("  No encontré nada. Revisa VCC/GND/SDA/SCL de la pantalla.");
}

static void buscarDHT() {
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
