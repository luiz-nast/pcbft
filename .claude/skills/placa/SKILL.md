---
name: placa
description: Editar uma placa deste repositório (placa.txt, requisitos.md, biblioteca) e gerar os arquivos de fábrica (Gerber + Excellon). Use sempre que o Luiz pedir mudança numa placa, peça nova, ligação, ou pra mandar pra fábrica.
---

# Placa

O Claude decide só a **intenção** (quais peças, onde, o que liga em quê). Contas, pinos, checagens e Gerber são código em `ferramenta/`. Especificação inteira: `PROJETO.md`.

## Fluxo

1. Edite `placas/<nome>/placa.txt` (e `requisitos.md` se o objetivo mudou). Nada mais à mão.
2. Rode a bateria (ela também gera tudo e salva a versão):
   ```
   .venv/bin/python ferramenta/testar.py placas/<nome> -m "o que mudou, numa frase"
   ```
   Sem `-m`, a frase sai do diff do txt.
3. Falhou? Leia `testes.json` (ou a saída do comando), corrija o txt e rode de novo, **sozinho**, até passar ou até precisar de uma decisão do Luiz.
4. Passou da etapa 6? Olhe `saida/foto.png` antes de dizer que está bom.
5. No fim da rodada, e só no fim, escreva o resumo (2 ou 3 frases, termine com a pergunta do próximo passo):
   ```
   .venv/bin/python ferramenta/testar.py placas/<nome> --resumo "..."
   ```
6. Atualize o `AGORA.md` no fim da sessão.

**Nunca diga que terminou sem ter rodado o `testar.py`.** A bancada (`python -m http.server` na raiz, `localhost:8000/bancada/?placa=<nome>`) se atualiza sozinha; não descreva o progresso no chat, o resumo final basta.

## placa.txt

Uma instrução por linha, mm, origem no canto inferior esquerdo. `#` começa comentário.

```
placa 70 45                 # contorno L x A
furos cantos 3.2            # 4 furos de fixação a 3,5 mm das bordas (3,2 = M3)
peca R1 resistor 38.62 5    # REF TIPO X Y (centro da peça); TIPO existe em biblioteca.py
liga DevKit.11 R1.1         # REF.PINO ou nome de net (GND)
liga D1.2 GND               # vai até o pino de GND mais perto
```

- Trilha é linha reta, 0,3 mm. Se duas cruzarem ou passarem perto de um pad, a etapa 3 acusa **curto**: mude a posição das peças (ou escolha outro pino) até a linha reta ficar limpa.
- Uma ligação entre nets com nome diferente (GND com 3V3) é erro.

## requisitos.md

```
# Objetivo: título
Uma frase.

## R1 Título do requisito
pecas: D1 R1
verifica: ligado R1.2 D1.1      # existe REF | ligado A B | sem_pino_solto REF
- sub-requisito em texto
```

O status é calculado pelo `testar.py`. Nunca escreva status à mão. Checagem nova vira código em `testar.py` (`CHECAGENS`, `checar`).

## Biblioteca

`ferramenta/biblioteca.py`: `tipo -> pinos (dx, dy, pad[, net]), furo, corpo, fonte`. **Nenhum número inventado**: medidas vêm do datasheet da peça escolhida, com o link em `fonte`. `fonte: None` = exemplo, e a bancada avisa. Não sabe a medida? Pergunte ou deixe pendente.

## Regras de formato (já aprendidas)

- Gerber: `%FSLAX46Y46*%` e `%MOMM*%`, coordenadas em milionésimos de mm (arredondar, não truncar), `G01*` antes de desenhar, `D02` move, `D01` desenha, `D03` carimba pad, `M02*` no fim. Aberturas a partir de `D10`.
- Excellon: `M48`, `METRIC,TZ`, ferramentas `T1C3.200`, **`G90` antes do `%`** (fora do cabeçalho o leitor reclama), `M30` no fim. Furo com cobre (PTH) e sem cobre (NPTH) em arquivos separados.
- Nomes no padrão do KiCad (`placa-F_Cu.gbr`, `placa-Edge_Cuts.gbr`, `placa-PTH.drl`, `placa-NPTH.drl`): o gerbonara e a fábrica reconhecem sozinhos.
- Regras da fábrica ficam em `testar.py`, com o link da página da JLCPCB. Mudou a página? Atualize o número e a data.

## Eletrônica (regras simples, pra explicar pro Luiz)

- LED sempre com resistor em série; sem ele, o LED queima. Pino 1 é o + (ânodo).
- GND é o terra, o 0 V de referência. Todo GND da placa é a mesma net.
- Furo de fixação não tem cobre; cobre perto dele conta como borda (0,2 mm).
