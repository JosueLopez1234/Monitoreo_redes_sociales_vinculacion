"""
gestionar/acciones.py
Mixin con las acciones sobre registros:
  - Guardar cambios en un registro existente
  - Eliminar un registro (con confirmación)
  - Limpiar el panel de edición
"""
from tkinter import messagebox

from database.database import actualizar_registro, eliminar_registro
from theme import GRAY


class AccionesMixin:
    """Acciones de edición y eliminación de registros."""

    # ── Guardar edición ───────────────────────────────────────────────────────
    def _guardar_edicion(self):
        if self._id_seleccionado is None:
            return
        try:
            agro  = int(self.edit_entries["Agropecuaria"].get())
            agron = int(self.edit_entries["Agronegocios"].get())
            agroi = int(self.edit_entries["Agroindustrial"].get())
        except ValueError:
            messagebox.showerror("Error", "Los valores deben ser números enteros.")
            return

        if actualizar_registro(self._id_seleccionado, agro, agron, agroi):
            messagebox.showinfo(
                "✅ Actualizado",
                f"Registro #{self._id_seleccionado} actualizado correctamente.")
            self._cargar_tabla()
            if self.on_cambio:
                self.on_cambio()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el registro.")

    # ── Eliminar registro ─────────────────────────────────────────────────────
    def _eliminar(self):
        if self._id_seleccionado is None:
            return

        fila = self.tree.item(str(self._id_seleccionado), "values")
        red  = fila[2].split(" ", 1)[-1].strip()

        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que deseas eliminar el registro #{self._id_seleccionado}?\n"
            f"Red: {red}  •  Fecha: {fila[1]}\n\n⚠️ Esta acción no se puede deshacer.",
        ):
            return

        if eliminar_registro(self._id_seleccionado):
            messagebox.showinfo("🗑️ Eliminado",
                                f"Registro #{self._id_seleccionado} eliminado.")
            self._cargar_tabla()
            if self.on_cambio:
                self.on_cambio()
        else:
            messagebox.showerror("Error", "No se pudo eliminar el registro.")

    # ── Limpiar panel ─────────────────────────────────────────────────────────
    def _limpiar_edicion(self):
        self._id_seleccionado = None
        for e in self.edit_entries.values():
            e.config(state="disabled")
            e.delete(0, "end")
        self.btn_guardar.config(state="disabled")
        self.btn_eliminar.config(state="disabled")
        self.lbl_selec.config(text="← Selecciona una fila de la tabla", fg=GRAY)
