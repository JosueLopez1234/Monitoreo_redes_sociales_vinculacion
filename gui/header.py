"""
gui/header.py
Mixin con los widgets estáticos de la ventana principal:
  - Barra de título (header)
  - Selector de red social (radiobuttons)
  - Pie de ventana
"""
import tkinter as tk

from theme import (
    BG_DARK, ACCENT, TEXT, PIE_BG, PIE_FG, YELLOW,
    REDES, EMOJIS,
    FONT_TITLE, FONT_LABEL, FONT_LABEL_BOLD, FONT_TINY,
    BG_INPUT,
)


class HeaderMixin:
    """Agrupa los métodos que construyen la cabecera, el selector y el pie."""

    # ── Barra de título ───────────────────────────────────────────────────────
    def _construir_header(self):
        frame = tk.Frame(self, bg=ACCENT, height=70)
        frame.pack(fill="x")
        frame.pack_propagate(False)

        tk.Label(
            frame,
            text="🌿  MONITOR DE REDES SOCIALES  •  ULEAM – FCVT",
            bg=ACCENT, fg="white",
            font=FONT_TITLE,
        ).pack(expand=True)

    # ── Selector de red social ────────────────────────────────────────────────
    def _construir_selector_red(self):
        frame = tk.Frame(self, bg=BG_DARK, pady=10)
        frame.pack(fill="x", padx=20)

        tk.Label(
            frame, text="Selecciona la red social:",
            bg=BG_DARK, fg=TEXT,
            font=FONT_LABEL_BOLD,
        ).pack(side="left")

        for red in REDES:
            tk.Radiobutton(
                frame,
                text=f"{EMOJIS[red]} {red}",
                variable=self.var_red, value=red,
                command=self._actualizar_tarjetas,
                bg=BG_DARK, fg=TEXT, selectcolor=BG_INPUT,
                activebackground=BG_DARK, activeforeground=YELLOW,
                font=FONT_LABEL, indicatoron=True, cursor="hand2",
            ).pack(side="left", padx=12)

    # ── Pie de ventana ────────────────────────────────────────────────────────
    def _construir_pie(self):
        frame = tk.Frame(self, bg=PIE_BG, height=30)
        frame.pack(fill="x", side="bottom")
        frame.pack_propagate(False)

        tk.Label(
            frame,
            text="ULEAM  •  Facultad de Ciencias Veterinarias y Agropecuarias  •  Datos locales",
            bg=PIE_BG, fg=PIE_FG,
            font=FONT_TINY,
        ).pack(expand=True)
