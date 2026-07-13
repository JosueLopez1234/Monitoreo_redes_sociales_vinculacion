document.addEventListener("DOMContentLoaded", function () {

    const ctx = document.getElementById("graficaSeguidores");

    if (!ctx) return;

    new Chart(ctx, {

        type: "line",

        data: {

            labels: [

                "Lunes",
                "Martes",
                "Miércoles",
                "Jueves",
                "Viernes",
                "Sábado",
                "Domingo"

            ],

            datasets: [

                {

                    label: "Agropecuaria",

                    data: [3100, 3130, 3150, 3180, 3200, 3230, 3250],

                    borderColor: "#198754",

                    backgroundColor: "rgba(25,135,84,.15)",

                    tension: .4,

                    fill: true

                },

                {

                    label: "Agronegocios",

                    data: [1760, 1775, 1780, 1790, 1800, 1810, 1820],

                    borderColor: "#0d6efd",

                    backgroundColor: "rgba(13,110,253,.12)",

                    tension: .4,

                    fill: true

                },

                {

                    label: "Agroindustrial",

                    data: [700,705,708,710,715,718,720],

                    borderColor:"#ffc107",

                    backgroundColor:"rgba(255,193,7,.18)",

                    tension:.4,

                    fill:true

                }

            ]

        },

        options:{

            responsive:true,

            maintainAspectRatio:false,

            plugins:{

                legend:{

                    position:"top"

                }

            }

        }

    });

});