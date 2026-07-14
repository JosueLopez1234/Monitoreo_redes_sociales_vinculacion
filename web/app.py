import os
import sys
from flask import Flask, render_template, request, redirect, url_for, flash

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

import database

app = Flask(__name__)
app.secret_key = "agrosocial-uleam"

database.inicializar_db()


def obtener_resumen():
    registros = database.obtener_todos_los_registros()

    total_registros = len(registros)
    total_agropecuaria = sum(r["Agropecuaria"] for r in registros)
    total_agronegocios = sum(r["Agronegocios"] for r in registros)
    total_agroindustrial = sum(r["Agroindustrial"] for r in registros)

    return {
        "registros": registros,
        "total_registros": total_registros,
        "total_agropecuaria": total_agropecuaria,
        "total_agronegocios": total_agronegocios,
        "total_agroindustrial": total_agroindustrial,
        "total_seguidores": total_agropecuaria + total_agronegocios + total_agroindustrial
    }


@app.route("/")
def dashboard():
    return render_template("dashboard.html", **obtener_resumen())


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        database.guardar_registro(
            request.form["red_social"],
            int(request.form["agropecuaria"]),
            int(request.form["agronegocios"]),
            int(request.form["agroindustrial"])
        )
        flash("Registro guardado correctamente.", "success")
        return redirect(url_for("gestion"))

    return render_template(
        "registrar.html",
        redes=database.obtener_redes_disponibles()
    )


@app.route("/gestion")
def gestion():
    return render_template(
        "gestionar.html",
        registros=database.obtener_todos_los_registros()
    )


@app.route("/editar/<int:id_registro>", methods=["POST"])
def editar(id_registro):
    database.actualizar_registro(
        id_registro,
        int(request.form["agropecuaria"]),
        int(request.form["agronegocios"]),
        int(request.form["agroindustrial"])
    )
    flash("Registro actualizado correctamente.", "success")
    return redirect(url_for("gestion"))


@app.route("/eliminar/<int:id_registro>", methods=["POST"])
def eliminar(id_registro):
    database.eliminar_registro(id_registro)
    flash("Registro eliminado correctamente.", "danger")
    return redirect(url_for("gestion"))


@app.route("/estadisticas")
def estadisticas():
    return render_template(
        "estadisticas.html",
        **obtener_resumen()
    )


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


@app.route("/reportes")
def reportes():
    return render_template(
        "reportes.html",
        **obtener_resumen()
    )


@app.route("/exportar")
def exportar():
    return render_template(
        "exportar.html",
        **obtener_resumen()
    )


if __name__ == "__main__":
    app.run(debug=True)
