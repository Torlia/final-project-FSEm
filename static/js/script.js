function controlRiego() {
    fetch('/control-irrigacion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
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
    const frecuencia = document.getElementById(`frecuencia-${tipo}`).value;

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

function programarCicloTemperatura(tipo) {
    const horaInicio = document.getElementById('hora-inicio-temperatura').value;
    const horaFin = document.getElementById('hora-fin-temperatura').value;

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

function updateTempLimits() {
    const minTemp = document.getElementById('min-temp').value || 14;
    const maxTemp = document.getElementById('max-temp').value || 22;

    document.getElementById('display-min-temp').innerText = minTemp;
    document.getElementById('display-max-temp').innerText = maxTemp;
}

function updateTemperature() {
    const minTemp = document.getElementById('min-temp').value || 14;
    const maxTemp = document.getElementById('max-temp').value || 22;

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

function obtenerTemperaturaActual() {
    fetch('/obtener-temperatura', {
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

function verificarTemperaturaPeriodicamente() {
    setInterval(() => {
        fetch('/verificar-temperatura')
            .then(response => response.json())
            .then(data => {
                console.log(data.mensaje);
            })
            .catch(error => console.error('Error al verificar la temperatura:', error));
    }, 1000);
}
verificarTemperaturaPeriodicamente();

function potencia(inputID, dispositivo) {
    const valorPotencia = document.getElementById(inputID).value;

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
