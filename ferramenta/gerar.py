# biblioteca: onde fica cada pino, em mm, a partir do centro da peca
BIBLIOTECA = {
    "resistor": {"1": (-1.0, 0), "2": (1.0, 0)},
    "led":      {"1": (-1.0, 0), "2": (1.0, 0)},
}

# 1. ler o txt
placa, pecas, ligacoes = None, {}, []
for linha in open("placa.txt"):
    p = linha.split()
    if p[0] == "placa":
        placa = (float(p[1]), float(p[2]))
    elif p[0] == "peca":
        pecas[p[1]] = {"tipo": p[2], "x": float(p[3]), "y": float(p[4])}
    elif p[0] == "liga":
        ligacoes.append((p[1], p[2]))

# 2. calcular onde cada pino fica na placa
def pino(nome):
    ref, n = nome.split(".")
    peca = pecas[ref]
    dx, dy = BIBLIOTECA[peca["tipo"]][n]
    return peca["x"] + dx, peca["y"] + dy

# 3. escrever o gerber do cobre
def xy(x, y):
    return f"X{int(x * 1e6)}Y{int(y * 1e6)}"

g = ["%FSLAX46Y46*%", "%MOMM*%", "%ADD10R,1.2X1.4*%", "%ADD11C,0.3*%"]
g.append("D10*")
for ref, peca in pecas.items():
    for n in BIBLIOTECA[peca["tipo"]]:
        g.append(xy(*pino(f"{ref}.{n}")) + "D03*")
g.append("D11*")
for a, b in ligacoes:
    g.append(xy(*pino(a)) + "D02*")
    g.append(xy(*pino(b)) + "D01*")
g.append("M02*")
open("cobre_cima.gbr", "w").write("\n".join(g) + "\n")
print("ok:", len(pecas), "pecas,", len(ligacoes), "ligacao")
