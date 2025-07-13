import time
import threading
from tkinter import *
from simple_pid import PID
import RPi.GPIO as GPIO

# ==== SIMULATION MODE ====
simulate = True
real_temp = 70.0  # Starting simulated temp (F)

# ==== SSR Output Setup ====
SSR_PIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(SSR_PIN, GPIO.OUT)
pwm = GPIO.PWM(SSR_PIN, 1000)  # 1kHz frequency
pwm.start(0)

# ==== PID Setup ====
Setpoint = 110.0
SetpointDiff = 5.0
kp, ki, kd = 2.5, 0.06, 0.8
pid = PID(kp, ki, kd, setpoint=Setpoint)
pid.output_limits = (0, 100)

# ==== Control State ====
state = 0  # 0: ramp_up, 1: PID control, 2: cool_down
running = True

# ==== GUI Setup ====
root = Tk()
root.title("PID Controller")

setpoint_var = DoubleVar(value=Setpoint)
temp_var = DoubleVar(value=real_temp)
state_label_var = StringVar(value="RAMP UP")

# ==== GUI Functions ====
def update_display():
    temp_var.set(round(real_temp, 1))
    setpoint_var.set(round(pid.setpoint, 1))

    if state == 0:
        state_label_var.set("RAMP UP")
    elif state == 1:
        state_label_var.set("PID CONTROL")
    elif state == 2:
        state_label_var.set("COOL DOWN")

def increase_setpoint():
    pid.setpoint += 1

def decrease_setpoint():
    pid.setpoint -= 1

def start_ramp():
    global state
    state = 0

def start_pid():
    global state
    state = 1

def start_cool():
    global state
    state = 2

def shutdown():
    global running
    running = False
    pwm.ChangeDutyCycle(0)
    GPIO.cleanup()
    root.destroy()

# ==== GUI Layout ====
Label(root, text="Current Temp (F)", font=("Helvetica", 14)).pack()
Label(root, textvariable=temp_var, font=("Helvetica", 24)).pack()

Label(root, text="Setpoint (F)", font=("Helvetica", 14)).pack()
Label(root, textvariable=setpoint_var, font=("Helvetica", 24)).pack()

Label(root, text="State:", font=("Helvetica", 14)).pack()
Label(root, textvariable=state_label_var, font=("Helvetica", 16)).pack(pady=(0, 10))

Button(root, text="▲ Increase", width=15, command=increase_setpoint).pack()
Button(root, text="▼ Decrease", width=15, command=decrease_setpoint).pack()
Button(root, text="Start Ramp Up", width=15, command=start_ramp).pack()
Button(root, text="Start PID Control", width=15, command=start_pid).pack()
Button(root, text="Cool Down", width=15, command=start_cool).pack()
Button(root, text="Quit", width=15, command=shutdown).pack(pady=(10, 0))

# ==== Control Loop Thread ====
def control_loop():
    global real_temp, state
    last_time = time.time()

    while running:
        now = time.time()
        if (now - last_time) * 1000 > 200:  # 200 ms interval
            if simulate:
                # Simulated control loop
                if state == 0:  # ramp up
                    if real_temp < (pid.setpoint - SetpointDiff):
                        pwm.ChangeDutyCycle(100)
                        real_temp += 0.5
                    else:
                        pwm.ChangeDutyCycle(0)
                        state = 1

                elif state == 1:  # PID control
                    output = pid(real_temp)
                    pwm_val = 100 - output  # SSR ON = lower output
                    pwm.ChangeDutyCycle(pwm_val)

                    # Simulate heating/cooling
                    if pwm_val > 0:
                        real_temp += 0.2 * (pwm_val / 100)
                    else:
                        real_temp -= 0.1

                elif state == 2:  # cool down
                    pwm.ChangeDutyCycle(0)
                    real_temp -= 0.3

                # Clamp the temperature
                real_temp = max(20.0, min(400.0, real_temp))

            else:
                # TODO: insert thermocouple reading here when available
                pass

            update_display()
            last_time = now

        time.sleep(0.05)

# ==== Start Background Thread ====
threading.Thread(target=control_loop, daemon=True).start()

# ==== Run GUI ====
root.mainloop()
