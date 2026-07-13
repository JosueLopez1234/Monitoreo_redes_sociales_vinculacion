import os
import sys

from flask import Flask, render_template, request, redirect, url_for

# Agregar la carpeta padre al path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

import database

app = Flask(__name__)

database.inicializar_db()

# ==========================
# Dashboard
# ==========================

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# ==========================
# Registrar
# ==========================

@app.route("/registrar", methods=["GET", "POST"])
def registrar():

    if request.method == "POST":

        red_social = request.form["red_social"]

        agropecuaria = int(request.form["agropecuaria"])

        agronegocios = int(request.form["agronegocios"])

        agroindustrial = int(request.form["agroindustrial"])

        database.guardar_registro(
            red_social,
            agropecuaria,
            agronegocios,
            agroindustrial,
        )

        return redirect(url_for("gestion"))

    return render_template(
        "registrar.html",
        redes=database.obtener_redes_disponibles(),
    )


# ==========================
# Gestión
# ==========================

@app.route("/gestion")
def gestion():

    registros = database.obtener_todos_los_registros()

    return render_template(
        "gestionar.html",
        registros=registros,
    )


# ==========================
# Eliminar Registro
# ==========================

@app.route("/eliminar/<int:id_registro>", methods=["POST"])
def eliminar(id_registro):

    database.eliminar_registro(id_registro)

    return redirect(url_for("gestion"))


# ==========================
# Estadísticas
# ==========================

@app.route("/estadisticas")
def estadisticas():
    return render_template("estadisticas.html")


# ==========================
# Gráficas
# ==========================

@app.route("/graficas")
def graficas():
    return render_template("graficas.html")


# ==========================
# Reportes
# ==========================

@app.route("/reportes")
def reportes():
    return render_template("reportes.html")


# ==========================
# Exportar
# ==========================

@app.route("/exportar")
def exportar():
    return render_template("exportar.html")


# ==========================
# Ejecutar aplicación
# ==========================

if __name__ == "__main__":
    app.run(debug=True)