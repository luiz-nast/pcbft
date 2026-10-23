# letras: fonte de tracos pra serigrafia, numa grade de 4 de largura por 6 de altura
# cada letra e uma lista de linhas; cada linha e "xy xy xy..." (um digito pra x, um pra y)
# minusculas viram maiusculas (DevKit -> DEVKIT)

O = "10 01 05 16 36 45 41 30 10"
P = "00 06 36 45 44 33 03"

LETRAS = {
    "A": ["00 04 26 44 40", "03 43"],
    "B": ["00 06 36 45 44 33 03", "33 42 41 30 00"],
    "C": ["45 36 16 05 01 10 30 41"],
    "D": ["00 06 26 44 42 20 00"],
    "E": ["46 06 00 40", "03 33"],
    "F": ["46 06 00", "03 33"],
    "G": ["45 36 16 05 01 10 30 41 43 23"],
    "H": ["00 06", "40 46", "03 43"],
    "I": ["16 36", "26 20", "10 30"],
    "J": ["46 41 30 10 01"],
    "K": ["00 06", "46 02", "13 40"],
    "L": ["06 00 40"],
    "M": ["00 06 23 46 40"],
    "N": ["00 06 40 46"],
    "O": [O],
    "P": [P],
    "Q": [O, "22 40"],
    "R": [P, "23 40"],
    "S": ["45 36 16 05 04 13 33 42 41 30 10 01"],
    "T": ["06 46", "26 20"],
    "U": ["06 01 10 30 41 46"],
    "V": ["06 20 46"],
    "W": ["06 10 23 30 46"],
    "X": ["00 46", "06 40"],
    "Y": ["06 23 46", "23 20"],
    "Z": ["06 46 00 40"],
    "0": [O, "01 45"],
    "1": ["15 26 20", "10 30"],
    "2": ["05 16 36 45 44 00 40"],
    "3": ["05 16 36 45 44 33 42 41 30 10 01", "13 33"],
    "4": ["30 36 02 42"],
    "5": ["46 06 03 33 42 41 30 10 01"],
    "6": ["36 16 05 01 10 30 41 42 33 03"],
    "7": ["06 46 10"],
    "8": ["13 04 05 16 36 45 44 33 13 02 01 10 30 41 42 33"],
    "9": ["43 13 04 05 16 36 45 41 30 10"],
    "-": ["13 33"],
    "+": ["03 43", "21 25"],
    "_": ["00 40"],
    ".": ["20 20"],
}


def tracos(texto, x, y, altura):
    """linhas (lista de pontos em mm) do texto centrado em x, com a base em y"""
    k = altura / 6
    passo = 6 * k   # 4 da letra + 2 de espaco
    x0 = x - (len(texto) * passo - 2 * k) / 2
    saida = []
    for i, c in enumerate(texto.upper()):
        for linha in LETRAS.get(c, []):
            saida.append([(x0 + i * passo + int(p[0]) * k, y + int(p[1]) * k) for p in linha.split()])
    return saida
