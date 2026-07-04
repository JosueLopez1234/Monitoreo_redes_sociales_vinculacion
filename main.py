from database.database import inicializar_db, cerrar_conexion
from gui import App


def main():
    inicializar_db()   # Crea la BD y carga datos iniciales si es la primera vez
    app = App()
    # Cierra la conexión persistente a Postgres al cerrar la ventana
    app.protocol("WM_DELETE_WINDOW", lambda: (cerrar_conexion(), app.destroy()))
    try:
        app.mainloop()
    finally:
        cerrar_conexion()


if __name__ == "__main__":
    main()