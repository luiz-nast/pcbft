"""instalar.py: poe o Chassi no menu de aplicativos (Linux).

uso: python3 ferramenta/instalar.py            (instala)
     python3 ferramenta/instalar.py --remover  (tira do menu)
"""
import shutil
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
ATALHO = Path.home() / ".local" / "share" / "applications" / "chassi.desktop"
PYTHON = "/usr/bin/python3" if Path("/usr/bin/python3").exists() else sys.executable   # o do sistema nao muda de lugar

if "--remover" in sys.argv:
    ATALHO.unlink(missing_ok=True)
    print(f"removido: {ATALHO}")
    sys.exit()

ATALHO.parent.mkdir(parents=True, exist_ok=True)
ATALHO.write_text(f"""[Desktop Entry]
Type=Application
Name=Chassi
Comment=Projetos de placa: objetivo, placa, testes, peças e fábrica
Exec="{PYTHON}" "{RAIZ / 'ferramenta' / 'app.py'}"
Icon={RAIZ / 'bancada' / 'icone.svg'}
Terminal=false
Categories=Development;Electronics;
Keywords=placa;pcb;gerber;bancada;
""")
ATALHO.chmod(0o755)
if shutil.which("update-desktop-database"):
    subprocess.run(["update-desktop-database", str(ATALHO.parent)], capture_output=True)
print(f"instalado: {ATALHO}\nprocure por 'Chassi' no menu de aplicativos")
