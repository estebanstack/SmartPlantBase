#include "red.h"
#include "config_pines.h"
#include "pantalla.h"
#include <WiFi.h>
#include <WiFiManager.h>
#include <ESPmDNS.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include <sys/time.h>

static const char* NOMBRE_MDNS = "matera-gotchi";

// --- WiFi -----------------------------------------------------------------------------

static String limpiarServidor(String s) {
    s.trim();
    s.replace("http://", "");
    s.replace("https://", "");
    while (s.endsWith("/")) s.remove(s.length() - 1);
    return s;
}

bool redConectarWiFi(String& servidor) {
    WiFiManager wm;
    WiFiManagerParameter campoServidor("servidor", "Servidor (equipo:puerto)", servidor.c_str(), 60);
    wm.addParameter(&campoServidor);
    wm.setAPCallback([](WiFiManager*) {
        pantallaTexto("Configura el WiFi:", "1. Conecta el celular", "   a la red", "   " PORTAL_NOMBRE_AP,
                      "2. Se abre sola o", "   ve a 192.168.4.1");
    });
    wm.setConnectTimeout(20);
    wm.setConfigPortalTimeout(300);

    pantallaTexto("Conectando al WiFi...");
    if (!wm.autoConnect(PORTAL_NOMBRE_AP)) return false;

    // Si no se abrió el portal, el campo conserva el valor que le dimos y nada cambia
    String nuevo = limpiarServidor(campoServidor.getValue());
    if (nuevo.length()) servidor = nuevo;
    Serial.printf("[WiFi] conectado, IP %s, servidor %s\n", WiFi.localIP().toString().c_str(), servidor.c_str());
    return true;
}

// --- Servidor -------------------------------------------------------------------------

bool redResolverServidor(const String& servidor, String& urlBase, String& ipTexto, uint16_t& puerto) {
    String host = servidor;
    puerto = 5000;
    int dosPuntos = servidor.lastIndexOf(':');
    if (dosPuntos > 0) {
        host = servidor.substring(0, dosPuntos);
        puerto = servidor.substring(dosPuntos + 1).toInt();
    }
    if (host.length() == 0 || puerto == 0) return false;

    IPAddress ip;
    if (!ip.fromString(host)) {                       // no es una IP: hay que resolver el nombre
        if (host.endsWith(".local")) {
            static bool mdnsListo = false;
            if (!mdnsListo) mdnsListo = MDNS.begin(NOMBRE_MDNS);
            String nombre = host.substring(0, host.length() - 6);
            for (int intento = 0; intento < 3 && ip == IPAddress(); intento++)
                ip = MDNS.queryHost(nombre.c_str(), 2000);
        } else {
            WiFi.hostByName(host.c_str(), ip);
        }
    }
    if (ip == IPAddress()) {
        Serial.printf("[Red] no pude resolver '%s'\n", host.c_str());
        return false;
    }
    ipTexto = ip.toString();
    urlBase = "http://" + ipTexto + ":" + String(puerto);
    return true;
}

// --- Hora -----------------------------------------------------------------------------

bool redHoraValida() {
    return time(nullptr) > 1700000000;   // cualquier fecha posterior a nov. 2023 sirve
}

// Plan B si el hotspot no tiene internet: la hora sale de la cabecera Date del propio servidor
static bool horaDesdeServidor(const String& urlBase) {
    HTTPClient http;
    WiFiClient cliente;
    const char* cabeceras[] = {"Date"};
    http.begin(cliente, urlBase + "/api/v1/especies");
    http.setTimeout(5000);
    http.collectHeaders(cabeceras, 1);
    int codigo = http.GET();
    String fecha = http.header("Date");              // ej. "Mon, 23 Nov 2026 15:00:00 GMT"
    http.end();
    if (codigo != 200 || fecha.length() == 0) return false;

    struct tm t = {};
    if (!strptime(fecha.c_str(), "%a, %d %b %Y %H:%M:%S GMT", &t)) return false;
    setenv("TZ", "UTC0", 1);      // con la zona en UTC, mktime() devuelve la hora UTC tal cual
    tzset();
    struct timeval ahora = {mktime(&t), 0};
    settimeofday(&ahora, nullptr);
    Serial.printf("[Hora] tomada del servidor: %s\n", fecha.c_str());
    return true;
}

bool redSincronizarHora(const String& urlBase) {
    configTime(0, 0, "pool.ntp.org", "time.google.com");
    for (int i = 0; i < 20 && !redHoraValida(); i++) delay(500);   // hasta 10 s
    if (redHoraValida()) {
        Serial.println("[Hora] sincronizada por NTP");
        return true;
    }
    return horaDesdeServidor(urlBase) && redHoraValida();
}

String redMarcaTiempo() {
    time_t ahora = time(nullptr);
    struct tm t;
    gmtime_r(&ahora, &t);
    char texto[24];
    strftime(texto, sizeof(texto), "%Y-%m-%dT%H:%M:%SZ", &t);
    return String(texto);
}

// --- Backend --------------------------------------------------------------------------

bool apiCrearSesionQR(const String& urlBase, const char* sesionId, const char* dispositivoId) {
    JsonDocument doc;
    doc["session_id"] = sesionId;
    doc["dispositivo_id"] = dispositivoId;
    String cuerpo;
    serializeJson(doc, cuerpo);

    HTTPClient http;
    WiFiClient cliente;
    http.begin(cliente, urlBase + "/api/auth/qr/generar");
    http.setTimeout(6000);
    http.addHeader("Content-Type", "application/json");
    int codigo = http.POST(cuerpo);
    http.end();
    Serial.printf("[API] crear sesión QR -> %d\n", codigo);
    return codigo == 201;
}

EstadoSesion apiConsultarSesion(const String& urlBase, const char* sesionId, String& token) {
    HTTPClient http;
    WiFiClient cliente;
    http.begin(cliente, urlBase + "/api/auth/qr/" + sesionId);
    http.setTimeout(6000);
    int codigo = http.GET();
    if (codigo == 404) { http.end(); return SESION_EXPIRADA; }   // el servidor se reinició y la olvidó
    if (codigo != 200) { http.end(); return SESION_SIN_RED; }

    JsonDocument filtro;
    filtro["estado"] = true;
    filtro["token"] = true;
    JsonDocument doc;
    DeserializationError error = deserializeJson(doc, http.getString(), DeserializationOption::Filter(filtro));
    http.end();
    if (error) return SESION_SIN_RED;

    String estado = doc["estado"] | "";
    if (estado == "AUTORIZADA") {
        token = doc["token"] | "";
        return token.length() ? SESION_AUTORIZADA : SESION_PENDIENTE;
    }
    return estado == "EXPIRADA" ? SESION_EXPIRADA : SESION_PENDIENTE;
}

int apiEnviarLectura(const String& urlBase, const char* dispositivoId, const String& token,
                     const Lecturas& lectura, const String& marcaTiempo, Gotchi& gotchi) {
    JsonDocument doc;
    doc["dispositivo_id"] = dispositivoId;
    doc["humedad"] = lectura.humedad;
    doc["luz"] = lectura.luz;
    doc["temperatura"] = lectura.temperatura;
    doc["marca_tiempo"] = marcaTiempo;
    String cuerpo;
    serializeJson(doc, cuerpo);

    HTTPClient http;
    WiFiClient cliente;
    http.begin(cliente, urlBase + "/api/dispositivos/" + dispositivoId + "/lecturas");
    http.setTimeout(6000);
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", "Bearer " + token);
    int codigo = http.POST(cuerpo);

    if (codigo == 201) {
        // Solo interesa el campo "gotchi": el filtro evita cargar todo el diagnóstico en RAM
        JsonDocument filtro;
        filtro["gotchi"] = true;
        JsonDocument respuesta;
        if (!deserializeJson(respuesta, http.getString(), DeserializationOption::Filter(filtro))
            && !respuesta["gotchi"].isNull()) {
            JsonObject g = respuesta["gotchi"];
            strlcpy(gotchi.estado, g["estado"] | "", sizeof(gotchi.estado));
            strlcpy(gotchi.cara, g["cara"] | "(^_^)", sizeof(gotchi.cara));
            strlcpy(gotchi.mensaje, g["mensaje"] | "", sizeof(gotchi.mensaje));
            gotchi.nivel = g["nivel"] | 1;
            gotchi.xp = g["xp"] | 0;
            gotchi.valido = true;
        }
    } else if (codigo > 0) {
        Serial.printf("[API] lectura rechazada %d: %s\n", codigo, http.getString().c_str());
    }
    http.end();
    return codigo;
}
