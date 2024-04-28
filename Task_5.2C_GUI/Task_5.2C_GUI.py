import tkinter as tk
from tkinter import ttk
import RPi.GPIO as GPIO
import threading
import time 

#Setup GPIO
GPIO.setmode(GPIO.BCM)
pins = {'red': 17, 'green': 18, 'blue': 19}
for pin in pins.values():
	GPIO.setup(pin, GPIO.OUT)

#Initialize PWM controllers
pwms = {color: GPIO.PWM(pin, 100) for color, pin in pins.items()}
for pwm in pwms.values():
	pwm.start(0) #Start with LEDs off

def update_led(color):
	try:
		brightness = brightness_scales[color].get()
		pwms[color].ChangeDutyCycle(brightness)
		update_canvas_color()
	except Exception as e:
		print("Failed to update brightness: {str(e)}")

def update_canvas_color():
	try:
		r = int(brightness_scales['red'].get() * 2.55)
		g = int(brightness_scales['green'].get() * 2.55)
		b = int(brightness_scales['blue'].get() * 2.55)
		color = f"#{r:02x}{g:02x}{b:02x}"
		canvas.config(bg=color)
	except Exception as e:
		print("Failed to update canvas color: {str(e)}")

def set_color_preset(r, g, b):
	brightness_scales['red'].set(r / 2.55)
	brightness_scales['green'].set(g / 2.55)
	brightness_scales['blue'].set(b / 2.55)
	for color in 'red', 'green', 'blue':
		update_led(color)

def blink_effect():
	current_brightness = {color: brightness_scales[color].get() for color in ('red', 'green', 'blue')}
	for _ in range(5):
		for pwm in pwms.values():
			pwm.ChangeDutyCycle(0)
		time.sleep(0.5)
		for color, brightness in current_brightness.items():
			pwms[color].ChangeDutyCycle(brightness)
		time.sleep(0.5)
	update_canvas_color()

def turn_off_lights():
	for pwm in pwms.values():
		pwm.ChangeDutyCycle(0)

#Create main window
root = tk.Tk()
root.title("RGB LED Controller")

#Layout frames
control_frame = ttk.Frame(root)
control_frame.pack(pady=20)
canvas_frame = ttk.Frame(root)
canvas_frame.pack(pady=10)

#Setup Canvas for color display
canvas = tk.Canvas(canvas_frame, width=100, height=100, bg="black")
canvas.pack()

#Setup individual color controls
brightness_scales = {}
for color in pins.keys():
	label =	ttk.Label(control_frame, text=f"{color.title()} Brightness:")
	label.pack()
	scale = ttk.Scale(control_frame, from_=0, to=100, orient="horizontal", command=lambda value, color=color: update_led(color))
	scale.pack()
	brightness_scales[color] = scale

#Preset colors and effects
ttk.Button(root, text = "Red", command = lambda: set_color_preset(255,0,0)).pack(side="left")
ttk.Button(root, text = "Green", command = lambda: set_color_preset(0, 255, 0)).pack(side="left") 
ttk.Button(root, text = "Blue", command = lambda: set_color_preset(0, 0, 255)).pack(side="left")
ttk.Button(root, text = "Blink", command=blink_effect).pack(side="left")

#Exit button
exit_button = ttk.Button(root, text = "Exit", command = lambda: [turn_off_lights(), root.quit()])
exit_button.pack(pady=10)


def on_closing():
	turn_off_lights()
	for pwm in pwms.values():
		pwm.stop()
	GPIO.cleanup()
	root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)

#Run the GUI
root.mainloop()  
