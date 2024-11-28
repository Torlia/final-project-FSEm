# * ** *********************************************
# *
# * main.py
# * This script controls hardware components in a greenhouse system, including fans,
# * a heater, and a water pump. It uses I2C communication to receive commands and adjust
# * the behavior of the system.
# *
# * Authors:  De los Cobos García Carlos Alberto
# *           Sánchez Hernández Marco Antonio
# *           Torres Bravo Cecilia
# * License:  MIT
# *
# * ** *********************************************

from utime import sleep_ms, sleep_us
from machine import Pin, PWM, ADC
from i2cslave import I2CSlave

import ustruct
import rp2

# Set up I2C communication as slave at address 0x0A
i2c = I2CSlave(address=0x0A)

# Initialize pins for controlling devices
zxpin = Pin(2, Pin.IN)
trpin = Pin(3, Pin.OUT)
fan_1 = Pin(19)
fan_2 = Pin(20)
water_pump = Pin(21)
humidity_sensor = ADC(0)

# Initialize PWM (Pulse Width Modulation) to control fan speeds
fan_1_pwm = PWM(fan_1)
fan_2_pwm = PWM(fan_2)

# Set PWM frequency for both fans
frequency = 31
fan_1_pwm.freq(frequency)
fan_2_pwm.freq(frequency)

# Default fan speeds and heater brightness
fan_1_speed = 32768
fan_2_speed = 32768
heater_brightness = 20

# Define a state machine for dimmer control 
# Controls the heater's brightness
@rp2.asm_pio(set_init=rp2.PIO.OUT_LOW)
def dimmer():
    set(pin, 0)
    pull()
    mov(x, osr)

    label('waitzx')
    wrap_target()
    wait(0, pin, 0)
    pull(noblock)
    mov(x, osr)
    mov(y, x)
    wait(1, pin, 0)
    nop() [4]

    label('delay')
    jmp(y_dec, 'delay')
    set(pins, 1)
    set(pins, 0)
    jmp('waitzx')
    wrap()
    
# Initialize the state machine
sm = rp2.StateMachine(0, dimmer, freq=5_000, in_base=zxpin, set_base=trpin)
sm.active(1)

def adjust_brightness(brightness):
    if brightness < 1:
        sm.active(0)  # Deactivate state machine to turn off the light completely
        print(f'Set Brightness: {brightness}% | Light OFF')
    else:
        delay = 21 - int(21 * brightness / 100)
        sm.put(delay)
        sm.active(1)  # Ensure the state machine is active for brightness control
        print(f'Set Brightness: {brightness}% | Delay: {delay}')

# Main function to process commands and control devices
def main():
    global fan_1_speed, fan_2_speed, heater_brightness
    
    while True:
        fan_1_pwm.duty_u16(fan_1_speed)
        # Wait until exactly 4 bytes (1 float) are received
        while i2c.rxBufferCount() < 5:
            sleep_us(10)
        received_data = i2c.read()
        data = ustruct.unpack("<bf", received_data)
        
        # Set fan_1 speed
        if data[0] == 0:
            fan_1_speed = int(data[1] * 65535 / 100)
        # Set fan_2 speed
        elif data[0] == 1:
            fan_2_speed = int(data[1] * 65535 / 100)
        # Set heater brightness
        elif data[0] == 2:
            heater_brightness = data[1]
        # Turn on fan_1
        elif data[0] == 3:
            fan_1_pwm.duty_u16(fan_1_speed)
        # Turn off fan_1
        elif data[0] == 4:
            fan_1_pwm.duty_u16(0)
        # Turn on fan_2
        elif data[0] == 5:
            fan_2_pwm.duty_u16(fan_2_speed)
        # Turn off fan_2
        elif data[0] == 6:
            fan_2_pwm.duty_u16(0)
        # Turn on heater
        elif data[0] == 7:
            brightness = max(0, min(100, data[1]))
            adjust_brightness(brightness)
        # Turn off heater
        elif data[0] == 8:
            adjust_brightness(0)
        # Turn on electrovalve
        elif data[0] == 9:
            print("Activate Water Pump")
            water_pump.toggle()
            sleep_ms(3500)
            water_pump.off()

# Entry point of the program
if __name__ == "__main__":
    main()