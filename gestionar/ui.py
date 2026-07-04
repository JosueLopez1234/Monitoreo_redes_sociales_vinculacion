"""
gestionar/ui.py
Mixin que construye todos los widgets de VentanaGestionar,
dividido en métodos pequeños para mayor claridad:
  - Cabecera
  - Barra de filtro/búsqueda
  - Tabla con scrollbar
  - Panel de edición
"""
import tkinter as tk
from tkinter import ttk

from theme import (
    BG_DARK, BG_CARD, BG_INPUT,
    ACCENT, GREEN, YELLOW,
    TEXT, GRAY, PIE_BG,
    FONT_LABEL, FONT_LABEL_BOLD,
)

COLUMNAS = ("ID", "Fecha", "Red Social", "Agropecuaria", "Agronegocios", "Agroindustrial")


class UIMixin:
    """Construcción de la interfaz visual de la ventana Gestionar."""

    def _construir_ui(self):
        self._construir_cabecera()
        self._construir_filtro()
        self._construir_tabla_widget()
        self._construir_panel_edicion()

    # ── Cabecera ──────────────────────────────────────────────────────────────
    def _construir_cabecera(self):
        header = tk.Frame(self, bg=PIE_BG, height=50)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header,
            text="🗂️  Registros guardados — puedes editar o eliminar cualquier fila",
            bg=PIE_BG, fg="white", font=FONT_LABEL_BOLD,
        ).pack(expand=True)

    # ── Barra de filtro ───────────────────────────────────────────────────────
    def _construir_filtro(self):
        frame = tk.Frame(self, bg=BG_DARK, pady=8)
        frame.pack(fill="x", padx=15)

        tk.Label(
            frame, text="🔍 Filtrar por red social:",
            bg=BG_DARK, fg=TEXT, font=FONT_LABEL,
        ).pack(side="left")

        self.var_filtro = tk.StringVar(value="Todas")
        cb = ttk.Combobox(
            frame, textvariable=self.var_filtro,
            values=["Todas", "Facebook", "TikTok", "Instagram"],
            state="readonly", width=12, font=FONT_LABEL,
        )
        cb.pack(side="left", padx=8)
        cb.bind("<<ComboboxSelected>>", lambda e: self._cargar_tabla())

        tk.Button(
            frame, text="🔄 Recargar", command=self._cargar_tabla,
            bg=ACCENT, fg="white", relief="flat",
            font=FONT_LABEL, padx=10, cursor="hand2",
        ).pack(side="left", padx=4)

    # ── Tabla con scrollbar ───────────────────────────────────────────────────
    def _construir_tabla_widget(self):
        frame = tk.Frame(self, bg=BG_DARK)
        frame.pack(fill="both", expand=True, padx=15, pady=(0, 8))

        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("FCVT.Treeview",
                         background=BG_CARD, foreground=TEXT,
                         rowheight=26, fieldbackground=BG_CARD,
                         font=("Segoe UI", 10))
        estilo.configure("FCVT.Treeview.Heading",
                         background=BG_INPUT, foreground=ACCENT,
                         font=("Segoe UI", 10, "bold"), relief="flat")
        estilo.map("FCVT.Treeview",
                   background=[("selected", GREEN)],
                   foreground=[("selected", "white")])

        self.tree = ttk.Treeview(
            frame, columns=COLUMNAS,
            show="headings", style="FCVT.Treeview", selectmode="browse",
        )
        for col, ancho in zip(COLUMNAS, [40, 160, 100, 115, 115, 115]):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=ancho, anchor="center")

        scroll_y = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll_y.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.tree.bind("<<TreeviewSelect>>", self._al_seleccionar)

    # ── Panel de edición ──────────────────────────────────────────────────────
    def _construir_panel_edicion(self):
        frame_ed = tk.Frame(self, bg=BG_CARD, padx=20, pady=12)
        frame_ed.pack(fill="x", padx=15, pady=(0, 10))

        tk.Label(
            frame_ed, text="✏️  Editar registro seleccionado:",
            bg=BG_CARD, fg=TEXT, font=("Segoe UI", 11, "bold"),
        ).grid(row=0, column=0, columnspan=8, sticky="w", pady=(0, 8))

        self.edit_entries = {}
        for i, campo in enumerate(["Agropecuaria", "Agronegocios", "Agroindustrial"]):
            tk.Label(
                frame_ed, text=f"{campo}:",
                bg=BG_CARD, fg=TEXT, font=FONT_LABEL,
            ).grid(row=1, column=i * 2, sticky="w", padx=(0, 4))

            e = tk.Entry(
                frame_ed, width=9,
                bg=BG_INPUT, fg=TEXT, insertbackground=TEXT,
                font=("Segoe UI", 11), relief="flat", bd=4,
                justify="center", state="disabled",
            )
            e.grid(row=1, column=i * 2 + 1, padx=(0, 18))
            self.edit_entries[campo] = e

        # Fila de botones de acción
        frame_acc = tk.Frame(frame_ed, bg=BG_CARD)
        frame_acc.grid(row=2, column=0, columnspan=8, pady=(10, 0), sticky="w")

        self.btn_guardar = tk.Button(
            frame_acc, text="💾 Guardar cambios",
            command=self._guardar_edicion,
            bg=GREEN, fg="white", relief="flat",
            font=("Segoe UI", 10, "bold"), padx=12, pady=5,
            cursor="hand2", state="disabled",
        )
        self.btn_guardar.pack(side="left", padx=(0, 10))

        self.btn_eliminar = tk.Button(
            frame_acc, text="🗑️ Eliminar registro",
            command=self._eliminar,
            bg=ACCENT, fg="white", relief="flat",
            font=("Segoe UI", 10, "bold"), padx=12, pady=5,
            cursor="hand2", state="disabled",
        )
        self.btn_eliminar.pack(side="left")

        self.lbl_selec = tk.Label(
            frame_acc,
            text="← Selecciona una fila de la tabla",
            bg=BG_CARD, fg=GRAY, font=("Segoe UI", 9, "italic"),
        )
        self.lbl_selec.pack(side="left", padx=16)
