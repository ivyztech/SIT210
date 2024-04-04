import RPi.GPIO as GPIO
import time
import random

#Setting GPIO mode to use BOARD pin numbering
GPIO. setmode (GPIO. BOARD)

#Dictionary structure for LED pins
led_pins = {
    'Y': 11,
    'G': 13,
    'R': 15,
    'B': 19,
    'O': 21,
}

for pin in led_pins.values () :
    GPIO. setup(pin, GPIO.OUT)

#turning on specific leds 
def light_up_led(led_pin):
    GPIO.output(led_pin, GPIO.HIGH)

#turning off LEDS 
def turn_off_leds():
    for pin in led_pins.values ():
        GPIO.output (pin, GPIO.LOW)

#blinking specific leds for duration 
def blink_led(led_pin, duration):
    light_up_led(led_pin)
    time.sleep(duration)
    turn_off_leds()
    time.sleep(duration)

#user input for led sequence 
def user_input ():
    user_sequence = input ("Enter your desired LED sequence (YGRBO in any order): ").upper ()
    #validating user input 
    for letter in user_sequence:
        if letter in led_pins:
            blink_led(led_pins[letter],0.25)
        else:
            print ("Invalid input. Please only enter Y, G, R, B or 0 .")

try:
    While True:
        user_input()
    
#cleaning up 
except KeyboardInterrupt:
GPIO.cleanup()
