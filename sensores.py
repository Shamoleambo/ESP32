from machine import Pin, I2C
from time import sleep_ms
import dht

from bmp280 import BMP280, BMP280_CASE_WEATHER


PINO_DHT22 = 4
PINO_SDA = 21
PINO_SCL = 22

ENDERECO_BMP280 = 0x76

_bmp280 = None


def ler_dht22():
    try:
        sensor = dht.DHT22(Pin(PINO_DHT22))
        sensor.measure()

        temperatura = sensor.temperature()
        umidade = sensor.humidity()

        if not (-40 <= temperatura <= 80):
            raise ValueError("Temperatura fora do intervalo esperado.")

        if not (0 <= umidade <= 100):
            raise ValueError("Umidade fora do intervalo esperado.")

        return {
            "temperatura_c": temperatura,
            "umidade_pct": umidade
        }, "ok"

    except (OSError, ValueError) as erro:
        print("Falha no DHT22:", erro)

        return {
            "temperatura_c": None,
            "umidade_pct": None
        }, "erro_leitura"


def ler_bmp280():
    global _bmp280

    try:
        if _bmp280 is None:
            barramento = I2C(
                0,
                sda=Pin(PINO_SDA),
                scl=Pin(PINO_SCL),
                freq=100000
            )

            identificacao = barramento.readfrom_mem(
                ENDERECO_BMP280, 0xD0, 1
            )[0]

            if identificacao != 0x58:
                raise ValueError("Identificação diferente de BMP280.")

            _bmp280 = BMP280(
                barramento,
                addr=ENDERECO_BMP280,
                use_case=BMP280_CASE_WEATHER
            )

        # Solicita uma nova medição em cada ciclo.
        _bmp280.force_measure()
        sleep_ms(_bmp280.read_wait_ms + 10)

        pressao_hpa = _bmp280.pressure / 100

        if not (300 <= pressao_hpa <= 1100):
            raise ValueError("Pressão fora do intervalo esperado.")

        return {"pressao_hpa": pressao_hpa}, "ok"

    except (OSError, ValueError) as erro:
        print("Falha no BMP280:", erro)

        # Permite tentar inicializar novamente no próximo ciclo.
        _bmp280 = None

        return {"pressao_hpa": None}, "erro_leitura"


def coletar_sensores():
    dados_dht, estado_dht = ler_dht22()
    dados_bmp, estado_bmp = ler_bmp280()

    leituras = {
        "temperatura_c": dados_dht["temperatura_c"],
        "umidade_pct": dados_dht["umidade_pct"],
        "pressao_hpa": dados_bmp["pressao_hpa"],
        "mq135_adc": None,
        "luminosidade_adc": None
    }

    estados = {
        "dht22": estado_dht,
        "bmp280": estado_bmp,
        "mq135": "nao_configurado",
        "ldr": "nao_configurado"
    }

    return leituras, estados