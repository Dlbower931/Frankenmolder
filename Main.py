from gpiozero import LED
import time

led = LED(17)

led.off()
time.sleep(3)
led.on()
time.sleep(4)
led.off()