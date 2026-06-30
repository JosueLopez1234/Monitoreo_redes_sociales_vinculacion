"""
database.py - Manejo de la base de datos SQLite
"""
import sqlite3
import sys
import os
from datetime import datetime


def _carpeta_persistente():
    """
    Devuelve la carpeta donde debe vivir datos_uleam.db.

    - Corriendo como script normal (python main.py): la carpeta raíz del
      proyecto (dos niveles arriba de este archivo).
    - Corriendo como .exe empaquetado con PyInstaller: PyInstaller extrae
      el código a una carpeta TEMPORAL distinta cada vez (sys._MEIPASS).
      Si guardáramos el .db ahí, los datos se "perderían" (en realidad
      quedarían en una carpeta temporal) cada vez que se cierra la app.
      Por eso, en modo empaquetado, usamos la carpeta donde está el .exe
      (sys.executable), que sí es estable entre ejecuciones.
    """
    if getattr(sys, "frozen", False):
        # Empaquetado con PyInstaller: usar la carpeta del .exe
        return os.path.dirname(os.path.abspath(sys.executable))
    # Ejecutando como script normal: usar la carpeta raíz del proyecto
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


DB_PATH = os.path.join(_carpeta_persistente(), "datos_uleam.db")


def get_connection():
    """Retorna una conexión a la base de datos."""
    return sqlite3.connect(DB_PATH)


def inicializar_db():
    """Crea las tablas si no existen e inserta datos iniciales."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seguidores (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha       TEXT NOT NULL,
            red_social  TEXT NOT NULL,
            agropecuaria   INTEGER DEFAULT 0,
            agronegocios   INTEGER DEFAULT 0,
            agroindustrial INTEGER DEFAULT 0
        )
    """)
    conn.commit()

    # Insertar datos iniciales del acta del 8 de mayo de 2026 si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM seguidores")
    if cursor.fetchone()[0] == 0:
        datos_iniciales = [
            ("2026-05-08 14:00:00", "Facebook",   3022, 1635, 200),
            ("2026-05-08 14:00:00", "TikTok",      163,   38,  95),
            ("2026-05-08 14:00:00", "Instagram",    61,  110,  45),
        ]
        cursor.executemany("""
            INSERT INTO seguidores (fecha, red_social, agropecuaria, agronegocios, agroindustrial)
            VALUES (?, ?, ?, ?, ?)
        """, datos_iniciales)
        conn.commit()

    conn.close()


def guardar_registro(red_social, agropecuaria, agronegocios, agroindustrial):
    """Inserta un nuevo registro en la base de datos."""
    conn = get_connection()
    cursor = conn.cursor()
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO seguidores (fecha, red_social, agropecuaria, agronegocios, agroindustrial)
        VALUES (?, ?, ?, ?, ?)
    """, (fecha, red_social, agropecuaria, agronegocios, agroindustrial))
    conn.commit()
    conn.close()
    return fecha


def obtener_datos(red_social="Facebook"):
    """Retorna todos los registros de una red social como lista de dicts."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fecha, agropecuaria, agronegocios, agroindustrial
        FROM seguidores
        WHERE red_social = ?
        ORDER BY fecha ASC
    """, (red_social,))
    filas = cursor.fetchall()
    conn.close()
    return [
        {
            "fecha": f[0],
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
        WHERE red_social = ?
        ORDER BY fecha DESC
        LIMIT 1
    """, (red_social,))
    fila = cursor.fetchone()
    conn.close()
    if fila:
        return {"fecha": fila[0], "Agropecuaria": fila[1],
                "Agronegocios": fila[2], "Agroindustrial": fila[3]}
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
    conn.close()
    return [
        {
            "id":            f[0],
            "fecha":         f[1],
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
        SET agropecuaria = ?, agronegocios = ?, agroindustrial = ?
        WHERE id = ?
    """, (agropecuaria, agronegocios, agroindustrial, id_registro))
    conn.commit()
    afectadas = cursor.rowcount
    conn.close()
    return afectadas > 0


def eliminar_registro(id_registro):
    """Elimina un registro por su ID."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM seguidores WHERE id = ?", (id_registro,))
    conn.commit()
    afectadas = cursor.rowcount
    conn.close()
    return afectadas > 0


def obtener_redes_disponibles():
    """Retorna las redes sociales con registros."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT red_social FROM seguidores ORDER BY red_social")
    redes = [r[0] for r in cursor.fetchall()]
    conn.close()
    return redes or ["Facebook", "TikTok", "Instagram"]

