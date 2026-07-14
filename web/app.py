import os
import sys
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    send_file,
)

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import database
from pdf_generator import PDFGenerator
from excel_generator import ExcelGenerator
from csv_generator import CSVGenerator

app = Flask(__name__)
app.secret_key = "agrosocial-uleam"

database.inicializar_db()


# ==========================================================
# RESUMEN GENERAL
# ==========================================================

def obtener_resumen():

    registros = database.obtener_todos_los_registros()

    total_registros = len(registros)

    total_agropecuaria = sum(
        r["Agropecuaria"] for r in registros
    )

    total_agronegocios = sum(
        r["Agronegocios"] for r in registros
    )

    total_agroindustrial = sum(
        r["Agroindustrial"] for r in registros
    )

    total_seguidores = (

        total_agropecuaria

        + total_agronegocios

        + total_agroindustrial

    )

    total = max(total_seguidores, 1)

    promedio = round(
        total_seguidores / 3,
        2,
    )

    porcentaje_agropecuaria = round(
        total_agropecuaria * 100 / total,
        1,
    )

    porcentaje_agronegocios = round(
        total_agronegocios * 100 / total,
        1,
    )

    porcentaje_agroindustrial = round(
        total_agroindustrial * 100 / total,
        1,
    )

    return {

        "registros": registros,

        "total_registros": total_registros,

        "total_agropecuaria": total_agropecuaria,

        "total_agronegocios": total_agronegocios,

        "total_agroindustrial": total_agroindustrial,

        "total_seguidores": total_seguidores,

        "promedio": promedio,

        "porcentaje_agropecuaria": porcentaje_agropecuaria,

        "porcentaje_agronegocios": porcentaje_agronegocios,

        "porcentaje_agroindustrial": porcentaje_agroindustrial,

    }


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/")
def dashboard():

    return render_template(

        "dashboard.html",

        **obtener_resumen()

    )


# ==========================================================
# REGISTRAR
# ==========================================================

@app.route("/registrar", methods=["GET", "POST"])
def registrar():

    if request.method == "POST":

        database.guardar_registro(

            request.form["red_social"],

            int(request.form["agropecuaria"]),

            int(request.form["agronegocios"]),

            int(request.form["agroindustrial"])

        )

        flash(

            "Registro guardado correctamente.",

            "success"

        )

        return redirect(

            url_for("gestion")

        )

    return render_template(

        "registrar.html",

        redes=database.obtener_redes_disponibles()

    )


# ==========================================================
# GESTION
# ==========================================================

@app.route("/gestion")
def gestion():

    return render_template(

        "gestionar.html",

        registros=database.obtener_todos_los_registros()

    )


# ==========================================================
# EDITAR
# ==========================================================

@app.route("/editar/<int:id_registro>", methods=["POST"])
def editar(id_registro):

    database.actualizar_registro(

        id_registro,

        int(request.form["agropecuaria"]),

        int(request.form["agronegocios"]),

        int(request.form["agroindustrial"])

    )

    flash(

        "Registro actualizado correctamente.",

        "success"

    )

    return redirect(

        url_for("gestion")

    )


# ==========================================================
# ELIMINAR
# ==========================================================

@app.route("/eliminar/<int:id_registro>", methods=["POST"])
def eliminar(id_registro):

    database.eliminar_registro(id_registro)

    flash(

        "Registro eliminado correctamente.",

        "danger"

    )

    return redirect(

        url_for("gestion")

    )
    # ==========================================================
# ESTADISTICAS
# ==========================================================

@app.route("/estadisticas")
def estadisticas():

    return render_template(

        "estadisticas.html",

        **obtener_resumen()

    )


# ==========================================================
# GRAFICAS
# ==========================================================

@app.route("/graficas")
def graficas():

    resumen = obtener_resumen()

    return render_template(

        "graficas.html",

        facebook=database.obtener_datos("Facebook"),

        instagram=database.obtener_datos("Instagram"),

        tiktok=database.obtener_datos("TikTok"),

        **resumen

    )


# ==========================================================
# REPORTES
# ==========================================================

@app.route("/reportes")
def reportes():

    return render_template(

        "reportes.html",

        **obtener_resumen()

    )


# ==========================================================
# EXPORTAR
# ==========================================================

@app.route("/exportar")
def exportar():

    return render_template(

        "exportar.html",

        **obtener_resumen()

    )


# ==========================================================
# GENERAR PDF
# ==========================================================

@app.route("/generar_pdf")
def generar_pdf():

    resumen = obtener_resumen()

    pdf = PDFGenerator()

    archivo = pdf.generar(

        registros=resumen["registros"],

        total_registros=resumen["total_registros"],

        total_seguidores=resumen["total_seguidores"],

        total_agropecuaria=resumen["total_agropecuaria"],

        total_agronegocios=resumen["total_agronegocios"],

        total_agroindustrial=resumen["total_agroindustrial"]

    )

    return send_file(

        archivo,

        as_attachment=True,

        download_name="Reporte_AgroSocial_Analytics.pdf",

        mimetype="application/pdf"

    )
    
    # ==========================================================
# GENERAR EXCEL
# ==========================================================

@app.route("/generar_excel")
def generar_excel():

    resumen = obtener_resumen()

    excel = ExcelGenerator()

    archivo = excel.generar(

        registros=resumen["registros"],

        total_registros=resumen["total_registros"],

        total_seguidores=resumen["total_seguidores"],

        total_agropecuaria=resumen["total_agropecuaria"],

        total_agronegocios=resumen["total_agronegocios"],

        total_agroindustrial=resumen["total_agroindustrial"]

    )

    return send_file(

        archivo,

        as_attachment=True,

        download_name="Reporte_AgroSocial_Analytics.xlsx",

        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

    )

# ==========================================================
# GENERAR CSV
# ==========================================================

@app.route("/generar_csv")
def generar_csv():

    from flask import Response

    resumen = obtener_resumen()

    csv_generator = CSVGenerator()

    contenido = csv_generator.generar(

        registros=resumen["registros"]

    )

    return Response(

        contenido,

        mimetype="text/csv",

        headers={

            "Content-Disposition":

            "attachment; filename=Reporte_AgroSocial_Analytics.csv"

        }

    )

# ==========================================================
# ERROR 404
# ==========================================================

@app.errorhandler(404)
def pagina_no_encontrada(error):

    return render_template(

        "404.html"

    ), 404


# ==========================================================
# ERROR 500
# ==========================================================

@app.errorhandler(500)
def error_servidor(error):

    return render_template(

        "500.html"

    ), 500


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    app.run(

        debug=True,

        host="127.0.0.1",

        port=5000

    )