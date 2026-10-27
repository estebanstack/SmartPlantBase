-- Carga de la tabla de referencia de especies (mismos valores que data/especies_referencia.csv).
-- Son los valores del Anexo B del enunciado de la Fase 1.
INSERT OR IGNORE INTO especies (nombre, humedad_min, humedad_max, luz_min, luz_max, temp_min, temp_max) VALUES
    ('sansevieria', 20, 45,  200, 1500, 15, 29),
    ('potos',       40, 70,  300, 1200, 18, 30),
    ('suculenta',   10, 30,  800, 2500, 15, 32),
    ('helecho',     60, 85,  150,  800, 16, 26),
    ('lavanda',     25, 50, 1000, 3000, 15, 30);
