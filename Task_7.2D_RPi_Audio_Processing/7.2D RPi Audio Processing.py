import speech_recognition as sr 
import RPi.GPIO as GPIO 
import time

# Initialize GPIO
LED_PIN = 17
GPIO.setmode (GPIO.BCM)
GPIO. setup(LED_PIN, GPIO.OUT)
GPIO.setwarnings (False)


# Function to turn the LED on
def led_on():
    GPIO.output (LED_PIN, GPIO.HIGH) 
    print("LED is ON")

# Function to turn the LED off
def led_off():
    GPIO.output(LED_PIN, GPIO.LOW)
    print ("LED is OFF")

# Initializing speech recognizer
recognizer = sr.Recognizer()
mic = sr.Microphone(device_index=3)

try:
    while True:
        with mic as source:
            print("Listening for command...")
            audio = recognizer.listen(source)
        
        try:
            words = recognizer.recognize_google(audio)
            print(f"Command received: {words}")

            if words.lower() == "led on":
                led_on()
            elif words.lower() == "led off":
                led_off()
            else:
                print("Unknown command")

        except sr.UnknownValueError:
            print("What?")
        except sr.RequestError:
            print("Could not request results from Google Speech Recognition service.")
        except Exception as e:
            print(f"An error occurred: {e}")

except KeyboardInterrupt:
    print("Program stopped by user")

finally:
    GPIO.cleanup()