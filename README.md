# pcbft

Ferramenta pessoal que transforma a descrição de uma placa em texto nos arquivos que a fábrica aceita (Gerber + Excellon), sem KiCad. Vem com um app local para investigar a placa, ligar o circuito no papel e acompanhar o caminho até a fábrica.

```
placa 52 34
furos cantos 3.2
peca BT1 pilha_cr2032 20 17
peca SW1 botao_6x6 43 25
peca R1 resistor_axial 43 15 100
peca D1 led_5mm 43 7
liga BT1.1 SW1.1
liga SW1.3 R1.1
liga R1.2 D1.1
liga D1.2 GND
```

## Usar

```bash
uv venv .venv && uv pip install -r requirements.txt
.venv/bin/python ferramenta/testar.py placas/estudo
python3 ferramenta/instalar.py   # põe o "pcbft" no menu de aplicativos
```

O app (`ferramenta/app.py`) abre numa janela própria, sem abas, com a lista de projetos. Cada projeto conta a história em 4 passos (objetivo, placa, testes, fábrica) e dá pra rodar os testes de novo de lá. Sem instalar: `python3 ferramenta/app.py`.

O `testar.py` gera `modelo.json`, os Gerbers, o Excellon e a versão, e depois roda 7 etapas: lê o txt, confere peças, confere ligações, liga o circuito no papel (pilha fraca, nominal e nova), regras da fábrica (JLCPCB), relê o Gerber com o `gerbonara` e tira uma foto da placa. O `fabrica.zip` só sai quando tudo passa.

O app tem quatro abas: **Processo** (a história do projeto: objetivo, placa, testes, peças, fábrica, montar), **Thinking** (objetivo e requisitos), **Projeto** (a placa, com inspetor e o ▶ que liga o circuito, com painel pra mexer na pilha e no resistor) e **Testes** (as etapas ao vivo).

A especificação inteira está em [PROJETO.md](PROJETO.md). A biblioteca tem quatro peças reais (resistor, LED, botão, suporte de CR2032), com footprint do KiCad e datasheet; as peças do ESP32 ainda são de exemplo.
