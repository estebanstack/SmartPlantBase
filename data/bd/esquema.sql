-- Esquema de la base de datos de SmartPlantBase (SQLite).
-- Se puede ejecutar varias veces: solo crea lo que no existe.

-- Tabla de referencia de especies (alternativa al CSV, R4)
CREATE TABLE IF NOT EXISTS especies (
    nombre      TEXT PRIMARY KEY,
    humedad_min REAL NOT NULL,
    humedad_max REAL NOT NULL,
    luz_min     REAL NOT NULL,
    luz_max     REAL NOT NULL,
    temp_min    REAL NOT NULL,
    temp_max    REAL NOT NULL
);

-- Usuarios (R7). La contraseña se guarda solo como hash.
CREATE TABLE IF NOT EXISTS usuarios (
    id            TEXT PRIMARY KEY,
    nombre        TEXT NOT NULL,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- Plantas: cada una es de un usuario y tiene un dispositivo único (R7)
CREATE TABLE IF NOT EXISTS plantas (
    id             TEXT PRIMARY KEY,
    nombre         TEXT NOT NULL,
    especie        TEXT NOT NULL,
    usuario_id     TEXT NOT NULL REFERENCES usuarios(id),
    dispositivo_id TEXT UNIQUE NOT NULL
);

-- Historial de lecturas (R5).
-- Los valores medidos van en una sola columna JSON ({"humedad": 30.0, "luz": 500.0, ...}),
-- así agregar un parámetro nuevo (por ejemplo pH) no obliga a cambiar esta tabla.
CREATE TABLE IF NOT EXISTS historial_lecturas (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    planta_id      TEXT NOT NULL REFERENCES plantas(id),
    dispositivo_id TEXT,
    especie        TEXT NOT NULL,
    valores        TEXT NOT NULL,
    estado_planta  TEXT NOT NULL,
    marca_tiempo   TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_historial_planta ON historial_lecturas (planta_id, id);
CREATE INDEX IF NOT EXISTS idx_historial_planta_marca ON historial_lecturas (planta_id, marca_tiempo);

-- Matera-Gotchi: perfil de gamificación de cada planta (XP, racha y último estado de ánimo).
-- El nivel no se guarda: se calcula desde la XP. Como todo el script, se puede repetir sin problema
-- (IF NOT EXISTS), así una base ya creada recibe la tabla al arrancar la app.
CREATE TABLE IF NOT EXISTS gamificacion (
    planta_id            TEXT PRIMARY KEY REFERENCES plantas(id),
    xp_total             INTEGER NOT NULL DEFAULT 0,
    racha_dias           INTEGER NOT NULL DEFAULT 0,
    racha_desde          TEXT,
    ultimo_animo         TEXT NOT NULL DEFAULT 'CONTENTA',
    ultima_actualizacion TEXT NOT NULL DEFAULT ''
);
