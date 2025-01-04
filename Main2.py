import tkinter as tk
from tkinter import ttk
import RPi.GPIO as GPIO
import threading
import time

class ToggleApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Frankenmolder")
        self.root.geometry("800x480")  # Adjust to fit the 5-inch screen (800x480 resolution)

        # Configure GPIO
        GPIO.setmode(GPIO.BCM)
        self.gpio_power_pin = 17
        self.gpio_motor_pin = 16
        GPIO.setup(self.gpio_power_pin, GPIO.OUT)
        GPIO.setup(self.gpio_motor_pin, GPIO.OUT)
        GPIO.output(self.gpio_power_pin, GPIO.LOW)
        GPIO.output(self.gpio_motor_pin, GPIO.LOW)

        # Configure grid layout to fill the display
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)
        self.root.rowconfigure(2, weight=1)
        self.root.rowconfigure(3, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Initial states
        self.power_state = False
        self.motor_running = False
        self.motor_frequency = 0

        # Label to display the current power state
        self.power_label = ttk.Label(self.root, text="Power: OFF", font=("Arial", 24), anchor="center")
        self.power_label.grid(row=0, column=0, sticky="nsew")

        # Label to display the motor state
        self.motor_label = ttk.Label(self.root, text="Motor: OFF", font=("Arial", 24), anchor="center")
        self.motor_label.grid(row=1, column=0, sticky="nsew")

        # Toggle button for GPIO 17 (Motor Power)
        self.power_button = ttk.Button(self.root, text="Toggle Motor Power", command=self.toggle_power)
        self.power_button.grid(row=2, column=0, sticky="nsew")

        # Toggle button for running the motor
        self.motor_button = ttk.Button(self.root, text="Run Motor", command=self.toggle_motor)
        self.motor_button.grid(row=3, column=0, sticky="nsew")

    def toggle_power(self):
        """Toggle the power state, update the display, and control GPIO 17."""
        self.power_state = not self.power_state
        power_text = "ON" if self.power_state else "OFF"
        self.power_label.config(text=f"Power: {power_text}")
        GPIO.output(self.gpio_power_pin, GPIO.HIGH if self.power_state else GPIO.LOW)

    def toggle_motor(self):
        """Toggle the motor on GPIO 16 and send a 10kHz signal."""
        if not self.motor_running:
            self.motor_running = True
            self.motor_frequency = 10000
            self.motor_button.config(text="Stop Motor")
            self.motor_thread = threading.Thread(target=self.run_motor_signal)
            self.motor_thread.start()
        else:
            self.motor_running = False
            self.motor_frequency = 0
            self.motor_button.config(text="Run Motor")
        self.update_motor_label()

    def run_motor_signal(self):
        """Generate a 10kHz signal on GPIO 16."""
        while self.motor_running:
            GPIO.output(self.gpio_motor_pin, GPIO.HIGH)
            time.sleep(0.00005)  # 10kHz signal (50 microseconds HIGH)
            GPIO.output(self.gpio_motor_pin, GPIO.LOW)
            time.sleep(0.00005)  # 10kHz signal (50 microseconds LOW)

    def update_motor_label(self):
        """Update the motor state label with current frequency."""
        motor_text = f"Motor: {'ON' if self.motor_running else 'OFF'} ({self.motor_frequency}Hz)"
        self.motor_label.config(text=motor_text)

    def __del__(self):
        """Cleanup GPIO on exit."""
        GPIO.cleanup()

# Main loop
if __name__ == "__main__":
    root = tk.Tk()
    app = ToggleApp(root)
    root.mainloop()
