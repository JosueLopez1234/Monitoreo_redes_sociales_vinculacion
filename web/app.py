from flask import Flask, render_template

app = Flask(__name__)


# ==========================
# Dashboard
# ==========================

@app.route("/")
def dashboard():
    return render_template("dashboard.html")


# ==========================
# Registrar
# ==========================

@app.route("/registrar")
def registrar():
    return render_template("registrar.html")


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
# Gestión
# ==========================

@app.route("/gestion")
def gestion():
    return render_template("gestionar.html")


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


if __name__ == "__main__":
    app.run(debug=True)