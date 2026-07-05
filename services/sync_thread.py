"""
services/sync_thread.py
Hilo en segundo plano que cada cierto tiempo:
  1. Revisa si hay conexión con Supabase.
  2. Si la hay y quedaron registros pendientes en la caché local
     (guardados mientras no había internet), los sube automáticamente.
  3. Avisa a la interfaz (callback) el estado actual para mostrar el
     punto verde/rojo y cuántos registros faltan por subir.

No usa nada además de la librería estándar (threading), así que no
agrega dependencias nuevas al proyecto.
"""
import threading

from database.database import (
    esta_online, sincronizar_pendientes, hay_cambios_pendientes, contar_cambios_pendientes,
)

INTERVALO_SEGUNDOS = 20  # cada cuánto revisa conexión / intenta sincronizar


class HiloSincronizacion(threading.Thread):
    """Hilo daemon: se cierra solo al cerrar la app, no requiere join()."""

    def __init__(self, callback_estado=None, intervalo=INTERVALO_SEGUNDOS):
        super().__init__(daemon=True)
        self.callback_estado = callback_estado  # función(online: bool, pendientes: int, mensaje: str)
        self.intervalo = intervalo
        self._detener = threading.Event()

    def run(self):
        while not self._detener.is_set():
            self._revisar_y_sincronizar()
            self._detener.wait(self.intervalo)

    def detener(self):
        self._detener.set()

    def sincronizar_ahora(self):
        """Fuerza una revisión inmediata (usado por el botón 'Sincronizar ahora')."""
        self._revisar_y_sincronizar()

    def _revisar_y_sincronizar(self):
        online = esta_online()
        mensaje = ""
        if online and hay_cambios_pendientes():
            exito, subidos, error = sincronizar_pendientes()
            if exito and subidos > 0:
                mensaje = f"Se sincronizaron {subidos} registro(s) pendientes."
            elif not exito:
                mensaje = f"No se pudo sincronizar: {error}"
                online = False

        pendientes = contar_cambios_pendientes()
        if self.callback_estado:
            try:
                self.callback_estado(online, pendientes, mensaje)
            except Exception:
                pass  # nunca dejar que un error de la UI tumbe el hilo
