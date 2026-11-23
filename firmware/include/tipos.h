// Estructuras de datos compartidas entre los módulos del firmware.
#pragma once
#include <Arduino.h>

// Lo que miden los sensores (ya recortado a los límites físicos que acepta el backend)
struct Lecturas {
    float humedad = 0;       // %
    float luz = 0;           // lux
    float temperatura = 0;   // °C
    bool ok = false;         // false si algún sensor falló
    char error[24] = "";     // qué sensor falló (para mostrarlo en la pantalla)
};

// El campo "gotchi" de la respuesta 201 del backend
struct Gotchi {
    bool valido = false;
    char estado[14] = "";    // CONTENTA, SEDIENTA, AGRADECIDA...
    char cara[10] = "(^_^)"; // ASCII corto para la OLED
    char mensaje[100] = "";
    int nivel = 1;
    int xp = 0;
};
