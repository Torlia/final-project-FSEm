function controlRiego() {
    const toggle = document.getElementById('irrigacionToggle');
    const estado = toggle.checked ? 'on' : 'off';

    fetch('/control-irrigacion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ estado })
    })
    .then(response => response.json())
    .then(data => {
        alert(`Estado de irrigación: ${data.message}`);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function programarCiclo(tipo) {
    const horaInicio = document.getElementById(`hora-inicio-${tipo}`).value;
    const duracion = document.getElementById(`duracion-${tipo}`).value;

    if (isNaN(duracion) || duracion < 1 || duracion % 1 !== 0) {
        alert("La duración debe ser un número entero mayor a 0.");
        return;
    }

    fetch('/programar-ciclo', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ tipo, horaInicio, duracion })
    })
    .then(response => response.json())
    .then(data => {
        alert(`Ciclo de ${tipo} programado con éxito: ${data.message}`);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function actualizarTemperatura() {
    let minTemp = document.getElementById('min-temp').value;
    let maxTemp = document.getElementById('max-temp').value;

    minTemp = parseFloat(parseFloat(minTemp).toFixed(1));
    maxTemp = parseFloat(parseFloat(maxTemp).toFixed(1));

    if (parseInt(minTemp) >= parseInt(maxTemp)) {
        alert("La temperatura mínima debe ser menor que la temperatura máxima.");
        return;
    }
    if (minTemp < -55 || minTemp > 150) {
        alert("La temperatura mínima debe estar entre -55°C y 150°C.");
        return;
    }
    if (maxTemp < -55 || maxTemp > 150) {
        alert("La temperatura máxima debe estar entre -55°C y 150°C.");
        return;
    }


    fetch('/actualizar-temperatura', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ minTemp, maxTemp })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('display-min-temp').innerText = `${data.minTemp}°C`;
        document.getElementById('display-max-temp').innerText = `${data.maxTemp}°C`;
        alert(`Temperaturas actualizadas: Mínima ${data.minTemp}°C, Máxima ${data.maxTemp}°C`);
    })
    .catch(error => {
        console.error('Error:', error);
    });
}

function potencia(slider, spanID, dispositivo) {
    const valorPotencia = slider.value;
    document.getElementById(spanID).innerText = valorPotencia + "%";

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

document.addEventListener('DOMContentLoaded', function() {
    fetch('/historico-datos')
        .then(response => response.json())
        .then(datos => {
            const ctxTemp = document.getElementById('graficaTemperatura').getContext('2d');
            new Chart(ctxTemp, {
                type: 'line',
                data: {
                    labels: datos.temperaturas.map(item => item.hora),
                    datasets: [
                        {
                            label: 'Temperatura Mínima (°C)',
                            data: datos.temperaturas.map(item => item.minTemp),
                            borderColor: 'blue',
                            backgroundColor: 'rgba(0, 0, 255, 0.1)',
                            fill: true
                        },
                        {
                            label: 'Temperatura Máxima (°C)',
                            data: datos.temperaturas.map(item => item.maxTemp),
                            borderColor: 'red',
                            backgroundColor: 'rgba(255, 0, 0, 0.1)',
                            fill: true
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

            const ctxIrrigacion = document.getElementById('graficaIrrigacion').getContext('2d');
            new Chart(ctxIrrigacion, {
                type: 'bar',
                data: {
                    labels: datos.irrigacion.map(item => item.hora),
                    datasets: [
                        {
                            label: 'Estado de Irrigación (1 = On, 0 = Off)',
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
