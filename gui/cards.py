"""
gui/cards.py
Mixin con las tarjetas de resumen por carrera:
  - Construcción de las tarjetas visuales
  - Actualización de conteos y diferencias con el registro anterior
"""
import tkinter as tk

from database.database import obtener_datos
from theme import (
    BG_DARK, BG_CARD, ACCENT, GREEN, TEXT, GRAY, YELLOW,
    COLORES_CARRERA, CARRERAS,
    FONT_CARD_NUM, FONT_SMALL, FONT_TINY,
)


class CardsMixin:
    """Crea y actualiza las tarjetas de seguidores por carrera."""

    # ── Construcción inicial ──────────────────────────────────────────────────
    def _construir_tarjetas_carreras(self):
        self.frame_tarjetas = tk.Frame(self, bg=BG_DARK)
        self.frame_tarjetas.pack(fill="x", padx=20, pady=8)

        for carrera in CARRERAS:
            color = COLORES_CARRERA[carrera]
            card = tk.Frame(
                self.frame_tarjetas, bg=BG_CARD,
                relief="flat", bd=0, padx=12, pady=10,
            )
            card.pack(side="left", expand=True, fill="both", padx=6)

            # Barra de color en la parte superior
            tk.Frame(card, bg=color, height=4).pack(fill="x")

            tk.Label(
                card, text=carrera, bg=BG_CARD, fg=color,
                font=("Segoe UI", 10, "bold"),
            ).pack(anchor="w", pady=(4, 0))

            lbl_seg = tk.Label(card, text="–", bg=BG_CARD, fg=TEXT, font=FONT_CARD_NUM)
            lbl_seg.pack(anchor="w")

            lbl_dif = tk.Label(card, text="", bg=BG_CARD, fg=GRAY, font=FONT_SMALL)
            lbl_dif.pack(anchor="w")

            tk.Label(card, text="seguidores", bg=BG_CARD, fg=GRAY, font=FONT_TINY).pack(anchor="w")

            self.labels_seg[carrera] = lbl_seg
            self.labels_dif[carrera] = lbl_dif

    # ── Actualización de datos ────────────────────────────────────────────────
    def _actualizar_tarjetas(self):
        red   = self.var_red.get()
        datos = obtener_datos(red)

        if datos:
            ultimo   = datos[-1]
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
