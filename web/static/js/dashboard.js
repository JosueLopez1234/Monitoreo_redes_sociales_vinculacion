document.addEventListener("DOMContentLoaded", () => {

    const canvas = document.getElementById("graficaSeguidores");

    if (!canvas) return;

    // Los datos son enviados desde Flask mediante data-* en el canvas.
    const agropecuaria = parseInt(canvas.dataset.agropecuaria || 0);
    const agronegocios = parseInt(canvas.dataset.agronegocios || 0);
    const agroindustrial = parseInt(canvas.dataset.agroindustrial || 0);

    new Chart(canvas, {

        type: "bar",

        data: {

            labels: [

                "Agropecuaria",

                "Agronegocios",

                "Agroindustrial"

            ],

            datasets: [

                {

                    label: "Seguidores",

                    data: [

                        agropecuaria,

                        agronegocios,

                        agroindustrial

                    ],

                    backgroundColor: [

                        "#198754",

                        "#0d6efd",

                        "#ffc107"

                    ],

                    borderRadius: 8,

                    borderWidth: 1

                }

            ]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    display: false

                },

                title: {

                    display: true,

                    text: "Seguidores por Carrera"

                }

            },

            scales: {

                y: {

                    beginAtZero: true

                }

            }

        }

    });

});