from waitress import serve

from app import app

if __name__ == "__main__":

    print()

    print("=" * 60)
    print("AgroSocial Analytics iniciado")
    print("http://127.0.0.1:5000")
    print("=" * 60)

    serve(

        app,

        host="127.0.0.1",

        port=5000,

        threads=8

    )