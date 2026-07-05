from database.database import inicializar_db, cerrar_conexion, ENV_ENCONTRADO
from gui import App


def main():
    inicializar_db()   # Crea la BD y carga datos iniciales si es la primera vez
    app = App()

    if not ENV_ENCONTRADO:
        from tkinter import messagebox
        messagebox.showwarning(
            "Sin archivo de configuración (.env)",
            "No se encontró el archivo .env con los datos de conexión a Supabase.\n\n"
            "La app va a funcionar en MODO SIN CONEXIÓN: todo lo que registres se "
            "guarda en tu computadora y se subirá automáticamente en cuanto se "
            "coloque el archivo .env correcto y se reinicie el programa.\n\n"
            "El .env debe ir junto al programa (.exe) o en:\n"
            "%USERPROFILE%\\MonitorRedesAGRO\\.env",
        )

    def _al_cerrar():
        if hasattr(app, "hilo_sync"):
            app.hilo_sync.detener()
        cerrar_conexion()
        app.destroy()

    # Cierra la conexión persistente a Postgres al cerrar la ventana
    app.protocol("WM_DELETE_WINDOW", _al_cerrar)
    try:
        app.mainloop()
    finally:
        cerrar_conexion()


if __name__ == "__main__":
    main()