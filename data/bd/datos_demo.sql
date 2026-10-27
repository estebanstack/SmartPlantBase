-- Datos de DEMOSTRACIÓN para la sustentación. No son parte del sistema real:
-- solo se cargan si CARGAR_DATOS_DEMO=1 (ver .env.example).
-- Ana y Carlos tienen la contraseña "clave123" (aquí va solo su hash, generado con werkzeug).
INSERT OR IGNORE INTO usuarios (id, nombre, email, password_hash) VALUES
    ('usr-ana',    'Ana María',   'ana@matera.edu.co',    'scrypt:32768:8:1$we3B8xAiMqwwecTc$3f34cf8c6f5605523fd9de8e55fdf3af49612a7a6b4a25516e4007ab03a7bf6404a5776627a9f8462dea944cead802c2ce5a2113e779290ef5f5b476e367ecba'),
    ('usr-carlos', 'Carlos Ruiz', 'carlos@matera.edu.co', 'scrypt:32768:8:1$7zR80J03tILqwZR1$0bcea71bc367fd831d1d2e0ade88df043d7fac1affc8532c5dc42ef6035a8316b5afc0a46a90a509f18edd427ca72c60daa9e285f82f809ded214cb3bb4b02a7');

INSERT OR IGNORE INTO plantas (id, nombre, especie, usuario_id, dispositivo_id) VALUES
    ('planta-01', 'Sansevieria de Sala', 'sansevieria', 'usr-ana',    'esp32-01'),
    ('planta-02', 'Helecho de Balcón',   'helecho',     'usr-carlos', 'esp32-02');
