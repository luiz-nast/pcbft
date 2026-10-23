"""circuito.py: liga o circuito no papel. Corrente contínua, só com pilha, resistor, LED e chave.

O mesmo modelo existe em JS na bancada (funcao simular), pro painel responder na hora. Mudou aqui, muda lá.
- resistor: I = V / R
- LED aceso: V = joelho + r_s · I (joelho = vf − r_s · i_teste, do datasheet); abaixo do joelho não passa nada
- chave: apertada vira fio; solta, fica aberta
- pilha: fonte de tensão com uma resistência bem pequena em série (R_PILHA): não é a resistência interna de
  verdade (o datasheet não dá), é só pra conta fechar com duas pilhas em paralelo
- pino sem net = circuito aberto

A conta é análise nodal: uma incógnita por net (tensão). Fonte com resistência em série entra como
condutância + corrente injetada (Norton), então a matriz nunca fica sem solução.
"""

GMIN = 1e-9      # condutância mínima de cada net pro terra, só pra net solta não travar a conta
R_CHAVE = 1e-3   # chave apertada = resistor bem pequeno
R_PILHA = 1e-3   # ver docstring


def joelho(e):
    return e["vf"] - e["r_s"] * e["i_teste"]


def resolver_linear(A, b):
    """Gauss com pivô; A quadrada, b vetor"""
    n = len(b)
    M = [linha[:] + [b[i]] for i, linha in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda i: abs(M[i][c]))
        M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-18:
            raise ZeroDivisionError("circuito sem solução")
        for i in range(n):
            if i != c and M[i][c]:
                f = M[i][c] / M[c][c]
                M[i] = [x - f * y for x, y in zip(M[i], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def resolver(modelo, ajustes=None):
    """ajustes: {"pilha": {ref: volts}, "resistor": {ref: ohms}, "chave": {ref: True = apertada}}
    devolve {"nets": {net: V}, "pecas": {ref: {...}}, "entra": {"REF.N": corrente que entra pelo pino}}
    ou None quando não tem pilha."""
    aj = {"pilha": {}, "resistor": {}, "chave": {}, **(ajustes or {})}
    pecas = [p for p in modelo["pecas"] if p.get("eletrica")]
    net_de = {(p["ref"], q["n"]): q["net"] for p in modelo["pecas"] for q in p["pinos"]}
    pilhas = [p for p in pecas if p["eletrica"]["modelo"] == "pilha"]
    if not pilhas:
        return None
    terra = net_de[(pilhas[0]["ref"], pilhas[0]["eletrica"]["menos"])]
    nets = sorted({n for n in net_de.values() if n and n != terra})
    idx = {n: i for i, n in enumerate(nets)}

    def net(ref, n):
        return net_de[(ref, n)]

    def tensao(v, a, b):
        return v[a] - v[b] if a is not None and b is not None else None

    acesos = {p["ref"]: True for p in pecas if p["eletrica"]["modelo"] == "led"}
    v = {}
    for _ in range(30):
        N = len(nets)
        A = [[0.0] * N for _ in range(N)]
        b = [0.0] * N
        for i in range(N):
            A[i][i] += GMIN

        def condutancia(na, nb, g):
            if na is None or nb is None:   # pino sem net: aberto
                return
            for x, outro in ((na, nb), (nb, na)):
                if x == terra:
                    continue
                A[idx[x]][idx[x]] += g
                if outro != terra:
                    A[idx[x]][idx[outro]] -= g

        def fonte(na, nb, volts, r):   # fonte de tensão com r em série, + em na: Norton
            if na is None or nb is None:
                return
            g = 1 / r
            condutancia(na, nb, g)
            if na != terra:
                b[idx[na]] += g * volts
            if nb != terra:
                b[idx[nb]] -= g * volts

        for p in pecas:
            e, ref = p["eletrica"], p["ref"]
            if e["modelo"] == "resistor":
                condutancia(net(ref, "1"), net(ref, "2"), 1 / aj["resistor"].get(ref, p["valor"]))
            elif e["modelo"] == "chave" and aj["chave"].get(ref, False):
                condutancia(net(ref, e["lados"][0][0]), net(ref, e["lados"][1][0]), 1 / R_CHAVE)
            elif e["modelo"] == "pilha":
                fonte(net(ref, e["mais"]), net(ref, e["menos"]), aj["pilha"].get(ref, e["v"]), R_PILHA)
            elif e["modelo"] == "led" and acesos[ref]:
                fonte(net(ref, "1"), net(ref, "2"), joelho(e), e["r_s"])
        x = resolver_linear(A, b)
        v = {n: x[idx[n]] for n in nets}
        v[terra] = 0.0

        # LED aceso puxando corrente pra trás apaga; LED apagado com tensão acima do joelho acende
        mudou = False
        for p in pecas:
            if p["eletrica"]["modelo"] != "led":
                continue
            ref, e = p["ref"], p["eletrica"]
            vab = tensao(v, net(ref, "1"), net(ref, "2"))
            if vab is None:
                acesos[ref] = False
            elif acesos[ref] and vab < joelho(e) - 1e-9:
                acesos[ref], mudou = False, True
            elif not acesos[ref] and vab > joelho(e) + 1e-9:
                acesos[ref], mudou = True, True
        if not mudou:
            break

    saida, entra = {}, {}
    for p in pecas:
        e, ref = p["eletrica"], p["ref"]
        if e["modelo"] == "resistor":
            ohms = aj["resistor"].get(ref, p["valor"])
            vab = tensao(v, net(ref, "1"), net(ref, "2"))
            i = vab / ohms if vab is not None else 0.0
            saida[ref] = {"i": i, "p": i * i * ohms, "ohms": ohms}
            entra[f"{ref}.1"], entra[f"{ref}.2"] = i, -i
        elif e["modelo"] == "led":
            vab = tensao(v, net(ref, "1"), net(ref, "2"))
            i = max((vab - joelho(e)) / e["r_s"], 0.0) if acesos[ref] and vab is not None else 0.0
            saida[ref] = {"i": i, "v": joelho(e) + e["r_s"] * i if i > 0 else (vab or 0.0),
                          "acende": i >= 0.001, "forte": i > (e["i_teste"] + e["i_max"]) / 2, "queima": i > e["i_max"]}
            entra[f"{ref}.1"], entra[f"{ref}.2"] = i, -i
        elif e["modelo"] == "pilha":
            volts = aj["pilha"].get(ref, e["v"])
            vab = tensao(v, net(ref, e["mais"]), net(ref, e["menos"]))
            i = (volts - vab) / R_PILHA if vab is not None else 0.0   # corrente que sai do +
            saida[ref] = {"i": i, "v": volts}
            entra[f"{ref}.{e['mais']}"], entra[f"{ref}.{e['menos']}"] = -i, i
        elif e["modelo"] == "chave":
            apertada = aj["chave"].get(ref, False)
            vab = tensao(v, net(ref, e["lados"][0][0]), net(ref, e["lados"][1][0]))
            i = vab / R_CHAVE if apertada and vab is not None else 0.0
            saida[ref] = {"i": i, "apertada": apertada}
            for n in e["lados"][0]:
                entra[f"{ref}.{n}"] = i
            for n in e["lados"][1]:
                entra[f"{ref}.{n}"] = -i
    return {"nets": v, "pecas": saida, "entra": entra}
