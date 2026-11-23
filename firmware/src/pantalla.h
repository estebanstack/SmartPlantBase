// Dibujo en la pantalla OLED SSD1306 128x64
#pragma once
#include "tipos.h"

bool pantallaIniciar();                 // false si no encuentra la OLED (el firmware sigue por serie)
void pantallaSplash();
// Pantalla de texto simple (hasta 6 líneas de 21 caracteres)
void pantallaTexto(const char* l1, const char* l2 = "", const char* l3 = "",
                   const char* l4 = "", const char* l5 = "", const char* l6 = "");
// Dibuja el QR de `url`. Devuelve false si no cabe (entonces se usa pantallaCodigoTexto).
bool pantallaQR(const char* url);
void pantallaCodigoTexto(const char* url);
void pantallaGotchi(const Gotchi& g, bool sinRed);
void pantallaLecturas(const Lecturas& l, bool sinRed);

// La fuente de la OLED solo tiene ASCII: quita tildes y signos de apertura (á -> a, ¡ -> !)
String aAscii(const char* utf8);
