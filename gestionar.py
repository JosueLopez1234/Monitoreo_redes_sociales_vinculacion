"""
gestionar.py - Ventana para ver, editar y eliminar registros
"""
import tkinter as tk
from tkinter import ttk, messagebox

from database import (obtener_todos_los_registros,
                      actualizar_registro, eliminar_registro)


# ── Colores (misma paleta que gui.py) ─────────────────────────────────────────
BG_DARK  = "#1a1a2e"
BG_CARD  = "#16213e"
BG_INPUT = "#0f3460"
ACCENT   = "#e94560"
GREEN    = "#2ecc71"
BLUE     = "#3498db"
YELLOW   = "#f1c40f"
WHITE    = "#ecf0f1"
GRAY     = "#7f8c8d"

COLUMNAS = ("ID", "Fecha", "Red Social", "Agropecuaria", "Agronegocios", "Agroindustrial")
EMOJIS   = {"Facebook": "🔵", "TikTok": "⚫", "Instagram": "🟣"}


class VentanaGestionar(tk.Toplevel):
    """Ventana para ver, editar y eliminar registros guardados."""

    def __init__(self, parent, on_cambio=None):
        super().__init__(parent)
        self.title("🗂️  Gestionar Registros — ULEAM FCVT")
        self.geometry("860x520")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        # Callback para avisar a la ventana principal que hubo cambios
        self.on_cambio = on_cambio

        self._construir_ui()
        self._cargar_tabla()

    # ── Construcción de interfaz ───────────────────────────────────────────────
    def _construir_ui(self):
        # ── Header ──
        header = tk.Frame(self, bg="#0f3460", height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(header, text="🗂️  Registros guardados — puedes editar o eliminar cualquier fila",
                 bg="#0f3460", fg=WHITE,
                 font=("Segoe UI", 11, "bold")).pack(expand=True)

        # ── Buscador ──
        frame_bus = tk.Frame(self, bg=BG_DARK, pady=8)
        frame_bus.pack(fill="x", padx=15)

        tk.Label(frame_bus, text="🔍 Filtrar por red social:",
                 bg=BG_DARK, fg=WHITE, font=("Segoe UI", 10)).pack(side="left")

        self.var_filtro = tk.StringVar(value="Todas")
        opciones = ["Todas", "Facebook", "TikTok", "Instagram"]
        cb = ttk.Combobox(frame_bus, textvariable=self.var_filtro,
                          values=opciones, state="readonly", width=12,
                          font=("Segoe UI", 10))
        cb.pack(side="left", padx=8)
        cb.bind("<<ComboboxSelected>>", lambda e: self._cargar_tabla())

        tk.Button(frame_bus, text="🔄 Recargar", command=self._cargar_tabla,
                  bg=BLUE, fg=WHITE, relief="flat",
                  font=("Segoe UI", 10), padx=10, cursor="hand2").pack(side="left", padx=4)

        # ── Tabla (Treeview) ──
        frame_tabla = tk.Frame(self, bg=BG_DARK)
        frame_tabla.pack(fill="both", expand=True, padx=15, pady=(0, 8))

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("Oscuro.Treeview",
                         background=BG_CARD, foreground=WHITE,
                         rowheight=26, fieldbackground=BG_CARD,
                         font=("Segoe UI", 10))
        estilo.configure("Oscuro.Treeview.Heading",
                         background=BG_INPUT, foreground=YELLOW,
                         font=("Segoe UI", 10, "bold"), relief="flat")
        estilo.map("Oscuro.Treeview",
                   background=[("selected", ACCENT)],
                   foreground=[("selected", WHITE)])

        self.tree = ttk.Treeview(frame_tabla, columns=COLUMNAS,
                                 show="headings", style="Oscuro.Treeview",
                                 selectmode="browse")

        anchos = [40, 160, 100, 115, 115, 115]
        for col, ancho in zip(COLUMNAS, anchos):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=ancho, anchor="center")

        scroll_y = ttk.Scrollbar(frame_tabla, orient="vertical",
                                 command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._al_seleccionar)

        # ── Panel de edición ──
        frame_ed = tk.Frame(self, bg=BG_CARD, padx=20, pady=12)
        frame_ed.pack(fill="x", padx=15, pady=(0, 10))

        tk.Label(frame_ed, text="✏️  Editar registro seleccionado:",
                 bg=BG_CARD, fg=WHITE,
                 font=("Segoe UI", 11, "bold")).grid(
                     row=0, column=0, columnspan=8, sticky="w", pady=(0, 8))

        etiquetas = ["Agropecuaria", "Agronegocios", "Agroindustrial"]
        self.edit_entries = {}

        for i, campo in enumerate(etiquetas):
            tk.Label(frame_ed, text=f"{campo}:",
                     bg=BG_CARD, fg=WHITE,
                     font=("Segoe UI", 10)).grid(row=1, column=i * 2, sticky="w", padx=(0, 4))
            e = tk.Entry(frame_ed, width=9, bg=BG_INPUT, fg=WHITE,
                         insertbackground=WHITE, font=("Segoe UI", 11),
                         relief="flat", bd=4, justify="center", state="disabled")
            e.grid(row=1, column=i * 2 + 1, padx=(0, 18))
            self.edit_entries[campo] = e

        # Botones de acción
        frame_acc = tk.Frame(frame_ed, bg=BG_CARD)
        frame_acc.grid(row=2, column=0, columnspan=8, pady=(10, 0), sticky="w")

        self.btn_guardar = tk.Button(
            frame_acc, text="💾 Guardar cambios",
            command=self._guardar_edicion,
            bg=GREEN, fg=WHITE, relief="flat",
            font=("Segoe UI", 10, "bold"), padx=12, pady=5,
            cursor="hand2", state="disabled")
        self.btn_guardar.pack(side="left", padx=(0, 10))

        self.btn_eliminar = tk.Button(
            frame_acc, text="🗑️ Eliminar registro",
            command=self._eliminar,
            bg=ACCENT, fg=WHITE, relief="flat",
            font=("Segoe UI", 10, "bold"), padx=12, pady=5,
            cursor="hand2", state="disabled")
        self.btn_eliminar.pack(side="left")

        self.lbl_selec = tk.Label(frame_acc,
                                  text="← Selecciona una fila de la tabla",
                                  bg=BG_CARD, fg=GRAY,
                                  font=("Segoe UI", 9, "italic"))
        self.lbl_selec.pack(side="left", padx=16)

        self._id_seleccionado = None

    # ── Lógica de tabla ────────────────────────────────────────────────────────
    def _cargar_tabla(self):
        for fila in self.tree.get_children():
            self.tree.delete(fila)

        filtro = self.var_filtro.get()
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

    def _al_seleccionar(self, _event=None):
        seleccion = self.tree.selection()
        if not seleccion:
            return

        iid = seleccion[0]
        valores = self.tree.item(iid, "values")
        # valores = (ID, Fecha, Red, Agropecuaria, Agronegocios, Agroindustrial)

        self._id_seleccionado = int(valores[0])
        campos = ["Agropecuaria", "Agronegocios", "Agroindustrial"]
        nums   = [valores[3], valores[4], valores[5]]

        for campo, val in zip(campos, nums):
            e = self.edit_entries[campo]
            e.config(state="normal")
            e.delete(0, tk.END)
            e.insert(0, val.replace(",", ""))   # quitar separador de miles

        self.btn_guardar.config(state="normal")
        self.btn_eliminar.config(state="normal")
        red = valores[2].split(" ", 1)[-1].strip()
        self.lbl_selec.config(
            text=f"Editando ID #{self._id_seleccionado}  •  {red}  •  {valores[1]}",
            fg=YELLOW)

    # ── Acciones ───────────────────────────────────────────────────────────────
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

        ok = actualizar_registro(self._id_seleccionado, agro, agron, agroi)
        if ok:
            messagebox.showinfo("✅ Actualizado",
                                f"Registro #{self._id_seleccionado} actualizado correctamente.")
            self._cargar_tabla()
            if self.on_cambio:
                self.on_cambio()
        else:
            messagebox.showerror("Error", "No se pudo actualizar el registro.")

    def _eliminar(self):
        if self._id_seleccionado is None:
            return

        fila = self.tree.item(str(self._id_seleccionado), "values")
        red  = fila[2].split(" ", 1)[-1].strip()
        conf = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Seguro que deseas eliminar el registro #{self._id_seleccionado}?\n"
            f"Red: {red}  •  Fecha: {fila[1]}\n\n"
            "⚠️ Esta acción no se puede deshacer.")

        if not conf:
            return

        ok = eliminar_registro(self._id_seleccionado)
        if ok:
            messagebox.showinfo("🗑️ Eliminado",
                                f"Registro #{self._id_seleccionado} eliminado.")
            self._cargar_tabla()
            if self.on_cambio:
                self.on_cambio()
        else:
            messagebox.showerror("Error", "No se pudo eliminar el registro.")

    def _limpiar_edicion(self):
        self._id_seleccionado = None
        for e in self.edit_entries.values():
            e.config(state="disabled")
            e.delete(0, tk.END)
        self.btn_guardar.config(state="disabled")
        self.btn_eliminar.config(state="disabled")
        self.lbl_selec.config(text="← Selecciona una fila de la tabla", fg=GRAY)