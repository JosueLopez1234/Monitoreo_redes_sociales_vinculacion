"""
migrar_a_postgres.py
---------------------
Copia todos los registros existentes en datos_uleam.db (SQLite) hacia la
base de datos PostgreSQL configurada en database/database.py.

Uso:
    1. Asegúrate de que database/database.py ya apunta a Postgres y que
       ejecutaste la app una vez para que se cree la tabla "seguidores"
       (o simplemente corre inicializar_db() abajo).
    2. Coloca este archivo en la raíz del proyecto (junto a main.py).
    3. Ejecuta:  python migrar_a_postgres.py
"""
import sqlite3
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import explícito del módulo de Postgres (ya debe estar en database/database.py)
from database.database import get_connection, inicializar_db

SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datos_uleam.db")


def migrar():
    if not os.path.exists(SQLITE_PATH):
        print(f"❌ No se encontró {SQLITE_PATH}. Verifica la ruta.")
        return

    # Asegura que la tabla exista en Postgres antes de insertar
    inicializar_db()

    # Leer todos los registros de SQLite
    conn_sqlite = sqlite3.connect(SQLITE_PATH)
    cur_sqlite = conn_sqlite.cursor()
    cur_sqlite.execute("""
        SELECT fecha, red_social, agropecuaria, agronegocios, agroindustrial
        FROM seguidores
        ORDER BY fecha ASC
    """)
    filas = cur_sqlite.fetchall()
    conn_sqlite.close()

    if not filas:
        print("⚠️ No hay registros en la base de datos SQLite.")
        return

    print(f"📦 {len(filas)} registros encontrados en SQLite. Migrando a PostgreSQL...")

    # Conectar a Postgres e insertar, evitando duplicados exactos
    conn_pg = get_connection()
    cur_pg = conn_pg.cursor()

    # Vaciar los datos semilla de ejemplo antes de migrar, para no mezclarlos
    # con el histórico real. Si prefieres conservarlos, comenta esta línea.
    cur_pg.execute("DELETE FROM seguidores")
    conn_pg.commit()

    insertados = 0
    for fecha, red_social, agro, agroneg, agroind in filas:
        cur_pg.execute("""
            INSERT INTO seguidores (fecha, red_social, agropecuaria, agronegocios, agroindustrial)
            VALUES (%s, %s, %s, %s, %s)
        """, (fecha, red_social, agro, agroneg, agroind))
        insertados += 1

    conn_pg.commit()
    cur_pg.close()
    conn_pg.close()

    print(f"✅ Migración completa: {insertados} registros copiados a PostgreSQL.")


if __name__ == "__main__":
    migrar()