from time import sleep
import json

from sensores import coletar_sensores


sequencia = 0

# Aguarda estabilização dos sensores após ligar.
sleep(2)

while True:
    sequencia += 1

    leituras, estados = coletar_sensores()

    mensagem = {
        "versao": 2,
        "estacao_id": "estacao-01",
        "sequencia": sequencia,
        "leituras": leituras,
        "estado_sensores": estados
    }

    print(json.dumps(mensagem))
    sleep(3)