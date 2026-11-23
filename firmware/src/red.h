// WiFi (portal cautivo), búsqueda del servidor, hora y llamadas HTTP al backend
#pragma once
#include <Arduino.h>
#include <IPAddress.h>
#include "tipos.h"

// --- WiFi -----------------------------------------------------------------------------
// Conecta con las credenciales guardadas; si no hay (o fallan) abre el portal "MateraGotchi-Setup"
// con un campo extra para el servidor. `servidor` entra con el valor actual y sale con el que
// escribió el usuario. Devuelve false si se acabó el tiempo del portal sin configurarse.
bool redConectarWiFi(String& servidor);

// --- Servidor -------------------------------------------------------------------------
// Convierte "equipo:puerto" (o "equipo", o una IP) en la URL base http://IP:puerto.
// Los nombres .local se resuelven con mDNS. Devuelve false si no lo encuentra.
bool redResolverServidor(const String& servidor, String& urlBase, String& ipTexto, uint16_t& puerto);

// --- Hora -----------------------------------------------------------------------------
bool redHoraValida();
bool redSincronizarHora(const String& urlBase);   // NTP y, si no hay internet, la cabecera Date del servidor
String redMarcaTiempo();                          // ISO-8601 en UTC: 2026-11-23T15:00:00Z

// --- Backend --------------------------------------------------------------------------
enum EstadoSesion { SESION_PENDIENTE, SESION_AUTORIZADA, SESION_EXPIRADA, SESION_SIN_RED };

// POST /api/auth/qr/generar. El id de sesión lo elige el dispositivo (12 hex aleatorios).
bool apiCrearSesionQR(const String& urlBase, const char* sesionId, const char* dispositivoId);
// GET /api/auth/qr/<id>. Si ya está autorizada, `token` trae el token del dispositivo.
EstadoSesion apiConsultarSesion(const String& urlBase, const char* sesionId, String& token);
// POST /api/dispositivos/<id>/lecturas. Devuelve el código HTTP (negativo si no hubo conexión)
// y rellena `gotchi` cuando la respuesta lo trae.
int apiEnviarLectura(const String& urlBase, const char* dispositivoId, const String& token,
                     const Lecturas& lectura, const String& marcaTiempo, Gotchi& gotchi);
