"""
gui/actions.py
Mixin con los botones de la ventana principal y las acciones que disparan:
  - Guardar registro
  - Ver gráfica
  - Ver/editar historial
  - Limpiar campos
  - Generar PDF
"""
import tkinter as tk
from tkinter import messagebox

from database.database import guardar_registro
from services.graficas import VentanaGrafica
from services.exportar import generar_pdf
from validaciones import validar_valores_seguidores
from theme import (
    BG_DARK, BG_INPUT, GREEN, BLUE, GRAY,
    CARRERAS, FONT_BTN,
)


class ActionsMixin:
    """Botones de la barra de acciones y sus handlers."""

    # ── Barra de botones ──────────────────────────────────────────────────────
    def _construir_botones(self):
        frame_btn = tk.Frame(self, bg=BG_DARK)
        frame_btn.pack(pady=10)

        def btn(texto, cmd, color, fg="white"):
            return tk.Button(
                frame_btn, text=texto, command=cmd,
                bg=color, fg=fg, relief="flat",
                font=FONT_BTN, padx=16, pady=8, cursor="hand2",
                activebackground=BG_INPUT, activeforeground="white",
            )

        btn("💾  Guardar registro",       self._guardar,        GREEN   ).pack(side="left", padx=8)
        btn("📊  Ver gráfica",            self._ver_grafica,    BLUE    ).pack(side="left", padx=8)
        btn("📋  Ver / Editar historial", self._ver_historial,  "#5B4FBE").pack(side="left", padx=8)
        btn("🗑️  Limpiar campos",         self._limpiar,        GRAY    ).pack(side="left", padx=8)
        btn("📄  Generar PDF",            self._generar_pdf,    "#c0392b").pack(side="left", padx=8)
        btn("🔄  Sincronizar ahora",      self._sincronizar_ahora, "#5B4FBE").pack(side="left", padx=8)

    # ── Guardar registro ──────────────────────────────────────────────────────
    def _guardar(self):
        red = self.var_red.get()
        try:
            valores = {c: int(self.entries[c].get()) for c in CARRERAS}
        except ValueError:
            messagebox.showerror(
                "Error de entrada",
                "Por favor ingresa solo números enteros en los tres campos.")
            return

        ok, mensaje_error = validar_valores_seguidores(valores)
        if not ok:
            messagebox.showerror("Dato fuera de rango", mensaje_error)
            return

        try:
            fecha = guardar_registro(
                red,
                valores["Agropecuaria"],
                valores["Agronegocios"],
                valores["Agroindustrial"],
            )
        except Exception as e:
            messagebox.showerror(
                "No se pudo guardar",
                "Ocurrió un problema inesperado al guardar el registro.\n\n"
                f"Detalle técnico: {e}")
            return

        messagebox.showinfo(
            "✅ Registro guardado",
            f"Se guardaron los datos de {red}\nFecha: {fecha}")
        self._actualizar_tarjetas()
        self._limpiar()

    # ── Ver gráfica ───────────────────────────────────────────────────────────
    def _ver_grafica(self):
        try:
            VentanaGrafica(self, self.var_red.get())
        except Exception as e:
            messagebox.showerror(
                "No se pudo abrir la gráfica",
                f"Ocurrió un problema al generar la gráfica.\n\nDetalle técnico: {e}")

    # ── Ver historial ─────────────────────────────────────────────────────────
    def _ver_historial(self):
        # Importación tardía para evitar dependencia circular
        try:
            from gestionar import VentanaGestionar
            VentanaGestionar(self, on_cambio=self._actualizar_tarjetas)
        except Exception as e:
            messagebox.showerror(
                "No se pudo abrir el historial",
                f"Ocurrió un problema al abrir el historial.\n\nDetalle técnico: {e}")

    # ── Limpiar campos ────────────────────────────────────────────────────────
    def _limpiar(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    # ── Generar PDF ───────────────────────────────────────────────────────────
    def _generar_pdf(self):
        try:
            generar_pdf(self.var_red.get())
        except Exception as e:
            messagebox.showerror("Error PDF", str(e))

    # ── Sincronizar ahora ─────────────────────────────────────────────────────
    def _sincronizar_ahora(self):
        from database.database import hay_cambios_pendientes
        if not hay_cambios_pendientes():
            messagebox.showinfo("🔄 Sincronizar", "No hay registros pendientes por subir.")
            return
        # La revisión real la hace el hilo de fondo; aquí solo forzamos
        # que corra de inmediato en vez de esperar el intervalo.
        self.hilo_sync.sincronizar_ahora()
