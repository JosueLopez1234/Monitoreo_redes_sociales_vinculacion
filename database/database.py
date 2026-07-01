"""
database.py - Manejo de la base de datos PostgreSQL

"""
import psycopg2
import psycopg2.extras
from datetime import datetime
from dotenv import load_dotenv
import os
import sys

# ──────────────────────────────────────────────────────────────────────────
# CONEXIÓN
# ──────────────────────────────────────────────────────────────────────────
def _get_base_path():
    """Ruta base: junto al .exe si está congelado (PyInstaller),
    o junto a este .py si corre como script normal."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))
_env_path = os.path.join(_get_base_path(), ".env")
load_dotenv(override=True)

DB_CONFIG = {
    "host":     os.environ.get("DB_HOST"),
    "port":     os.environ.get("DB_PORT"),
    "dbname":   os.environ.get("DB_NAME"),
    "user":     os.environ.get("DB_USER"),
    "password": os.environ.get("DB_PASSWORD"),
    # keepalives para detectar conexiones muertas rápido en vez de colgarse
    "keepalives": 1,
    "keepalives_idle": 30,
    "keepalives_interval": 10,
    "keepalives_count": 3,
}

_conn = None  # conexión persistente, reutilizada en toda la app


def get_connection():
    """Devuelve la conexión persistente, reconectando si hace falta.

    Ya no abre una conexión nueva en cada llamada: crea UNA la primera
    vez y la reutiliza. Si detecta que está cerrada o rota, la reabre.
    """
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(**DB_CONFIG)
        return _conn
    try:
        with _conn.cursor() as cur:
            cur.execute("SELECT 1")
    except psycopg2.OperationalError:
        _conn = psycopg2.connect(**DB_CONFIG)
    return _conn


def cerrar_conexion():
    """Cierra la conexión persistente. Llamar al salir de la aplicación."""
    global _conn
    if _conn is not None and not _conn.closed:
        _conn.close()
    _conn = None


def inicializar_db():
    """Crea las tablas/índices si no existen e inserta datos iniciales."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seguidores (
            id          SERIAL PRIMARY KEY,
            fecha       TIMESTAMP NOT NULL,
            red_social  TEXT NOT NULL,
            agropecuaria   INTEGER DEFAULT 0,
            agronegocios   INTEGER DEFAULT 0,
            agroindustrial INTEGER DEFAULT 0
        )
    """)

    # Índice para acelerar los filtros/orden por red_social + fecha,
    # que son el patrón de consulta más usado (obtener_datos, último registro).
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_seguidores_red_fecha
        ON seguidores (red_social, fecha DESC)
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM seguidores")
    if cursor.fetchone()[0] == 0:
        datos_iniciales = [
            ("2026-05-08 14:00:00", "Facebook",   3022, 1635, 200),
            ("2026-05-08 14:00:00", "TikTok",      163,   38,  95),
            ("2026-05-08 14:00:00", "Instagram",    61,  110,  45),
        ]
        cursor.executemany("""
            INSERT INTO seguidores (fecha, red_social, agropecuaria, agronegocios, agroindustrial)
            VALUES (%s, %s, %s, %s, %s)
        """, datos_iniciales)
        conn.commit()

    cursor.close()


def guardar_registro(red_social, agropecuaria, agronegocios, agroindustrial):
    """Inserta un nuevo registro en la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO seguidores (fecha, red_social, agropecuaria, agronegocios, agroindustrial)
        VALUES (%s, %s, %s, %s, %s)
    """, (fecha, red_social, agropecuaria, agronegocios, agroindustrial))
    conn.commit()
    cursor.close()
    return fecha


def obtener_datos(red_social="Facebook"):
    """Retorna todos los registros de una red social como lista de dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha, agropecuaria, agronegocios, agroindustrial
        FROM seguidores
        WHERE red_social = %s
        ORDER BY fecha ASC
    """, (red_social,))
    filas = cursor.fetchall()
    cursor.close()
    return [
        {
            "fecha": f[0].strftime("%Y-%m-%d %H:%M:%S") if hasattr(f[0], "strftime") else f[0],
            "Agropecuaria": f[1],
            "Agronegocios": f[2],
            "Agroindustrial": f[3],
        }
        for f in filas
    ]


def obtener_ultimo_registro(red_social="Facebook"):
    """Retorna el último registro guardado de una red social."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha, agropecuaria, agronegocios, agroindustrial
        FROM seguidores
        WHERE red_social = %s
        ORDER BY fecha DESC
        LIMIT 1
    """, (red_social,))
    fila = cursor.fetchone()
    cursor.close()
    if fila:
        return {
            "fecha": fila[0].strftime("%Y-%m-%d %H:%M:%S") if hasattr(fila[0], "strftime") else fila[0],
            "Agropecuaria": fila[1],
            "Agronegocios": fila[2],
            "Agroindustrial": fila[3],
        }
    return None


def obtener_todos_los_registros():
    """Retorna todos los registros de todas las redes, con su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, fecha, red_social, agropecuaria, agronegocios, agroindustrial
        FROM seguidores
        ORDER BY fecha DESC, red_social ASC
    """)
    filas = cursor.fetchall()
    cursor.close()
    return [
        {
            "id":            f[0],
            "fecha":         f[1].strftime("%Y-%m-%d %H:%M:%S") if hasattr(f[1], "strftime") else f[1],
            "red_social":    f[2],
            "Agropecuaria":  f[3],
            "Agronegocios":  f[4],
            "Agroindustrial":f[5],
        }
        for f in filas
    ]


def actualizar_registro(id_registro, agropecuaria, agronegocios, agroindustrial):
    """Actualiza los seguidores de un registro existente por su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE seguidores
        SET agropecuaria = %s, agronegocios = %s, agroindustrial = %s
        WHERE id = %s
    """, (agropecuaria, agronegocios, agroindustrial, id_registro))
    conn.commit()
    afectadas = cursor.rowcount
    cursor.close()
    return afectadas > 0


def eliminar_registro(id_registro):
    """Elimina un registro por su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM seguidores WHERE id = %s", (id_registro,))
    conn.commit()
    afectadas = cursor.rowcount
    cursor.close()
    return afectadas > 0


def obtener_redes_disponibles():
    """Retorna las redes sociales con registros."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT red_social FROM seguidores ORDER BY red_social")
    redes = [r[0] for r in cursor.fetchall()]
    cursor.close()
    return redes or ["Facebook", "TikTok", "Instagram"]
