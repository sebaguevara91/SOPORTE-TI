-- ==============================================================================
-- PLATAFORMA DE REGISTRO DE VISITAS DE SOPORTE TI
-- Esquema Relacional de Base de Datos (Compatible con SQLite y PostgreSQL)
-- ==============================================================================

-- 1. TABLA: establecimientos
CREATE TABLE IF NOT EXISTS establecimientos (
    rbd INTEGER PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    comuna VARCHAR(100) NOT NULL,
    direccion VARCHAR(255),
    correo_establecimiento VARCHAR(150),
    director VARCHAR(150) NOT NULL,
    correo_director VARCHAR(150) NOT NULL,
    telefono VARCHAR(50),
    matricula INTEGER DEFAULT 0 CHECK (matricula >= 0),
    dependencia VARCHAR(50) DEFAULT 'SLEP', -- SLEP, Particular Subvencionado, Municipal
    contacto_enlaces VARCHAR(150),
    tipo_establecimiento VARCHAR(50) DEFAULT 'Escuela', -- Liceo, Escuela, Sala Cuna
    activo INTEGER DEFAULT 1 CHECK (activo IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA: visitas
CREATE TABLE IF NOT EXISTS visitas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rbd INTEGER NOT NULL,
    tecnico_responsable VARCHAR(150) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'En Proceso', 'Realizada', 'Programada')),
    tipo_soporte VARCHAR(100) NOT NULL DEFAULT 'Soporte Correctivo',
    prioridad VARCHAR(20) NOT NULL DEFAULT 'Media' CHECK (prioridad IN ('Baja', 'Media', 'Alta', 'Urgente')),
    fecha_solicitud DATE NOT NULL,
    fecha_atencion TIMESTAMP NULL,
    fecha_programada DATE NULL, -- Retrocompatibilidad
    fecha_realizada TIMESTAMP NULL, -- Retrocompatibilidad
    motivo TEXT NOT NULL,
    detalle_hardware TEXT, -- JSON con detalle de equipos (APs, switches, impresoras, etc.)
    seguimiento_bitacora TEXT, -- JSON Array con bitácora de notas: [{"fecha": "...", "autor": "...", "nota": "..."}]
    observaciones_cierre TEXT NULL,
    firma_recepcion VARCHAR(150) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rbd) REFERENCES establecimientos(rbd) ON DELETE RESTRICT ON UPDATE CASCADE
);

-- 3. TABLA: usuarios (Autenticación y Perfil)
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    rol VARCHAR(50) DEFAULT 'Administrador TI',
    activo INTEGER DEFAULT 1 CHECK (activo IN (0, 1)),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. ÍNDICES DE RENDIMIENTO
CREATE INDEX IF NOT EXISTS idx_visitas_rbd ON visitas(rbd);
CREATE INDEX IF NOT EXISTS idx_visitas_estado ON visitas(estado);
CREATE INDEX IF NOT EXISTS idx_visitas_fecha_programada ON visitas(fecha_programada);
CREATE INDEX IF NOT EXISTS idx_visitas_tecnico ON visitas(tecnico_responsable);
CREATE INDEX IF NOT EXISTS idx_establecimientos_comuna ON establecimientos(comuna);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
