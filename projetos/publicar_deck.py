"""Anexa o zip Steam Deck/Linux a uma release existente: sobe o zip, atualiza SHA256SUMS.txt e as notas."""
import hashlib
import json
import os
import subprocess
import sys
import tempfile

tag, zpath = sys.argv[1], sys.argv[2]
nome = os.path.basename(zpath)
sha = hashlib.sha256(open(zpath, "rb").read()).hexdigest()
tmp = tempfile.mkdtemp()

subprocess.check_call(["gh", "release", "download", tag, "-p", "SHA256SUMS.txt", "-D", tmp])
sums = os.path.join(tmp, "SHA256SUMS.txt")
linhas = [l for l in open(sums, encoding="utf-8").read().splitlines() if l.strip() and not l.endswith(nome)]
linhas.append(f"{sha}  {nome}")
open(sums, "w", encoding="utf-8", newline="\n").write("\n".join(linhas) + "\n")
subprocess.check_call(["gh", "release", "upload", tag, zpath, sums, "--clobber"])

body = json.loads(subprocess.check_output(["gh", "release", "view", tag, "--json", "body"]))["body"]
if "Steam Deck" not in body:
    body += ("\n\n### Steam Deck / Linux\n"
             f"Baixe o `{nome}`, extraia no Modo Desktop e dê dois cliques em `Instalar.sh` "
             "(instruções no LEIA-ME do zip). Precisa do jogo instalado; o Python 3 já vem no SteamOS.\n"
             f"```\n{sha}  {nome}\n```")
    notas = os.path.join(tmp, "notes.md")
    open(notas, "w", encoding="utf-8").write(body)
    subprocess.check_call(["gh", "release", "edit", tag, "--notes-file", notas])
print("publicado:", tag, nome, sha)
