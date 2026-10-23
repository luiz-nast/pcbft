# [NOME DO PROJETO]

Ferramenta pessoal que transforma a descrição de uma placa em texto nos arquivos que a fábrica aceita (Gerber + Excellon), sem KiCad. O Claude Code constrói e edita; o Luiz investiga e aprende pela bancada (um app leve no navegador).

Este arquivo é a especificação inteira. Leia tudo antes do primeiro passo.

---

## 1. Princípios (não quebrar)

1. **Texto é a fonte da verdade.** Tudo que importa vive em arquivos de texto no repositório. O app só lê e desenha.
2. **O que pode ser código vira código.** O Claude decide só a intenção (quais peças, onde, o que liga em quê). Contas, posições de pinos, checagens e Gerber são código determinístico.
3. **Clean.** Interface mínima, informação sob demanda. Nada aberto que não foi pedido.
4. **IA não gasta token com acompanhamento.** Status de requisitos e progresso dos testes são calculados pelo script. O Claude só dá um resumo **no final** da rodada.
5. **Nenhum número inventado.** Medidas de componentes vêm de datasheet. Regras da fábrica vêm da página de capacidades da fábrica (JLCPCB como referência). Se não souber, pergunte ou marque como pendente.
6. **Simples primeiro.** Python puro, poucas dependências, arquivos pequenos. Nada de framework no app.

---

## 2. Como o trabalho flui

```
Luiz pede no Claude Code
  → Claude edita requisitos.md e/ou placa.txt (só intenção)
  → ferramenta/gerar.py: txt → modelo.json + Gerber + Excellon
  → ferramenta/testar.py: bateria de 6 etapas → testes.json
      falhou? Claude corrige e roda de novo, sozinho
  → nova versão salva em versoes/
  → bancada atualiza sozinha (lê os arquivos)
  → Luiz investiga → pede mudança (volta ao início) ou aprova
  → saida/fabrica.zip pra JLCPCB
```

---

## 3. Estrutura do repositório

```
PROJETO.md            ← este arquivo
AGORA.md              ← onde paramos (4 linhas, Claude atualiza a cada sessão)
.claude/skills/placa/SKILL.md   ← skill (marco 6)
ferramenta/
  gerar.py            ← lê placa.txt, escreve modelo.json, Gerbers, Excellon
  biblioteca.py       ← pinos de cada tipo de peça (de datasheet)
  testar.py           ← bateria de testes → testes.json
bancada/
  index.html          ← o app (HTML + JS puro, SVG)
placas/estudo/
  requisitos.md
  placa.txt
  saida/              ← gerado: modelo.json, *.gbr, *.drl, foto.png, fabrica.zip
  testes.json         ← gerado
  versoes/            ← v1.txt, v2.txt, ... + versoes.json
```

Rodar a bancada: `python -m http.server` na raiz e abrir `localhost:8000/bancada/`. A página relê os arquivos a cada 1 s (polling simples).

---

## 4. Os arquivos de texto

### 4.1 `placa.txt` (o Claude escreve)

Uma instrução por linha. Unidades em mm, origem no canto inferior esquerdo.

```
placa 60 40
furos cantos 3.2
peca DevKit esp32_devkit 24 21
peca R1 resistor 44 27
peca D1 led 52 27
peca SW1 botao 47 12
peca BZ1 buzzer 24 8
liga DevKit.4 R1.1
liga R1.2 D1.1
liga D1.2 GND
```

- `placa L A` — contorno retangular.
- `furos cantos D` — 4 furos de fixação a 3,5 mm das bordas (D = 3,2 mm pra M3).
- `peca REF TIPO X Y` — TIPO precisa existir na biblioteca.
- `liga A B` — `REF.PINO` ou o nome de uma net (`GND`). Vira trilha em linha reta por enquanto.
- Depois (quando trilhas cruzarem): `liga A B via X Y`.
- Quando as ligações ficarem complexas (marco 7+), avaliar trocar o formato por TOML. Não antes.

### 4.2 `requisitos.md` (o Claude escreve uma vez)

Cada requisito declara as peças e **como é verificado**. O script calcula o status, a IA nunca atualiza status à mão.

```
# Objetivo: Placa de estudo pro ESP32
Encaixa o DevKit e já vem com LED, botão e buzzer.

## R1 Encaixar o DevKit
pecas: DevKit
verifica: existe DevKit
- Furos na distância dos pinos do DevKit
- Placa presa com 4 parafusos M3

## R2 LED acende sem queimar
pecas: D1 R1
verifica: ligado DevKit.4 R1.1
verifica: ligado R1.2 D1.1
verifica: ligado D1.2 GND
- R1 limita a corrente
- LED do lado certo
```

Checagens disponíveis no começo: `existe REF`, `ligado A B`, `sem_pino_solto REF`. Novas checagens viram código em `testar.py`.

### 4.3 `testes.json` (o script escreve, etapa por etapa)

```json
{
  "versao": 3,
  "rodando": false,
  "etapas": [
    {"nome": "Lê o txt", "estado": "ok", "detalhe": "10 linhas"},
    {"nome": "Confere ligações", "estado": "falhou", "detalhe": "SW1 e BZ1 sem ligação",
     "onde": ["SW1", "BZ1"], "requisitos": ["R3", "R4"]}
  ],
  "requisitos": {"R1": "ok", "R2": "ok", "R3": "falha", "R4": "falha"}
}
```

O script reescreve o arquivo a cada etapa, e é assim que a bancada mostra "ao vivo" sem IA.

### 4.4 `saida/modelo.json` (o gerar.py escreve)

É o que a bancada desenha e inspeciona: cada peça e pino com posição absoluta, net e **a linha do placa.txt que o criou**.

```json
{
  "placa": {"w": 60, "h": 40},
  "pecas": [{"ref": "R1", "tipo": "resistor", "x": 44, "y": 27, "linha": 4,
             "pinos": [{"n": "1", "x": 43, "y": 27, "net": "LED"}]}],
  "trilhas": [{"de": "DevKit.4", "ate": "R1.1", "largura": 0.3, "linha": 6}],
  "furos": [{"x": 3.5, "y": 3.5, "d": 3.2}]
}
```

---

## 5. A ferramenta (Python)

`ferramenta/gerar.py` já existe numa versão mínima testada (ler txt → calcular pinos pela biblioteca → escrever Gerber). Evoluir, sem reescrever do zero:

1. Ler (linha por linha, guardando o número da linha).
2. Calcular posição absoluta de cada pino = posição da peça + offset da biblioteca.
3. Escrever `modelo.json`.
4. Escrever os Gerbers: contorno, cobre de cima (pads + trilhas). Depois: cobre de baixo, máscara, serigrafia.
5. Escrever o Excellon (furos).
6. Copiar `placa.txt` pra `versoes/vN.txt` e anotar em `versoes.json` uma frase do que mudou.

**Biblioteca (`biblioteca.py`):** um dicionário `tipo → {pino: (dx, dy, tamanho_pad)}`. Os valores do `gerar.py` atual são **de exemplo**. Os reais saem do datasheet de cada peça escolhida, e cada entrada leva um comentário com a fonte.

**Regras de formato já aprendidas (ir pra skill):**
- Gerber: cabeçalho `%FSLAX46Y46*%` e `%MOMM*%`, coordenadas em milionésimos de mm, `D02` move, `D01` desenha, `D03` carimba pad, `M02*` fim.
- Excellon: `M48`, `METRIC,TZ`, ferramentas `T1C3.200`, **`G90` antes do `%`** (fora do cabeçalho o leitor reclama), `M30` fim.

---

## 6. A bateria de testes (`testar.py`)

Seis etapas, em ordem. Para na primeira que falhar.

1. **Lê o txt**: sintaxe, comandos conhecidos.
2. **Confere peças**: todo TIPO existe na biblioteca.
3. **Confere ligações**: pino solto, ligação pra pino que não existe, curto (duas nets diferentes encostando).
4. **Regras da fábrica**: trilha mínima, furo mínimo, distância da borda (números da página da JLCPCB, com link no código).
5. **Relê o Gerber**: abre os arquivos gerados com um leitor independente (`gerbonara`) e confere que lê sem aviso.
6. **Tira foto da placa**: renderiza `foto.png` pra o Claude olhar.

Também calcula o status de cada requisito a partir das linhas `verifica:`.

---

## 7. A bancada (app)

HTML + JS puro, desenho em SVG (facilita clique, destaque e zoom via viewBox). Tema escuro, fonte IBM Plex Sans/Mono. Referência visual: `design/App.dc.html` e `design/Board.dc.html` (abrir no navegador não roda; é pra ler o layout e as cores).

**Topo:** nome do projeto · abas **Thinking | Projeto | Testes** · status dos testes (✓/✗) · relógio de versões (abre lista; escolher v1/v2 mostra a placa daquela versão; opção "destacar o que mudou").

**Thinking:** o objetivo num card em cima, os requisitos em cards ligados embaixo, cada um com status (ok / falta ligar) e peças. Modo **Simples** e **Detalhado** (mostra os sub-requisitos). "Ver na placa →" abre a peça na aba Projeto. Começar como árvore simples; canvas roteado só depois.

**Projeto:** a placa ocupa a tela.
- Ferramentas no canto: **seta**, **mão** (arrastar), **+ / −** zoom, centralizar.
- **HUD** que segue o mouse: nome do que está embaixo + x/y em mm.
- Clicar numa peça ou pino abre o **inspetor** (direita): tipo, ligações, linha do `placa.txt` que criou aquilo, "O que é isso?" (explicação curta pra aprender), requisito atendido.
- Clicar num pino: **escurece tudo que não é da net dele**.

**Testes:** a lista das 6 etapas atualizando ao vivo (lê `testes.json`) e, ao lado, a placa com o que falhou contornado em vermelho ("sem ligação"). Ao terminar, um único bloco "Resumo do Claude" (texto que o Claude escreve no fim, em `testes.json` campo `resumo`).

Paleta: fundo `#14171A`, área da placa `#0E1012`, painéis `#1C2024`, bordas `#2A3036`, texto `#E8EAED`, secundário `#9AA3AD`, placa `#1F6F4A`, cobre `#E0A458`, ok `#6FD39B`, erro `#FF8A80`, destaque `#8EC5FF`.

---

## 8. Marcos (fazer em ordem, um por vez)

Cada marco termina com algo que o Luiz vê funcionando, testado pelo Claude.

1. **Ferramenta mínima completa**: `gerar.py` com contorno, furos (Excellon), pads, trilhas e `modelo.json`. Testar com `gerbonara` e mostrar a imagem.
2. **Bateria de testes**: `testar.py` com as 6 etapas escrevendo `testes.json` etapa por etapa.
3. **Bancada, aba Projeto**: SVG da placa a partir do `modelo.json`, seta/mão/zoom, HUD, inspetor, destaque de net.
4. **Bancada, aba Testes**: etapas ao vivo + placa com os erros contornados + resumo final.
5. **Requisitos + aba Thinking** (modo simples primeiro).
6. **Skill**: `.claude/skills/placa/SKILL.md` com o fluxo, o formato do `placa.txt`, as regras de Gerber/Excellon e "rode testar.py antes de dizer que terminou".
7. **Placa de estudo de verdade**: biblioteca com valores de datasheet (DevKit, LED, resistor, botão, buzzer), pads passantes nos dois lados pros pinos do DevKit, máscara e serigrafia, regras reais da JLCPCB, `fabrica.zip`. **Encomendar.**
8. Depois, se fizer falta: MCP pra o Claude consultar a bancada direto.

Fora do escopo por agora: chat embutido no app, simulação elétrica, autoroteamento, mais de 2 camadas.

---

## 9. Como trabalhar com o Luiz

- Um passo de cada vez. Mostre o resultado de cada passo antes do próximo.
- Código pequeno e simples, que dá pra ler e decorar. Mantenha o estilo que já existe.
- **O Claude testa, sempre.** Rode, confira e mostre o resultado (imagem quando der). O Luiz não testa na mão.
- Edite sempre o mesmo arquivo em vez de criar caminho novo.
- Respostas curtas e diretas.
- Quando explicar algo de eletrônica, explique simples e adicione a regra na skill.
- No fim de cada sessão, atualize o `AGORA.md`.
