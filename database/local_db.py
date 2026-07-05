"""
database/local_db.py
Caché local en SQLite. Sirve como copia de respaldo cuando no hay
conexión a Supabase/Postgres, y como cola de cambios pendientes por
sincronizar.

Reglas de IDs:
  - id > 0  -> registro que existe (o existió) en Postgres (id real).
  - id < 0  -> registro creado sin conexión, todavía no tiene id real.
               Se reemplaza por el id real apenas se sincroniza.

sync_status:
  - 'synced'          -> igual que en Postgres, no hay nada pendiente.
  - 'pending_insert'  -> creado offline, falta subirlo (id negativo).
  - 'pending_update'  -> editado offline, falta subir el cambio.
  - 'pending_delete'  -> borrado offline, falta borrar en Postgres.
"""
import os
import sqlite3
from datetime import datetime


def _carpeta_datos():
    carpeta = os.path.join(os.path.expanduser("~"), "MonitorRedesAGRO")
    os.makedirs(carpeta, exist_ok=True)
    return carpeta


RUTA_LOCAL_DB = os.path.join(_carpeta_datos(), "cache_local.db")

_conn_local = None


def get_local_connection():
    global _conn_local
    if _conn_local is None:
        _conn_local = sqlite3.connect(RUTA_LOCAL_DB, check_same_thread=False)
    return _conn_local


def inicializar_local_db():
    conn = get_local_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS cache_seguidores (
            id             INTEGER PRIMARY KEY,
            fecha          TEXT NOT NULL,
            red_social     TEXT NOT NULL,
            agropecuaria   INTEGER DEFAULT 0,
            agronegocios   INTEGER DEFAULT 0,
            agroindustrial INTEGER DEFAULT 0,
            sync_status    TEXT NOT NULL DEFAULT 'synced'
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS local_seq (
            nombre TEXT PRIMARY KEY,
            valor  INTEGER NOT NULL
        )
    """)
    cur.execute(
        "INSERT OR IGNORE INTO local_seq (nombre, valor) VALUES ('siguiente_id_negativo', -1)"
    )
    conn.commit()


def _siguiente_id_negativo():
    conn = get_local_connection()
    cur = conn.cursor()
    cur.execute("SELECT valor FROM local_seq WHERE nombre = 'siguiente_id_negativo'")
    valor = cur.fetchone()[0]
    cur.execute(
        "UPDATE local_seq SET valor = valor - 1 WHERE nombre = 'siguiente_id_negativo'"
    )
    conn.commit()
    return valor


# ── Escritura en caché ────────────────────────────────────────────────────
def cache_insertar_pendiente(red_social, agropecuaria, agronegocios, agroindustrial, fecha=None):
    """Guarda un registro nuevo creado SIN conexión. Devuelve (id_local, fecha)."""
    conn = get_local_connection()
    cur = conn.cursor()
    fecha = fecha or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    id_local = _siguiente_id_negativo()
    cur.execute("""
        INSERT INTO cache_seguidores (id, fecha, red_social, agropecuaria, agronegocios, agroindustrial, sync_status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending_insert')
    """, (id_local, fecha, red_social, agropecuaria, agronegocios, agroindustrial))
    conn.commit()
    return id_local, fecha


def cache_guardar_sincronizado(id_real, fecha, red_social, agropecuaria, agronegocios, agroindustrial):
    """Refleja en la caché un registro ya confirmado en Postgres."""
    conn = get_local_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT OR REPLACE INTO cache_seguidores
            (id, fecha, red_social, agropecuaria, agronegocios, agroindustrial, sync_status)
        VALUES (?, ?, ?, ?, ?, ?, 'synced')
    """, (id_real, fecha, red_social, agropecuaria, agronegocios, agroindustrial))
    conn.commit()


def cache_actualizar(id_registro, agropecuaria, agronegocios, agroindustrial, pendiente=False):
    conn = get_local_connection()
    cur = conn.cursor()
    estado = "pending_update" if pendiente else "synced"
    cur.execute("""
        UPDATE cache_seguidores
        SET agropecuaria = ?, agronegocios = ?, agroindustrial = ?, sync_status = ?
        WHERE id = ?
    """, (agropecuaria, agronegocios, agroindustrial, estado, id_registro))
    conn.commit()
    return cur.rowcount > 0


def cache_marcar_pendiente_delete(id_registro):
    conn = get_local_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE cache_seguidores SET sync_status = 'pending_delete' WHERE id = ?",
        (id_registro,),
    )
    conn.commit()
    return cur.rowcount > 0


def cache_eliminar_fila(id_registro):
    """Borra la fila directamente de la caché (usado en deletes ya confirmados)."""
    conn = get_local_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM cache_seguidores WHERE id = ?", (id_registro,))
    conn.commit()
    return cur.rowcount > 0


def cache_reemplazar_todo(registros):
    """Reemplaza toda la caché 'synced' con lo que hay en Postgres.

    Conserva las filas todavía pendientes (no confirmadas), para no perder
    cambios hechos offline que aún no se han subido.
    """
    conn = get_local_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM cache_seguidores WHERE sync_status = 'synced'")
    cur.executemany("""
        INSERT OR REPLACE INTO cache_seguidores
            (id, fecha, red_social, agropecuaria, agronegocios, agroindustrial, sync_status)
        VALUES (?, ?, ?, ?, ?, ?, 'synced')
    """, [
        (r["id"], r["fecha"], r["red_social"], r["Agropecuaria"], r["Agronegocios"], r["Agroindustrial"])
        for r in registros
    ])
    conn.commit()


# ── Lectura desde caché ───────────────────────────────────────────────────
def cache_obtener_todos():
    conn = get_local_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, fecha, red_social, agropecuaria, agronegocios, agroindustrial
        FROM cache_seguidores
        WHERE sync_status != 'pending_delete'
        ORDER BY fecha DESC, red_social ASC
    """)
    filas = cur.fetchall()
    return [
        {
            "id": f[0], "fecha": f[1], "red_social": f[2],
            "Agropecuaria": f[3], "Agronegocios": f[4], "Agroindustrial": f[5],
        }
        for f in filas
    ]


def cache_obtener_por_red(red_social):
    conn = get_local_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT fecha, agropecuaria, agronegocios, agroindustrial
        FROM cache_seguidores
        WHERE red_social = ? AND sync_status != 'pending_delete'
        ORDER BY fecha ASC
    """, (red_social,))
    filas = cur.fetchall()
    return [
        {"fecha": f[0], "Agropecuaria": f[1], "Agronegocios": f[2], "Agroindustrial": f[3]}
        for f in filas
    ]


def cache_obtener_ultimo(red_social):
    datos = cache_obtener_por_red(red_social)
    return datos[-1] if datos else None


def cache_obtener_redes():
    conn = get_local_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT red_social FROM cache_seguidores
        WHERE sync_status != 'pending_delete'
        ORDER BY red_social
    """)
    return [r[0] for r in cur.fetchall()] or ["Facebook", "TikTok", "Instagram"]


def cache_obtener_pendientes():
    """Todo lo que falta subir a Postgres, en orden de creación."""
    conn = get_local_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, fecha, red_social, agropecuaria, agronegocios, agroindustrial, sync_status
        FROM cache_seguidores
        WHERE sync_status != 'synced'
        ORDER BY id ASC
    """)
    filas = cur.fetchall()
    return [
        {
            "id": f[0], "fecha": f[1], "red_social": f[2],
            "agropecuaria": f[3], "agronegocios": f[4], "agroindustrial": f[5],
            "sync_status": f[6],
        }
        for f in filas
    ]


def hay_pendientes():
    conn = get_local_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM cache_seguidores WHERE sync_status != 'synced'")
    return cur.fetchone()[0] > 0


def cache_reemplazar_id(id_viejo, id_nuevo):
    """Usado al sincronizar un pending_insert: cambia el id negativo por el real."""
    conn = get_local_connection()
    cur = conn.cursor()
    cur.execute(
        "UPDATE cache_seguidores SET id = ?, sync_status = 'synced' WHERE id = ?",
        (id_nuevo, id_viejo),
    )
    conn.commit()
