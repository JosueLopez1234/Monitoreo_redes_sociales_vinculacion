"""
graficas.py - Gráfica de crecimiento embebida en tkinter
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import matplotlib.dates as mdates

from database.database import obtener_datos, obtener_redes_disponibles
from services.exportar import exportar_excel, exportar_grafica, generar_pdf
from theme import (
    COLORES_CARRERA, ICONOS_RED,
    PLOT_BG, PLOT_AX_BG, PLOT_SPINE, PLOT_GRID, PLOT_TEXT,
    FONT_LABEL,
)


class VentanaGrafica(tk.Toplevel):
    """Ventana emergente con gráfica de crecimiento de seguidores."""

    def __init__(self, parent, red_social="Facebook"):
        super().__init__(parent)
        self.title(f"📊 Evolución de Seguidores — {red_social}")
        self.geometry("900x600")
        self.configure(bg=PLOT_BG)
        self.resizable(True, True)

        self.red_social = red_social
        self.fig = None

        self._construir_ui()
        self._dibujar_grafica()

    # ── UI ─────────────────────────────────────────────────────────────────────
    def _construir_ui(self):
        top = tk.Frame(self, bg=PLOT_BG)
        top.pack(fill="x", padx=15, pady=10)

        tk.Label(top, text="Red social:", bg=PLOT_BG, fg=PLOT_TEXT,
                 font=FONT_LABEL).pack(side="left")

        self.var_red = tk.StringVar(value=self.red_social)
        cb = ttk.Combobox(
            top, textvariable=self.var_red,
            values=obtener_redes_disponibles(),
            state="readonly", width=14, font=FONT_LABEL,
        )
        cb.pack(side="left", padx=8)
        cb.bind("<<ComboboxSelected>>", lambda e: self._dibujar_grafica())

        # ── Botones de toolbar ────────────────────────────────────────────────
        botones = [
            ("🔄 Actualizar",     self._dibujar_grafica, "#4E8A1E"),
            ("📊 Exportar Excel", lambda: exportar_excel(self.var_red.get()), "#5E8C31"),
            ("🖼️ Guardar gráfica", self._guardar_grafica, "#F28C28"),
            ("📄 Generar PDF",    self._generar_pdf,     "#c0392b"),
        ]
        for texto, cmd, color in botones:
            tk.Button(
                top, text=texto, command=cmd,
                bg=color, fg="white",
                font=("Segoe UI", 10, "bold"),
                relief="flat", padx=10, cursor="hand2",
            ).pack(side="left", padx=6)

        self.frame_fig = tk.Frame(self, bg=PLOT_BG)
        self.frame_fig.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    # ── Gráfica ────────────────────────────────────────────────────────────────
    def _dibujar_grafica(self):
        red   = self.var_red.get()
        datos = obtener_datos(red)

        for w in self.frame_fig.winfo_children():
            w.destroy()

        if not datos:
            tk.Label(
                self.frame_fig,
                text="⚠️ No hay datos suficientes para graficar.",
                bg=PLOT_BG, fg="#F28C28",
                font=("Segoe UI", 13),
            ).pack(expand=True)
            return

        fechas = [datetime.strptime(d["fecha"], "%Y-%m-%d %H:%M:%S") for d in datos]

        self.fig = Figure(figsize=(9, 4.8), dpi=100, facecolor=PLOT_BG)
        ax = self.fig.add_subplot(111, facecolor=PLOT_AX_BG)

        for carrera, color in COLORES_CARRERA.items():
            valores = [d[carrera] for d in datos]
            ax.plot(fechas, valores, marker="o", linewidth=2.5,
                    color=color, label=carrera, markersize=6)

            if valores:
                ax.annotate(
                    f"{valores[-1]:,}",
                    xy=(fechas[-1], valores[-1]),
                    xytext=(8, 4), textcoords="offset points",
                    color=color, fontsize=9, fontweight="bold",
                )

        # ── Estilo de ejes ────────────────────────────────────────────────────
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m\n%H:%M"))
        self.fig.autofmt_xdate(rotation=0)

        ax.tick_params(colors=PLOT_TEXT, labelsize=9)
        for spine in ax.spines.values():
            spine.set_color(PLOT_SPINE)

        ax.set_ylabel("Seguidores", color=PLOT_TEXT, fontsize=10)
        ax.set_title(
            f"{ICONOS_RED.get(red, '')} Seguidores en {red} — ULEAM FCVT",
            color=PLOT_TEXT, fontsize=13, fontweight="bold", pad=12,
        )
        ax.legend(facecolor=PLOT_BG, edgecolor=PLOT_SPINE,
                  labelcolor=PLOT_TEXT, fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.3, color=PLOT_GRID)
        self.fig.tight_layout(pad=1.5)

        # ── Canvas ────────────────────────────────────────────────────────────
        canvas = FigureCanvasTkAgg(self.fig, master=self.frame_fig)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        NavigationToolbar2Tk(canvas, self.frame_fig).update()

    def _guardar_grafica(self):
        if self.fig is not None:
            exportar_grafica(self.fig)

    def _generar_pdf(self):
        from tkinter import messagebox
        try:
            generar_pdf(self.var_red.get(), fig_grafica=self.fig)
        except Exception as e:
            messagebox.showerror("Error PDF", str(e))