from machine import Pin
from time import sleep, ticks_ms, ticks_diff
import dht
import json
import network

from credenciais import WIFI_NOME, WIFI_SENHA

sensor = dht.DHT22(Pin(4))

ESTACAO_ID = "estacao-01"
PINO_DHT22 = 4
INTERVALO_LEITURA_S = 3
TEMPO_LIMITE_WIFI_MS = 20000

def conectar_wifi():
    wifi = network.WLAN(network.WLAN.IF_STA)
    wifi.active(True)

    if not wifi.isconnected():
        print("Conectando ao Wi-Fi...")
        wifi.connect(WIFI_NOME, WIFI_SENHA)

        inicio = ticks_ms()

        while not wifi.isconnected():
            if ticks_diff(ticks_ms(), inicio) >= TEMPO_LIMITE_WIFI_MS:
                wifi.active(False)
                raise RuntimeError(
                    "Não conectou ao Wi-Fi em 20 segundos. "
                    "Confira nome, senha e rede de 2,4 GHz."
                )

            sleep(0.2)

    print("Wi-Fi conectado!")
    print("Endereço da placa:", wifi.ifconfig()[0])
    return wifi


def montar_mensagem(sensor, sequencia):
    try:
        sensor.measure()

        leituras = {
            "temperatura_c": sensor.temperature(),
            "umidade_pct": sensor.humidity()
        }
        estado = "ok"

    except OSError as erro:
        print("Falha ao ler o DHT22:", erro)

        leituras = {
            "temperatura_c": None,
            "umidade_pct": None
        }
        estado = "erro_leitura"

    return {
        "versao": 1,
        "estacao_id": ESTACAO_ID,
        "sequencia": sequencia,
        "leituras": leituras,
        "estado_dht22": estado
    }


def main():
    wifi = conectar_wifi()
    sensor = dht.DHT22(Pin(PINO_DHT22))
    sequencia = 0

    sleep(2)

    while True:
        sequencia += 1

        mensagem = montar_mensagem(sensor, sequencia)
        texto_json = json.dumps(mensagem)

        print("Wi-Fi conectado:", wifi.isconnected())
        print(texto_json)

        sleep(INTERVALO_LEITURA_S)


main()