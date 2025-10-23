#!/usr/bin/env python3
import spidev
import time

# SPI bus 0, device 0 (CE0)
SPI_BUS = 0
SPI_DEVICE = 0

spi = spidev.SpiDev()
spi.open(SPI_BUS, SPI_DEVICE)
spi.max_speed_hz = 4000000
spi.mode = 0  # CPOL=0, CPHA=0 works well for MAX6675

def read_temp_c():
    raw = spi.readbytes(2)
    if len(raw) != 2:
        raise RuntimeError("SPI read failed")

    value = (raw[0] << 8) | raw[1]

    # bit 2 (0x04) indicates open thermocouple
    if value & 0x04:
        return None

    temp_c = (value >> 3) * 0.25
    return temp_c

try:
    while True:
        temp = read_temp_c()
        if temp is None:
            print("Thermocouple not connected!")
        else:
            print(f"Temperature: {temp:.2f} °C")
        time.sleep(0.25)  # ≈4 Hz, matches sensor’s internal update rate
except KeyboardInterrupt:
    pass
finally:
    spi.close()
