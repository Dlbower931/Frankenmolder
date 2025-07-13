import time
import threading
from tkinter import *
from simple_pid import PID
import RPi.GPIO as GPIO

# === SIMULATION SETTINGS ===
simulate = True
manual_temp_control = False
real_temp = 70.0  # Starting simulated temp (F)

# === GPIO SETUP ===
SSR_PIN = 13
GPIO.setmode(GPIO.BCM)
GPIO.setup(SSR_PIN, GPIO.OUT)
pwm = GPIO.PWM(SSR_PIN, 1000)  # 1kHz frequency
pwm.start(0)

# === PID SETUP ===
Setpoint = 110.0
SetpointDiff = 5.0
kp, ki, kd = 2.5, 0.06, 0.8
pid = PID(kp, ki, kd, setpoint=Setpoint)
pid.output_limits = (0, 100)

# === STATE VARIABLES ===
state = 0  # 0: ramp_up, 1: PID control, 2: cool_down
running = True

# === GUI SETUP ===
root = Tk()
root.title("PID Controller")
root.attributes("-fullscreen", True)  # FULLSCREEN mode

setpoint_var = DoubleVar(value=Setpoint)
temp_var = DoubleVar(value=real_temp)
state_label_var = StringVar(value="RAMP UP")

# === GUI FUNCTIONS ===
def update_display():
    temp_var.set(round(real_temp, 1))
    setpoint_var.set(round(pid.setpoint, 1))

    if state == 0:
        state_label_var.set("RAMP UP")
    elif state == 1:
        state_label_var.set("PID CONTROL")
    elif state == 2:
        state_label_var.set("COOL DOWN")

    if manual_temp_control:
        state_label_var.set(state_label_var.get() + " (MANUAL TEMP)")

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

# === GUI LAYOUT ===
Label(root, text="Current Temp (F)", font=("Helvetica", 18)).pack()
Label(root, textvariable=temp_var, font=("Helvetica", 36)).pack()

Label(root, text="Setpoint (F)", font=("Helvetica", 18)).pack()
Label(root, textvariable=setpoint_var, font=("Helvetica", 36)).pack()

Label(root, text="State:", font=("Helvetica", 18)).pack()
Label(root, textvariable=state_label_var, font=("Helvetica", 20)).pack(pady=(0, 10))

Button(root, text="▲ Increase Setpoint", font=("Helvetica", 16), width=25, command=increase_setpoint).pack()
Button(root, text="▼ Decrease Setpoint", font=("Helvetica", 16), width=25, command=decrease_setpoint).pack()
Button(root, text="Start Ramp Up", font=("Helvetica", 16), width=25, command=start_ramp).pack()
Button(root, text="Start PID Control", font=("Helvetica", 16), width=25, command=start_pid).pack()
Button(root, text="Cool Down", font=("Helvetica", 16), width=25, command=start_cool).pack()
Button(root, text="Quit", font=("Helvetica", 16), width=25, command=shutdown).pack(pady=(10, 0))

# === Manual Temp Control (only shown if simulate = True) ===
temp_control_frame = Frame(root)

Label(temp_control_frame, text="Simulated Temp Control", font=("Helvetica", 18)).pack(pady=(10, 0))

def toggle_manual_temp():
    global manual_temp_control
    manual_temp_control = not manual_temp_control
    update_display()

def increase_temp():
    global real_temp
    if manual_temp_control:
        real_temp += 1

def decrease_temp():
    global real_temp
    if manual_temp_control:
        real_temp -= 1

Button(temp_control_frame, text="Toggle Manual Temp", font=("Helvetica", 16), width=25, command=toggle_manual_temp).pack()
Button(temp_control_frame, text="▲ Increase Temp", font=("Helvetica", 16), width=25, command=increase_temp).pack()
Button(temp_control_frame, text="▼ Decrease Temp", font=("Helvetica", 16), width=25, command=decrease_temp).pack()

if simulate:
    temp_control_frame.pack()

# === CONTROL LOOP THREAD ===
def control_loop():
    global real_temp, state
    last_time = time.time()

    while running:
        now = time.time()
        if (now - last_time) * 1000 > 200:  # 200ms interval
            if simulate:
                if manual_temp_control:
                    pwm.ChangeDutyCycle(0)
                else:
                    if state == 0:  # ramp up
                        if real_temp < (pid.setpoint - SetpointDiff):
                            pwm.ChangeDutyCycle(100)
                            real_temp += 0.5
                        else:
                            pwm.ChangeDutyCycle(0)
                            state = 1

                    elif state == 1:  # PID control
                        output = pid(real_temp)
                        pwm_val = 100 - output
                        pwm.ChangeDutyCycle(pwm_val)
                        if pwm_val > 0:
                            real_temp += 0.2 * (pwm_val / 100)
                        else:
                            real_temp -= 0.1

                    elif state == 2:  # cool down
                        pwm.ChangeDutyCycle(0)
                        real_temp -= 0.3

                # Clamp the simulated temperature
                real_temp = max(20.0, min(400.0, real_temp))

            else:
                # Future: Add real thermocouple reading here
                pass

            update_display()
            last_time = now

        time.sleep(0.05)

# === START THREAD & GUI ===
threading.Thread(target=control_loop, daemon=True).start()
root.mainloop()
