"""Teste isolado do DHT22 em MicroPython: DATA no GPIO4 (D4).

VCC -> 3V3; GND -> GND; DATA -> D4; pino NC livre.
Para o sensor sem placa auxiliar, use pull-up de 10 kohms entre DATA e 3V3.
Execute com F5 no Thonny, usando o interpretador MicroPython (ESP32).
Nao importa sensores.py nem conecta ao Wi-Fi ou ao broker.
"""

from machine import Pin
from time import sleep
import dht


PINO_DHT22 = 4
INTERVALO_SEGUNDOS = 3
TOTAL_TENTATIVAS = 20


def main():
    sensor = dht.DHT22(Pin(PINO_DHT22))
    tentativas = 0
    sucessos = 0
    falhas = 0

    print("Teste isolado do DHT22 no GPIO", PINO_DHT22)
    print("Aguardando 2 segundos antes da primeira leitura...")

    try:
        sleep(2)

        for numero in range(1, TOTAL_TENTATIVAS + 1):
            tentativas += 1
            print("\nTentativa", numero, "de", TOTAL_TENTATIVAS)

            try:
                sensor.measure()
                temperatura = sensor.temperature()
                umidade = sensor.humidity()

                print("Temperatura:", temperatura, "C | Umidade:", umidade, "%")

                if not (-40 <= temperatura <= 80):
                    raise ValueError("Temperatura fora do intervalo esperado.")
                if not (0 <= umidade <= 100):
                    raise ValueError("Umidade fora do intervalo esperado.")

                sucessos += 1
                print("Resultado: leitura aceita.")

            except Exception as erro:
                falhas += 1
                print("Falha no DHT22:", erro)

            if numero < TOTAL_TENTATIVAS:
                sleep(INTERVALO_SEGUNDOS)

    except KeyboardInterrupt:
        print("\nTeste interrompido pelo usuario.")

    finally:
        print("\nResumo")
        print("Tentativas iniciadas:", tentativas)
        print("Leituras aceitas:", sucessos)
        print("Falhas:", falhas)
        print("Leitura aceita nao comprova calibracao ou exatidao do sensor.")


if __name__ == "__main__":
    main()

