#include "pantalla.h"
#include "config_pines.h"
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <qrcode.h>

// Dos chips posibles: SSD1306 (OLED 0.96", pines GND VCC SCL SDA) o SH1106 (OLED 1.3", pines VDD GND SCK SDA)
#if OLED_CONTROLADOR == OLED_SH1106
#include <Adafruit_SH110X.h>
static Adafruit_SH1106G oled(OLED_ANCHO, OLED_ALTO, &Wire, -1);
#define COLOR_BLANCO SH110X_WHITE
#define COLOR_NEGRO  SH110X_BLACK
#else
#include <Adafruit_SSD1306.h>
static Adafruit_SSD1306 oled(OLED_ANCHO, OLED_ALTO, &Wire, -1);
#define COLOR_BLANCO SSD1306_WHITE
#define COLOR_NEGRO  SSD1306_BLACK
#endif
static bool hayOled = false;

bool pantallaIniciar() {
    Wire.begin(OLED_SDA, OLED_SCL);
    // Antes de iniciar la librería, comprueba que algo conteste en el bus: con la OLED mal
    // conectada o sin alimentación, oled.begin() puede colgar el arranque (pasó con el SH1106).
    Wire.setTimeOut(20);
    Wire.beginTransmission(OLED_DIRECCION);
    bool contesta = (Wire.endTransmission() == 0);
    hayOled = false;
    if (contesta) {
#if OLED_CONTROLADOR == OLED_SH1106
        hayOled = oled.begin(OLED_DIRECCION, true);
#else
        hayOled = oled.begin(SSD1306_SWITCHCAPVCC, OLED_DIRECCION);
#endif
    }
    if (!hayOled) {
        Serial.printf("[OLED] no responde en 0x%02X (SDA=%d, SCL=%d). Sigo solo por serie.\n",
                      OLED_DIRECCION, OLED_SDA, OLED_SCL);
        return false;
    }
    oled.setTextColor(COLOR_BLANCO);
    oled.cp437(true);
    oled.clearDisplay();
    oled.display();
    return true;
}

String aAscii(const char* utf8) {
    String salida;
    for (const uint8_t* p = (const uint8_t*)utf8; *p; p++) {
        if (*p < 0x80) { salida += (char)*p; continue; }
        if (*p == 0xC3 && p[1]) {                 // letras latinas con tilde: á é í ó ú ü ñ ...
            p++;
            switch (*p) {
                case 0xA1: case 0xA0: case 0x81: salida += 'a'; break;
                case 0xA9: case 0x89: salida += 'e'; break;
                case 0xAD: case 0x8D: salida += 'i'; break;
                case 0xB3: case 0x93: salida += 'o'; break;
                case 0xBA: case 0xBC: case 0x9A: salida += 'u'; break;
                case 0xB1: case 0x91: salida += 'n'; break;
                default: break;
            }
        } else if (*p == 0xC2 && p[1]) {          // ¡ y ¿
            p++;
            if (*p == 0xA1) salida += '!';
            else if (*p == 0xBF) salida += '?';
        } else {                                   // emojis y otros: se saltan sus bytes de continuación
            while (p[1] && (p[1] & 0xC0) == 0x80) p++;
        }
    }
    return salida;
}

// Parte `texto` en líneas de hasta `ancho` caracteres sin cortar palabras (si una palabra no cabe, la corta)
static int ajustarLineas(const String& texto, int ancho, String* lineas, int maxLineas) {
    int n = 0;
    String actual;
    int inicio = 0;
    while (inicio <= (int)texto.length() && n < maxLineas) {
        int fin = texto.indexOf(' ', inicio);
        if (fin < 0) fin = texto.length();
        String palabra = texto.substring(inicio, fin);
        inicio = fin + 1;
        while ((int)palabra.length() > ancho) {   // palabra más larga que la línea
            if (actual.length()) { lineas[n++] = actual; actual = ""; if (n >= maxLineas) return n; }
            lineas[n++] = palabra.substring(0, ancho);
            palabra = palabra.substring(ancho);
            if (n >= maxLineas) return n;
        }
        if (actual.length() == 0) actual = palabra;
        else if ((int)(actual.length() + 1 + palabra.length()) <= ancho) actual += " " + palabra;
        else { lineas[n++] = actual; actual = palabra; }
    }
    if (actual.length() && n < maxLineas) lineas[n++] = actual;
    return n;
}

static void marcaSinRed() {   // pequeña "X" arriba a la derecha
    oled.drawLine(120, 0, 126, 6, COLOR_BLANCO);
    oled.drawLine(126, 0, 120, 6, COLOR_BLANCO);
}

void pantallaSplash() {
    if (!hayOled) return;
    oled.clearDisplay();
    oled.setTextSize(1);
    oled.setCursor(22, 6);
    oled.print("MATERA-GOTCHI");
    oled.setTextSize(3);
    oled.setCursor(10, 26);
    oled.print("(^_^)");
    oled.display();
}

void pantallaTexto(const char* l1, const char* l2, const char* l3,
                   const char* l4, const char* l5, const char* l6) {
    const char* lineas[] = {l1, l2, l3, l4, l5, l6};
    for (const char* l : lineas) if (*l) Serial.printf("[OLED] %s\n", l);
    if (!hayOled) return;
    oled.clearDisplay();
    oled.setTextSize(1);
    for (int i = 0; i < 6; i++) {
        oled.setCursor(0, i * 10 + 2);
        oled.print(aAscii(lineas[i]));
    }
    oled.display();
}

bool pantallaQR(const char* url) {
    // Versión 3 (29x29 módulos, hasta 53 bytes con corrección baja): a 2 píxeles por módulo mide
    // 58 px y cabe en los 64 px de alto. La URL con IP (http://192.168.x.x:5000/?vincular=<12>) entra.
    const uint8_t version = 3;
    QRCode qr;
    uint8_t datos[qrcode_getBufferSize(version)];
    if (qrcode_initText(&qr, datos, version, ECC_LOW, url) != 0) return false;
    if (!hayOled) return true;

    oled.clearDisplay();
    oled.setTextSize(1);
    oled.setCursor(0, 4);  oled.print("Escanea");
    oled.setCursor(0, 14); oled.print("el QR con");
    oled.setCursor(0, 24); oled.print("tu celular");
    oled.setCursor(0, 44); oled.print("e inicia");
    oled.setCursor(0, 54); oled.print("sesion");

    // Fondo blanco (zona tranquila) y módulos oscuros, como en un QR impreso
    oled.fillRect(64, 0, 64, 64, COLOR_BLANCO);
    const int escala = 2;
    const int origenX = 64 + (64 - qr.size * escala) / 2;
    const int origenY = (64 - qr.size * escala) / 2;
    for (uint8_t y = 0; y < qr.size; y++)
        for (uint8_t x = 0; x < qr.size; x++)
            if (qrcode_getModule(&qr, x, y))
                oled.fillRect(origenX + x * escala, origenY + y * escala, escala, escala, COLOR_NEGRO);
    oled.display();
    return true;
}

void pantallaCodigoTexto(const char* url) {
    Serial.printf("[OLED] QR no cabe. URL: %s\n", url);
    if (!hayOled) return;
    oled.clearDisplay();
    oled.setTextSize(1);
    oled.setCursor(0, 0);
    oled.print("Abre en el celular:");
    oled.setCursor(0, 12);
    oled.print(url);      // el texto se parte solo en varias líneas
    oled.display();
}

void pantallaGotchi(const Gotchi& g, bool sinRed) {
    if (!hayOled) return;
    oled.clearDisplay();
    oled.setTextSize(1);
    oled.setCursor(0, 0);
    oled.printf("Nv%d %dXP", g.nivel, g.xp);
    oled.setCursor(66, 0);
    oled.print(g.estado);

    // Cara centrada (tamaño 2: 12 px por carácter)
    oled.setTextSize(2);
    int ancho = strlen(g.cara) * 12;
    oled.setCursor((OLED_ANCHO - ancho) / 2, 11);
    oled.print(g.cara);

    // Mensaje de la planta, partido por palabras (4 líneas de 21 caracteres)
    oled.setTextSize(1);
    String lineas[4];
    int n = ajustarLineas(aAscii(g.mensaje), 21, lineas, 4);
    for (int i = 0; i < n; i++) {
        oled.setCursor(0, 32 + i * 8);
        oled.print(lineas[i]);
    }
    if (sinRed) marcaSinRed();
    oled.display();
}

void pantallaLecturas(const Lecturas& l, bool sinRed) {
    if (!hayOled) return;
    oled.clearDisplay();
    oled.setTextSize(2);
    oled.setCursor(0, 2);  oled.printf("Hum %.1f%%", l.humedad);
    oled.setCursor(0, 24); oled.printf("Luz %.0f", l.luz);
    oled.setCursor(0, 46); oled.printf("Tmp %.1fC", l.temperatura);
    if (sinRed) marcaSinRed();
    oled.display();
}
