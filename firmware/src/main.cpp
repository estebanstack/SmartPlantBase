// Matera-Gotchi · firmware del ESP32
//
// Flujo: splash -> WiFi (portal cautivo si no hay credenciales) -> hora -> vinculación por QR
//        (solo la primera vez) -> ciclo: leer sensores, enviar al backend, dibujar el Gotchi.
//
// Lo único que se edita para cambiar de montaje es include/config_pines.h.
#include <Arduino.h>
#include <Preferences.h>
#include <WiFi.h>
#include <WiFiManager.h>
#include "config_pines.h"
#include "tipos.h"
#include "pantalla.h"
#include "sensores.h"
#include "red.h"

// --- Estado -----------------------------------------------------------------------------
static Preferences nvs;                  // memoria no volátil: sobrevive a apagones
static String servidor;                  // "equipo:puerto" que escribió el usuario
static String urlBase;                   // http://IP:puerto (ya resuelto)
static String ipServidor;
static uint16_t puertoServidor = 5000;
static String token;                     // token de dispositivo (se pide por QR la primera vez)
static char dispositivoId[20];           // esp32-XXXXXX, sale de la MAC del chip

static Lecturas ultimaLectura;
static Gotchi ultimoGotchi;
static bool sinRed = false;
static int fallosSeguidos = 0;
static unsigned long proximaLectura = 0;
static unsigned long ultimoCambioPantalla = 0;
static bool mostrarGotchi = true;
static bool pantallaPisada = false;      // la cuenta regresiva del botón borró lo que había en la OLED

// --- Utilidades -------------------------------------------------------------------------

static void restablecerDeFabrica() {
    pantallaTexto("Restableciendo...", "Borrando WiFi y", "vinculacion");
    nvs.clear();
    WiFiManager wm;
    wm.resetSettings();
    delay(1500);
    ESP.restart();
}

// Mantener BOOT (GPIO0) BOTON_RESET_MS milisegundos = restablecer. Se llama en todas las esperas.
static void revisarBoton() {
    static unsigned long desde = 0;
    if (digitalRead(BOTON_RESET_PIN) == HIGH) {
        if (desde) { desde = 0; ultimoCambioPantalla = 0; }   // soltó el botón: se redibuja la pantalla normal
        return;
    }
    if (!desde) desde = millis();
    unsigned long mantenido = millis() - desde;
    if (mantenido >= BOTON_RESET_MS) restablecerDeFabrica();
    if (mantenido > 1000) {
        char linea[24];
        snprintf(linea, sizeof(linea), "Falta %lu s", (BOTON_RESET_MS - mantenido) / 1000 + 1);
        pantallaTexto("Mantén BOOT para", "restablecer", linea, "(suelta para", "cancelar)");
        pantallaPisada = true;
    }
}

static void esperar(unsigned long ms) {
    unsigned long inicio = millis();
    while (millis() - inicio < ms) {
        revisarBoton();
        delay(20);
    }
}

// Busca al servidor hasta encontrarlo (el portátil puede cambiar de IP entre pruebas)
static void asegurarServidor() {
    while (!redResolverServidor(servidor, urlBase, ipServidor, puertoServidor)) {
        pantallaTexto("No encuentro al", "servidor:", servidor.c_str(), "Si es .local prueba", "con la IP (BOOT 5 s", "para reconfigurar)");
        esperar(5000);
        if (WiFi.status() != WL_CONNECTED) WiFi.reconnect();
    }
    Serial.printf("[Red] servidor en %s\n", urlBase.c_str());
}

static void asegurarHora() {
    while (!redHoraValida()) {
        pantallaTexto("Ajustando la hora...");
        if (redSincronizarHora(urlBase)) break;
        pantallaTexto("No pude ajustar la", "hora (NTP ni servidor)", "Reintentando...");
        esperar(5000);
    }
}

// --- Vinculación por QR -----------------------------------------------------------------

static void vincular() {
    char sesion[13];
    char url[100] = "";
    bool sesionCreada = false;
    unsigned long ultimaConsulta = 0;

    while (true) {
        revisarBoton();
        if (WiFi.status() != WL_CONNECTED) {
            pantallaTexto("Sin WiFi", "Reconectando...");
            WiFi.reconnect();
            esperar(3000);
            continue;
        }

        if (!sesionCreada) {
            // El dispositivo crea su propia sesión: 12 hex aleatorios (48 bits) para que el QR sea pequeño
            snprintf(sesion, sizeof(sesion), "%08x%04x", (unsigned)esp_random(), (unsigned)(esp_random() & 0xFFFF));
            if (!apiCrearSesionQR(urlBase, sesion, dispositivoId)) {
                pantallaTexto("No pude crear la", "sesion de vinculacion", "Reintentando...");
                esperar(3000);
                asegurarServidor();
                continue;
            }
            snprintf(url, sizeof(url), "http://%s:%u/?vincular=%s", ipServidor.c_str(), puertoServidor, sesion);
            Serial.printf("[QR] %s\n", url);
            if (!pantallaQR(url)) pantallaCodigoTexto(url);
            sesionCreada = true;
        } else if (pantallaPisada && digitalRead(BOTON_RESET_PIN) == HIGH) {
            pantallaPisada = false;                 // soltó el botón: se vuelve a dibujar el QR
            if (!pantallaQR(url)) pantallaCodigoTexto(url);
        }

        if (millis() - ultimaConsulta >= 2000) {
            ultimaConsulta = millis();
            String nuevoToken;
            switch (apiConsultarSesion(urlBase, sesion, nuevoToken)) {
                case SESION_AUTORIZADA:
                    token = nuevoToken;
                    nvs.putString("token", token);
                    pantallaTexto("", "  Vinculado!", "", "  Ya puedo medir");
                    esperar(2000);
                    return;
                case SESION_EXPIRADA:
                    sesionCreada = false;       // se pide otra sesión y se redibuja el QR
                    break;
                default:
                    break;
            }
        }
        delay(50);
    }
}

// --- Ciclo de medición ------------------------------------------------------------------

static void dibujarPantalla() {
    if (mostrarGotchi && ultimoGotchi.valido) pantallaGotchi(ultimoGotchi, sinRed);
    else pantallaLecturas(ultimaLectura, sinRed);
}

static void cicloLectura() {
    ultimaLectura = leerSensores();
    if (!ultimaLectura.ok) {
        pantallaTexto("Error de sensor:", ultimaLectura.error, "Revisa el cableado", "y config_pines.h");
        proximaLectura = millis() + INTERVALO_LECTURA_MS;
        return;
    }

    if (WiFi.status() != WL_CONNECTED) {
        sinRed = true;
        proximaLectura = millis() + 3000;
        dibujarPantalla();
        return;
    }
    if (!redHoraValida()) asegurarHora();

    int codigo = apiEnviarLectura(urlBase, dispositivoId, token, ultimaLectura, redMarcaTiempo(), ultimoGotchi);
    Serial.printf("[Lectura] hum=%.1f luz=%.0f temp=%.1f -> HTTP %d  %s %s\n",
                  ultimaLectura.humedad, ultimaLectura.luz, ultimaLectura.temperatura, codigo,
                  ultimoGotchi.estado, ultimoGotchi.cara);

    if (codigo == 201) {
        sinRed = false;
        fallosSeguidos = 0;
        proximaLectura = millis() + INTERVALO_LECTURA_MS;
    } else if (codigo == 401 || codigo == 403 || codigo == 404) {
        // Token inválido (por ejemplo el servidor cambió de clave) o planta desvinculada: a vincular otra vez
        pantallaTexto("El servidor no me", "reconoce. Vuelvo a", "vincularme...");
        token = "";
        nvs.remove("token");
        esperar(2000);
        vincular();
        proximaLectura = millis();
    } else if (codigo == 400) {
        proximaLectura = millis() + INTERVALO_LECTURA_MS;    // dato rechazado: el detalle está en el serial
    } else {
        // Sin conexión con el servidor: reintento con espera creciente (5, 10, 20, 40, 60 s)
        sinRed = true;
        fallosSeguidos++;
        unsigned long espera = min(60000UL, 5000UL << min(fallosSeguidos - 1, 4));
        proximaLectura = millis() + espera;
        Serial.printf("[Red] sin respuesta (fallo %d), reintento en %lu s\n", fallosSeguidos, espera / 1000);
        if (fallosSeguidos % 3 == 0) asegurarServidor();     // quizá cambió la IP del portátil
    }
    ultimoCambioPantalla = 0;   // redibujar con el dato nuevo
}

// --- Arranque ---------------------------------------------------------------------------

void setup() {
    Serial.begin(115200);
    delay(200);
    pinMode(BOTON_RESET_PIN, INPUT_PULLUP);

    pantallaIniciar();
    sensoresIniciar();
    pantallaSplash();

    uint8_t mac[6];
    WiFi.macAddress(mac);
    snprintf(dispositivoId, sizeof(dispositivoId), "esp32-%02X%02X%02X", mac[3], mac[4], mac[5]);
    Serial.printf("\n[Matera-Gotchi] dispositivo %s\n", dispositivoId);

    String avisos = sensoresAdvertencias();
    if (avisos.length()) {
        Serial.println("[Pines] " + avisos);
        pantallaTexto("Revisa config_pines.h", avisos.c_str());
        delay(4000);
    } else {
        delay(1200);
    }

    nvs.begin("matera", false);
    servidor = nvs.getString("servidor", SERVIDOR_POR_DEFECTO);
    token = nvs.getString("token", "");

    String servidorAnterior = servidor;
    while (!redConectarWiFi(servidor)) {      // el portal venció sin configurarse
        pantallaTexto("No se configuro el", "WiFi. Reiniciando...");
        delay(2000);
        ESP.restart();
    }
    if (servidor != servidorAnterior) nvs.putString("servidor", servidor);

    asegurarServidor();
    asegurarHora();
    if (token.length() == 0) vincular();
    proximaLectura = millis();
}

void loop() {
    revisarBoton();

    if (millis() >= proximaLectura) cicloLectura();

    // Alterna Gotchi / lecturas; ultimoCambioPantalla = 0 fuerza un redibujo inmediato
    if (ultimoCambioPantalla == 0 || millis() - ultimoCambioPantalla >= CAMBIO_PANTALLA_MS) {
        if (ultimoCambioPantalla != 0) mostrarGotchi = !mostrarGotchi;
        ultimoCambioPantalla = millis();
        if (ultimaLectura.ok) dibujarPantalla();
    }
    delay(20);
}
