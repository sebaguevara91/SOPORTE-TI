-- ==============================================================================
-- PLATAFORMA DE REGISTRO DE VISITAS DE SOPORTE TI - SLEP VALLE DIGUILLÍN
-- Esquema PostgreSQL / Supabase Oficial
-- ==============================================================================

-- 1. TABLA: usuarios
CREATE TABLE IF NOT EXISTS usuarios (
    id SERIAL PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    nombre VARCHAR(150) NOT NULL,
    rol VARCHAR(50) DEFAULT 'Tecnico TI',
    telefono VARCHAR(50),
    activo INTEGER DEFAULT 1 CHECK (activo IN (0, 1)),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 2. TABLA: establecimientos
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
    dependencia VARCHAR(50) DEFAULT 'SLEP',
    contacto_enlaces VARCHAR(150),
    tipo_establecimiento VARCHAR(50) DEFAULT 'Escuela',
    activo INTEGER DEFAULT 1 CHECK (activo IN (0, 1)),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- 3. TABLA: visitas
CREATE TABLE IF NOT EXISTS visitas (
    id SERIAL PRIMARY KEY,
    rbd INTEGER NOT NULL REFERENCES establecimientos(rbd) ON DELETE RESTRICT ON UPDATE CASCADE,
    tecnico_responsable VARCHAR(150) NOT NULL,
    estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'En Proceso', 'Realizada', 'Programada')),
    tipo_soporte VARCHAR(100) NOT NULL DEFAULT 'Soporte Correctivo',
    prioridad VARCHAR(20) NOT NULL DEFAULT 'Media' CHECK (prioridad IN ('Baja', 'Media', 'Alta', 'Urgente')),
    fecha_solicitud DATE NOT NULL,
    fecha_atencion TIMESTAMP WITH TIME ZONE NULL,
    fecha_programada DATE NULL,
    fecha_realizada TIMESTAMP WITH TIME ZONE NULL,
    motivo TEXT NOT NULL,
    detalle_hardware TEXT,
    seguimiento_bitacora TEXT,
    observaciones_cierre TEXT NULL,
    firma_recepcion VARCHAR(150) NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices de alto rendimiento
CREATE INDEX IF NOT EXISTS idx_visitas_rbd ON visitas(rbd);
CREATE INDEX IF NOT EXISTS idx_visitas_estado ON visitas(estado);
CREATE INDEX IF NOT EXISTS idx_visitas_fecha_solicitud ON visitas(fecha_solicitud);
CREATE INDEX IF NOT EXISTS idx_visitas_tecnico ON visitas(tecnico_responsable);
CREATE INDEX IF NOT EXISTS idx_establecimientos_comuna ON establecimientos(comuna);
CREATE INDEX IF NOT EXISTS idx_usuarios_email ON usuarios(email);
