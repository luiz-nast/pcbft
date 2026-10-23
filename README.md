# projeto-placa

Ferramenta pessoal que transforma a descrição de uma placa em texto nos arquivos que a fábrica aceita (Gerber + Excellon), sem KiCad. Vem com uma bancada no navegador para investigar a placa.

```
placa 70 45
furos cantos 3.2
peca DevKit esp32_devkit 30 24
peca R1 resistor 38.62 5
peca D1 led 44.24 5
liga DevKit.11 R1.1
liga R1.2 D1.1
liga D1.2 GND
```

## Usar

```bash
uv venv .venv && uv pip install -r requirements.txt
.venv/bin/python ferramenta/testar.py placas/estudo
python3 -m http.server   # abrir localhost:8000/bancada/?placa=estudo
```

O `testar.py` gera `modelo.json`, os Gerbers, o Excellon e a versão, e depois roda 6 etapas: lê o txt, confere peças, confere ligações, regras da fábrica (JLCPCB), relê o Gerber com o `gerbonara` e tira uma foto da placa.

A bancada tem três abas: **Thinking** (objetivo e requisitos), **Projeto** (a placa, com inspetor) e **Testes** (as etapas ao vivo).

A especificação inteira está em [PROJETO.md](PROJETO.md). As medidas da biblioteca ainda são de exemplo, até cada peça ter o datasheet.
