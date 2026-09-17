**Matera Inteligente — Sistema de Diagnóstico de Plantas (Base del Núcleo)**  
Sistema de diagnóstico del estado de salud de plantas basado en mediciones ambientales (humedad del sustrato en %, nivel de iluminación en lux y temperatura ambiental en °C). Desarrollado bajo los principios de **Clean Architecture**, principios  **SOLID**, desacoplamiento estricto del dominio (RA1–RA8) y un frontend web asíncrono sin recargas.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSPBCj7fFwtCmJHAjAU2QtIq6DIzW7UHAMBfnGt1V8fHEQAA3rsexOkF3va0dq8AAAAASUVORK5CYII=)  
**1. Requisitos Previos**  
- **Python 3.10+** (probado y verificado en Python 3.14).  
- Gestor de paquetes pip y entorno virtual venv.  
- Navegador web moderno con soporte para JavaScript Fetch API.  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCUpfD6ZYGZDAgAU2QtIq6DIzW7UHAMBfHGt1V+fXEwAAXrseHCoGAe/SKtAAAAAASUVORK5CYII=)  
**2. Instalación del Entorno**  
1. Clonar el repositorio y ubicarse en la raíz del proyecto:  
2. git clone <URL_DEL_REPOSITORIO>  
 cd SmartPlantBase  
   
3. Crear y activar el entorno virtual de Python:  
4. python3 -m venv venv  
 source venv/bin/activate  
   
5. Instalar dependencias de producción y pruebas:  
6. pip install -r requirements.txt  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNhwgJe0PYTKpnRgQU2QtIq6DIze3UGAMBf3Gu1VcfXEwAAXrseaIEEMYtKmi4AAAAASUVORK5CYII=)  
**3. Ejecución de Pruebas Unitarias del Dominio (RA4)**  
Las pruebas unitarias del dominio son la evidencia ejecutable del desacoplamiento total (**RA4**). Se ejecutan de forma 100% aislada:  **sin levantar el servidor web y sin leer archivos ni bases de datos reales** (utilizando dobles de prueba / fakes de la abstracción de repositorio):  
# Ejecutar únicamente las pruebas del dominio puro:  
 pytest tests/test_domain_rules.py -v  
   
 # O ejecutar toda la suite de pruebas (dominio, aplicación, infraestructura y API REST):  
 pytest tests/ -v  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANklEQVR4nO3OQQmAABRAsSeYxZw/lVeDGMACBrCCNxG2BFtmZquOAAD4i3Ot7mr/egIAwGvXA6fOBdd+dKAKAAAAAElFTkSuQmCC)  
**4. Ejecución del Sistema Completo**  
El backend y el frontend están completamente desacoplados y se ejecutan como servicios independientes (**RA1**,  **RA2**,  **RA7**).  
**Paso 1: Levantar el Backend (API REST en Flask)**  
En una primera terminal, con el entorno virtual activado:  
python app.py  
   
El backend iniciará en: http://127.0.0.1:5000  
- GET  /api/v1/especies : Catálogo de especies y rangos óptimos.  
- POST /api/v1/diagnosticos : Endpoint de evaluación de diagnóstico.  
**Paso 2: Servir el Frontend (Cliente Web Estático Desacoplado)**  
En una segunda terminal, sirva la carpeta frontend/ mediante cualquier servidor HTTP estático (por ejemplo, el módulo estándar de Python):  
python3 -m http.server 8000 --directory frontend/  
   
Abra su navegador en: http://localhost:8000  
***Nota sobre CORS (RA7):*** * La API de Flask tiene configurado CORS (* *flask-cors* *) para autorizar las solicitudes asíncronas originadas desde * *http://localhost:8000* * hacia * *http://127.0.0.1:5000* *.*  
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OQQmAABRAsSd4NIGBzPXBmAawhhW8ibAl2DIze3UGAMBf3Gu1VcfXEwAAXrsehaQEN+8fLHEAAAAASUVORK5CYII=)  
**5. Endpoints Principales de la API (Anexo A)**  
GET /api/v1/especies  
Devuelve la lista de especies botánicas soportadas con sus rangos de referencia.  
   
 **Respuesta 200 OK:**  
[  
   {  
     "nombre": "sansevieria",  
     "rangos": {  
       "humedad": { "min": 20.0, "max": 45.0, "unidad": "%" },  
       "luz": { "min": 200.0, "max": 1500.0, "unidad": "lux" },  
       "temperatura": { "min": 15.0, "max": 29.0, "unidad": "°C" }  
     }  
   }  
 ]  
   
POST /api/v1/diagnosticos  
Evalúa una medición y devuelve el diagnóstico con recomendaciones.  
   
 **Cuerpo de la Petición:**  
{  
   "especie": "sansevieria",  
   "humedad": 32.5,  
   "luz": 850,  
   "temperatura": 21.0  
 }  
   
**Respuesta 200 OK:**  
{  
   "especie": "sansevieria",  
   "estado": "SALUDABLE",  
   "parametros": [  
     { "nombre": "humedad", "valor": 32.5, "unidad": "%", "rangoOptimo": [20.0, 45.0], "estado": "OPTIMO" },  
     { "nombre": "luz", "valor": 850.0, "unidad": "lux", "rangoOptimo": [200.0, 1500.0], "estado": "OPTIMO" },  
     { "nombre": "temperatura", "valor": 21.0, "unidad": "°C", "rangoOptimo": [15.0, 29.0], "estado": "OPTIMO" }  
   ],  
   "recomendaciones": []  
 }  
   
**Respuesta 400 BAD REQUEST (RF6):**  
{  
   "error": "PARAMETRO_INVALIDO",  
   "mensaje": "Humedad de -5.0% está fuera del rango físicamente posible (0.0% - 100.0%).",  
   "detalle": { "campo": "humedad" }  
 }  
   
**Respuesta 404 NOT FOUND (RF6):**  
{  
   "error": "ESPECIE_NO_SOPORTADA",  
   "mensaje": "La especie 'bonsai' no está registrada en el catálogo de referencia.",  
   "detalle": { "especie": "bonsai" }  
 }  
   
![](data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAnEAAAACCAYAAAA3pIp+AAAABmJLR0QA/wD/AP+gvaeTAAAACXBIWXMAAA7EAAAOxAGVKw4bAAAANUlEQVR4nO3OMQ2AABAAsSNBCkLfE07YGfHAiAU2QtIq6DIzW7UHAMBfnGt1V8fXEwAAXrse4eQF6VhvmPsAAAAASUVORK5CYII=)  
**6. Documentación Adicional**  
- [Documento de Arquitectura: Diagrama de componentes, diagrama de secuencia, tabla de responsabilidades, justificación SOLID y plan de evolución.](docs/documento_arquitectura.md "docs/documento_arquitectura.md")  
- [Bitácora de Uso de IA: Relato del trabajo interactivo con asistentes de inteligencia artificial.](docs/bitacora_ia.md "docs/bitacora_ia.md")  
