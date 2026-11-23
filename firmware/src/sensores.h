// Lectura de los sensores según lo que se declaró en include/config_pines.h
#pragma once
#include "tipos.h"

void sensoresIniciar();

// Lee temperatura, humedad y luz. Si un sensor falla, devuelve ok=false y dice cuál en `error`.
// Los valores salen recortados a los límites físicos del backend (humedad 0-100, luz 0-150000,
// temperatura -50..80): si no, el backend rechazaría la lectura completa con un 400.
Lecturas leerSensores();

// Texto con los problemas de configuración de pines (por ejemplo un pin ADC2 que no sirve con
// WiFi). Cadena vacía si todo está bien.
String sensoresAdvertencias();
