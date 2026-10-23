"""circuito.py: liga o circuito no papel. Corrente contínua, só com pilha, resistor, LED e chave.

O mesmo modelo existe em JS na bancada (funcao simular), pro painel responder na hora. Mudou aqui, muda lá.
- resistor: I = V / R
- LED: conduz com uma queda fixa vf (do datasheet); abaixo disso não passa nada
- chave: apertada vira fio; solta, fica aberta
- pilha: fonte de tensão ideal, do − pro +

A conta é análise nodal: uma incógnita por net (tensão) e uma por fonte de tensão (corrente).
"""

GMIN = 1e-9      # condutância mínima de cada net pro terra, só pra net solta não travar a conta
R_CHAVE = 1e-3   # chave apertada = resistor bem pequeno


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
    devolve {"nets": {net: V}, "pecas": {ref: {...}}, "entra": {"REF.N": corrente que entra pelo pino}}"""
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

    # fontes de tensão: pilhas sempre; LED só quando aceso (a gente vai acertando quais acendem)
    acesos = {p["ref"]: True for p in pecas if p["eletrica"]["modelo"] == "led"}
    for _ in range(20):
        fontes = []   # (ref, net_mais, net_menos, volts)
        for p in pilhas:
            e = p["eletrica"]
            fontes.append((p["ref"], net(p["ref"], e["mais"]), net(p["ref"], e["menos"]), aj["pilha"].get(p["ref"], e["v"])))
        for p in pecas:
            if p["eletrica"]["modelo"] == "led" and acesos[p["ref"]]:
                fontes.append((p["ref"], net(p["ref"], "1"), net(p["ref"], "2"), p["eletrica"]["vf"]))
        N, M = len(nets), len(fontes)
        A = [[0.0] * (N + M) for _ in range(N + M)]
        b = [0.0] * (N + M)
        for i in range(N):
            A[i][i] += GMIN

        def condutancia(na, nb, g):
            for x, sx in ((na, 1), (nb, -1)):
                if x == terra:
                    continue
                A[idx[x]][idx[x]] += g
                if na != terra and nb != terra:
                    A[idx[x]][idx[nb if x == na else na]] -= g

        for p in pecas:
            e, ref = p["eletrica"], p["ref"]
            if e["modelo"] == "resistor":
                condutancia(net(ref, "1"), net(ref, "2"), 1 / aj["resistor"].get(ref, p["valor"]))
            elif e["modelo"] == "chave" and aj["chave"].get(ref, False):
                condutancia(net(ref, e["lados"][0][0]), net(ref, e["lados"][1][0]), 1 / R_CHAVE)
        for k, (ref, mais, menos, volts) in enumerate(fontes):
            # corrente I_k anda do + pro − por dentro da fonte (convenção de carga)
            for x, s in ((mais, 1), (menos, -1)):
                if x != terra:
                    A[idx[x]][N + k] += s
                    A[N + k][idx[x]] += s
            b[N + k] = volts
        x = resolver_linear(A, b)
        v = {n: x[idx[n]] for n in nets}
        v[terra] = 0.0
        i_fonte = {ref: x[N + k] for k, (ref, *_) in enumerate(fontes)}

        # LED aceso puxando corrente pra trás apaga; LED apagado com tensão acima de vf acende
        mudou = False
        for p in pecas:
            if p["eletrica"]["modelo"] != "led":
                continue
            ref = p["ref"]
            if acesos[ref] and i_fonte[ref] < -1e-12:
                acesos[ref], mudou = False, True
            elif not acesos[ref] and v[net(ref, "1")] - v[net(ref, "2")] > p["eletrica"]["vf"] + 1e-9:
                acesos[ref], mudou = True, True
        if not mudou:
            break

    saida, entra = {}, {}
    for p in pecas:
        e, ref = p["eletrica"], p["ref"]
        if e["modelo"] == "resistor":
            ohms = aj["resistor"].get(ref, p["valor"])
            i = (v[net(ref, "1")] - v[net(ref, "2")]) / ohms
            saida[ref] = {"i": i, "p": i * i * ohms, "ohms": ohms}
            entra[f"{ref}.1"], entra[f"{ref}.2"] = i, -i
        elif e["modelo"] == "led":
            i = max(i_fonte.get(ref, 0.0), 0.0) if acesos[ref] else 0.0
            saida[ref] = {"i": i, "acende": i >= 0.001, "forte": i > (e["i_teste"] + e["i_max"]) / 2, "queima": i > e["i_max"]}
            entra[f"{ref}.1"], entra[f"{ref}.2"] = i, -i
        elif e["modelo"] == "pilha":
            i = -i_fonte[ref]   # a pilha empurra corrente pra fora do +
            saida[ref] = {"i": i, "v": aj["pilha"].get(ref, e["v"])}
            entra[f"{ref}.{e['mais']}"], entra[f"{ref}.{e['menos']}"] = -i, i
        elif e["modelo"] == "chave":
            apertada = aj["chave"].get(ref, False)
            a, bb = net(ref, e["lados"][0][0]), net(ref, e["lados"][1][0])
            i = (v[a] - v[bb]) / R_CHAVE if apertada else 0.0
            saida[ref] = {"i": i, "apertada": apertada}
            for n in e["lados"][0]:
                entra[f"{ref}.{n}"] = i
            for n in e["lados"][1]:
                entra[f"{ref}.{n}"] = -i
    return {"nets": v, "pecas": saida, "entra": entra}
