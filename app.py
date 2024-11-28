from flask import Flask, send_from_directory, render_template, request, jsonify
import threading
import time
from datetime import datetime, timedelta
import json
import smbus2
import struct

from time import sleep

i2c = smbus2.SMBus(1)
SLAVE_ADDR = 0x0A

app = Flask(__name__)

temperatura = 0.0
temp_min = 18.0
temp_max = 20.0
frecuencia = 2
duracion = 3

# PID
proportional_constant = 20
integral_constant = 0.008
differential_constant = 10

integral = 0
previous_error = 0

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/graph")
def graph():
    return render_template("graph.html")

def verificar_temperatura():
    global temperatura, temp_min, temp_max
    global error, temperatura, temp_min, integral, previous_error
    global proportional_constant, integral_constant, differential_constant

    while True:
        if temperatura < temp_min:
            error = temp_min - temperatura
            integral += error
            differential = error - previous_error
        
            proportional_output = proportional_constant * error
            integral_output = integral_constant * integral
            differential_output = differential_constant * differential
        
            total_output = proportional_output + integral_output + differential_output
        
            previous_error = error

            print(total_output)

            data = struct.pack("<bf", 7, total_output)
            msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
            i2c.i2c_rdwr(msg)
            sleep(1)
            print("Temperatura actual:", temperatura,"°C. Radiador encendido.")
            #control_radiador()
            hora_actual = datetime.now().strftime('%D %H:%M:%S')
            historico = leer_datos()
            historico["acciones"].append({"hora": hora_actual, "tipo": "radiador"})
            escribir_datos(historico)
        elif temperatura > temp_max:
            data = struct.pack("<bf", 5, 0.00)
            msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
            i2c.i2c_rdwr(msg)
            sleep(1)
            print("Temperatura actual:", temperatura,"°C. Ventilador 2 encendido.")
            hora_actual = datetime.now().strftime('%D %H:%M:%S')
            historico = leer_datos()
            historico["acciones"].append({"hora": hora_actual, "tipo": "ventilador"})
            escribir_datos(historico)
        else:
            print("Temperatura actual:", temperatura, "°C. Dispositivos apagados.")
            data = struct.pack("<bf", 6, 0.00)
            msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
            i2c.i2c_rdwr(msg)
            sleep(1)
            data = struct.pack("<bf", 8, 0.00)
            msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
            i2c.i2c_rdwr(msg)
            sleep(1)

def obtener_temperatura():
    global temperatura
    while True:
        try:
            with open('/sys/bus/w1/devices/28-3ce1d444ecd1/temperature', 'r') as file:
                content = file.read().replace('\n', ' ')
                temp1 = float(content)/1000
            with open('/sys/bus/w1/devices/28-1906d444568b/temperature', 'r') as file:
                content = file.read().replace('\n', ' ')
                temp2 = float(content)/1000

            temperatura = (temp1+temp2)/2
        except Exception as e:
            print(f"Error al obtener la temperatura: {e}")

def control_radiador():
    global error, temperatura, temp_min, integral, previous_error
    global proportional_constant, integral_constant, differential_constant

    while temp_min < temperatura:
        error = temp_min - temperatura
        integral += error
        differential = error - previous_error
        
        proportional_output = proportional_constant * error
        integral_output = integral_constant * integral
        differential_output = differential_constant * differential
        
        total_output = proportional_output + integral_output + differential_output
        
        previous_error = error

        print(total_output)
        
        data = struct.pack("<bf", 7, float(total_output))
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
        i2c.i2c_rdwr(msg)

        sleep(1)

@app.route("/mostrar-temperatura")
def mostrar_temperatura():
    global temperatura
    hora_actual = datetime.now().strftime('%D %H:%M:%S')
    historico = leer_datos()
    historico["temperaturas"].append({"hora": hora_actual, "actualTemp": temperatura})
    escribir_datos(historico)
    return jsonify({"temperatura": temperatura}), 200

@app.route("/control-irrigacion", methods=["POST"])
def control_irrigacion():
    try:
        packed_data = struct.pack("<bf", 9, 1)
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, packed_data)
        i2c.i2c_rdwr(msg)
        print(f"Enviando a Pico: Irrigación activada")

        hora_actual = datetime.now().strftime('%D %H:%M:%S')
        historico = leer_datos()
        historico["irrigacion"].append({"hora": hora_actual, "estado": "on"})
        historico["acciones"].append({"hora": hora_actual, "tipo": "irrigacion"})
        escribir_datos(historico)

        return jsonify({"message": "Irrigación activada con éxito"}), 200
    except Exception as e:
        print(f"Error enviando datos a Pico: {e}")
        return jsonify({"error": "Error al enviar datos a la Raspberry Pi."}), 500
    
    return jsonify({"message": "Irrigación activada con éxito"})

@app.route("/programar-ciclo", methods=["POST"])
def programar_ciclo():
    data = request.get_json()
    hora_inicio = str(data.get('hora_inicio'))
    duracion = int(data.get('duracion')) 
    frecuencia = int(data.get('frecuencia'))

    frecuencia_segundos = frecuencia * 86400 

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
        segundos_inicio += 86400

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

    return jsonify({"message": f"Ciclo programado: cada {frecuencia} días, comenzando a las {hora_inicio}"})

@app.route("/programar-ciclo-temperatura", methods=["POST"])
def programar_ciclo_temperatura():
    data = request.get_json()
    hora_inicio = str(data.get('horaInicio'))
    hora_fin = str(data.get('horaFin'))

    if not hora_inicio or not hora_fin:
        return jsonify({"error": "Datos incompletos"}), 400

    ahora = datetime.now()
    hora_inicio_dt = datetime.strptime(hora_inicio, '%H:%M')
    hora_fin_dt = datetime.strptime(hora_fin, '%H:%M')
    segundos_inicio = (
        (hora_inicio_dt.hour - ahora.hour) * 3600 +
        (hora_inicio_dt.minute - ahora.minute) * 60 -
        ahora.second
    )
    if segundos_inicio < 0:
        duracion_ciclo = (hora_fin_dt - hora_inicio_dt).seconds 

    def ciclo_temperatura():
        print(f"Iniciando ciclo de temperatura a las {datetime.now().strftime('%H:%M:%S')}")
        #data_sent = [dispositivos['radiador'], 1]
        #msg = smbus2.i2c_msg.write(SLAVE_ADDR, [data_sent])
        #i2c.i2c_rdwr(msg)
        time.sleep(duracion_ciclo)
        #data_sent = [dispositivos['radiador'], 0]
        #msg = smbus2.i2c_msg.write(SLAVE_ADDR, [data_sent])
        #i2c.i2c_rdwr(msg)
        print(f"Finalizando ciclo de temperatura a las {datetime.now().strftime('%H:%M:%S')}")

    return jsonify({"message": f"Ciclo de temperatura programado: desde {hora_inicio} hasta {hora_fin}"})
    
@app.route('/actualizar-limites', methods=['POST'])
def actualizar_limites():
    global temp_min, temp_max
    data = request.get_json()
    temp_min = float(data.get('minTemp'))
    temp_max = float(data.get('maxTemp'))

    if not temp_min or not temp_max or temp_min >= temp_max:
        return jsonify({"message": "Error: los límites de temperatura no son válidos."}), 400

    print(f"Temperatura mínima: {temp_min}°C, Temperatura máxima: {temp_max}°C")

    return jsonify({"message": "Límites de temperatura actualizados correctamente."})

@app.route("/actualizar-potencia", methods=["POST"])
def actualizar_potencia():
    data = request.get_json()
    dispositivo = int(data.get('dispositivo'))
    valor_potencia = float(data.get('valorPotencia'))
    
    if not (0 <= valor_potencia <= 100):
        return jsonify({"error": "Potencia debe estar entre 0 y 100"}), 400

    packed_data = struct.pack("<bf", dispositivo, valor_potencia)
    
    try:
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, packed_data)
        i2c.i2c_rdwr(msg)
        print(f"Enviando a Pico: Dispositivo {dispositivo}, Potencia {valor_potencia}")

        dispositivoTipo = ""
        if dispositivo == 0 or dispositivo == 1:
            dispositivoTipo = "ventilador"
        else: 
            dispositivoTipo = "radiador"

        hora_actual = datetime.now().strftime('%H:%M')
        historico = leer_datos()
        historico["acciones"].append({"hora": hora_actual, "tipo": dispositivoTipo})
        escribir_datos(historico)

        return jsonify({"message": "Potencia actualizada"})
    except Exception as e:
        print(f"Error enviando datos a Pico: {e}")
        return jsonify({"error": "Error al enviar datos a la Raspberry Pi."}), 500

    return jsonify({"message": f"Potencia de dispositivo con ID {dispositivo} actualizada a {valor_potencia}%"})

def leer_datos():
    try:
        with open('/home/greenhouse/final-project-FSEM/historico.txt', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"temperaturas": [], "irrigacion": [], "acciones": []}
    except json.JSONDecodeError:
        return {"temperaturas": [], "irrigacion": [], "acciones": []}

def escribir_datos(datos):
    with open('/home/greenhouse/final-project-FSEM/historico.txt', 'w') as file:
        json.dump(datos, file, indent=4)

@app.route("/historico-datos", methods=["GET"])
def historico_datos():
    historico = leer_datos()

    historico_recortado = {
        "temperaturas": historico["temperaturas"][-20:],
        "irrigacion": historico["irrigacion"][-20:],
        "acciones": historico["acciones"][-20:]
    }

    return jsonify(historico_recortado)


if __name__ == "__main__":
    t1 = threading.Thread(target=obtener_temperatura, args=())
    t1.start()
    sleep(3)
    t2 = threading.Thread(target=verificar_temperatura, args=())
    t2.start()
    app.run(host="0.0.0.0", port=5000)

