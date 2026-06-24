"""
grafica.py - Generación de gráficas con matplotlib embebido en tkinter
"""

import tkinter as tk
from tkinter import ttk

import matplotlib
matplotlib.use("TkAgg")

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg,
    NavigationToolbar2Tk
)
import matplotlib.dates as mdates

from datetime import datetime

from database import obtener_datos, obtener_redes_disponibles
from exportar import exportar_excel, exportar_grafica


COLORES = {
    "Agropecuaria": "#2ecc71",
    "Agronegocios": "#3498db",
    "Agroindustrial": "#e74c3c",
}

ICONOS_RED = {
    "Facebook": "🔵",
    "TikTok": "⚫",
    "Instagram": "🟣",
}


class VentanaGrafica(tk.Toplevel):
    """Ventana emergente con gráfica de crecimiento/disminución."""

    def __init__(self, parent, red_social="Facebook"):
        super().__init__(parent)

        self.title(f"📊 Evolución de Seguidores — {red_social}")
        self.geometry("900x600")
        self.configure(bg="#1a1a2e")
        self.resizable(True, True)

        self.red_social = red_social
        self.fig = None

        self._construir_ui()
        self._dibujar_grafica()

    def _construir_ui(self):

        top = tk.Frame(self, bg="#1a1a2e")
        top.pack(fill="x", padx=15, pady=10)

        tk.Label(
            top,
            text="Red social:",
            bg="#1a1a2e",
            fg="white",
            font=("Segoe UI", 11)
        ).pack(side="left")

        self.var_red = tk.StringVar(value=self.red_social)

        redes = obtener_redes_disponibles()

        cb = ttk.Combobox(
            top,
            textvariable=self.var_red,
            values=redes,
            state="readonly",
            width=14,
            font=("Segoe UI", 11)
        )

        cb.pack(side="left", padx=8)
        cb.bind("<<ComboboxSelected>>",
                lambda e: self._dibujar_grafica())

        tk.Button(
            top,
            text="🔄 Actualizar",
            command=self._dibujar_grafica,
            bg="#3498db",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=10,
            cursor="hand2"
        ).pack(side="left", padx=6)

        tk.Button(
            top,
            text="📊 Exportar Excel",
            command=exportar_excel,
            bg="#27ae60",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=10,
            cursor="hand2"
        ).pack(side="left", padx=6)

        tk.Button(
            top,
            text="🖼️ Guardar gráfica",
            command=self._guardar_grafica,
            bg="#e67e22",
            fg="white",
            font=("Segoe UI", 10, "bold"),
            relief="flat",
            padx=10,
            cursor="hand2"
        ).pack(side="left", padx=6)

        self.frame_fig = tk.Frame(
            self,
            bg="#1a1a2e"
        )

        self.frame_fig.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=(0, 10)
        )

    def _guardar_grafica(self):
        if self.fig is not None:
            exportar_grafica(self.fig)

    def _dibujar_grafica(self):

        red = self.var_red.get()
        datos = obtener_datos(red)

        for widget in self.frame_fig.winfo_children():
            widget.destroy()

        if len(datos) < 1:
            tk.Label(
                self.frame_fig,
                text="⚠️ No hay datos suficientes para graficar.",
                bg="#1a1a2e",
                fg="#f39c12",
                font=("Segoe UI", 13)
            ).pack(expand=True)
            return

        fechas = [
            datetime.strptime(
                d["fecha"],
                "%Y-%m-%d %H:%M:%S"
            )
            for d in datos
        ]

        self.fig = Figure(
            figsize=(9, 4.8),
            dpi=100,
            facecolor="#16213e"
        )

        ax = self.fig.add_subplot(
            111,
            facecolor="#0f3460"
        )

        for carrera, color in COLORES.items():

            valores = [d[carrera] for d in datos]

            ax.plot(
                fechas,
                valores,
                marker="o",
                linewidth=2.5,
                color=color,
                label=carrera,
                markersize=6
            )

            if valores:
                ax.annotate(
                    f"{valores[-1]:,}",
                    xy=(fechas[-1], valores[-1]),
                    xytext=(8, 4),
                    textcoords="offset points",
                    color=color,
                    fontsize=9,
                    fontweight="bold"
                )

        ax.xaxis.set_major_formatter(
            mdates.DateFormatter("%d/%m\n%H:%M")
        )

        self.fig.autofmt_xdate(rotation=0)

        ax.tick_params(
            colors="white",
            labelsize=9
        )

        for spine in ax.spines.values():
            spine.set_color("#2c3e50")

        ax.yaxis.label.set_color("white")
        ax.xaxis.label.set_color("white")

        ax.set_ylabel(
            "Seguidores",
            color="white",
            fontsize=10
        )

        ax.set_title(
            f"{ICONOS_RED.get(red, '')} Seguidores en {red} — ULEAM FCVT",
            color="white",
            fontsize=13,
            fontweight="bold",
            pad=12
        )

        ax.legend(
            facecolor="#16213e",
            edgecolor="#2c3e50",
            labelcolor="white",
            fontsize=10
        )

        ax.grid(
            True,
            linestyle="--",
            alpha=0.3,
            color="#7f8c8d"
        )

        self.fig.tight_layout(pad=1.5)

        canvas = FigureCanvasTkAgg(
            self.fig,
            master=self.frame_fig
        )

        canvas.draw()

        canvas.get_tk_widget().pack(
            fill="both",
            expand=True
        )

        toolbar = NavigationToolbar2Tk(
            canvas,
            self.frame_fig
        )

        toolbar.update()