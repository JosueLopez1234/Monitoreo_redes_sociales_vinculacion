"""
database.py - Manejo de la base de datos SQLite
"""

import os
import sys
import sqlite3
from datetime import datetime


# ==========================================================
# RUTA DE LA BASE DE DATOS
# ==========================================================

def obtener_ruta_db():
    """
    Devuelve la ruta correcta de la base de datos tanto
    cuando se ejecuta desde Python como desde el ejecutable.
    """

    if getattr(sys, "frozen", False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(
            os.path.abspath(__file__)
        )

    ruta = os.path.join(
        base_path,
        "web",
        "datos_uleam.db"
    )

    if not os.path.exists(ruta):
        ruta = os.path.join(
            base_path,
            "datos_uleam.db"
        )

    return ruta


DB_PATH = obtener_ruta_db()


# ==========================================================
# CONEXIÓN
# ==========================================================

def get_connection():
    """Retorna una conexión a la base de datos."""

    conexion = sqlite3.connect(DB_PATH)

    conexion.row_factory = sqlite3.Row

    return conexion


# ==========================================================
# INICIALIZAR BD
# ==========================================================

def inicializar_db():
    """Crea las tablas si no existen e inserta datos iniciales."""

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        CREATE TABLE IF NOT EXISTS seguidores (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            fecha TEXT NOT NULL,

            red_social TEXT NOT NULL,

            agropecuaria INTEGER DEFAULT 0,

            agronegocios INTEGER DEFAULT 0,

            agroindustrial INTEGER DEFAULT 0

        )

    """)

    conn.commit()

    cursor.execute(

        "SELECT COUNT(*) FROM seguidores"

    )

    if cursor.fetchone()[0] == 0:

        datos_iniciales = [

            ("2026-05-08 14:00:00", "Facebook", 3022, 1635, 200),

            ("2026-05-08 14:00:00", "TikTok", 163, 38, 95),

            ("2026-05-08 14:00:00", "Instagram", 61, 110, 45),

        ]

        cursor.executemany(

            """

            INSERT INTO seguidores

            (

                fecha,

                red_social,

                agropecuaria,

                agronegocios,

                agroindustrial

            )

            VALUES

            (?, ?, ?, ?, ?)

            """,

            datos_iniciales,

        )

        conn.commit()

    conn.close()


# ==========================================================
# GUARDAR REGISTRO
# ==========================================================

def guardar_registro(

    red_social,

    agropecuaria,

    agronegocios,

    agroindustrial,

):

    conn = get_connection()

    cursor = conn.cursor()

    fecha = datetime.now().strftime(

        "%Y-%m-%d %H:%M:%S"

    )

    cursor.execute(

        """

        INSERT INTO seguidores

        (

            fecha,

            red_social,

            agropecuaria,

            agronegocios,

            agroindustrial

        )

        VALUES

        (?, ?, ?, ?, ?)

        """,

        (

            fecha,

            red_social,

            agropecuaria,

            agronegocios,

            agroindustrial,

        ),

    )

    conn.commit()

    conn.close()

    return fecha
# ==========================================================
# OBTENER DATOS POR RED SOCIAL
# ==========================================================

def obtener_datos(red_social="Facebook"):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT

            fecha,

            agropecuaria,

            agronegocios,

            agroindustrial

        FROM seguidores

        WHERE red_social = ?

        ORDER BY fecha ASC

        """,

        (red_social,)

    )

    filas = cursor.fetchall()

    conn.close()

    return [

        {

            "fecha": fila["fecha"],

            "Agropecuaria": fila["agropecuaria"],

            "Agronegocios": fila["agronegocios"],

            "Agroindustrial": fila["agroindustrial"],

        }

        for fila in filas

    ]


# ==========================================================
# OBTENER ÚLTIMO REGISTRO
# ==========================================================

def obtener_ultimo_registro(red_social="Facebook"):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT

            fecha,

            agropecuaria,

            agronegocios,

            agroindustrial

        FROM seguidores

        WHERE red_social = ?

        ORDER BY fecha DESC

        LIMIT 1

        """,

        (red_social,)

    )

    fila = cursor.fetchone()

    conn.close()

    if fila is None:

        return None

    return {

        "fecha": fila["fecha"],

        "Agropecuaria": fila["agropecuaria"],

        "Agronegocios": fila["agronegocios"],

        "Agroindustrial": fila["agroindustrial"],

    }


# ==========================================================
# OBTENER TODOS LOS REGISTROS
# ==========================================================

def obtener_todos_los_registros():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT

            id,

            fecha,

            red_social,

            agropecuaria,

            agronegocios,

            agroindustrial

        FROM seguidores

        ORDER BY fecha DESC, red_social ASC

        """

    )

    filas = cursor.fetchall()

    conn.close()

    return [

        {

            "id": fila["id"],

            "fecha": fila["fecha"],

            "red_social": fila["red_social"],

            "Agropecuaria": fila["agropecuaria"],

            "Agronegocios": fila["agronegocios"],

            "Agroindustrial": fila["agroindustrial"],

        }

        for fila in filas

    ]


# ==========================================================
# ACTUALIZAR REGISTRO
# ==========================================================

def actualizar_registro(

    id_registro,

    agropecuaria,

    agronegocios,

    agroindustrial,

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        UPDATE seguidores

        SET

            agropecuaria = ?,

            agronegocios = ?,

            agroindustrial = ?

        WHERE id = ?

        """,

        (

            agropecuaria,

            agronegocios,

            agroindustrial,

            id_registro,

        ),

    )

    conn.commit()

    actualizado = cursor.rowcount > 0

    conn.close()

    return actualizado


# ==========================================================
# ELIMINAR REGISTRO
# ==========================================================

def eliminar_registro(id_registro):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        "DELETE FROM seguidores WHERE id = ?",

        (id_registro,)

    )

    conn.commit()

    eliminado = cursor.rowcount > 0

    conn.close()

    return eliminado


# ==========================================================
# REDES DISPONIBLES
# ==========================================================

def obtener_redes_disponibles():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(

        """

        SELECT DISTINCT red_social

        FROM seguidores

        ORDER BY red_social

        """

    )

    redes = [

        fila["red_social"]

        for fila in cursor.fetchall()

    ]

    conn.close()

    if not redes:

        return [

            "Facebook",

            "Instagram",

            "TikTok",

        ]

    return redes