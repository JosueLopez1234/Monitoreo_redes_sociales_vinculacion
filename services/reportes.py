"""
reportes.py
-----------
Este archivo se mantiene solo por compatibilidad con código que aún
importe `from services.reportes import generar_pdf`.

La generación real del PDF vive ahora en services/exportar.py (versión
profesional: incluye estado actual, tabla de crecimiento, gráfica
embebida e histórico completo). Aquí solo reexportamos esa función para
no romper nada que dependa de la ruta anterior.
"""
from services.exportar import generar_pdf  # noqa: F401
