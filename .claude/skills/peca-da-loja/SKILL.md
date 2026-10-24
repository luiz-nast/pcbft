---
name: peca-da-loja
description: Procurar, importar e conferir no datasheet uma peça de verdade da JLCPCB/LCSC pro Sianvolt (loja.py, conferidos.json). Use quando precisar de uma peça nova, trocar uma peça, ou quando o app avisar "falta o Claude conferir no datasheet".
---

# Peça da loja

`ferramenta/loja.py` busca no estoque da JLCPCB (a busca é por palavra exata: `CR2032 Plugin` acha, `CR2032 battery holder through hole` não), pega foto e datasheet na página da LCSC e o desenho oficial (pads, furos, serigrafia) no EasyEDA, o editor da própria JLCPCB.

```
python3 ferramenta/loja.py buscar "LED 5mm red"
python3 ferramenta/loja.py importar C779439 led placas/lanterna
```

O desenho e a foto ficam só na máquina (`placas/<nome>/pecas/` e `~/.cache/sianvolt/`). Só peça de furo (`Plugin`/`Through Hole`): a gente solda na mão.

## O que a loja não diz (e você confere no datasheet)

O import marca `pendente` e a peça não liga no papel nem vai pra fábrica até isso entrar em `ferramenta/conferidos.json` (vai pro repositório: é o que **nós** lemos, não o desenho deles). Baixe o PDF pelo link `pdfUrl` da página da LCSC e leia as figuras (`pdftoppm` e Read na imagem). Cada número com a origem em `fonte`/`_eletrica`.

| bloco | conferir |
|---|---|
| pilha (suporte) | qual furo é o + (desenho "PCB layout"); a pilha que vai nele e o datasheet dela: `v`, `v_min`, `mah`, `r_interna` (gráfico IR), `i_testada` (o maior consumo que o fabricante testou) |
| botão | quais pinos são ligados por dentro (o SCHEMATIC do datasheet), `i_max` |
| LED | o + e o − (símbolo do EasyEDA: A = +, K = −), `i_max` (IF contínua), `vf` típica e `r_s` (curva IF × VF entre 10 e 30 mA), `brilho` (curva de intensidade relativa × corrente, pares `[corrente A, fração]` com 1,0 na corrente de teste) |
| resistor | nada: valor e potência vêm dos atributos da loja |

Formato (o `C779439` já está lá de exemplo):

```json
"C779439": {"fonte": "datasheet ... (data): o que foi lido e onde",
  "nomes": {"1": "−", "2": "+"},
  "eletrica": {"modelo": "led", "mais": "2", "menos": "1", "vf": 1.97, "vf_max": 2.4, "i_teste": 0.020, "i_max": 0.030, "r_s": 3.5,
               "brilho": [[0.001, 0], [0.005, 0.32], ...]}}
```

Depois de mexer no `conferidos.json`, importe de novo (`loja.py importar ...` ou `blocos.escolher`) e rode o `testar.py`.

**Nunca chute** o + de uma peça ou os pinos de um botão: se o datasheet não deixar claro, deixe pendente e diga ao Luiz qual figura faltou.
