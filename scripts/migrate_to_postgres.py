"""
Utilidad de Migración de SQLite a PostgreSQL / Supabase
Plataforma de Visitas de Soporte TI - SLEP Valle Diguillín

Uso:
  python scripts/migrate_to_postgres.py
  python scripts/migrate_to_postgres.py --url="postgresql://postgres.xxx:password@aws-0-sa-east-1.pooler.supabase.com:6543/postgres?sslmode=require"
"""

import os
import sys
import argparse
import sqlite3
import json

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "soporte_ti.db")
SCHEMA_PG_PATH = os.path.join(BASE_DIR, "database", "schema_postgresql.sql")

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("[ERROR] Debes instalar psycopg2-binary: pip install psycopg2-binary")
    sys.exit(1)


def migrate(postgres_url: str):
    print("=" * 65)
    print("   MIGRACIÓN A POSTGRESQL / SUPABASE - SLEP VALLE DIGUILLÍN")
    print("=" * 65)
    print(f" * Origen (SQLite): {DB_PATH}")
    # Enmascarar password en URL
    import re
    masked_url = re.sub(r':([^:@]+)@', ':****@', postgres_url)
    print(f" * Destino (PostgreSQL): {masked_url}")
    print("=" * 65)

    if not os.path.exists(DB_PATH):
        print(f"[ERROR] No se encontró el archivo SQLite de origen: {DB_PATH}")
        sys.exit(1)

    # 1. Conectar a SQLite
    conn_sqlite = sqlite3.connect(DB_PATH)
    conn_sqlite.row_factory = sqlite3.Row
    cur_sqlite = conn_sqlite.cursor()

    # 2. Conectar a PostgreSQL
    try:
        if postgres_url.startswith("postgres://"):
            postgres_url = postgres_url.replace("postgres://", "postgresql://", 1)
        conn_pg = psycopg2.connect(postgres_url)
        conn_pg.autocommit = False
        cur_pg = conn_pg.cursor()
        print("[+] Conexión a PostgreSQL/Supabase establecida exitosamente.")
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a PostgreSQL: {e}")
        sys.exit(1)

    # 3. Aplicar esquema DDL en PostgreSQL
    print("[+] Creando/verificando tablas e índices en PostgreSQL...")
    if os.path.exists(SCHEMA_PG_PATH):
        with open(SCHEMA_PG_PATH, "r", encoding="utf-8") as f:
            cur_pg.execute(f.read())
        conn_pg.commit()
    else:
        print(f"[ERROR] No se encontró {SCHEMA_PG_PATH}")
        sys.exit(1)

    # 4. Migrar usuarios
    print("[+] Migrando usuarios...")
    cur_sqlite.execute("SELECT email, password, nombre, rol, telefono, activo FROM usuarios")
    usuarios = [tuple(r) for r in cur_sqlite.fetchall()]
    if usuarios:
        cur_pg.execute("TRUNCATE TABLE usuarios RESTART IDENTITY CASCADE")
        insert_usr = """
            INSERT INTO usuarios (email, password, nombre, rol, telefono, activo)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
        """
        for u in usuarios:
            cur_pg.execute(insert_usr, u)
        conn_pg.commit()
        print(f"    {len(usuarios)} usuarios migrados.")

    # 5. Migrar establecimientos
    print("[+] Migrando establecimientos...")
    cur_sqlite.execute("""
        SELECT rbd, nombre, comuna, direccion, correo_establecimiento, director,
               correo_director, telefono, matricula, dependencia, contacto_enlaces,
               tipo_establecimiento, activo
        FROM establecimientos
        ORDER BY rbd ASC
    """)
    est_rows = [tuple(r) for r in cur_sqlite.fetchall()]
    if est_rows:
        cur_pg.execute("TRUNCATE TABLE establecimientos RESTART IDENTITY CASCADE")
        insert_est = """
            INSERT INTO establecimientos (
                rbd, nombre, comuna, direccion, correo_establecimiento, director,
                correo_director, telefono, matricula, dependencia, contacto_enlaces,
                tipo_establecimiento, activo
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (rbd) DO UPDATE SET
                nombre = EXCLUDED.nombre,
                comuna = EXCLUDED.comuna,
                direccion = EXCLUDED.direccion,
                correo_establecimiento = EXCLUDED.correo_establecimiento,
                director = EXCLUDED.director,
                correo_director = EXCLUDED.correo_director,
                telefono = EXCLUDED.telefono,
                matricula = EXCLUDED.matricula,
                dependencia = EXCLUDED.dependencia,
                contacto_enlaces = EXCLUDED.contacto_enlaces,
                tipo_establecimiento = EXCLUDED.tipo_establecimiento,
                activo = EXCLUDED.activo,
                updated_at = CURRENT_TIMESTAMP
        """
        for e in est_rows:
            cur_pg.execute(insert_est, e)
        conn_pg.commit()
        print(f"    {len(est_rows)} establecimientos migrados.")

    # 6. Migrar visitas
    print("[+] Migrando visitas técnicas...")
    cur_sqlite.execute("""
        SELECT id, rbd, tecnico_responsable, estado, tipo_soporte, prioridad,
               fecha_solicitud, fecha_atencion, fecha_programada, fecha_realizada,
               motivo, detalle_hardware, seguimiento_bitacora, observaciones_cierre, firma_recepcion
        FROM visitas
        ORDER BY id ASC
    """)
    vis_rows = [tuple(r) for r in cur_sqlite.fetchall()]
    if vis_rows:
        cur_pg.execute("TRUNCATE TABLE visitas RESTART IDENTITY CASCADE")
        insert_vis = """
            INSERT INTO visitas (
                id, rbd, tecnico_responsable, estado, tipo_soporte, prioridad,
                fecha_solicitud, fecha_atencion, fecha_programada, fecha_realizada,
                motivo, detalle_hardware, seguimiento_bitacora, observaciones_cierre, firma_recepcion
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET
                rbd = EXCLUDED.rbd,
                tecnico_responsable = EXCLUDED.tecnico_responsable,
                estado = EXCLUDED.estado,
                tipo_soporte = EXCLUDED.tipo_soporte,
                prioridad = EXCLUDED.prioridad,
                fecha_solicitud = EXCLUDED.fecha_solicitud,
                fecha_atencion = EXCLUDED.fecha_atencion,
                fecha_programada = EXCLUDED.fecha_programada,
                fecha_realizada = EXCLUDED.fecha_realizada,
                motivo = EXCLUDED.motivo,
                detalle_hardware = EXCLUDED.detalle_hardware,
                seguimiento_bitacora = EXCLUDED.seguimiento_bitacora,
                observaciones_cierre = EXCLUDED.observaciones_cierre,
                firma_recepcion = EXCLUDED.firma_recepcion,
                updated_at = CURRENT_TIMESTAMP
        """
        for v in vis_rows:
            cur_pg.execute(insert_vis, v)
        
        # Ajustar la secuencia de PostgreSQL para el ID autoincremental
        cur_pg.execute("SELECT setval(pg_get_serial_sequence('visitas', 'id'), COALESCE(MAX(id), 1)) FROM visitas;")
        conn_pg.commit()
        print(f"    {len(vis_rows)} visitas técnicas migradas con secuencia sincronizada.")

    # 7. Resumen y verificación
    cur_pg.execute("SELECT COUNT(*) FROM establecimientos")
    tot_est_pg = cur_pg.fetchone()[0]
    cur_pg.execute("SELECT COUNT(*) FROM visitas")
    tot_vis_pg = cur_pg.fetchone()[0]
    cur_pg.execute("SELECT COUNT(*) FROM usuarios")
    tot_usr_pg = cur_pg.fetchone()[0]

    conn_sqlite.close()
    conn_pg.close()

    print("=" * 65)
    print("   ¡MIGRACIÓN COMPLETADA EXITOSAMENTE!")
    print(f"   * Total Establecimientos en PostgreSQL: {tot_est_pg}")
    print(f"   * Total Visitas en PostgreSQL: {tot_vis_pg}")
    print(f"   * Total Usuarios en PostgreSQL: {tot_usr_pg}")
    print("=" * 65)
    print("Para activar PostgreSQL permanentemente, agrega tu DATABASE_URL en el archivo .env:")
    print(f'DATABASE_URL="{postgres_url}"')
    print("=" * 65)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Migración de SQLite a PostgreSQL / Supabase")
    parser.add_argument("--url", type=str, help="Cadena de conexión PostgreSQL (DATABASE_URL)")
    args = parser.parse_args()

    pg_url = args.url or os.environ.get("DATABASE_URL")
    if not pg_url:
        print("[!] No se especificó DATABASE_URL ni el parámetro --url.")
        print("    Ejemplo: python scripts/migrate_to_postgres.py --url=\"postgresql://usuario:password@host:5432/bd\"")
        sys.exit(1)

    migrate(pg_url)
