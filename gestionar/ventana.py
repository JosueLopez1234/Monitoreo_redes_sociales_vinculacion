"""
gestionar/ventana.py
Ventana para ver, editar y eliminar registros.

Usa herencia múltiple (mixins) para mantener cada responsabilidad
en su propio archivo:

  UIMixin      → gestionar/ui.py       (construcción de widgets)
  TablaMixin   → gestionar/tabla.py    (carga y selección de filas)
  AccionesMixin→ gestionar/acciones.py (guardar, eliminar, limpiar)
"""
import tkinter as tk

from .ui       import UIMixin
from .tabla    import TablaMixin
from .acciones import AccionesMixin
from theme import BG_DARK


class VentanaGestionar(tk.Toplevel, UIMixin, TablaMixin, AccionesMixin):
    """Ventana emergente para gestionar el historial de registros."""

    def __init__(self, parent, on_cambio=None):
        super().__init__(parent)
        self.title("🗂️  Gestionar Registros — ULEAM FCVT")
        self.geometry("860x520")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        self.on_cambio         = on_cambio   # callback para refrescar la ventana principal
        self._id_seleccionado  = None        # ID de la fila actualmente seleccionada

        self._construir_ui()   # UIMixin
        self._cargar_tabla()   # TablaMixin
