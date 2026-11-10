from machine import Pin, I2C
from time import sleep

i2c = I2C(
    0,
    sda=Pin(21),
    scl=Pin(22),
    freq=100000
)

sleep(0.5)

enderecos = i2c.scan()

print("Dispositivos encontrados:")
print([hex(endereco) for endereco in enderecos])

for endereco in (0x76, 0x77):
    if endereco in enderecos:
        identificacao = i2c.readfrom_mem(endereco, 0xD0, 1)[0]

        print("Endereço:", hex(endereco))
        print("Identificação do chip:", hex(identificacao))

        if identificacao == 0x58:
            print("BMP280 identificado.")
        else:
            print("Identificação diferente da esperada para o BMP280.")