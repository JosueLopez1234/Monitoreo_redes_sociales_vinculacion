import os
from io import BytesIO
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib.pagesizes import A4

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image,
    Table,
    TableStyle
)


class PDFGenerator:

    def __init__(self):

        self.styles = getSampleStyleSheet()

        self.styles["Heading1"].alignment = TA_CENTER
        self.styles["Heading2"].alignment = TA_CENTER

    def generar(
        self,
        registros,
        total_registros,
        total_seguidores,
        total_agropecuaria,
        total_agronegocios,
        total_agroindustrial,
    ):

        buffer = BytesIO()

        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
        )

        elementos = []

        ruta_logo = os.path.join(
            os.path.dirname(__file__),
            "static",
            "img",
            "logo_uleam.png",
        )

        if os.path.exists(ruta_logo):

            logo = Image(
                ruta_logo,
                width=3.5 * cm,
                height=3.5 * cm,
            )

            logo.hAlign = "CENTER"

            elementos.append(logo)

        elementos.append(
            Paragraph(
                "<b>UNIVERSIDAD LAICA ELOY ALFARO DE MANABÍ</b>",
                self.styles["Heading2"],
            )
        )

        elementos.append(
            Paragraph(
                "<b>FACULTAD DE CIENCIAS AGROPECUARIAS</b>",
                self.styles["Heading2"],
            )
        )

        elementos.append(Spacer(1, 0.4 * cm))

        elementos.append(
            Paragraph(
                "<font size='18'><b>AgroSocial Analytics</b></font>",
                self.styles["Heading1"],
            )
        )

        elementos.append(
            Paragraph(
                "Reporte General de Redes Sociales",
                self.styles["Heading2"],
            )
        )

        elementos.append(Spacer(1, 0.5 * cm))

        fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

        elementos.append(
            Paragraph(
                f"<b>Fecha de generación:</b> {fecha}",
                self.styles["Normal"],
            )
        )

        elementos.append(Spacer(1, 0.4 * cm))
                # ===========================
        # RESUMEN GENERAL
        # ===========================

        resumen = [

            ["Indicador", "Valor"],

            ["Total de Registros", str(total_registros)],

            ["Total de Seguidores", str(total_seguidores)],

            ["Agropecuaria", str(total_agropecuaria)],

            ["Agronegocios", str(total_agronegocios)],

            ["Agroindustrial", str(total_agroindustrial)],

        ]

        tabla_resumen = Table(
            resumen,
            colWidths=[8 * cm, 7 * cm]
        )

        tabla_resumen.setStyle(

            TableStyle([

                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.darkgreen,
                ),

                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),

                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.black,
                ),

                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.beige,
                ),

                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),

                (
                    "ALIGN",
                    (0, 0),
                    (-1, -1),
                    "CENTER",
                ),

                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    10,
                ),

            ])

        )

        elementos.append(tabla_resumen)

        elementos.append(
            Spacer(
                1,
                0.8 * cm,
            )
        )

        elementos.append(

            Paragraph(

                "<b>Detalle de Registros</b>",

                self.styles["Heading2"],

            )

        )

        elementos.append(

            Spacer(

                1,

                0.3 * cm,

            )

        )

        datos = [

            [

                "Fecha",

                "Red",

                "Agropec.",

                "Agroneg.",

                "AgroInd.",

                "Total",

            ]

        ]
                # ==========================================
        # AGREGAR TODOS LOS REGISTROS AL PDF
        # ==========================================

        for registro in registros:

            total = (

                registro["Agropecuaria"]

                + registro["Agronegocios"]

                + registro["Agroindustrial"]

            )

            datos.append(

                [

                    registro["fecha"],

                    registro["red_social"],

                    registro["Agropecuaria"],

                    registro["Agronegocios"],

                    registro["Agroindustrial"],

                    total,

                ]

            )

        tabla = Table(

            datos,

            colWidths=[

                4.0 * cm,

                2.8 * cm,

                2.5 * cm,

                2.7 * cm,

                2.8 * cm,

                2.2 * cm,

            ],

            repeatRows=1,

        )

        tabla.setStyle(

            TableStyle(

                [

                    (

                        "BACKGROUND",

                        (0, 0),

                        (-1, 0),

                        colors.darkgreen,

                    ),

                    (

                        "TEXTCOLOR",

                        (0, 0),

                        (-1, 0),

                        colors.white,

                    ),

                    (

                        "GRID",

                        (0, 0),

                        (-1, -1),

                        0.5,

                        colors.grey,

                    ),

                    (

                        "FONTNAME",

                        (0, 0),

                        (-1, 0),

                        "Helvetica-Bold",

                    ),

                    (

                        "ALIGN",

                        (0, 0),

                        (-1, -1),

                        "CENTER",

                    ),

                    (

                        "VALIGN",

                        (0, 0),

                        (-1, -1),

                        "MIDDLE",

                    ),

                    (

                        "BOTTOMPADDING",

                        (0, 0),

                        (-1, 0),

                        8,

                    ),

                    (

                        "BACKGROUND",

                        (0, 1),

                        (-1, -1),

                        colors.whitesmoke,

                    ),

                ]

            )

        )

        elementos.append(tabla)

        elementos.append(

            Spacer(

                1,

                0.7 * cm,

            )

        )
                # ==========================================
        # OBSERVACIONES
        # ==========================================

        elementos.append(

            Paragraph(

                "<b>Observaciones</b>",

                self.styles["Heading2"],

            )

        )

        elementos.append(

            Spacer(

                1,

                0.25 * cm,

            )

        )

        elementos.append(

            Paragraph(

                "El presente reporte fue generado automáticamente por "

                "<b>AgroSocial Analytics</b>. "

                "La información corresponde al monitoreo manual de "

                "seguidores de las redes sociales oficiales de la "

                "Facultad de Ciencias Agropecuarias de la "

                "Universidad Laica Eloy Alfaro de Manabí.",

                self.styles["BodyText"],

            )

        )

        elementos.append(

            Spacer(

                1,

                0.5 * cm,

            )

        )

        elementos.append(

            Paragraph(

                "<b>Conclusiones</b>",

                self.styles["Heading2"],

            )

        )

        elementos.append(

            Paragraph(

                f"""

                • Total de registros almacenados: <b>{total_registros}</b><br/>

                • Total de seguidores registrados: <b>{total_seguidores}</b><br/>

                • Agropecuaria: <b>{total_agropecuaria}</b><br/>

                • Agronegocios: <b>{total_agronegocios}</b><br/>

                • Agroindustrial: <b>{total_agroindustrial}</b><br/><br/>

                Este documento constituye un respaldo institucional de la

                información registrada en el sistema AgroSocial Analytics.

                """,

                self.styles["BodyText"],

            )

        )

        elementos.append(

            Spacer(

                1,

                0.8 * cm,

            )

        )

        elementos.append(

            Paragraph(

                "<font size='9'>"

                "Universidad Laica Eloy Alfaro de Manabí<br/>"

                "Facultad de Ciencias Agropecuarias<br/>"

                "Sistema AgroSocial Analytics © 2026"

                "</font>",

                self.styles["Heading2"],

            )

        )

        pdf.build(elementos)

        buffer.seek(0)

        return buffer