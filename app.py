
# ## ###############################################
#
# app.py
# It starts the Flask based webserver for the 
# greenhouse control system. It also handles the 
# users requests,sensors data, and the dynamic 
# graphs data.
#
# Autores:  De los Cobos Garca Carlos Alberto
#           Sánchez Hernández Marco Antonio
#           Torres Bravo Cecilia
# License:  MIT
#
# ## ###############################################

from flask import Flask, send_from_directory, render_template, request, jsonify
import threading
import time
from datetime import datetime, timedelta
import json
import smbus2
import struct

from time import sleep

# I2C configuration
i2c = smbus2.SMBus(1)
SLAVE_ADDR = 0x0A

app = Flask(__name__)

# Temperature variables
temperatura = 0.0
temp_min = 18.0
temp_max = 20.0

# Irrigation control variables
frecuencia = 2
duracion = 3

# PID variables
proportional_constant = 20
integral_constant = 0.008
differential_constant = 10
integral = 0
previous_error = 0

"""Principal route for greenhouse control webserver"""
@app.route("/")
def dashboard():
    # Renders dashboard.html as the principal page
    return render_template("dashboard.html")

"""Route for graphs additional page in webserver"""
@app.route("/graph")
def graph():
    # Renders graph.html with dynamic graphs
    return render_template("graph.html")

"""Function to verify and automatically adjust the temperature
to the defined limits"""
def verificar_temperatura():
    # Calls required global variables
    global temperatura, temp_min, temp_max
    global error, temperatura, temp_min, integral, previous_error
    global proportional_constant, integral_constant, differential_constant

    # As long as the application is running it will follow the
    # designed conditionals
    while True:
        # In case the temperature is below the designed minimum
        # It will turn on the radiator
        if temperatura < temp_min:
            # Calculates the error por PID
            error = temp_min - temperatura
            integral += error
            differential = error - previous_error

            # Calculates the output for PID
            proportional_output = proportional_constant * error
            integral_output = integral_constant * integral
            differential_output = differential_constant * differential
            total_output = proportional_output + integral_output + differential_output
            previous_error = error

            # Packages and sends the command in binary to the Pi Pico
            # to turn on the radiator
            data = struct.pack("<bf", 7, total_output)
            msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
            i2c.i2c_rdwr(msg)

            # Sleeps for 1 second, allowing the information to be sent and recieved
            sleep(1)
            print("Temperatura actual:", temperatura,"°C. Radiador encendido.")

            # Registers the taken action in the history file for the dynamic graphs
            hora_actual = datetime.now().strftime('%D %H:%M:%S')
            historico = leer_datos()
            historico["acciones"].append({"hora": hora_actual, "tipo": "radiador"})
            escribir_datos(historico)

        # In case the temperature is over the designed maximum
        # It will turn on the second fan
        elif temperatura > temp_max:
            # Packages and sends the command in binary to the Pi Pico
            # to turn on the second fan
            data = struct.pack("<bf", 5, 0.00)
            msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
            i2c.i2c_rdwr(msg)

            # Sleeps for 1 second, allowing the information to be sent and recieved
            sleep(1)
            print("Temperatura actual:", temperatura,"°C. Ventilador 2 encendido.")

            # Registers the taken action in the history file for the dynamic graphs
            hora_actual = datetime.now().strftime('%D %H:%M:%S')
            historico = leer_datos()
            historico["acciones"].append({"hora": hora_actual, "tipo": "ventilador"})
            escribir_datos(historico)

        # In case the temperature is between the designed minimum and maximum
        else:
            print("Temperatura actual:", temperatura, "°C. Dispositivos apagados.")

            # Packages and sends the command in binary to the Pi Pico
            # to turn off the second fan
            data = struct.pack("<bf", 6, 0.00)
            msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
            i2c.i2c_rdwr(msg)

            # Sleeps for 1 second, allowing the information to be sent and recieved
            sleep(1)

            # Registers the taken action in the history file for the dynamic graphs
            hora_actual = datetime.now().strftime('%D %H:%M:%S')
            historico = leer_datos()
            historico["acciones"].append({"hora": hora_actual, "tipo": "ventilador"})
            escribir_datos(historico)

            # Packages and sends the command in binary to the Pi Pico
            # to turn off the radiator
            data = struct.pack("<bf", 8, 0.00)
            msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
            i2c.i2c_rdwr(msg)

            # Sleeps for 1 second, allowing the information to be sent and recieved
            sleep(1)

            # Registers the taken action in the history file for the dynamic graphs
            hora_actual = datetime.now().strftime('%D %H:%M:%S')
            historico = leer_datos()
            historico["acciones"].append({"hora": hora_actual, "tipo": "radiador"})
            escribir_datos(historico)

"""Function to read temperature from sensors and
obtain the mean"""
def obtener_temperatura():
    # Calls required global variable
    global temperatura
    
    # As long as the application is running,
    # it will obtain the temperature
    while True:
        try:
            # Opens and read files where the sensors stores the information
            with open('/sys/bus/w1/devices/28-3ce1d444ecd1/temperature', 'r') as file:
                content = file.read().replace('\n', ' ')
                temp1 = float(content)/1000
            with open('/sys/bus/w1/devices/28-1906d444568b/temperature', 'r') as file:
                content = file.read().replace('\n', ' ')
                temp2 = float(content)/1000

            # Obtains the mean
            temperatura = (temp1+temp2)/2
        except Exception as e:
            print(f"Error al obtener la temperatura: {e}")

"""Function to show the current greenhouse temperature
in the webserver"""
@app.route("/mostrar-temperatura")
def mostrar_temperatura():
    # Calls required global variables
    global temperatura

    # Registers the current temperature in the history file for the dynamic graphs
    hora_actual = datetime.now().strftime('%D %H:%M:%S')
    historico = leer_datos()
    historico["temperaturas"].append({"hora": hora_actual, "actualTemp": temperatura})
    escribir_datos(historico)
    return jsonify({"temperatura": temperatura}), 200

"""Route to control the irrigation system"""
@app.route("/control-irrigacion", methods=["POST"])
def control_irrigacion():
    try:
        # Packages and sends the command in binary to the Pi Pico
        # to turn on the water pump (irrigation system)
        packed_data = struct.pack("<bf", 9, 1)
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, packed_data)
        i2c.i2c_rdwr(msg)
        print(f"Enviando a Pico: Irrigación activada")

        # Registers the current action in the history file for the dynamic graphs
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

"""Route to schedule an irrigation cyle"""
@app.route("/programar-ciclo", methods=["POST"])
def programar_ciclo():
    # Parses the incoming JSON data for the start time, duration, 
    # and frequency of the cycle
    data = request.get_json()
    hora_inicio = str(data.get('hora_inicio'))
    duracion = int(data.get('duracion')) 
    frecuencia = int(data.get('frecuencia'))

    # Converts the frequency from days into seconds
    frecuencia_segundos = frecuencia * 86400 

    # Validates the data, returns an error if any required value is missing
    if not hora_inicio or not duracion or not frecuencia:
        return jsonify({"error": "Datos incompletos"}), 400

    # Converts and calculates the number of seconds until 
    # the irrigation cycle should start
    ahora = datetime.now()
    hora_inicio_dt = datetime.strptime(hora_inicio, '%H:%M')
    segundos_inicio = (
        (hora_inicio_dt.hour - ahora.hour) * 3600 +
        (hora_inicio_dt.minute - ahora.minute) * 60 -
        ahora.second
    )
    if segundos_inicio < 0:
        segundos_inicio += 86400

    # Defines the irrigation cycle function, which will activate the irrigation
    # system for the set duration
    def ciclo_irrigacion():
        print(f"Iniciando irrigación a las {datetime.now().strftime('%H:%M:%S')}")

        # Packages and sends the command in binary to the Pi Pico
        # to turn on the water pump
        '''packed_data = struct.pack("<bf", 9, 1)
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, packed_data)
        i2c.i2c_rdwr(msg)'''

        # Registers the current action in the history file for the dynamic graphs
        '''hora_actual = datetime.now().strftime('%D %H:%M:%S')
        historico = leer_datos()
        historico["irrigacion"].append({"hora": hora_actual, "estado": "on"})
        historico["acciones"].append({"hora": hora_actual, "tipo": "irrigacion"})
        escribir_datos(historico)'''

        # Waits till the irrigation duration ends
        time.sleep(duracion)

        # Packages and sends the command in binary to the Pi Pico
        # to turn off the water pump
        '''packed_data = struct.pack("<bf", 9, 0)
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, packed_data)
        i2c.i2c_rdwr(msg)'''

        print(f"Finalizando irrigación a las {datetime.now().strftime('%H:%M:%S')}")

    return jsonify({"message": f"Ciclo programado: cada {frecuencia} días, comenzando a las {hora_inicio}"})

"""Route to schedule the night and day cycle"""
@app.route("/programar-ciclo-temperatura", methods=["POST"])
def programar_ciclo_temperatura():
    # Parses the incoming JSON data for the start and end times
    # of the temperature control cycle
    data = request.get_json()
    hora_inicio = str(data.get('horaInicio'))
    hora_fin = str(data.get('horaFin'))

    # Validates the data, returns an error if any required value is missing
    if not hora_inicio or not hora_fin:
        return jsonify({"error": "Datos incompletos"}), 400

    # Converts and calculates the number of seconds until 
    # the temperature cycle should start
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

    # Defines the temperature cycle function, which will activate the day
    # system for the set duration
    def ciclo_temperatura():
        print(f"Iniciando ciclo de temperatura a las {datetime.now().strftime('%H:%M:%S')}")
        # Packages and sends the command in binary to the Pi Pico
        # to turn on the radiator
        '''data = struct.pack("<bf", 7, total_output)
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
        i2c.i2c_rdwr(msg)'''

        # Registers the taken action in the history file for the dynamic graphs
        '''hora_actual = datetime.now().strftime('%D %H:%M:%S')
        historico = leer_datos()
        historico["acciones"].append({"hora": hora_actual, "tipo": "radiador"})
        escribir_datos(historico)'''

        # Waits till the temperature cycle ends
        time.sleep(duracion_ciclo)

        # Packages and sends the command in binary to the Pi Pico
        # to turn off the radiator
        '''data = struct.pack("<bf", 8, 0.00)
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, data)
        i2c.i2c_rdwr(msg)'''

        # Registers the taken action in the history file for the dynamic graphs
        '''hora_actual = datetime.now().strftime('%D %H:%M:%S')
        historico = leer_datos()
        historico["acciones"].append({"hora": hora_actual, "tipo": "radiador"})
        escribir_datos(historico)'''

        print(f"Finalizando ciclo de temperatura a las {datetime.now().strftime('%H:%M:%S')}")

    return jsonify({"message": f"Ciclo de temperatura programado: desde {hora_inicio} hasta {hora_fin}"})

 """Route to update the temperature minimum and maximum"""
@app.route('/actualizar-limites', methods=['POST'])
def actualizar_limites():
    # Calls the global required variables
    global temp_min, temp_max

    # Parses the incoming JSON data for the minimum
    # and maximum temperatures
    data = request.get_json()
    temp_min = float(data.get('minTemp'))
    temp_max = float(data.get('maxTemp'))

    # Validates the date, returns an error in case any parameter is missing
    if not temp_min or not temp_max or temp_min >= temp_max:
        return jsonify({"message": "Error: los límites de temperatura no son válidos."}), 400

    print(f"Temperatura mínima: {temp_min}°C, Temperatura máxima: {temp_max}°C")

    return jsonify({"message": "Límites de temperatura actualizados correctamente."})

"""Route to update the power setting of the radiator"""
@app.route("/actualizar-potencia", methods=["POST"])
def actualizar_potencia():
    # Parses the incoming JSON data for the device
    # and designed power values
    data = request.get_json()
    dispositivo = int(data.get('dispositivo'))
    valor_potencia = float(data.get('valorPotencia'))
    
    # Validates the new power value, ensuring it is a valid number between 0 and 100
    if not (0 <= valor_potencia <= 100):
        return jsonify({"error": "Potencia debe estar entre 0 y 100"}), 400

    # Packages the command in binary to update the power
    packed_data = struct.pack("<bf", dispositivo, valor_potencia)
    
    try:
        # Sends the command in binary to the Pi Pico
        # to update the device power settings
        msg = smbus2.i2c_msg.write(SLAVE_ADDR, packed_data)
        i2c.i2c_rdwr(msg)
        print(f"Enviando a Pico: Dispositivo {dispositivo}, Potencia {valor_potencia}")
        
        # Defines the device type according to the devices code
        dispositivoTipo = ""
        if dispositivo == 0 or dispositivo == 1:
            dispositivoTipo = "ventilador"
        else: 
            dispositivoTipo = "radiador"

        # Registers the taken action in the history file for the dynamic graphs        
        hora_actual = datetime.now().strftime('%H:%M')
        historico = leer_datos()
        historico["acciones"].append({"hora": hora_actual, "tipo": dispositivoTipo})
        escribir_datos(historico)

        return jsonify({"message": "Potencia actualizada"})
    except Exception as e:
        print(f"Error enviando datos a Pico: {e}")
        return jsonify({"error": "Error al enviar datos a la Raspberry Pi."}), 500

    return jsonify({"message": f"Potencia de dispositivo con ID {dispositivo} actualizada a {valor_potencia}%"})

"""Function to read data from the historical data file"""
def leer_datos():
    try:
        # Opens and reads the historical data file
        with open('/home/greenhouse/final-project-FSEM/historico.txt', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {"temperaturas": [], "irrigacion": [], "acciones": []}
    except json.JSONDecodeError:
        return {"temperaturas": [], "irrigacion": [], "acciones": []}

"""Function to write data from the historical data file"""
def escribir_datos(datos):
    # Opens and write the updated data in the historical data file
    with open('/home/greenhouse/final-project-FSEM/historico.txt', 'w') as file:
        json.dump(datos, file, indent=4)

"""Route to retrieve the 20 latest historical data for temperatures, irrigation,
and actions"""
@app.route("/historico-datos", methods=["GET"])
def historico_datos():
    # Retrieves the data by calling the required function
    historico = leer_datos()

    # For a better visualization, it retrieves only the latest 20 
    # records for each graph
    historico_recortado = {
        "temperaturas": historico["temperaturas"][-20:],
        "irrigacion": historico["irrigacion"][-20:],
        "acciones": historico["acciones"][-20:]
    }

    return jsonify(historico_recortado)

"""Main entry point for the application"""
if __name__ == "__main__":
    # Start a thread to continuously retrieve the current temperature
    t1 = threading.Thread(target=obtener_temperatura, args=())
    t1.start()

    # Waits for 3 seconds in order to allow inital data collection
    sleep(3)

    # Start a thread to continuously verify and adjust the temperature
    # to its designed limits
    t2 = threading.Thread(target=verificar_temperatura, args=())
    t2.start()

    # Starts the Flask web server, 
    # Allows access on all network interfaces (0.0.0.0) at port 5000
    app.run(host="0.0.0.0", port=5000)

