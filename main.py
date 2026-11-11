from machine import unique_id
from binascii import hexlify
from time import sleep, ticks_ms, ticks_diff

import json
import network

from umqtt.simple import MQTTClient, MQTTException

from credenciais import WIFI_NOME, WIFI_SENHA
from sensores import coletar_sensores


# Configuração da estação
ESTACAO_ID = "estacao-01"
VERSAO_MENSAGEM = 3
INTERVALO_LEITURA_S = 3
TEMPO_LIMITE_WIFI_MS = 20000

# Configuração MQTT
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
                    "Tempo limite de conexão Wi-Fi excedido."
                )

            sleep(0.2)

    print("Wi-Fi conectado:", wifi.ifconfig()[0])
    return wifi


def conectar_mqtt():
    cliente = MQTTClient(
        client_id=MQTT_CLIENTE_ID,
        server=MQTT_SERVIDOR,
        port=MQTT_PORTA,
        keepalive=60
    )

    print("Conectando ao broker MQTT...")
    cliente.connect(timeout=10)

    print("Broker conectado!")
    print("Tópico:", MQTT_TOPICO.decode())

    return cliente


def montar_mensagem(sequencia):
    leituras, estados = coletar_sensores()

    return {
        "versao": VERSAO_MENSAGEM,
        "estacao_id": ESTACAO_ID,
        "sequencia": sequencia,
        "leituras": leituras,
        "estado_sensores": estados
    }


def desconectar_mqtt(cliente):
    if cliente is not None:
        try:
            cliente.disconnect()
        except OSError:
            pass


def main():
    wifi = network.WLAN(network.WLAN.IF_STA)
    cliente = None
    sequencia = 0

    # Aguarda estabilização dos sensores.
    sleep(2)

    try:
        while True:
            sequencia += 1

            # As falhas individuais são tratadas em sensores.py.
            mensagem = montar_mensagem(sequencia)
            texto_json = json.dumps(mensagem)

            print("Ciclo coletado:", texto_json)

            try:
                if not wifi.isconnected():
                    desconectar_mqtt(cliente)
                    cliente = None
                    wifi = conectar_wifi()

                if cliente is None:
                    cliente = conectar_mqtt()

                cliente.publish(
                    MQTT_TOPICO,
                    texto_json.encode(),
                    retain=False,
                    qos=0
                )

                print("Publicação enviada.")

            except (OSError, RuntimeError, MQTTException) as erro:
                print("Falha no envio:", erro)
                print("Nova tentativa no próximo ciclo.")

                desconectar_mqtt(cliente)
                cliente = None

            sleep(INTERVALO_LEITURA_S)

    except KeyboardInterrupt:
        print("Programa interrompido.")

    finally:
        desconectar_mqtt(cliente)


if __name__ == "__main__":
    main()