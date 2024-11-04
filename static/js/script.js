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
