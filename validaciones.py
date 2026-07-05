"""
validaciones.py
Reglas de validación compartidas para los números de seguidores que se
ingresan en el formulario principal y en la ventana de editar historial.

Se centraliza aquí para no repetir el mismo límite/mensaje en varios
lugares (form principal + edición de historial).
"""

# Un límite generoso pero razonable: ninguna cuenta de la facultad va a
# tener más de 50 millones de seguidores. Sirve para atajar errores de
# tecleo como escribir de más un cero.
MAXIMO_SEGUIDORES = 50_000_000


def validar_valores_seguidores(valores: dict):
    """valores: dict {"Agropecuaria": int, "Agronegocios": int, "Agroindustrial": int}

    Devuelve (ok: bool, mensaje_error: str). Si ok es True, mensaje_error
    va vacío.
    """
    for campo, valor in valores.items():
        if valor < 0:
            return False, (
                f"El campo '{campo}' no puede ser negativo.\n"
                f"Ingresaste: {valor}"
            )
        if valor > MAXIMO_SEGUIDORES:
            return False, (
                f"El campo '{campo}' tiene un valor demasiado alto ({valor:,}).\n"
                f"Revisa que no hayas escrito un dígito de más."
            )
    return True, ""
