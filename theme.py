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
# Elegidos para tener buen contraste tanto en la gráfica (fondo claro, ver
# abajo) como en el PDF (fondo blanco) y ser distinguibles entre sí incluso
# para personas con dificultades para distinguir colores.
COLORES_CARRERA = {
    "Agropecuaria":   "#2E7D32",   # verde medio — visible sobre fondo claro
    "Agronegocios":   "#1565C0",   # azul fuerte
    "Agroindustrial": "#C2185B",   # magenta/vino fuerte
}

# ── Colores para matplotlib ───────────────────────────────────────────────────
# Antes el fondo era verde muy oscuro (#1a3d1a / #0d2b0d), lo que hacía casi
# invisible la línea de "Agropecuaria" (verde oscuro sobre verde oscuro).
# Ahora usamos un fondo claro, consistente con el resto de la app (BG_DARK),
# así las 3 líneas de colores fuertes resaltan bien.
PLOT_BG       = "#F8FAF5"   # Fondo de la figura (igual a BG_DARK de la app)
PLOT_AX_BG    = "#FFFFFF"   # Fondo del área de ejes (blanco, máximo contraste)
PLOT_SPINE    = "#B5B5B5"   # Color de bordes de ejes
PLOT_GRID     = "#DDDDDD"   # Cuadrícula tenue, no compite con las líneas
PLOT_TEXT     = "#2F2F2F"   # Texto oscuro, igual al TEXT de la app

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