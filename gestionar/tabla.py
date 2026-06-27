"""
gestionar/tabla.py
Mixin con la lógica de la tabla:
  - Cargar/recargar filas desde la BD (con filtro opcional por red)
  - Manejar la selección de una fila y poblar el panel de edición
"""
from theme import EMOJIS, YELLOW, GRAY


class TablaMixin:
    """Carga la tabla de registros y responde a la selección del usuario."""

    # ── Carga de datos ────────────────────────────────────────────────────────
    def _cargar_tabla(self):
        from database.database import obtener_todos_los_registros

        for fila in self.tree.get_children():
            self.tree.delete(fila)

        filtro    = self.var_filtro.get()
        registros = obtener_todos_los_registros()

        if filtro != "Todas":
            registros = [r for r in registros if r["red_social"] == filtro]

        for r in registros:
            emoji = EMOJIS.get(r["red_social"], "")
            self.tree.insert("", "end", iid=str(r["id"]), values=(
                r["id"],
                r["fecha"],
                f"{emoji} {r['red_social']}",
                f"{r['Agropecuaria']:,}",
                f"{r['Agronegocios']:,}",
                f"{r['Agroindustrial']:,}",
            ))

        self._limpiar_edicion()

    # ── Selección de fila ─────────────────────────────────────────────────────
    def _al_seleccionar(self, _event=None):
        seleccion = self.tree.selection()
        if not seleccion:
            return

        valores = self.tree.item(seleccion[0], "values")
        self._id_seleccionado = int(valores[0])

        for campo, val in zip(
            ["Agropecuaria", "Agronegocios", "Agroindustrial"],
            [valores[3], valores[4], valores[5]],
        ):
            e = self.edit_entries[campo]
            e.config(state="normal")
            e.delete(0, "end")
            e.insert(0, val.replace(",", ""))

        self.btn_guardar.config(state="normal")
        self.btn_eliminar.config(state="normal")

        red = valores[2].split(" ", 1)[-1].strip()
        self.lbl_selec.config(
            text=f"Editando ID #{self._id_seleccionado}  •  {red}  •  {valores[1]}",
            fg=YELLOW,
        )
