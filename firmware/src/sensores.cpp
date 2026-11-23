#include "sensores.h"
#include "config_pines.h"
#include <DHT.h>

#define TEMP_USA_DHT  (TEMP_TIPO == TEMP_DHT11 || TEMP_TIPO == TEMP_DHT22)
#define HUM_USA_DHT   (HUM_TIPO == HUM_DHT11 || HUM_TIPO == HUM_DHT22)
// Mismo DHT para temperatura y humedad: se declara una sola vez
#define DHT_UNICO     (TEMP_USA_DHT && HUM_USA_DHT && TEMP_PIN == HUM_PIN)

#if TEMP_USA_DHT
static DHT dhtTemperatura(TEMP_PIN, TEMP_TIPO == TEMP_DHT11 ? DHT11 : DHT22);
#endif
#if HUM_USA_DHT && !DHT_UNICO
static DHT dhtHumedad(HUM_PIN, HUM_TIPO == HUM_DHT11 ? DHT11 : DHT22);
#endif

// Los pines ADC2 no funcionan mientras el WiFi está encendido
static bool esPinAdc2(int pin) {
    const int adc2[] = {0, 2, 4, 12, 13, 14, 15, 25, 26, 27};
    for (int p : adc2) if (p == pin) return true;
    return false;
}

static bool esPinAdc1(int pin) {
    return pin == 32 || pin == 33 || pin == 34 || pin == 35 || pin == 36 || pin == 39;
}

static void prepararPinAnalogico(int pin) {
    analogSetPinAttenuation(pin, ADC_11db);   // rango completo, ~0 a 3.3 V
}

// Promedio de varias muestras para quitar el ruido del ADC del ESP32
static float adcCrudo(int pin) {
    long suma = 0;
    for (int i = 0; i < 16; i++) suma += analogRead(pin);
    return suma / 16.0f;
}

static float milivoltios(int pin) {
    long suma = 0;
    for (int i = 0; i < 16; i++) suma += analogReadMilliVolts(pin);
    return suma / 16.0f;
}

// Convierte `x` del rango [a, b] al rango [c, d] y recorta a ese rango. Sirve también si a > b.
static float mapear(float x, float a, float b, float c, float d) {
    if (a == b) return c;
    float t = (x - a) / (b - a);
    t = constrain(t, 0.0f, 1.0f);
    return c + t * (d - c);
}

void sensoresIniciar() {
    analogReadResolution(12);
#if TEMP_USA_DHT
    dhtTemperatura.begin();
#else
    prepararPinAnalogico(TEMP_PIN);
#endif
#if HUM_USA_DHT && !DHT_UNICO
    dhtHumedad.begin();
#endif
#if HUM_TIPO == HUM_SUELO
    prepararPinAnalogico(HUM_PIN);
#endif
#if POT_ROL != ROL_NINGUNO
    prepararPinAnalogico(POT_PIN);
#endif
}

String sensoresAdvertencias() {
    String texto;
    auto revisar = [&](int pin, const char* nombre) {
        if (esPinAdc2(pin)) texto += String(nombre) + " GPIO" + pin + " es ADC2: no sirve con WiFi. ";
        else if (!esPinAdc1(pin)) texto += String(nombre) + " GPIO" + pin + " no es un pin ADC1. ";
    };
#if !TEMP_USA_DHT
    revisar(TEMP_PIN, "Temp");
#endif
#if HUM_TIPO == HUM_SUELO
    revisar(HUM_PIN, "Hum");
#endif
#if POT_ROL != ROL_NINGUNO
    revisar(POT_PIN, "Pot");
#endif
    return texto;
}

static void marcarError(Lecturas& l, const char* que) {
    l.ok = false;
    strlcpy(l.error, que, sizeof(l.error));
}

Lecturas leerSensores() {
    Lecturas l;
    l.ok = true;

    // --- Temperatura ---
#if TEMP_USA_DHT
    float t = dhtTemperatura.readTemperature();
#else
    float t = (milivoltios(TEMP_PIN) - TEMP_ANALOGICO_OFFSET_MV) / TEMP_ANALOGICO_MV_POR_GRADO;
#endif
    if (isnan(t)) marcarError(l, "temperatura");
    l.temperatura = constrain(isnan(t) ? 0.0f : t, -50.0f, 80.0f);

    // --- Humedad ---
#if POT_ROL == ROL_HUMEDAD
    // La perilla manda: girarla sube o baja la humedad como si se regara
    float pot = mapear(adcCrudo(POT_PIN), POT_ADC_MIN, POT_ADC_MAX, 0, 100);
    float h = POT_INVERTIR ? 100.0f - pot : pot;
#elif HUM_USA_DHT
  #if DHT_UNICO
    float h = dhtTemperatura.readHumidity();
  #else
    float h = dhtHumedad.readHumidity();
  #endif
    if (isnan(h)) marcarError(l, "humedad");
#else
    float h = mapear(adcCrudo(HUM_PIN), HUM_SUELO_ADC_SECO, HUM_SUELO_ADC_MOJADO, 0, 100);
#endif
    l.humedad = constrain(isnan(h) ? 0.0f : h, 0.0f, 100.0f);

    // --- Luz ---
#if POT_ROL == ROL_LUZ
    float pl = mapear(adcCrudo(POT_PIN), POT_ADC_MIN, POT_ADC_MAX, 0, POT_LUZ_MAXIMA_LUX);
    float luz = POT_INVERTIR ? POT_LUZ_MAXIMA_LUX - pl : pl;
#else
    float luz = LUZ_FIJA_LUX;
#endif
    l.luz = constrain(luz, 0.0f, 150000.0f);

    return l;
}
