from flask import Flask, send_from_directory, render_template, request, jsonify
#import smbus
#import struct

#i2c = smbus2.SMBus(1)
#SLAVE_ADDR = 0x0A

app = Flask(__name__)

dispositivos = {
    'radiador': 0x01,
    'ventilador1': 0x02,
    'ventilador2': 0x03
}

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/graph")
def graph():
    return render_template("graph.html")

@app.route("/control-irrigacion", methods=["POST"])
def control_irrigacion():
    data = request.get_json()
    estado = data.get('estado')
    try:
        #estado_value = 1 if estado == 'on' else 0
        #msg = smbus2.i2c_msg.write(SLAVE_ADDR, [estado_value])
        #i2c.i2c_rdwr(msg)
        print(f"Enviando a Pico: Irrigación {estado}")
    except Exception as e:
        print(f"Error enviando datos a Pico: {e}")
        return jsonify({"error": "Error al enviar datos a la Raspberry Pi."}), 500
    
    return jsonify({"message": f"{estado}"})

@app.route("/programar-ciclo", methods=["POST"])
def programar_ciclo():
    data = request.get_json()
    tipo = data.get('tipo')
    hora_inicio = data.get('horaInicio')
    duracion = data.get('duracion')
    frecuencia = data.get('frecuencia')
    try:
        #horas, minutos = map(int, hora_inicio.split(':'))
        #if horas > 255 or minutos > 255 or duracion > 255 or frecuencia > 255:
        #    raise ValueError("Los valores de hora o duración o frecuencia son demasiado altos.")
        #data_sent = [horas, minutos, duracion, frecuencia]
        #msg = smbus2.i2c_msg.write(SLAVE_ADDR, data_sent)
        #i2c.i2c_rdwr(msg)
        print(f"Enviando a Pico: Hora {hora_inicio}, Duración {duracion} minutos, Frecuencia {frecuencia} días")
    except Exception as e:
        print(f"Error enviando datos a Pico: {e}")
        return jsonify({"error": "Error al enviar datos a la Raspberry Pi."}), 500

    return jsonify({"message": f"Ciclo de {tipo} programado para comenzar a las {hora_inicio} por {duracion} minutos cada {frecuencia} días"})

@app.route("/programar-ciclo-temperatura", methods=["POST"])
def programar_ciclo_temperatura():
    data = request.get_json()
    tipo = data.get('tipo')
    hora_inicio = data.get('horaInicio')
    hora_fin = data.get('horaFin')

    try:
        #data_sent = [hora_inicio, hora_fin]
        #msg = smbus2.i2c_msg.write(SLAVE_ADDR, data_sent)
        #i2c.i2c_rdwr(msg)
        print(f"Enviando a Pico: Hora inicio: {hora_inicio}, Hora fin: {hora_fin}")
        return jsonify({"message": f"Ciclo de {tipo} programado para comenzar a las {hora_inicio} y terminar a las {hora_fin}"})
    except Exception as e:
        print(f"Error enviando datos a Pico: {e}")
        return jsonify({"error": "Error al enviar datos a la Raspberry Pi."}), 500

@app.route("/actualizar-potencia", methods=["POST"])
def actualizar_potencia():
    data = request.get_json()
    dispositivo = data.get('dispositivo')
    valor_potencia = int(data.get('valorPotencia'))

    if dispositivo not in dispositivos:
        return jsonify({"error": "Dispositivo no válido."}), 400

    try:
        identificador = dispositivos[dispositivo]
        # msg = smbus2.i2c_msg.write(SLAVE_ADDR, [identificador, valor_potencia])
        # i2c.i2c_rdwr(msg)
        print(f"Enviando a Pico: Dispositivo {dispositivo} (ID: {identificador}), Potencia {valor_potencia}")
    except Exception as e:
        print(f"Error enviando datos a Pico: {e}")
        return jsonify({"error": "Error al enviar datos a la Raspberry Pi."}), 500

    return jsonify({"message": f"Potencia de {dispositivo} actualizada a {valor_potencia}%"})

@app.route("/historico-datos", methods=["GET"])
def historico_datos():
    datos_dummy = {
        "temperaturas": [
            {"hora": "08:00", "minTemp": 15.2, "maxTemp": 22.5},
            {"hora": "12:00", "minTemp": 16.0, "maxTemp": 24.0},
            {"hora": "16:00", "minTemp": 17.5, "maxTemp": 23.5},
            {"hora": "20:00", "minTemp": 14.5, "maxTemp": 20.5},
        ],
        "irrigacion": [
            {"hora": "09:00", "estado": "on"},
            {"hora": "14:00", "estado": "off"},
            {"hora": "18:00", "estado": "on"},
        ],
        "acciones": [
            {"hora": "08:00", "tipo": "irrigacion"},
            {"hora": "11:00", "tipo": "ventilador"},
            {"hora": "12:00", "tipo": "radiador"},
            {"hora": "12:06", "tipo": "ventilador"},
            {"hora": "12:10", "tipo": "ventilador"},
            {"hora": "16:00", "tipo": "temperatura"},
        ]
    }
    return jsonify(datos_dummy)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)