import sqlite3
import pandas as pd
from tkinter import filedialog, messagebox

DB_PATH = "datos_uleam.db"


def exportar_excel():
    
    
    try:
        archivo = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel", "*.xlsx")],
            title="Guardar Excel"
        )

        if not archivo:
            return

        conn = sqlite3.connect(DB_PATH)

        df = pd.read_sql_query("""
            SELECT *
            FROM seguidores
            ORDER BY fecha DESC
        """, conn)

        conn.close()

        df.to_excel(archivo, index=False)

        messagebox.showinfo(
            "Éxito",
            f"Archivo exportado:\n{archivo}"
        )

    except Exception as e:
        messagebox.showerror(
            "Error",
            str(e)
        )
def exportar_grafica(figura):
    try:
        archivo = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG", "*.png"),
                ("JPEG", "*.jpg")
            ],
            title="Guardar gráfica"
        )

        if not archivo:
            return

        figura.savefig(
            archivo,
            dpi=300,
            bbox_inches="tight"
        )

        messagebox.showinfo(
            "Éxito",
            f"Gráfica guardada:\n{archivo}"
        )

    except Exception as e:
        messagebox.showerror(
            "Error",
            str(e)
        )