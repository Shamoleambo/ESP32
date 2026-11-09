from machine import Pin
from time import sleep, ticks_ms, ticks_diff
import dht
import json
import network
# Config MQTT
from machine import unique_id
from binascii import hexlify
from umqtt.simple import MQTTClient

from credenciais import WIFI_NOME, WIFI_SENHA

sensor = dht.DHT22(Pin(4))

# Constantes da estacao
ESTACAO_ID = "estacao-01"
PINO_DHT22 = 4
INTERVALO_LEITURA_S = 3
TEMPO_LIMITE_WIFI_MS = 20000

# Constantes do MQTT
MQTT_SERVIDOR = "test.mosquitto.org"
MQTT_PORTA = 1883
IDENTIFICADOR_PLACA = hexlify(unique_id()).decode()
MQTT_CLIENTE_ID = (
    "estacao-" + IDENTIFICADOR_PLACA
).encode()
MQTT_TOPICO = (
    "pi-meteorologia/"
    + IDENTIFICADOR_PLACA
    + "/leituras"
).encode()

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

def conectar_mqtt():
    cliente = MQTTClient(
        client_id=MQTT_CLIENTE_ID,
        server=MQTT_SERVIDOR,
        port=MQTT_PORTA,
        keepalive=60
    )

    print("Conectando ao broker MQTT...")
    cliente.connect(timeout=10)

    print("Conectado ao broker!")
    print("Tópico:", MQTT_TOPICO.decode())

    return cliente

def main():
    wifi = conectar_wifi()
    cliente = conectar_mqtt()
    sensor = dht.DHT22(Pin(PINO_DHT22))
    sequencia = 0
    sleep(2)

    try:
        while True:
            if not wifi.isconnected():
                print("Conexão Wi-Fi perdida. Interrompendo o teste.")
                break

            sequencia += 1

            mensagem = montar_mensagem(sensor, sequencia)
            texto_json = json.dumps(mensagem)

            cliente.publish(
                MQTT_TOPICO,
                texto_json.encode(),
                retain=False,
                qos=0
            )

            print("Publicação enviada:", texto_json)

            sleep(INTERVALO_LEITURA_S)

    except OSError as erro:
        print("Falha na comunicação MQTT:", erro)

    finally:
        try:
            cliente.disconnect()
        except OSError:
            pass


main()