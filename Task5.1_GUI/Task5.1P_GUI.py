import tkinter as tk
import RPi.GPIO as GPIO

class LEDController:
    def __init__(self, master):
        self.master = master
        self.master.title("LED Controller")

        # GPIO setup
        self.pins = {
            'red': 17,
            'green': 18,
            'blue': 19
        }
        GPIO.setmode(GPIO.BCM)
        for pin in self.pins.values():
            GPIO.setup(pin, GPIO.OUT)

        # Radio buttons for LED control
        self.radio_value = tk.StringVar()
        for color, pin in self.pins.items():
            tk.Radiobutton(master, text=color.capitalize(), variable=self.radio_value, value=color,
                           command=self.update_leds).pack()

        # Exit button
        tk.Button(master, text="Exit", command=self.exit_app).pack()

    def update_leds(self):
        # Turn off all LEDs
        for pin in self.pins.values():
            GPIO.output(pin, GPIO.LOW)

        # Turn on selected LED
        color = self.radio_value.get()
        if color in self.pins:
            GPIO.output(self.pins[color], GPIO.HIGH)

    def exit_app(self):
        # Clean up GPIO
        GPIO.cleanup()
        self.master.quit()

def main():
    root = tk.Tk()
    app = LEDController(root)
    root.mainloop()

if __name__ == '__main__':
    main()
