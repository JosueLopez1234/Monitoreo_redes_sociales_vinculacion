from waitress import serve
from app import app

import threading
import time
import webbrowser


def abrir_navegador():

    time.sleep(2)

    webbrowser.open("http://127.0.0.1:5000")


if __name__ == "__main__":

    print()

    print("=" * 60)
    print("AgroSocial Analytics iniciado")
    print("http://127.0.0.1:5000")
    print("=" * 60)

    threading.Thread(

        target=abrir_navegador,

        daemon=True

    ).start()

    serve(

        app,

        host="127.0.0.1",

        port=5000,

        threads=8

    )