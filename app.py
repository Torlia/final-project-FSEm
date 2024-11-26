from flask import Flask, send_from_directory, render_template, request, jsonify
import threading
import time
from timeloop import Timeloop
from datetime import datetime, timedelta
#import smbus
#import struct

#i2c = smbus2.SMBus(1)
#SLAVE_ADDR = 0x0A

app = Flask(__name__)

dispositivos = {
    'radiador': 0x01,
    'ventilador1': 0x02,
    'ventilador2': 0x03,
    'bomba': 0x04
}
temperatura = 0.0
temp_min = 18.0
temp_max = 20.0
'''ciclo_riego = None
ciclo_temperatura = None
ciclo_thread = None
hora_fin = "00:00"
hora_inicio = "00:00"
frecuencia = 0'''

tl = Timeloop()
frecuencia = 2
duracion = 3
ciclo_irrigacion_thread = None

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
        #data_sent = [dispositivos['bomba'], estado_value]
        #msg = smbus2.i2c_msg.write(SLAVE_ADDR, [data_sent])
        #i2c.i2c_rdwr(msg)
        print(f"Enviando a Pico: Irrigación {estado}")
    except Exception as e:
        print(f"Error enviando datos a Pico: {e}")
        return jsonify({"error": "Error al enviar datos a la Raspberry Pi."}), 500
    
    return jsonify({"message": f"{estado}"})

@app.route("/programar-ciclo", methods=["POST"])
def programar_ciclo():
    global ciclo_irrigacion_thread
    data = request.get_json()
    hora_inicio = str(data.get('hora_inicio'))
    duracion = int(data.get('duracion')) 
    frecuencia = int(data.get('frecuencia'))

    frecuencia_segundos = frecuencia * 86400 

    if ciclo_irrigacion_thread is not None:
        ciclo_irrigacion_thread.cancel()

    if not hora_inicio or not duracion or not frecuencia:
        return jsonify({"error": "Datos incompletos"}), 400

    ahora = datetime.now()
    hora_inicio_dt = datetime.strptime(hora_inicio, '%H:%M')
    segundos_inicio = (
        (hora_inicio_dt.hour - ahora.hour) * 3600 +
        (hora_inicio_dt.minute - ahora.minute) * 60 -
        ahora.second
    )
    if segundos_inicio < 0:
        segundos_inicio += 86400  # Ajustar para el día siguiente si ya pasó la hora de inicio

    @tl.job(interval=timedelta(seconds=frecuencia_segundos))
    def ciclo_irrigacion():
        print(f"Iniciando irrigación a las {datetime.now().strftime('%H:%M:%S')}")
        #data_sent = [dispositivos['bomba'], 1]
        #msg = smbus2.i2c_msg.write(SLAVE_ADDR, [data_sent])
        #i2c.i2c_rdwr(msg)
        time.sleep(duracion)
        #data_sent = [dispositivos['bomba'], 0]
        #msg = smbus2.i2c_msg.write(SLAVE_ADDR, [data_sent])
        #i2c.i2c_rdwr(msg)
        print(f"Finalizando irrigación a las {datetime.now().strftime('%H:%M:%S')}")

    ciclo_irrigacion_thread = threading.Timer(segundos_inicio, lambda: ciclo_irrigacion())
    ciclo_irrigacion_thread.start()

    return jsonify({"message": f"Ciclo programado: cada {frecuencia} días, comenzando a las {hora_inicio}"})


    '''
    global ciclo_thread, hora_fin, hora_inicio, frecuencia
    data = request.get_json()
    tipo = data.get('tipo')
    hora_inicio = data.get('horaInicio')
    duracion = int(data.get('duracion'))
    frecuencia = data.get('frecuencia')
    try:
        horas, minutos = map(int, hora_inicio.split(":"))
        minutos += duracion
        if minutos >= 60:
            horas += minutos // 60
            minutos = minutos % 60
        hora_fin = f"{horas % 24:02d}:{minutos:02d}"
        if ciclo_thread and ciclo_thread.is_alive():
            ciclo_thread.join()
        ciclo_thread = threading.Thread(
            target=supervisar_ciclo,
            args=(tipo, hora_inicio, hora_fin, dispositivos['bomba'], frecuencia)
        )
        ciclo_thread.start()
    except Exception as e:
        print(f"Error programando ciclo: {e}")
        return jsonify({"error": "Error al programar ciclo."}), 500

    return jsonify({"message": f"Ciclo de {tipo} programado para comenzar a las {hora_inicio} por {duracion} minutos cada {frecuencia} días"})
    '''

@app.route("/supervisar-ciclo", methods=["POST"])
def supervisar_ciclo():
    global hora_inicio, frecuencia
    hora_inicio = data.get('horaInicio')

    while True:
        fecha_actual = datetime.now()
        hora_actual = fecha_actual.strftime("%H:%M")
        dia_actual = fecha_actual.strftime("%d")

        if hora_actual == hora_inicio:
            # data_sent = [dispositivos['bomba'], 1]
            # smbus2.i2c_msg.write(SLAVE_ADDR, data_sent)
            # i2c.i2c_rdwr(msg)
            print(f"{tipo} iniciado a las {hora_actual}")

        last_irrigation = datetime.min.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
        days_since_last_irrigation = (fecha_actual - last_irrigation).days
        if days_since_last_irrigation >= frecuencia:
            print(f"Riego ejecutado")
            # data_sent = [dispositivos['bomba'], 1]
            # smbus2.i2c_msg.write(SLAVE_ADDR, data_sent)
            # i2c.i2c_rdwr(msg)
            last_irrigation = fecha_actual

        if hora_actual == hora_fin:
            # data_sent = [dispositivos['bomba'], 0]
            # smbus2.i2c_msg.write(SLAVE_ADDR, data_sent)
            # i2c.i2c_rdwr(msg)
            print(f"{tipo} terminado a las {hora_actual}")

'''
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
    '''
@app.route("/obtener-temperatura", methods=["GET"])
def obtener_temperatura():
    global temperatura
    try:
        with open('/home/user/Documents/sensor.txt', 'r') as file:
            content = file.read().replace('\n', ' ')
            temperatura = float(content)

        return jsonify({"temperatura": temperatura}), 200
    except Exception as e:
        print(f"Error al obtener la temperatura: {e}")
        return jsonify({"error": "No se pudo obtener la temperatura"}), 500

@app.route('/actualizar-limites', methods=['POST'])
def actualizar_limites():
    global temp_min, temp_max
    data = request.get_json()
    temp_min = float(data.get('minTemp'))
    temp_max = float(data.get('maxTemp'))

    if not temp_min or not temp_max or temp_min >= temp_max:
        return jsonify({"message": "Error: los límites de temperatura no son válidos."}), 400

    #data_sent = [temp_min, temp_max]
    #msg = smbus2.i2c_msg.write(SLAVE_ADDR, data_sent)
    #i2c.i2c_rdwr(msg)
    print(f"Temperatura mínima: {temp_min}°C, Temperatura máxima: {temp_max}°C")
    return jsonify({"message": "Límites de temperatura actualizados correctamente."})

@app.route('/verificar-temperatura', methods=['GET'])
def verificar_temperatura():
    global temperatura, temp_min, temp_max
    if temperatura is None:
        return jsonify({"mensaje": "Error: No se pudo obtener la temperatura actual."})

    if temperatura < temp_min:
        # smbus2.i2c_msg.write(SLAVE_ADDR, [dispositivos['ventilador2'], 0])
        # smbus2.i2c_msg.write(SLAVE_ADDR, [dispositivos['radiador'], 1])
        print("Temperatura actual:", temperatura,"°C. Radiador encendido.")
        return jsonify({"mensaje": f"Temperatura actual: {temperatura}°C. Radiador encendido."})
    elif temperatura > temp_max:
        # smbus2.i2c_msg.write(SLAVE_ADDR, [dispositivos['radiador'], 0])
        # smbus2.i2c_msg.write(SLAVE_ADDR, [dispositivos['ventilador2'], 1])
        print("Temperatura actual:", temperatura,"°C. Ventilador 2 encendido.")
        return jsonify({"mensaje": f"Temperatura actual: {temperatura}°C. Ventilador 2 encendido."})
    else:
        print("Temperatura actual:", temperatura, "°C. Dispositivos apagados.")
        # smbus2.i2c_msg.write(SLAVE_ADDR, [dispositivos['radiador'], 0])
        # smbus2.i2c_msg.write(SLAVE_ADDR, [dispositivos['ventilador2'], 0])
        return jsonify({"mensaje": f"Temperatura actual: {temperatura}°C. Todo en orden, dispositivos apagados."})

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
    threading.Thread(target=lambda: tl.start(block=True), daemon=True).start()
    app.run(host="0.0.0.0", port=5000)