-- Script de inicialización para la base de datos del chat
CREATE DATABASE IF NOT EXISTS chat_online CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE chat_online;

-- Tabla de usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ultimo_acceso TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    rol ENUM('admin', 'moderador', 'usuario') DEFAULT 'usuario',
    activo BOOLEAN DEFAULT TRUE,
    INDEX idx_username (username),
    INDEX idx_email (email)
);

-- Tabla de salas
CREATE TABLE IF NOT EXISTS salas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion TEXT,
    creador_id INT,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    publica BOOLEAN DEFAULT TRUE,
    max_usuarios INT DEFAULT 100,
    FOREIGN KEY (creador_id) REFERENCES usuarios(id) ON DELETE SET NULL,
    INDEX idx_nombre (nombre)
);

-- Tabla de mensajes
CREATE TABLE IF NOT EXISTS mensajes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    sala_id INT,
    mensaje TEXT NOT NULL,
    fecha_envio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo ENUM('texto', 'imagen', 'archivo', 'sistema') DEFAULT 'texto',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE CASCADE,
    INDEX idx_fecha (fecha_envio),
    INDEX idx_sala (sala_id)
);

-- Tabla de usuarios en salas
CREATE TABLE IF NOT EXISTS usuarios_salas (
    usuario_id INT,
    sala_id INT,
    fecha_union TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rol_sala ENUM('admin', 'moderador', 'miembro') DEFAULT 'miembro',
    PRIMARY KEY (usuario_id, sala_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (sala_id) REFERENCES salas(id) ON DELETE CASCADE
);

-- Insertar sala general por defecto
INSERT IGNORE INTO salas (nombre, descripcion, publica) 
VALUES ('General', 'Sala principal para todos los usuarios', TRUE);

-- Insertar usuario administrador por defecto
INSERT IGNORE INTO usuarios (username, email, password_hash, rol) 
VALUES ('admin', 'admin@chat.com', MD5('admin123'), 'admin');

-- Procedimiento para limpiar mensajes antiguos (opcional)
DELIMITER //
CREATE PROCEDURE IF NOT EXISTS LimpiarMensajesAntiguos()
BEGIN
    DELETE FROM mensajes 
    WHERE fecha_envio < DATE_SUB(NOW(), INTERVAL 30 DAY);
END //
DELIMITER ;

-- Evento para ejecutar limpieza automática (opcional)
-- SET GLOBAL event_scheduler = ON;
-- CREATE EVENT IF NOT EXISTS limpiar_mensajes_evento
-- ON SCHEDULE EVERY 1 DAY
-- STARTS CURRENT_TIMESTAMP
-- DO CALL LimpiarMensajesAntiguos();

COMMIT;
