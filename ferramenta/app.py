"""app.py: abre o Chassi como um app. Serve o repositorio so pra esta maquina e abre uma janela.

uso: python3 ferramenta/app.py               (abre a janela; fecha sozinho uns minutos depois da janela)
     python3 ferramenta/app.py --sem-janela  (so o servidor, ate o Ctrl+C)
"""
import json
import shutil
import subprocess
import sys
import threading
import time
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

RAIZ = Path(__file__).resolve().parent.parent
PLACAS = RAIZ / "placas"
PORTA = 8765
OCIOSO = 180          # sem nenhum pedido por 3 min (janela fechada), o app fecha
rodando = {}          # placa -> processo do testar.py
ultimo = [time.monotonic()]


def python():
    """o python do .venv (tem o gerbonara), se existir"""
    venv = RAIZ / ".venv" / "bin" / "python"
    return str(venv) if venv.exists() else sys.executable


def placa(nome):
    """pasta da placa, so se for uma pasta direto dentro de placas/ com placa.txt"""
    pasta = (PLACAS / nome).resolve()
    if pasta.parent == PLACAS.resolve() and (pasta / "placa.txt").exists():
        return pasta
    return None


class Bancada(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")   # a bancada sempre ve o arquivo que acabou de mudar
        super().end_headers()

    def log_message(self, *args):
        pass

    def responder(self, dado, codigo=200):
        corpo = json.dumps(dado, ensure_ascii=False).encode()
        self.send_response(codigo)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def do_GET(self):
        ultimo[0] = time.monotonic()
        url = urlparse(self.path)
        if url.path == "/":
            self.send_response(302)
            self.send_header("Location", "/bancada/")
            self.end_headers()
            return
        if url.path == "/api/placas":
            nomes = sorted(p.name for p in PLACAS.iterdir() if placa(p.name)) if PLACAS.exists() else []
            return self.responder({"placas": nomes, "rodando": [n for n, p in rodando.items() if p.poll() is None]})
        super().do_GET()

    def do_POST(self):
        ultimo[0] = time.monotonic()
        url = urlparse(self.path)
        # o cabecalho proprio faz o navegador barrar pedido vindo de outro site
        if url.path != "/api/testar" or self.headers.get("X-Bancada") != "1":
            return self.responder({"erro": "não existe"}, 404)
        nome = parse_qs(url.query).get("placa", [""])[0]
        pasta = placa(nome)
        if not pasta:
            return self.responder({"erro": f"a placa '{nome}' não existe"}, 404)
        if nome in rodando and rodando[nome].poll() is None:
            return self.responder({"ok": True, "ja_rodando": True})
        rodando[nome] = subprocess.Popen([python(), str(RAIZ / "ferramenta" / "testar.py"), str(pasta)], cwd=RAIZ,
                                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.responder({"ok": True})


def abrir_janela(url):
    """janela de app (sem abas) no Chrome/Chromium; senao, o navegador padrao"""
    for nome in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        exe = shutil.which(nome)
        if exe:
            subprocess.Popen([exe, f"--app={url}", "--window-size=1400,900"], stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL, start_new_session=True)
            return
    webbrowser.open(url)


def fechar_quando_ocioso(servidor):
    while time.monotonic() - ultimo[0] < OCIOSO:
        time.sleep(10)
    servidor.shutdown()


if __name__ == "__main__":
    janela = "--sem-janela" not in sys.argv
    url = f"http://127.0.0.1:{PORTA}/bancada/"
    try:
        servidor = ThreadingHTTPServer(("127.0.0.1", PORTA), partial(Bancada, directory=str(RAIZ)))
    except OSError:   # ja tem uma bancada aberta: so abre outra janela
        if janela:
            abrir_janela(url)
        sys.exit()
    if janela:
        threading.Thread(target=fechar_quando_ocioso, args=(servidor,), daemon=True).start()
        abrir_janela(url)
    print(f"bancada em {url}" + ("" if janela else " (Ctrl+C fecha)"))
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        pass
