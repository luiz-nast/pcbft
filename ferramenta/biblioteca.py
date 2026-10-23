# biblioteca: cada tipo de peca e onde ficam os pinos, em mm, a partir do centro da peca
#
# pinos: {numero: (dx, dy, pad)} ou (dx, dy, pad, net) quando o pino ja nasce numa net (ex: GND)
#        pad = diametro (redondo) ou (largura, altura) (retangulo)
# furo:  diametro do furo passante de cada pino; None = peca de superficie (SMD)
# corpo: (largura, altura) do contorno da peca, pra desenhar; redondo: True se o corpo for redondo
# juntos: pares de pinos ligados por dentro da peca (ex: os dois pinos de cada lado do botao)
# nomes:  como a bancada chama cada pino pra gente ("+", "−", "A", "B", "lado 1"); sem isso mostra o numero
# eletrica: o que o simulador precisa saber (circuito.py e o painel da bancada); sem isso a peca nao liga no papel
# compra: o que comprar; extras: coisas que a peca pede e nao vem com ela (a pilha do suporte)
# fonte: datasheet de onde vieram os numeros
#        None = valores de EXEMPLO, nao mandar pra fabrica (trocar no marco 7)

def fileira(primeiro, quantos, x0, passo, y, pad):
    """pinos em linha reta, numerados a partir de `primeiro`"""
    return {str(primeiro + i): (round(x0 + i * passo, 3), y, pad) for i in range(quantos)}


BIBLIOTECA = {
    "resistor": {
        "nome": "Resistor",
        "nomes": {"1": "lado 1", "2": "lado 2"},
        "explica": "Fica no caminho da corrente e limita quanto passa. Sem ele, um LED ligado direto no pino queima.",
        "fonte": None,
        "furo": None,
        "corpo": (3.2, 1.8),
        "pinos": {"1": (-1.0, 0, (1.2, 1.4)), "2": (1.0, 0, (1.2, 1.4))},
    },
    "led": {
        "nome": "LED",
        "nomes": {"1": "+", "2": "−"},
        "explica": "Acende quando a corrente passa por ele. Tem lado certo: entra pelo + (a perna comprida) e sai pelo −.",
        "fonte": None,
        "furo": None,
        "corpo": (3.2, 1.8),
        "pinos": {"1": (-1.0, 0, (1.2, 1.4)), "2": (1.0, 0, (1.2, 1.4))},
    },
    "botao": {
        "nome": "Botão",
        "nomes": {"1": "A", "2": "A", "3": "B", "4": "B"},
        "explica": "Quando você aperta, ele junta os dois lados do circuito. Tem o lado A (dois pinos) e o lado B (os outros dois).",
        "fonte": None,
        "furo": 1.0,
        "corpo": (6.0, 6.0),
        "pinos": {"1": (-3.25, 2.25, 1.8), "2": (3.25, 2.25, 1.8),
                  "3": (-3.25, -2.25, 1.8), "4": (3.25, -2.25, 1.8)},
        "juntos": [("1", "2"), ("3", "4")],
    },
    "buzzer": {
        "nome": "Buzzer",
        "nomes": {"1": "+", "2": "−"},
        "explica": "Faz som quando recebe sinal. Tem lado certo: o + e o −.",
        "fonte": None,
        "furo": 0.9,
        "corpo": (12.0, 12.0),
        "redondo": True,
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

# pecas reais: pinos, pads e furos do footprint oficial do KiCad (kicad-footprints, master de 2026-10-23),
# conferidos contra o datasheet do fabricante por uma segunda pesquisa independente
KICAD = "https://gitlab.com/kicad/libraries/kicad-footprints/-/raw/master/"
BIBLIOTECA.update({
    "resistor_axial": {
        "nome": "Resistor 1/4 W (axial)",
        "explica": "Freia a corrente: quanto mais ohms, menos corrente passa. É o cilindrinho com faixas coloridas que dizem o valor. "
                   "Fica deitado, com as perninhas dobradas nos furos. Não tem lado certo.",
        "fonte": "Yageo CFR-25 https://cdn.sparkfun.com/assets/a/9/3/0/e/yageo-cfr_datasheet.pdf; "
                 + KICAD + "Resistor_THT.pretty/R_Axial_DIN0207_L6.3mm_D2.5mm_P10.16mm_Horizontal.kicad_mod",
        "furo": 0.8,
        "corpo": (6.3, 2.5),
        "pinos": {"1": (-5.08, 0, 1.6), "2": (5.08, 0, 1.6)},
        "nomes": {"1": "lado 1", "2": "lado 2"},
        "eletrica": {"modelo": "resistor", "potencia_max": 0.25},   # Yageo CFR-25: 1/4 W a 70 °C
        "compra": "Yageo CFR-25 (ou qualquer resistor de 1/4 W com o valor certo)",
    },
    "led_5mm": {
        "nome": "LED vermelho 5 mm",
        "explica": "Uma luzinha que só acende com a corrente no sentido certo: entra pelo + (a perna comprida) "
                   "e sai pelo − (a perna curta, do lado chato; na placa é o pad quadrado). Sempre com um resistor na frente.",
        "fonte": "Kingbright WP7113ID https://www.kingbrightusa.com/images/catalog/SPEC/WP7113ID.pdf; "
                 + KICAD + "LED_THT.pretty/LED_D5.0mm.kicad_mod (nosso 1 = pad 2 do KiCad, nosso 2 = pad 1)",
        "furo": 0.9,
        "corpo": (5.8, 5.8),
        "redondo": True,
        "pinos": {"1": (1.27, 0, 1.8), "2": (-1.27, 0, (1.8, 1.8))},
        "nomes": {"1": "+", "2": "−"},
        # Kingbright WP7113ID: VF 1,9 V típica (2,3 máx) medida a 10 mA; IF máxima contínua 30 mA.
        # r_s = inclinação estimada entre esses dois pontos: (2,3 − 1,9) / (0,030 − 0,010) = 20 Ω
        "eletrica": {"modelo": "led", "vf": 1.9, "vf_max": 2.3, "i_teste": 0.010, "i_max": 0.030, "r_s": 20},
        "compra": "Kingbright WP7113ID (ou qualquer LED vermelho de 5 mm)",
    },
    "botao_6x6": {
        "nome": "Botão 6×6 mm",
        "explica": "Apertou, liga; soltou, desliga. Tem o lado A (dois pinos, ligados por dentro) e o lado B (os outros dois). "
                   "Só faz alguma coisa se cada lado for pra um lugar diferente.",
        "fonte": "Omron B3F-1000 https://omronfs.omron.com/en_US/ecb/products/pdf/en-b3f.pdf; "
                 + KICAD + "Button_Switch_THT.pretty/SW_PUSH_6mm.kicad_mod",
        "furo": 1.1,
        "corpo": (6.0, 6.0),
        "pinos": {"1": (-3.25, 2.25, 2.0), "2": (3.25, 2.25, 2.0),
                  "3": (-3.25, -2.25, 2.0), "4": (3.25, -2.25, 2.0)},
        "juntos": [("1", "2"), ("3", "4")],
        "nomes": {"1": "A", "2": "A", "3": "B", "4": "B"},
        "eletrica": {"modelo": "chave", "lados": [["1", "2"], ["3", "4"]], "i_max": 0.050},   # Omron B3F: 1 a 50 mA
        "compra": "Omron B3F-1000 (ou botão tátil 6×6 mm de 4 pinos)",
    },
    "pilha_cr2032": {
        "nome": "Suporte de pilha CR2032",
        "explica": "Segura uma pilha moeda CR2032 de 3 V. O + fica na aba (pad quadrado); "
                   "o −, embaixo da pilha, é o GND da placa, o 0 V de referência.",
        "fonte": "Keystone 103 https://www.keyelco.com/userAssets/file/M65p3.pdf; "
                 + KICAD + "Battery.pretty/BatteryHolder_Keystone_103_1x20mm.kicad_mod",
        "furo": 1.5,
        "corpo": (28.7, 22.8),
        "pinos": {"1": (-12.25, 0, (3.0, 3.0), "VBAT"), "2": (8.24, 0, 3.0, "GND")},
        "nomes": {"1": "+", "2": "−"},
        # Energizer CR2032 (https://data.energizer.com/pdfs/cr2032.pdf): 3,0 V nominal, 235 mAh até 2,0 V.
        # v_max 3,3 = pilha nova, so o limite do painel: o datasheet da a nominal e o corte, nao o valor nova
        "eletrica": {"modelo": "pilha", "mais": "1", "menos": "2", "v": 3.0, "v_min": 2.0, "v_max": 3.3, "mah": 235},
        "compra": "Keystone 103",
        "extras": ["Pilha CR2032 de 3 V"],
    },
})

# pinos que ja nascem numa net (EXEMPLO: confirmar no datasheet do DevKit escolhido)
for n, net in {"14": "GND", "17": "GND"}.items():
    dx, dy, pad = BIBLIOTECA["esp32_devkit"]["pinos"][n]
    BIBLIOTECA["esp32_devkit"]["pinos"][n] = (dx, dy, pad, net)
