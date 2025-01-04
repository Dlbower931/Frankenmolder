from gpiozero import LED
import time

led = LED(16)

led.off()
time.sleep(3)
led.on()
time.sleep(3)
led.off()
time.sleep(3)
led.on()
time.sleep(3)
led.off()
