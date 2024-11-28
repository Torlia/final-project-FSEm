
/*!
* ** *********************************************
*
* script.js
* It contains the logic required for interacting
* with the greenhouse control system, including 
* sending and receiving data to/from the server 
* and updating the users interface dynamically.
*
* Autores:  De los Cobos Garca Carlos Alberto
*           Sánchez Hernández Marco Antonio
*           Torres Bravo Cecilia
* License:  MIT
*
* ** *********************************************
*/

// Function to control irrigation by sending a POST request to the server
function controlRiego() {
    fetch('/control-irrigacion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    })
    .then(response => response.json())
    .then(data => {
        alert(`Estado de irrigación encendido`);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to program irrigation cycle based on user inputs
function programarCiclo(tipo) {
    const horaInicio = document.getElementById(`hora-inicio-${tipo}`).value;
    const duracion = document.getElementById(`duracion-${tipo}`).value;
    const frecuencia = document.getElementById(`frecuencia-${tipo}`).value;

    // Checks for valid inputs
    if (isNaN(duracion) || duracion < 1 || duracion % 1 !== 0) {
        alert("La duración debe ser un número entero mayor a 0.");
        return;
    }
    if (isNaN(frecuencia) || frecuencia < 1 || frecuencia % 1 !== 0) {
        alert("La frecuencia debe ser un número entero mayor a 0.");
        return;
    }
    if (frecuencia > 7) {
        alert("La frecuencia no puede ser mayor a 7 días, ya que las plantas requieren agua.");
        return;
    }
    if (!horaInicio) {
        alert("La hora de inicio es requerida.");
        return;
    }

    fetch('/programar-ciclo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tipo, hora_inicio:horaInicio, duracion, frecuencia})
    })
    .then(response => response.json())
    .then(data => {
        alert(`Ciclo de ${tipo} programado con éxito: ${data.message}`);
        document.getElementById('ciclo-programado').innerText = 
            `Ciclo programado a las ${horaInicio} por ${duracion} seg, cada ${frecuencia} días`;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to schedule temperature cycle
function programarCicloTemperatura(tipo) {
    const horaInicio = document.getElementById('hora-inicio-temperatura').value;
    const horaFin = document.getElementById('hora-fin-temperatura').value;

    // Validates start and end times
    if (!horaInicio || !horaFin) {
        alert("Se debe de ingresar hora de inicio y de fin del día.");
        return;
    }
    if (horaInicio >= horaFin) {
        alert("La hora de inicio debe ser antes que la hora de fin.");
        return;
    }

    fetch('/programar-ciclo-temperatura', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({tipo, horaInicio, horaFin })
    })
    .then(response => response.json())
    .then(data => {
        alert(`Ciclo de ${tipo} programado con éxito: ${data.message}`);
        document.getElementById('display-ciclo-temperatura').innerText = `Ciclo programado de las ${horaInicio} a las ${horaFin}`;
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// Function to update temperature limits (minimum and maximum values)
function updateTempLimits() {
    const minTemp = document.getElementById('min-temp').value || 14;
    const maxTemp = document.getElementById('max-temp').value || 22;

    document.getElementById('display-min-temp').innerText = minTemp;
    document.getElementById('display-max-temp').innerText = maxTemp;
}

// Function to update temperature limits on the server
function updateTemperature() {
    const minTemp = document.getElementById('min-temp').value || 14;
    const maxTemp = document.getElementById('max-temp').value || 22;

    // Temperature range validation
    if (parseInt(minTemp) >= parseInt(maxTemp)) {
        alert("La temperatura mínima no puede ser mayor o igual a la máxima.");
        return;
    }

    fetch('/actualizar-limites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ minTemp, maxTemp })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
    })
    .catch(error => {
        console.error('Error:', error);
        alert("Hubo un problema al actualizar los límites.");
    });
}

// Function to retrieve and display the current temperature
function obtenerTemperaturaActual() {
    fetch('/mostrar-temperatura', {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        const temperatura = data.temperatura;
        document.getElementById('display-temperatura-actual').innerText = `Temperatura actual: ${temperatura} °C`;
    })
    .catch(error => {
        console.error('Error al obtener la temperatura:', error);
        document.getElementById('display-temperatura-actual').innerText = `Error al cargar la temperatura.`;
    });
}
setInterval(obtenerTemperaturaActual, 1000);
obtenerTemperaturaActual();

// Function to update device power (e.g., for fans, lights, etc.)
function potencia(inputID, dispositivo) {
    const valorPotencia = document.getElementById(inputID).value;

    // Validates power input value
    if (isNaN(valorPotencia) || valorPotencia < 0 || valorPotencia > 100) {
        alert("La potencia debe estar entre 0 y 100.");
        return;
    }

    fetch('/actualizar-potencia', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ dispositivo, valorPotencia })
    })
    .then(response => response.json())
    .then(data => {
        console.log(`Potencia actualizada: ${data.message}`);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

// When the document is loaded, retrieve the historical data and display the three graphs
document.addEventListener('DOMContentLoaded', function() {
    fetch('/historico-datos')
        .then(response => response.json())
        .then(datos => {
            // Display temperature graph
            const ctxTemp = document.getElementById('graficaTemperatura').getContext('2d');
            new Chart(ctxTemp, {
                type: 'line',
                data: {
                    labels: datos.temperaturas.map(item => item.hora),
                    datasets: [
                        {
                            label: 'Temperatura Actual (°C)',
                            data: datos.temperaturas.map(item => item.actualTemp),
                            borderColor: 'yellow',
                            backgroundColor: 'rgba(255, 255, 0, 0.1)',
                            fill: true
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            min: -10,
                            max: 40,
                            ticks: {
                                color: 'white'
                            }
                        },
                        x: {
                            ticks: {
                                color: 'white'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: 'white'
                            }
                        }
                    }
                }
                
            });

            // Display irrigation graph
            const ctxIrrigacion = document.getElementById('graficaIrrigacion').getContext('2d');
            new Chart(ctxIrrigacion, {
                type: 'scatter',
                data: {
                    labels: datos.irrigacion.map(item => item.hora),
                    datasets: [
                        {
                            label: 'Estado de Irrigación',
                            data: datos.irrigacion.map(item => item.estado === 'on' ? 1 : 0),
                            backgroundColor: 'green'
                        }
                    ]
                },
                options: {
                    responsive: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                color: 'white'
                            }
                        },
                        x: {
                            ticks: {
                                color: 'white'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: 'white'
                            }
                        }
                    }
                }                
            });
            
            // Display actions graph
            const graph_acciones = document.getElementById('graficaAcciones').getContext('2d');
            const horas = datos.acciones.map(item => item.hora);
            const tipos = datos.acciones.map(item => item.tipo);
            const tiposAcciones = {
                'irrigacion': 1,
                'ventilador': 2,
                'radiador': 3,
                'temperatura': 4
            };
            const accionesData = tipos.map(tipo => tiposAcciones[tipo]);

            new Chart(graph_acciones, {
                type: 'scatter', 
                data: {
                    datasets: [{
                        label: 'Acciones',
                        data: horas.map((hora, index) => ({
                            x: hora,
                            y: accionesData[index]
                        })),
                        backgroundColor: 'yellow'
                    }]
                },
                options: {
                    scales: {
                        responsive: true,
                        x: {
                            type: 'category',
                            ticks: {
                                color: 'white'
                            }
                        },
                        y: {
                            type: 'linear',
                            ticks: {
                                callback: function(value) {
                                    return Object.keys(tiposAcciones).find(key => tiposAcciones[key] === value);
                                },
                                color: 'white'
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            labels: {
                                color: 'white'
                            }
                        }
                    }
                }
            });

        });
    });

