from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from tkinter import filedialog, messagebox
from database.database import obtener_ultimo_registro
import os

def generar_pdf(red):

    archivo = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")]
    )

    if not archivo:
        return

    doc = SimpleDocTemplate(
        archivo,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=60,
        bottomMargin=60
    )

    estilos = getSampleStyleSheet()
    elementos = []

    # ───────────────── ENCABEZADO ─────────────────
    titulo = Paragraph(
        "<b>REPORTE DE MONITOREO DE REDES SOCIALES</b><br/>"
        "Facultad de Ciencias Veterinarias y Agropecuarias - ULEAM",
        estilos["Title"]
    )

    elementos.append(titulo)
    elementos.append(Spacer(1, 20))

    # ───────────────── LOGO ─────────────────
    logo_path = "imagenes/logo_uleam.png"  # cambia si está en otra carpeta

    if os.path.exists(logo_path):
        logo = Image(logo_path, width=200, height=100)
        elementos.append(logo)
        elementos.append(Spacer(1, 20))

    # ───────────────── RED SELECCIONADA ─────────────────
    elementos.append(Paragraph(f"<b>Red seleccionada:</b> {red}", estilos["Heading2"]))
    elementos.append(Spacer(1, 10))

    # ───────────────── DATOS ─────────────────
    datos = obtener_ultimo_registro(red)

    if datos:

        tabla_data = [
            ["Carrera", "Seguidores"],
            ["Agropecuaria", datos["Agropecuaria"]],
            ["Agronegocios", datos["Agronegocios"]],
            ["Agroindustrial", datos["Agroindustrial"]],
        ]

        tabla = Table(tabla_data)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("BACKGROUND", (0, 1), (-1, -1), colors.whitesmoke),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
        ]))

        elementos.append(tabla)

    elementos.append(Spacer(1, 30))

    # ───────────────── PIE DE PÁGINA ─────────────────
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("Helvetica", 9)
        canvas.drawString(40, 30, "ULEAM - Sistema de Monitoreo de Redes Sociales")
        canvas.drawRightString(550, 30, f"Página {doc.page}")
        canvas.restoreState()

    doc.build(elementos, onFirstPage=footer, onLaterPages=footer)

    messagebox.showinfo("PDF", "Reporte profesional generado correctamente")