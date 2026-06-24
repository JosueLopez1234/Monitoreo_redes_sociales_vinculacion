"""
gui.py - Ventana principal del monitor de redes sociales ULEAM
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from database import guardar_registro, obtener_ultimo_registro, obtener_datos
from graficas import VentanaGrafica
from gestionar import VentanaGestionar
from reportes import generar_pdf

# ── Paleta de colores ──────────────────────────────────────────────────────────
BG_DARK   = "#1a1a2e"
BG_CARD   = "#16213e"
BG_INPUT  = "#0f3460"
ACCENT    = "#e94560"
GREEN     = "#2ecc71"
BLUE      = "#3498db"
YELLOW    = "#f1c40f"
WHITE     = "#ecf0f1"
GRAY      = "#7f8c8d"

CARRERAS  = ["Agropecuaria", "Agronegocios", "Agroindustrial"]
REDES     = ["Facebook", "TikTok", "Instagram"]
EMOJIS    = {"Facebook": "🔵", "TikTok": "⚫", "Instagram": "🟣"}


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📡 Monitor de Redes Sociales — ULEAM FCVT")
        self.geometry("780x680")
        self.configure(bg=BG_DARK)
        self.resizable(True, True)

        self.var_red    = tk.StringVar(value="Facebook")
        self.entries    = {}      # {carrera: Entry widget}
        self.labels_seg = {}      # {carrera: Label con número actual}
        self.labels_dif = {}      # {carrera: Label con diferencia}

        self._construir_header()
        self._construir_selector_red()
        self._construir_tarjetas_carreras()
        self._construir_formulario()
        self._construir_botones()
        self._construir_pie()

        self._actualizar_tarjetas()
                
    # ── Header ─────────────────────────────────────────────────────────────────
    
    def _construir_header(self):
        frame = tk.Frame(self, bg=ACCENT, height=70)
        frame.pack(fill="x")
        frame.pack_propagate(False)

        tk.Label(frame,
                 text="🌿  MONITOR DE REDES SOCIALES  •  ULEAM – FCVT",
                 bg=ACCENT, fg=WHITE,
                 font=("Segoe UI", 15, "bold")).pack(expand=True)

    # ── Selector de red social ─────────────────────────────────────────────────
    def _construir_selector_red(self):
        frame = tk.Frame(self, bg=BG_DARK, pady=10)
        frame.pack(fill="x", padx=20)

        tk.Label(frame, text="Selecciona la red social:",
                 bg=BG_DARK, fg=WHITE,
                 font=("Segoe UI", 11, "bold")).pack(side="left")

        for red in REDES:
            rb = tk.Radiobutton(
                frame, text=f"{EMOJIS[red]} {red}",
                variable=self.var_red, value=red,
                command=self._actualizar_tarjetas,
                bg=BG_DARK, fg=WHITE, selectcolor=BG_INPUT,
                activebackground=BG_DARK, activeforeground=YELLOW,
                font=("Segoe UI", 11), indicatoron=True, cursor="hand2")
            rb.pack(side="left", padx=12)

    # ── Tarjetas de resumen ────────────────────────────────────────────────────
    def _construir_tarjetas_carreras(self):
        self.frame_tarjetas = tk.Frame(self, bg=BG_DARK)
        self.frame_tarjetas.pack(fill="x", padx=20, pady=8)

        COLORES_CARRERA = {
            "Agropecuaria":   "#2ecc71",
            "Agronegocios":   "#3498db",
            "Agroindustrial": "#e74c3c",
        }

        for carrera in CARRERAS:
            color = COLORES_CARRERA[carrera]
            card = tk.Frame(self.frame_tarjetas, bg=BG_CARD,
                            relief="flat", bd=0, padx=12, pady=10)
            card.pack(side="left", expand=True, fill="both", padx=6)

            # Barra de color superior
            tk.Frame(card, bg=color, height=4).pack(fill="x")

            tk.Label(card, text=carrera, bg=BG_CARD, fg=color,
                     font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(4, 0))

            lbl_seg = tk.Label(card, text="–", bg=BG_CARD, fg=WHITE,
                               font=("Segoe UI", 22, "bold"))
            lbl_seg.pack(anchor="w")

            lbl_dif = tk.Label(card, text="", bg=BG_CARD, fg=GRAY,
                               font=("Segoe UI", 9))
            lbl_dif.pack(anchor="w")

            tk.Label(card, text="seguidores", bg=BG_CARD, fg=GRAY,
                     font=("Segoe UI", 8)).pack(anchor="w")

            self.labels_seg[carrera] = lbl_seg
            self.labels_dif[carrera] = lbl_dif

    def _actualizar_tarjetas(self):
        red = self.var_red.get()
        datos = obtener_datos(red)

        if datos:
            ultimo = datos[-1]
            anterior = datos[-2] if len(datos) >= 2 else None

            for carrera in CARRERAS:
                val = ultimo[carrera]
                self.labels_seg[carrera].config(text=f"{val:,}")

                if anterior:
                    diff = val - anterior[carrera]
                    if diff > 0:
                        txt, col = f"▲ +{diff:,} desde el registro anterior", GREEN
                    elif diff < 0:
                        txt, col = f"▼ {diff:,} desde el registro anterior", ACCENT
                    else:
                        txt, col = "Sin cambios", GRAY
                    self.labels_dif[carrera].config(text=txt, fg=col)
                else:
                    self.labels_dif[carrera].config(text="Primer registro", fg=YELLOW)
        else:
            for carrera in CARRERAS:
                self.labels_seg[carrera].config(text="–")
                self.labels_dif[carrera].config(text="Sin datos aún", fg=GRAY)

    # ── Formulario de ingreso ──────────────────────────────────────────────────
    def _construir_formulario(self):
        frame_form = tk.Frame(self, bg=BG_CARD, padx=20, pady=15)
        frame_form.pack(fill="x", padx=20, pady=6)

        tk.Label(frame_form, text="✏️  Registrar nuevos seguidores",
                 bg=BG_CARD, fg=WHITE,
                 font=("Segoe UI", 12, "bold")).grid(
                     row=0, column=0, columnspan=4, sticky="w", pady=(0, 10))

        for i, carrera in enumerate(CARRERAS):
            tk.Label(frame_form, text=f"{carrera}:",
                     bg=BG_CARD, fg=WHITE,
                     font=("Segoe UI", 10)).grid(
                         row=1, column=i * 2, sticky="w", padx=(0, 6))

            entry = tk.Entry(frame_form, width=10,
                             bg=BG_INPUT, fg=WHITE, insertbackground=WHITE,
                             font=("Segoe UI", 12), relief="flat", bd=4,
                             justify="center")
            entry.grid(row=1, column=i * 2 + 1, padx=(0, 20))
            self.entries[carrera] = entry

        # Fecha y hora actual (informativo)
        self.lbl_fecha = tk.Label(frame_form,
                                  text=f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                                  bg=BG_CARD, fg=GRAY, font=("Segoe UI", 9))
        self.lbl_fecha.grid(row=2, column=0, columnspan=6, sticky="w", pady=(8, 0))
        self._tick_reloj()

    def _tick_reloj(self):
        self.lbl_fecha.config(
            text=f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.after(1000, self._tick_reloj)

    # ── Botones ────────────────────────────────────────────────────────────────
    def _construir_botones(self):
        frame_btn = tk.Frame(self, bg=BG_DARK)
        frame_btn.pack(pady=10)

        def btn(parent, texto, cmd, color):
            return tk.Button(parent, text=texto, command=cmd,
                             bg=color, fg=WHITE, relief="flat",
                             font=("Segoe UI", 11, "bold"),
                             padx=16, pady=8, cursor="hand2",
                             activebackground=BG_INPUT,
                             activeforeground=WHITE)

        btn(frame_btn, "💾  Guardar registro",
            self._guardar, GREEN).pack(side="left", padx=8)

        btn(frame_btn, "📊  Ver gráfica de crecimiento",
            self._ver_grafica, BLUE).pack(side="left", padx=8)

        btn(frame_btn, "📋  Ver / Editar historial",
            self._ver_historial, "#8e44ad").pack(side="left", padx=8)

        btn(frame_btn, "🗑️  Limpiar campos",
            self._limpiar, GRAY).pack(side="left", padx=8)
        tk.Button(
            frame_btn,
            text="📄 Generar PDF",
            command=self._generar_pdf,
            bg="#c0392b",
            fg="white",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=8)

    def _guardar(self):
        red = self.var_red.get()
        try:
            valores = {c: int(self.entries[c].get()) for c in CARRERAS}
        except ValueError:
            messagebox.showerror(
                "Error de entrada",
                "Por favor ingresa solo números enteros en los tres campos.")
            return

        fecha = guardar_registro(
            red,
            valores["Agropecuaria"],
            valores["Agronegocios"],
            valores["Agroindustrial"]
        )
        messagebox.showinfo(
            "✅ Registro guardado",
            f"Se guardaron los datos de {red}\nFecha: {fecha}")
        self._actualizar_tarjetas()
        self._limpiar()

    def _ver_grafica(self):
        VentanaGrafica(self, self.var_red.get())

    def _gestionar(self):
        VentanaGestionar(self, on_cambio=self._actualizar_tarjetas)

    def _ver_historial(self):
        self._gestionar()

    def _limpiar(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)
    def _generar_pdf(self):
        try:
            generar_pdf(self.var_red.get())
            messagebox.showinfo("PDF", "PDF generado correctamente")
        except Exception as e:
            messagebox.showerror("Error PDF", str(e)) 
    # ── Pie de ventana ─────────────────────────────────────────────────────────
    def _construir_pie(self):
        frame = tk.Frame(self, bg="#0f3460", height=30)
        frame.pack(fill="x", side="bottom")
        frame.pack_propagate(False)

        tk.Label(frame,
                 text="ULEAM  •  Facultad de Ciencias Veterinarias y Agropecuarias  •  Datos locales",
                 bg="#0f3460", fg=GRAY,
                 font=("Segoe UI", 8)).pack(expand=True)
    