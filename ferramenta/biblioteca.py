# biblioteca: cada tipo de peca e onde ficam os pinos, em mm, a partir do centro da peca
#
# pinos: {numero: (dx, dy, pad)} ou (dx, dy, pad, net) quando o pino ja nasce numa net (ex: GND)
#        pad = diametro (redondo) ou (largura, altura) (retangulo)
# furo:  diametro do furo passante de cada pino; None = peca de superficie (SMD)
# corpo: (largura, altura) do contorno da peca, pra desenhar
# fonte: datasheet de onde vieram os numeros
#        None = valores de EXEMPLO, nao mandar pra fabrica (trocar no marco 7)

def fileira(primeiro, quantos, x0, passo, y, pad):
    """pinos em linha reta, numerados a partir de `primeiro`"""
    return {str(primeiro + i): (round(x0 + i * passo, 3), y, pad) for i in range(quantos)}


BIBLIOTECA = {
    "resistor": {
        "nome": "Resistor",
        "explica": "Fica no caminho da corrente e limita quanto passa. Sem ele, um LED ligado direto no pino queima.",
        "fonte": None,
        "furo": None,
        "corpo": (3.2, 1.8),
        "pinos": {"1": (-1.0, 0, (1.2, 1.4)), "2": (1.0, 0, (1.2, 1.4))},
    },
    "led": {
        "nome": "LED",
        "explica": "Acende quando a corrente passa por ele. Tem lado certo: o pino 1 é o + (ânodo), o 2 é o − (cátodo).",
        "fonte": None,
        "furo": None,
        "corpo": (3.2, 1.8),
        "pinos": {"1": (-1.0, 0, (1.2, 1.4)), "2": (1.0, 0, (1.2, 1.4))},
    },
    "botao": {
        "nome": "Botão",
        "explica": "Quando você aperta, ele junta os dois lados do circuito. Os pinos 1 e 2 são o mesmo lado; 3 e 4, o outro.",
        "fonte": None,
        "furo": 1.0,
        "corpo": (6.0, 6.0),
        "pinos": {"1": (-3.25, 2.25, 1.8), "2": (3.25, 2.25, 1.8),
                  "3": (-3.25, -2.25, 1.8), "4": (3.25, -2.25, 1.8)},
    },
    "buzzer": {
        "nome": "Buzzer",
        "explica": "Faz som quando recebe sinal. O pino 1 é o +.",
        "fonte": None,
        "furo": 0.9,
        "corpo": (12.0, 12.0),
        "pinos": {"1": (-3.8, 0, 1.7), "2": (3.8, 0, 1.7)},
    },
    "esp32_devkit": {
        "nome": "Módulo ESP32 DevKit",
        "explica": "A plaquinha pronta com o ESP32. Ela encaixa nesses furos e é o cérebro do circuito.",
        "fonte": None,
        "furo": 1.0,
        "corpo": (51.0, 28.0),
        # 2 fileiras de 15, passo 2,54 mm; 1-15 embaixo (esq -> dir), 16-30 em cima (dir -> esq)
        "pinos": {
            **fileira(1, 15, -17.78, 2.54, -12.7, 1.7),
            **fileira(16, 15, 17.78, -2.54, 12.7, 1.7),
        },
    },
}

# pinos que ja nascem numa net (EXEMPLO: confirmar no datasheet do DevKit escolhido)
for n, net in {"14": "GND", "17": "GND"}.items():
    dx, dy, pad = BIBLIOTECA["esp32_devkit"]["pinos"][n]
    BIBLIOTECA["esp32_devkit"]["pinos"][n] = (dx, dy, pad, net)
