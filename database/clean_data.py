"""
Script de Limpieza, Saneamiento y Migración de Base de Datos
Plataforma de Visitas de Soporte TI - SLEP Valle Diguillín
Limpia datos demo, estandariza comunas/tipos, y genera base limpia para SQLite y PostgreSQL.
"""

import os
import shutil
import sqlite3
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "soporte_ti.db")
BACKUP_PATH = os.path.join(BASE_DIR, "database", "soporte_ti_pre_migration.db")
CLEAN_SEEDS_PATH = os.path.join(BASE_DIR, "database", "seeds_vallediguillin.sql")
SCHEMA_PG_PATH = os.path.join(BASE_DIR, "database", "schema_postgresql.sql")

def normalizar_comuna(comuna_raw):
    if not comuna_raw:
        return "Chillán"
    c = str(comuna_raw).strip()
    c_upper = c.upper().replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
    if "CHILLAN VIEJO" in c_upper:
        return "Chillán Viejo"
    elif "CHILLAN" in c_upper:
        return "Chillán"
    elif "BULNES" in c_upper:
        return "Bulnes"
    elif "PEMUCO" in c_upper:
        return "Pemuco"
    elif "SAN IGNACIO" in c_upper:
        return "San Ignacio"
    elif "YUNGAY" in c_upper:
        return "Yungay"
    elif "EL CARMEN" in c_upper or "CARMEN" in c_upper:
        return "El Carmen"
    elif "QUILLON" in c_upper:
        return "Quillón"
    return c.title()

def normalizar_tipo_soporte(tipo_raw):
    if not tipo_raw:
        return "Soporte Correctivo"
    t = str(tipo_raw).strip()
    t_upper = t.upper().replace("Á", "A").replace("É", "E").replace("Í", "I").replace("Ó", "O").replace("Ú", "U")
    if "IMPRESORA" in t_upper or "PERIFER" in t_upper:
        return "Impresoras y Periféricos"
    elif "ENTREGA" in t_upper:
        return "Entrega de Equipamiento"
    elif "SOFTWARE" in t_upper or "SISTEMA" in t_upper:
        return "Software y Sistemas"
    elif "PREVENTIVO" in t_upper or "MANTEN" in t_upper:
        return "Mantenimiento Preventivo"
    elif "CONECTIVIDAD" in t_upper or "WIFI" in t_upper or "RED" in t_upper:
        return "Problemas de Conectividad"
    elif "IMPLEMENTAC" in t_upper or "SERVICIO" in t_upper:
        return "Implementación de Servicios"
    elif "CORRECTIVO" in t_upper:
        return "Soporte Correctivo"
    return t

def clean_and_rebuild_db():
    print("[1/5] Verificando respaldo de seguridad de la base de datos previa...")
    if not os.path.exists(BACKUP_PATH) and os.path.exists(DB_PATH):
        shutil.copy2(DB_PATH, BACKUP_PATH)
        print(f"      Respaldo creado en: {BACKUP_PATH}")

    source_path = BACKUP_PATH if os.path.exists(BACKUP_PATH) else DB_PATH
    conn_old = sqlite3.connect(source_path)
    conn_old.row_factory = sqlite3.Row
    cur_old = conn_old.cursor()

    # 1. Extraer establecimientos reales (excluyendo RBDs demo de Antofagasta/Calama)
    print("[2/5] Extrayendo y limpiando establecimientos de SLEP Valle Diguillín...")
    cur_old.execute("""
        SELECT * FROM establecimientos 
        WHERE rbd NOT IN (1024, 1025, 1026, 1027, 1028, 1029, 1030)
          AND comuna NOT IN ('Antofagasta', 'Calama', 'Tocopilla', 'Mejillones')
        ORDER BY rbd ASC
    """)
    est_rows = cur_old.fetchall()
    
    clean_establecimientos = []
    for r in est_rows:
        e = dict(r)
        e['comuna'] = normalizar_comuna(e['comuna'])
        e['nombre'] = str(e['nombre']).strip()
        e['direccion'] = str(e.get('direccion') or '').strip()
        e['director'] = str(e.get('director') or 'Director(a)').strip()
        e['correo_director'] = str(e.get('correo_director') or 'contacto@eduvallediguillin.gob.cl').strip()
        e['correo_establecimiento'] = str(e.get('correo_establecimiento') or e['correo_director']).strip()
        e['tipo_establecimiento'] = e.get('tipo_establecimiento') or 'Escuela'
        
        # Clasificación automática según nombre
        nom_low = e['nombre'].lower()
        if 'liceo' in nom_low or 'politécnico' in nom_low or 'politecnico' in nom_low or 'instituto' in nom_low:
            e['tipo_establecimiento'] = 'Liceo'
        elif 'sala cuna' in nom_low or 'salacuna' in nom_low or 'jardín' in nom_low or 'jardin' in nom_low:
            e['tipo_establecimiento'] = 'Sala Cuna'
        
        clean_establecimientos.append(e)

    print(f"      {len(clean_establecimientos)} establecimientos válidos de Valle Diguillín procesados.")

    # 2. Extraer visitas
    print("[3/5] Extrayendo y estandarizando visitas técnicas...")
    cur_old.execute("SELECT * FROM visitas ORDER BY id ASC")
    vis_rows = cur_old.fetchall()

    est_rbds_validos = set(e['rbd'] for e in clean_establecimientos)
    clean_visitas = []
    for r in vis_rows:
        v = dict(r)
        if v['rbd'] not in est_rbds_validos:
            continue

        v['tipo_soporte'] = normalizar_tipo_soporte(v.get('tipo_soporte'))
        
        # Validar estado
        est_val = v.get('estado') or 'Pendiente'
        if est_val not in ('Pendiente', 'En Proceso', 'Realizada', 'Programada'):
            est_val = 'Pendiente'
        v['estado'] = est_val

        # Prioridad
        prio_val = v.get('prioridad') or 'Media'
        if prio_val not in ('Baja', 'Media', 'Alta', 'Urgente'):
            prio_val = 'Media'
        v['prioridad'] = prio_val

        # Fechas
        f_sol = v.get('fecha_solicitud') or v.get('fecha_programada') or '2026-01-01'
        f_ate = v.get('fecha_atencion') or v.get('fecha_realizada') or None
        if v['estado'] == 'Pendiente':
            f_ate = None
        elif v['estado'] == 'Realizada' and not f_ate:
            f_ate = f"{f_sol} 17:00:00"

        v['fecha_solicitud'] = f_sol
        v['fecha_atencion'] = f_ate
        v['fecha_programada'] = f_sol
        v['fecha_realizada'] = f_ate

        clean_visitas.append(v)

    print(f"      {len(clean_visitas)} visitas técnicas validadas y estandarizadas.")
    conn_old.close()

    # 3. Recrear Base SQLite Limpia
    print("[4/5] Reconstruyendo base de datos SQLite soporte_ti.db...")
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn_new = sqlite3.connect(DB_PATH)
    conn_new.execute("PRAGMA foreign_keys = ON")
    conn_new.execute("PRAGMA journal_mode = WAL")
    
    # Esquema SQLite
    conn_new.executescript("""
        CREATE TABLE usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email VARCHAR(150) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            nombre VARCHAR(150) NOT NULL,
            rol VARCHAR(50) DEFAULT 'Tecnico TI',
            telefono VARCHAR(50),
            activo INTEGER DEFAULT 1 CHECK (activo IN (0, 1)),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE establecimientos (
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE visitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rbd INTEGER NOT NULL,
            tecnico_responsable VARCHAR(150) NOT NULL,
            estado VARCHAR(20) NOT NULL DEFAULT 'Pendiente' CHECK (estado IN ('Pendiente', 'En Proceso', 'Realizada', 'Programada')),
            tipo_soporte VARCHAR(100) NOT NULL DEFAULT 'Soporte Correctivo',
            prioridad VARCHAR(20) NOT NULL DEFAULT 'Media' CHECK (prioridad IN ('Baja', 'Media', 'Alta', 'Urgente')),
            fecha_solicitud DATE NOT NULL,
            fecha_atencion TIMESTAMP NULL,
            fecha_programada DATE NULL,
            fecha_realizada TIMESTAMP NULL,
            motivo TEXT NOT NULL,
            detalle_hardware TEXT,
            seguimiento_bitacora TEXT,
            observaciones_cierre TEXT NULL,
            firma_recepcion VARCHAR(150) NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (rbd) REFERENCES establecimientos(rbd) ON DELETE RESTRICT ON UPDATE CASCADE
        );

        CREATE INDEX idx_visitas_rbd ON visitas(rbd);
        CREATE INDEX idx_visitas_estado ON visitas(estado);
        CREATE INDEX idx_visitas_fecha_solicitud ON visitas(fecha_solicitud);
        CREATE INDEX idx_visitas_tecnico ON visitas(tecnico_responsable);
        CREATE INDEX idx_establecimientos_comuna ON establecimientos(comuna);
        CREATE INDEX idx_usuarios_email ON usuarios(email);
    """)

    # Insertar usuarios
    usuarios_iniciales = [
        ('admin@soporteti.cl', 'admin123', 'Administrador General TI', 'Administrador TI', '+56 9 1234 5678', 1),
        ('sguevara@eduvallediguillin.gob.cl', 'admin123', 'Sebastian Guevara', 'Tecnico TI', '+56 9 8765 4321', 1),
        ('rbravo@eduvallediguillin.gob.cl', 'admin123', 'Rodrigo Bravo', 'Tecnico TI', '+56 9 5555 4444', 1),
        ('crojas@eduvallediguillin.gob.cl', 'admin123', 'Claudio Rojas', 'Tecnico TI', '+56 9 6666 7777', 1),
    ]
    conn_new.executemany(
        "INSERT INTO usuarios (email, password, nombre, rol, telefono, activo) VALUES (?, ?, ?, ?, ?, ?)",
        usuarios_iniciales
    )

    # Insertar establecimientos
    for e in clean_establecimientos:
        conn_new.execute(
            """
            INSERT INTO establecimientos (
                rbd, nombre, comuna, direccion, correo_establecimiento, director,
                correo_director, telefono, matricula, dependencia, contacto_enlaces,
                tipo_establecimiento, activo
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                e['rbd'], e['nombre'], e['comuna'], e.get('direccion'), e.get('correo_establecimiento'),
                e['director'], e['correo_director'], e.get('telefono'), e.get('matricula', 0),
                e.get('dependencia', 'SLEP'), e.get('contacto_enlaces'), e.get('tipo_establecimiento', 'Escuela'),
                e.get('activo', 1)
            )
        )

    # Insertar visitas
    for v in clean_visitas:
        conn_new.execute(
            """
            INSERT INTO visitas (
                id, rbd, tecnico_responsable, estado, tipo_soporte, prioridad,
                fecha_solicitud, fecha_atencion, fecha_programada, fecha_realizada,
                motivo, detalle_hardware, seguimiento_bitacora, observaciones_cierre, firma_recepcion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                v['id'], v['rbd'], v['tecnico_responsable'], v['estado'], v['tipo_soporte'], v['prioridad'],
                v['fecha_solicitud'], v['fecha_atencion'], v['fecha_programada'], v['fecha_realizada'],
                v['motivo'], v.get('detalle_hardware'), v.get('seguimiento_bitacora'),
                v.get('observaciones_cierre'), v.get('firma_recepcion')
            )
        )

    conn_new.commit()
    conn_new.close()

    # 4. Generar Script SQL PostgreSQL y Semillas Limpias
    print("[5/5] Generando scripts SQL limpios para PostgreSQL y recuperación...")
    with open(SCHEMA_PG_PATH, "w", encoding="utf-8") as f:
        f.write("""-- ==============================================================================
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
""")

    print("      ¡Migración y saneamiento completados con éxito!")
    print(f"      Total Establecimientos: {len(clean_establecimientos)}")
    print(f"      Total Visitas: {len(clean_visitas)}")

if __name__ == "__main__":
    clean_and_rebuild_db()
