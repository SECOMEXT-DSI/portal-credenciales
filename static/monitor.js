console.log("Script loaded"); // Verificar que el script está cargado

// Elementos HTML
const statusElement = document.getElementById('status');
const timestampElement = document.getElementById('timestamp');
const ctxLine = document.getElementById('statusChart').getContext('2d');
const ctxPie = document.getElementById('availabilityChart').getContext('2d');

// Variables de datos
let statusData = [];
let onlineCount = 0;
let offlineCount = 0;

// Configuración del gráfico de líneas (Historial de Estado)
const statusChart = new Chart(ctxLine, {
    type: 'line',
    data: {
        labels: [],
        datasets: [{
            label: 'Estado del Sitio',
            data: [],
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 2,
            fill: false,
            tension: 0.1 // Suavizar líneas
        }]
    },
    options: {
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'minute'
                },
                title: {
                    display: true,
                    text: 'Tiempo'
                },
                adapters: {
                    date: {
                        zone: 'America/Mexico_City' // Mostrar en UTC-6
                    }
                }
            },
            y: {
                title: {
                    display: true,
                    text: 'Estado'
                },
                ticks: {
                    callback: function(value) {
                        return value === 1 ? 'Online' : 'Offline';
                    },
                    stepSize: 1, // Asegura que solo muestra 1 y 0
                    min: 0,
                    max: 1
                }
            }
        }
    }
});

// Configuración del gráfico de torta (Porcentaje de Disponibilidad)
const availabilityChart = new Chart(ctxPie, {
    type: 'pie',
    data: {
        labels: ['Online', 'Offline'],
        datasets: [{
            data: [0, 0],
            backgroundColor: ['#4CAF50', '#f44336']
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Porcentaje de Disponibilidad'
            }
        }
    }
});

// Función para actualizar los gráficos
function updateCharts() {
    console.log("Updating charts"); // Verificar que se intenta actualizar los gráficos
    fetch('/get_history')
        .then(response => response.json())
        .then(data => {
            console.log("History data:", data); // Verificar los datos recibidos
            statusData = data.slice(-200); // Mantener solo las últimas 50 entradas

            // Actualizar gráfico de líneas
            statusChart.data.labels = statusData.map(entry => new Date(entry.timestamp));
            statusChart.data.datasets[0].data = statusData.map(entry => entry.status === 'Online' ? 1 : 0);
            statusChart.update();

            // Calcular porcentaje de disponibilidad
            onlineCount = statusData.filter(entry => entry.status === 'Online').length;
            offlineCount = statusData.length - onlineCount;
            const onlinePercentage = (onlineCount / statusData.length) * 100;
            const offlinePercentage = 100 - onlinePercentage;

            // Actualizar gráfico de torta
            availabilityChart.data.datasets[0].data = [onlinePercentage, offlinePercentage];
            availabilityChart.update();
        })
        .catch(error => console.error('Error fetching history:', error)); // Manejar errores
}

// Función para comprobar el estado del sitio
function checkStatus() {
    console.log("Checking status"); // Verificar que se intenta comprobar el estado
    fetch('/check_status')
        .then(response => response.json())
        .then(data => {
            console.log("Check status data:", data); // Verificar los datos recibidos
            statusElement.textContent = data.status;
            timestampElement.textContent = "Última verificación: " + data.timestamp;
            if (data.status === 'Online') {
                statusElement.classList.add('active');
                statusElement.classList.remove('inactive');
            } else {
                statusElement.classList.add('inactive');
                statusElement.classList.remove('active');
            }
            updateCharts();
        })
        .catch(error => console.error('Error checking status:', error)); // Manejar errores
}

// Configurar la verificación cada 5 segundos
setInterval(checkStatus, 10000); // Verificar cada 5 segundos
window.onload = checkStatus; // Verificar cuando se carga la página