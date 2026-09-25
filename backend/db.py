"""
Módulo de Gestión y Conexión de Base de Datos Unificada
Plataforma de Visitas de Soporte TI - SLEP Valle Diguillín

Soporta:
1. PostgreSQL / Supabase / Neon / Render (Producción Centralizada Concurrente)
2. SQLite (Desarrollo / Respaldo Local)

Traduce automáticamente placeholders '?' -> '%s' y normaliza filas a diccionarios.
"""

import os
import re
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union
from contextlib import contextmanager

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "soporte_ti.db")
SCHEMA_SQLITE_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
SCHEMA_PG_PATH = os.path.join(BASE_DIR, "database", "schema_postgresql.sql")

# Intentar importar psycopg2
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False


class DatabaseManager:
    def __init__(self):
        self._database_url = os.environ.get("DATABASE_URL", "").strip()
        self.is_postgres = bool(
            self._database_url and (
                self._database_url.startswith("postgresql://") or 
                self._database_url.startswith("postgres://")
            )
        )
        self._pg_conn = None

    def reload_config(self):
        """Recarga la configuración desde las variables de entorno."""
        self._database_url = os.environ.get("DATABASE_URL", "").strip()
        self.is_postgres = bool(
            self._database_url and (
                self._database_url.startswith("postgresql://") or 
                self._database_url.startswith("postgres://")
            )
        )
        if not self.is_postgres and self._pg_conn:
            try:
                self._pg_conn.close()
            except Exception:
                pass
            self._pg_conn = None

    def get_raw_connection(self):
        """Retorna una conexión cruda al motor configurado."""
        if self.is_postgres:
            if not PSYCOPG2_AVAILABLE:
                raise RuntimeError("psycopg2 no está instalado en el entorno Python.")
            # Normalizar postgres:// a postgresql:// si aplica
            url = self._database_url
            if url.startswith("postgres://"):
                url = url.replace("postgres://", "postgresql://", 1)
            conn = psycopg2.connect(url, cursor_factory=RealDictCursor)
            conn.autocommit = False
            return conn
        else:
            os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
            conn = sqlite3.connect(DB_PATH, timeout=30.0, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")
            return conn

    @contextmanager
    def connection(self):
        """Context manager seguro para obtener conexión y cerrar al finalizar."""
        conn = self.get_raw_connection()
        try:
            yield conn
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def _adapt_sql(self, sql: str) -> str:
        """Adapta la sintaxis SQL de SQLite (?) a PostgreSQL (%s) si es necesario."""
        if self.is_postgres:
            # Reemplazar ? por %s si no está dentro de comillas
            # En la gran mayoría de consultas REST, basta con sustituir '?' por '%s'
            return sql.replace("?", "%s")
        return sql

    def query(self, sql: str, params: Optional[Union[List, Tuple]] = None) -> List[Dict[str, Any]]:
        """Ejecuta una consulta SELECT y retorna una lista de diccionarios."""
        adapted_sql = self._adapt_sql(sql)
        params = params or []
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(adapted_sql, tuple(params))
            rows = cur.fetchall()
            cur.close()
            if self.is_postgres:
                return [dict(r) for r in rows]
            else:
                return [dict(r) for r in rows]

    def query_one(self, sql: str, params: Optional[Union[List, Tuple]] = None) -> Optional[Dict[str, Any]]:
        """Ejecuta una consulta SELECT y retorna un solo diccionario o None."""
        adapted_sql = self._adapt_sql(sql)
        params = params or []
        with self.connection() as conn:
            cur = conn.cursor()
            cur.execute(adapted_sql, tuple(params))
            row = cur.fetchone()
            cur.close()
            if row:
                return dict(row)
            return None

    def execute(self, sql: str, params: Optional[Union[List, Tuple]] = None, return_id: bool = False) -> int:
        """
        Ejecuta una sentencia INSERT, UPDATE o DELETE con commit automático.
        Retorna lastrowid (si return_id=True y es INSERT) o rowcount.
        """
        adapted_sql = self._adapt_sql(sql)
        params = params or []
        
        with self.connection() as conn:
            cur = conn.cursor()
            
            if self.is_postgres and return_id and "INSERT INTO" in sql.upper() and "RETURNING" not in sql.upper():
                # En PostgreSQL se añade RETURNING id para emular lastrowid
                pg_sql = f"{adapted_sql} RETURNING id"
                cur.execute(pg_sql, tuple(params))
                res = cur.fetchone()
                conn.commit()
                cur.close()
                return res["id"] if res else 0

            cur.execute(adapted_sql, tuple(params))
            
            if not self.is_postgres and return_id:
                last_id = cur.lastrowid
                conn.commit()
                cur.close()
                return last_id

            row_count = cur.rowcount
            conn.commit()
            cur.close()
            return row_count

    def executemany(self, sql: str, params_list: List[Union[List, Tuple]]) -> int:
        """Ejecuta múltiples sentencias con commit atómico."""
        if not params_list:
            return 0
        adapted_sql = self._adapt_sql(sql)
        with self.connection() as conn:
            cur = conn.cursor()
            cur.executemany(adapted_sql, params_list)
            conn.commit()
            count = len(params_list)
            cur.close()
            return count

    def init_schema(self):
        """Inicializa las tablas e índices si no existen."""
        with self.connection() as conn:
            cur = conn.cursor()
            if self.is_postgres:
                if os.path.exists(SCHEMA_PG_PATH):
                    with open(SCHEMA_PG_PATH, "r", encoding="utf-8") as f:
                        cur.execute(f.read())
                    conn.commit()
            else:
                if os.path.exists(SCHEMA_SQLITE_PATH):
                    with open(SCHEMA_SQLITE_PATH, "r", encoding="utf-8") as f:
                        cur.executescript(f.read())
                    conn.commit()
            cur.close()

    def get_status(self) -> Dict[str, Any]:
        """Retorna información detallada del estado y motor de la base de datos."""
        self.reload_config()
        engine_name = "PostgreSQL (Supabase/Central)" if self.is_postgres else "SQLite (Local Persistente)"
        
        try:
            with self.connection() as conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.close()
            
            est_count = self.query_one("SELECT COUNT(*) as c FROM establecimientos")
            vis_count = self.query_one("SELECT COUNT(*) as c FROM visitas")
            usr_count = self.query_one("SELECT COUNT(*) as c FROM usuarios")

            # Extraer host seguro
            db_target = "sqlite:///database/soporte_ti.db"
            if self.is_postgres and self._database_url:
                try:
                    # Ocultar password en la URL
                    masked = re.sub(r':([^:@]+)@', ':****@', self._database_url)
                    db_target = masked
                except Exception:
                    db_target = "postgresql://[protegido]"

            return {
                "status": "connected",
                "engine": "PostgreSQL" if self.is_postgres else "SQLite",
                "engine_display": engine_name,
                "target": db_target,
                "establecimientos_count": est_count["c"] if est_count else 0,
                "visitas_count": vis_count["c"] if vis_count else 0,
                "usuarios_count": usr_count["c"] if usr_count else 0,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "status": "error",
                "engine": "PostgreSQL" if self.is_postgres else "SQLite",
                "engine_display": engine_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }


# Instancia Global Singleton
db = DatabaseManager()
