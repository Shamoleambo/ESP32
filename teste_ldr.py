from machine import Pin
from time import sleep

ldr = Pin(27, Pin.IN)

while True:
    print("Saída digital do LDR:", ldr.value())
    sleep(0.5)