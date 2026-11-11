from machine import Pin, ADC
from time import sleep, ticks_ms, ticks_diff


sensor = ADC(Pin(34))
sensor.atten(ADC.ATTN_11DB)
sensor.width(ADC.WIDTH_12BIT)

inicio = ticks_ms()

print("Teste do MQ-135: leitura bruta, sem calibração.")

while True:
    try:
        valor = sensor.read()
        segundos = ticks_diff(ticks_ms(), inicio) // 1000

        print(
            "Tempo de teste:", segundos, "s",
            "| MQ-135 ADC:", valor
        )

    except OSError as erro:
        print("Falha ao ler a entrada analógica:", erro)

    sleep(1)