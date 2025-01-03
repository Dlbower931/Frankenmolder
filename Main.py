from gpiozero import LED
led = LED(17)

led.on()
delay(1000)
led.off()