from machine import Pin
from time import sleep
import dht

sensor = dht.DHT22(Pin(4))

# Aguarda a estabilização após ligar o sensor.
sleep(2)

while True:
    try:
        sensor.measure()

        temperatura = sensor.temperature()
        umidade = sensor.humidity()

        print("Temperatura:", temperatura, "°C")
        print("Umidade:", umidade, "%")
        print()

    except OSError as erro:
        print("Falha ao ler o DHT22:", erro)

    sleep(3)
