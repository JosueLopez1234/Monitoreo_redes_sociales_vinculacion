"""
theme.py - Paleta de colores y constantes visuales ULEAM FCVT
Importar desde cualquier módulo: from theme import *
"""

# ── Paleta principal FCVT ─────────────────────────────────────────────────────
BG_DARK    = "#F8FAF5"   # Fondo principal (crema vegetal)
BG_CARD    = "#FFFFFF"   # Tarjetas / paneles
BG_INPUT   = "#EAF4E2"   # Campos de entrada

ACCENT     = "#4E8A1E"   # Verde institucional (botones primarios, header)
GREEN      = "#7AAE3B"   # Verde claro (positivo / guardar)
BLUE       = "#5E8C31"   # Verde secundario (gráficas)
YELLOW     = "#F28C28"   # Naranja institucional (alertas / primer registro)

TEXT       = "#2F2F2F"   # Texto principal (reemplaza WHITE del diseño oscuro)
GRAY       = "#6B6B6B"   # Texto secundario / placeholders

PIE_BG     = "#2D5A1B"   # Fondo del pie de ventana
PIE_FG     = "#A8D5A2"   # Texto del pie

# ── Colores por carrera ───────────────────────────────────────────────────────
COLORES_CARRERA = {
    "Agropecuaria":   "#4E8A1E",   # Verde institucional
    "Agronegocios":   "#7AAE3B",   # Verde claro
    "Agroindustrial": "#2D5A1B",   # Verde oscuro
}

# ── Colores para matplotlib (fondo oscuro de la gráfica) ─────────────────────
PLOT_BG       = "#1a3d1a"   # Fondo de la figura
PLOT_AX_BG   = "#0d2b0d"   # Fondo del área de ejes
PLOT_SPINE    = "#2d5a1b"   # Color de bordes de ejes
PLOT_GRID     = "#4a7c3f"   # Color de la cuadrícula
PLOT_TEXT     = "#ecf0f1"   # Color de texto en gráfica

# ── Datos del sistema ─────────────────────────────────────────────────────────
CARRERAS = ["Agropecuaria", "Agronegocios", "Agroindustrial"]
REDES    = ["Facebook", "TikTok", "Instagram"]
EMOJIS   = {"Facebook": "🔵", "TikTok": "⚫", "Instagram": "🟣"}
ICONOS_RED = EMOJIS   # alias para graficas.py

# ── Fuentes ───────────────────────────────────────────────────────────────────
FONT_TITLE  = ("Segoe UI", 15, "bold")
FONT_LABEL  = ("Segoe UI", 11)
FONT_LABEL_BOLD = ("Segoe UI", 11, "bold")
FONT_CARD_NUM   = ("Segoe UI", 22, "bold")
FONT_SMALL  = ("Segoe UI", 9)
FONT_TINY   = ("Segoe UI", 8)
FONT_BTN    = ("Segoe UI", 11, "bold")