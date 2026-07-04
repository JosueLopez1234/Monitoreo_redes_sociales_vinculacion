"""
gui/form.py
Mixin con el formulario de ingreso de seguidores y el reloj en tiempo real.
"""
import tkinter as tk
from datetime import datetime

from theme import (
    BG_CARD, BG_INPUT, TEXT, GRAY,
    CARRERAS, FONT_LABEL, FONT_SMALL,
)


class FormMixin:
    """Construye el formulario de ingreso y mantiene el reloj actualizado."""

    # ── Formulario ────────────────────────────────────────────────────────────
    def _construir_formulario(self):
        frame_form = tk.Frame(self, bg=BG_CARD, padx=20, pady=15)
        frame_form.pack(fill="x", padx=20, pady=6)

        tk.Label(
            frame_form,
            text="✏️  Registrar nuevos seguidores",
            bg=BG_CARD, fg=TEXT,
            font=("Segoe UI", 12, "bold"),
        ).grid(row=0, column=0, columnspan=6, sticky="w", pady=(0, 10))

        for i, carrera in enumerate(CARRERAS):
            tk.Label(
                frame_form, text=f"{carrera}:",
                bg=BG_CARD, fg=TEXT, font=FONT_LABEL,
            ).grid(row=1, column=i * 2, sticky="w", padx=(0, 6))

            entry = tk.Entry(
                frame_form, width=10,
                bg=BG_INPUT, fg=TEXT, insertbackground=TEXT,
                font=("Segoe UI", 12), relief="flat", bd=4,
                justify="center",
            )
            entry.grid(row=1, column=i * 2 + 1, padx=(0, 20))
            self.entries[carrera] = entry

        self.lbl_fecha = tk.Label(
            frame_form,
            text=f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M')}",
            bg=BG_CARD, fg=GRAY, font=FONT_SMALL,
        )
        self.lbl_fecha.grid(row=2, column=0, columnspan=6, sticky="w", pady=(8, 0))
        self._tick_reloj()

    # ── Reloj en tiempo real ──────────────────────────────────────────────────
    def _tick_reloj(self):
        self.lbl_fecha.config(
            text=f"🕐 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        self.after(1000, self._tick_reloj)
