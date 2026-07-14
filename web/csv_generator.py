from io import StringIO

import csv


class CSVGenerator:

    def generar(

        self,

        registros,

    ):

        archivo = StringIO()

        escritor = csv.writer(

            archivo,

            delimiter=",",

            quotechar='"',

            quoting=csv.QUOTE_MINIMAL,

        )

        escritor.writerow(

            [

                "Fecha",

                "Red Social",

                "Agropecuaria",

                "Agronegocios",

                "Agroindustrial",

                "Total",

            ]

        )

        for registro in registros:

            total = (

                registro["Agropecuaria"]

                + registro["Agronegocios"]

                + registro["Agroindustrial"]

            )

            escritor.writerow(

                [

                    registro["fecha"],

                    registro["red_social"],

                    registro["Agropecuaria"],

                    registro["Agronegocios"],

                    registro["Agroindustrial"],

                    total,

                ]

            )
                    # ==========================================
        # REGRESAR EL ARCHIVO EN MEMORIA
        # ==========================================

        contenido = archivo.getvalue()

        archivo.close()

        return contenido