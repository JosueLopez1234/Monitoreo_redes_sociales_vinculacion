"""
database.py - Manejo de la base de datos PostgreSQL

"""
import psycopg2
import psycopg2.extras
from datetime import datetime
from dotenv import load_dotenv
import os
import sys

from . import local_db as cache

# ──────────────────────────────────────────────────────────────────────────
# CONEXIÓN
# ──────────────────────────────────────────────────────────────────────────
def _get_base_path():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _encontrar_env():
    candidatos = [
        os.path.join(_get_base_path(), ".env"),
        os.path.join(os.path.expanduser("~"), "MonitorRedesAGRO", ".env"),
    ]
    for ruta in candidatos:
        if os.path.exists(ruta):
            return ruta
    return None  # <-- antes devolvía candidatos[0] como fallback "fantasma"


ruta_env = _encontrar_env()
ENV_ENCONTRADO = ruta_env is not None
if ruta_env:
    load_dotenv(dotenv_path=ruta_env, override=True)
else:
    # Antes esto hacía `raise FileNotFoundError(...)` y tronaba la app
    # al abrir, con un traceback crudo. Ahora simplemente lo dejamos
    # arrancar en modo offline (sin credenciales, así que get_connection()
    # fallará limpio como cualquier otro corte de conexión) y avisamos
    # una sola vez desde main.py con una ventana amigable.
    print(
        "[AVISO] No se encontró el archivo .env. Debe estar junto al .exe "
        "o en la carpeta %USERPROFILE%\\MonitorRedesAGRO\\.env. "
        "La app arrancará en modo sin conexión."
    )

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


# ──────────────────────────────────────────────────────────────────────────
# MODO OFFLINE — detección de conexión y caché local (SQLite)
# ──────────────────────────────────────────────────────────────────────────
# Cualquier error de este tipo al hablar con Postgres se interpreta como
# "no hay conexión" y hace caer la operación a la caché local en vez de
# reventar la app.
ERRORES_DE_CONEXION = (
    psycopg2.OperationalError,
    psycopg2.InterfaceError,
)

_ultimo_estado_online = True  # se actualiza cada vez que se intenta hablar con Postgres


def esta_online():
    """Prueba rápida y barata de conectividad contra Supabase."""
    global _ultimo_estado_online
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
        _ultimo_estado_online = True
        return True
    except ERRORES_DE_CONEXION:
        _ultimo_estado_online = False
        return False


def ultimo_estado_conocido():
    """Último estado de conexión detectado, sin volver a probar la red."""
    return _ultimo_estado_online


def hay_cambios_pendientes():
    return cache.hay_pendientes()


def contar_cambios_pendientes():
    return len(cache.cache_obtener_pendientes())


def inicializar_db():
    """Crea las tablas/índices si no existen e inserta datos iniciales."""
    cache.inicializar_local_db()
    try:
        conn = get_connection()
    except ERRORES_DE_CONEXION:
        # Sin conexión desde el arranque: seguimos con la caché local,
        # ya se sincronizará cuando vuelva la red.
        global _ultimo_estado_online
        _ultimo_estado_online = False
        return
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
    """Inserta un nuevo registro. Si no hay conexión, lo guarda en la
    caché local y queda pendiente de subir a Supabase."""
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    global _ultimo_estado_online
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO seguidores (fecha, red_social, agropecuaria, agronegocios, agroindustrial)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (fecha, red_social, agropecuaria, agronegocios, agroindustrial))
        id_real = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        _ultimo_estado_online = True
        cache.cache_guardar_sincronizado(
            id_real, fecha, red_social, agropecuaria, agronegocios, agroindustrial)
        return fecha
    except ERRORES_DE_CONEXION:
        _ultimo_estado_online = False
        cache.cache_insertar_pendiente(
            red_social, agropecuaria, agronegocios, agroindustrial, fecha)
        return fecha


def obtener_datos(red_social="Facebook"):
    """Retorna todos los registros de una red social como lista de dicts.
    Si no hay conexión, se sirve desde la caché local."""
    global _ultimo_estado_online
    try:
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
        _ultimo_estado_online = True
        return [
            {
                "fecha": f[0].strftime("%Y-%m-%d %H:%M:%S") if hasattr(f[0], "strftime") else f[0],
                "Agropecuaria": f[1],
                "Agronegocios": f[2],
                "Agroindustrial": f[3],
            }
            for f in filas
        ]
    except ERRORES_DE_CONEXION:
        _ultimo_estado_online = False
        return cache.cache_obtener_por_red(red_social)


def obtener_ultimo_registro(red_social="Facebook"):
    """Retorna el último registro guardado de una red social."""
    global _ultimo_estado_online
    try:
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
        _ultimo_estado_online = True
        if fila:
            return {
                "fecha": fila[0].strftime("%Y-%m-%d %H:%M:%S") if hasattr(fila[0], "strftime") else fila[0],
                "Agropecuaria": fila[1],
                "Agronegocios": fila[2],
                "Agroindustrial": fila[3],
            }
        return None
    except ERRORES_DE_CONEXION:
        _ultimo_estado_online = False
        return cache.cache_obtener_ultimo(red_social)


def obtener_todos_los_registros():
    """Retorna todos los registros de todas las redes, con su ID.
    Con conexión: lee de Postgres y refresca la caché local.
    Sin conexión: lee de la caché (incluye lo pendiente de subir)."""
    global _ultimo_estado_online
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, fecha, red_social, agropecuaria, agronegocios, agroindustrial
            FROM seguidores
            ORDER BY fecha DESC, red_social ASC
        """)
        filas = cursor.fetchall()
        cursor.close()
        _ultimo_estado_online = True
        registros = [
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
        cache.cache_reemplazar_todo(registros)
        # Si había pendientes ya subidos en esta misma llamada (poco común),
        # los combinamos con lo que aún falte sincronizar.
        pendientes = [p for p in cache.cache_obtener_pendientes() if p["sync_status"] != "synced"]
        if pendientes:
            extra = [
                {
                    "id": p["id"], "fecha": p["fecha"], "red_social": p["red_social"],
                    "Agropecuaria": p["agropecuaria"], "Agronegocios": p["agronegocios"],
                    "Agroindustrial": p["agroindustrial"],
                }
                for p in pendientes if p["sync_status"] == "pending_insert"
            ]
            registros = extra + registros
        return registros
    except ERRORES_DE_CONEXION:
        _ultimo_estado_online = False
        return cache.cache_obtener_todos()


def actualizar_registro(id_registro, agropecuaria, agronegocios, agroindustrial):
    """Actualiza los seguidores de un registro existente por su ID."""
    global _ultimo_estado_online

    # Registro creado offline y todavía no subido (id negativo): solo
    # existe en la caché, se edita ahí directamente.
    if id_registro < 0:
        return cache.cache_actualizar(
            id_registro, agropecuaria, agronegocios, agroindustrial, pendiente=True)

    try:
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
        _ultimo_estado_online = True
        if afectadas > 0:
            cache.cache_actualizar(id_registro, agropecuaria, agronegocios, agroindustrial)
        return afectadas > 0
    except ERRORES_DE_CONEXION:
        _ultimo_estado_online = False
        return cache.cache_actualizar(
            id_registro, agropecuaria, agronegocios, agroindustrial, pendiente=True)


def eliminar_registro(id_registro):
    """Elimina un registro por su ID."""
    global _ultimo_estado_online

    # Nunca llegó a existir en Postgres: se borra directo de la caché.
    if id_registro < 0:
        return cache.cache_eliminar_fila(id_registro)

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM seguidores WHERE id = %s", (id_registro,))
        conn.commit()
        afectadas = cursor.rowcount
        cursor.close()
        _ultimo_estado_online = True
        if afectadas > 0:
            cache.cache_eliminar_fila(id_registro)
        return afectadas > 0
    except ERRORES_DE_CONEXION:
        _ultimo_estado_online = False
        return cache.cache_marcar_pendiente_delete(id_registro)


def obtener_redes_disponibles():
    """Retorna las redes sociales con registros."""
    global _ultimo_estado_online
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT red_social FROM seguidores ORDER BY red_social")
        redes = [r[0] for r in cursor.fetchall()]
        cursor.close()
        _ultimo_estado_online = True
        return redes or ["Facebook", "TikTok", "Instagram"]
    except ERRORES_DE_CONEXION:
        _ultimo_estado_online = False
        return cache.cache_obtener_redes()


# ──────────────────────────────────────────────────────────────────────────
# SINCRONIZACIÓN — sube a Postgres lo que quedó pendiente en la caché
# ──────────────────────────────────────────────────────────────────────────
def sincronizar_pendientes():
    """Sube a Supabase todo lo acumulado en la caché local mientras no
    hubo conexión. Devuelve (exito, cantidad_sincronizada, error)."""
    global _ultimo_estado_online

    if not cache.hay_pendientes():
        return True, 0, None

    try:
        conn = get_connection()
    except ERRORES_DE_CONEXION as e:
        _ultimo_estado_online = False
        return False, 0, str(e)

    cursor = conn.cursor()
    subidos = 0
    try:
        for p in cache.cache_obtener_pendientes():
            if p["sync_status"] == "pending_insert":
                cursor.execute("""
                    INSERT INTO seguidores (fecha, red_social, agropecuaria, agronegocios, agroindustrial)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                """, (p["fecha"], p["red_social"], p["agropecuaria"], p["agronegocios"], p["agroindustrial"]))
                id_real = cursor.fetchone()[0]
                conn.commit()
                cache.cache_reemplazar_id(p["id"], id_real)
                subidos += 1

            elif p["sync_status"] == "pending_update":
                cursor.execute("""
                    UPDATE seguidores
                    SET agropecuaria = %s, agronegocios = %s, agroindustrial = %s
                    WHERE id = %s
                """, (p["agropecuaria"], p["agronegocios"], p["agroindustrial"], p["id"]))
                conn.commit()
                cache.cache_actualizar(p["id"], p["agropecuaria"], p["agronegocios"], p["agroindustrial"])
                subidos += 1

            elif p["sync_status"] == "pending_delete":
                cursor.execute("DELETE FROM seguidores WHERE id = %s", (p["id"],))
                conn.commit()
                cache.cache_eliminar_fila(p["id"])
                subidos += 1

        cursor.close()
        _ultimo_estado_online = True
        return True, subidos, None
    except ERRORES_DE_CONEXION as e:
        _ultimo_estado_online = False
        return False, subidos, str(e)
