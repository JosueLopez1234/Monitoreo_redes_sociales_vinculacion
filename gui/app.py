"""
gui/app.py
Ventana principal de la aplicación.

Usa herencia múltiple (mixins) para mantener cada responsabilidad
en su propio archivo:

  HeaderMixin  → gui/header.py   (título, selector de red, pie)
  CardsMixin   → gui/cards.py    (tarjetas de seguidores por carrera)
  FormMixin    → gui/form.py     (formulario de ingreso + reloj)
  ActionsMixin → gui/actions.py  (botones y sus handlers)
"""
import tkinter as tk

from .header  import HeaderMixin
from .cards   import CardsMixin
from .form    import FormMixin
from .actions import ActionsMixin
from theme import BG_DARK
from services.sync_thread import HiloSincronizacion


class App(tk.Tk, HeaderMixin, CardsMixin, FormMixin, ActionsMixin):
    """Ventana raíz de la aplicación ULEAM – Monitor de Redes Sociales."""

    def __init__(self):
        super().__init__()
        self.title("📡 Monitor de Redes Sociales — ULEAM FCVT")
        self.geometry("780x680")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # Estado compartido entre mixins
        self.var_red    = tk.StringVar(value="Facebook")
        self.entries    = {}   # entradas del formulario  (FormMixin)
        self.labels_seg = {}   # etiquetas de conteo      (CardsMixin)
        self.labels_dif = {}   # etiquetas de diferencia  (CardsMixin)

        # Construcción de la interfaz (orden importa para el layout)
        self._construir_header()            # HeaderMixin
        self._construir_selector_red()      # HeaderMixin
        self._construir_tarjetas_carreras() # CardsMixin
        self._construir_formulario()        # FormMixin
        self._construir_botones()           # ActionsMixin
        self._construir_pie()               # HeaderMixin

        self._actualizar_tarjetas()         # CardsMixin

        # Hilo en segundo plano: revisa conexión y sube pendientes solo.
        self.hilo_sync = HiloSincronizacion(callback_estado=self._on_estado_sync)
        self.hilo_sync.start()

    def _on_estado_sync(self, online, pendientes, mensaje):
        """Se llama desde el hilo de fondo; Tkinter exige pasar por
        `after` para tocar la interfaz desde otro hilo."""
        def actualizar():
            self.actualizar_estado_conexion(online, pendientes, mensaje)
            if pendientes == 0 and hasattr(self, "_actualizar_tarjetas"):
                self._actualizar_tarjetas()
        try:
            self.after(0, actualizar)
        except tk.TclError:
            pass  # la ventana ya se cerró
