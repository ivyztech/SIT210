import RPi.GPIO as GPIO 
import time

#Setting the GPIO mode to use BOARD pin numbering
GPIO. setmode (GPIO. BOARD)

#Defining my chosen GPIO pin number
led_pin = 11

#Setting GPIO pin as an output
GPIO.setup(led_pin, GPIO.OUT)

try:
    while True:
        #Turning LED on
        GPIO.output (led_pin, GPIO.HIGH)
        print ("LED is on")
        time.sleep (0.15)

        #Turning LED off
        GPIO.output (led_pin, GPIO.LOW)
        print ("LED is off")
        time.sleep(0.15)

#Cleaning up code
except KeyboardInterrupt:
GPIO.cleanup()