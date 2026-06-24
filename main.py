from database import inicializar_db
from gui import App


def main():
    inicializar_db()   # Crea la BD y carga datos iniciales si es la primera vez
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()