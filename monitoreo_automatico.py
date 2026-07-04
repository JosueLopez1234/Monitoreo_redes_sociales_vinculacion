"""
monitoreo_automatico.py
------------------------
Script para automatizar el registro mensual de seguidores de Facebook /
Instagram de las 3 carreras (Agropecuaria, Agronegocios, Agroindustrial).

Qué hace:
  1. Consulta la Graph API de Facebook/Instagram para obtener el número
     actual de seguidores de cada página configurada en CONFIG.
  2. Guarda un nuevo registro en la misma base de datos que usa la app
     (datos_uleam.db), usando la función guardar_registro() ya existente.
  3. Escribe un log en automatizacion.log para poder revisar si corrió bien.

Requisitos:
  pip install requests

Cómo usarlo:
  - Coloca este archivo DENTRO de la carpeta del proyecto
    "monitereo_facebook" (al mismo nivel que main.py), para que pueda
    importar database.database sin problemas.
  - Completa la sección CONFIG con tus IDs de página y tokens.
  - Ejecuta una vez a mano para probar:  python monitoreo_automatico.py
  - Luego prográmalo con el Programador de tareas de Windows (ver guía
    al final de este archivo / en el mensaje de chat).
"""

import sys
import os
import logging
import requests

# Para poder importar database.database aunque el script se ejecute
# desde otra carpeta:
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import guardar_registro, inicializar_db

# ──────────────────────────────────────────────────────────────────────────
# CONFIGURACIÓN — RELLENA ESTO CON TUS DATOS REALES
# ──────────────────────────────────────────────────────────────────────────

# Token de acceso de página (Page Access Token) generado en
# https://developers.facebook.com  (App > Graph API Explorer > permisos
# pages_read_engagement / pages_show_list, luego conviértelo a token
# de larga duración).
ACCESS_TOKEN = "PEGA_AQUI_TU_TOKEN_DE_ACCESO"

# IDs de las páginas de Facebook de cada carrera.
# El ID de una página se obtiene en Configuración > Acerca de, o con
# https://developers.facebook.com/tools/explorer
PAGINAS_FACEBOOK = {
    "Agropecuaria":   "ID_PAGINA_AGROPECUARIA",
    "Agronegocios":   "ID_PAGINA_AGRONEGOCIOS",
    "Agroindustrial": "ID_PAGINA_AGROINDUSTRIAL",
}

# Si también automatizas Instagram (cuenta Business/Creator vinculada a
# la página de Facebook), pon aquí el Instagram Business Account ID.
# Déjalo como diccionario vacío {} si no lo vas a usar todavía.
CUENTAS_INSTAGRAM = {
    # "Agropecuaria": "ID_INSTAGRAM_AGROPECUARIA",
    # "Agronegocios": "ID_INSTAGRAM_AGRONEGOCIOS",
    # "Agroindustrial": "ID_INSTAGRAM_AGROINDUSTRIAL",
}

GRAPH_API_VERSION = "v19.0"

# ──────────────────────────────────────────────────────────────────────────
# LOGGING
# ──────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    filename=os.path.join(os.path.dirname(os.path.abspath(__file__)), "automatizacion.log"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def log_y_print(mensaje, nivel="info"):
    print(mensaje)
    getattr(logging, nivel)(mensaje)


# ──────────────────────────────────────────────────────────────────────────
# CONSULTA A LA GRAPH API
# ──────────────────────────────────────────────────────────────────────────

def obtener_seguidores_pagina(page_id, token):
    """Devuelve el número de seguidores de una página de Facebook, o None si falla."""
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}"
    params = {"fields": "followers_count", "access_token": token}
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data.get("followers_count")
    except Exception as e:
        log_y_print(f"Error consultando página {page_id}: {e}", "error")
        return None


def obtener_seguidores_instagram(ig_account_id, token):
    """Devuelve el número de seguidores de una cuenta de Instagram Business."""
    url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{ig_account_id}"
    params = {"fields": "followers_count", "access_token": token}
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        return data.get("followers_count")
    except Exception as e:
        log_y_print(f"Error consultando Instagram {ig_account_id}: {e}", "error")
        return None


# ──────────────────────────────────────────────────────────────────────────
# PROCESO PRINCIPAL
# ──────────────────────────────────────────────────────────────────────────

def ejecutar_monitoreo_facebook():
    valores = {}
    for carrera, page_id in PAGINAS_FACEBOOK.items():
        seguidores = obtener_seguidores_pagina(page_id, ACCESS_TOKEN)
        if seguidores is None:
            log_y_print(f"⚠️ No se pudo obtener Facebook de {carrera}, se omite el registro.", "warning")
            return  # si falta un dato, mejor no guardar registro incompleto
        valores[carrera] = seguidores

    fecha = guardar_registro(
        "Facebook",
        valores["Agropecuaria"],
        valores["Agronegocios"],
        valores["Agroindustrial"],
    )
    log_y_print(f"✅ Registro Facebook guardado correctamente ({fecha}): {valores}")


def ejecutar_monitoreo_instagram():
    if not CUENTAS_INSTAGRAM:
        log_y_print("ℹ️ Instagram no configurado, se omite.")
        return

    valores = {}
    for carrera, ig_id in CUENTAS_INSTAGRAM.items():
        seguidores = obtener_seguidores_instagram(ig_id, ACCESS_TOKEN)
        if seguidores is None:
            log_y_print(f"⚠️ No se pudo obtener Instagram de {carrera}, se omite el registro.", "warning")
            return
        valores[carrera] = seguidores

    fecha = guardar_registro(
        "Instagram",
        valores["Agropecuaria"],
        valores["Agronegocios"],
        valores["Agroindustrial"],
    )
    log_y_print(f"✅ Registro Instagram guardado correctamente ({fecha}): {valores}")


def main():
    log_y_print("──────── Iniciando monitoreo automático mensual ────────")
    inicializar_db()  # asegura que la BD y tablas existan
    ejecutar_monitoreo_facebook()
    ejecutar_monitoreo_instagram()
    log_y_print("──────── Proceso finalizado ────────\n")


if __name__ == "__main__":
    main()


# ──────────────────────────────────────────────────────────────────────────
# NOTA SOBRE TIKTOK
# ──────────────────────────────────────────────────────────────────────────
# TikTok no ofrece una API pública sencilla para leer el número de
# seguidores de una cuenta (su API oficial "TikTok for Business" requiere
# aprobación y permisos especiales del dueño de la cuenta). Mientras no se
# tenga acceso a esa API, ese dato se debe seguir ingresando manualmente
# desde el formulario de la app, o gestionarlo aparte si en el futuro se
# consigue acceso al API de negocio.