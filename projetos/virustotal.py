"""Envia arquivos ao VirusTotal (chave VT_API_KEY do ambiente ou do .env na raiz) e mostra o resultado.

Uso: python projetos/virustotal.py arquivo.zip [arquivo2.zip ...]
"""
import hashlib
import json
import os
import sys
import time
import urllib.request
import uuid

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://www.virustotal.com/api/v3"


def chave():
    if os.environ.get("VT_API_KEY"):
        return os.environ["VT_API_KEY"]
    env = os.path.join(RAIZ, ".env")
    for linha in open(env, encoding="utf-8"):
        if linha.strip().startswith("VT_API_KEY="):
            return linha.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit("VT_API_KEY não encontrada")


def pedir(url, k, dados=None, tipo=None):
    req = urllib.request.Request(url, data=dados, headers={"x-apikey": k, **({"Content-Type": tipo} if tipo else {})})
    with urllib.request.urlopen(req, timeout=300) as r:
        return json.load(r)


def enviar(caminho, k):
    fronteira = uuid.uuid4().hex
    corpo = (f"--{fronteira}\r\nContent-Disposition: form-data; name=\"file\"; "
             f"filename=\"{os.path.basename(caminho)}\"\r\nContent-Type: application/octet-stream\r\n\r\n").encode()
    corpo += open(caminho, "rb").read() + f"\r\n--{fronteira}--\r\n".encode()
    return pedir(f"{API}/files", k, corpo, f"multipart/form-data; boundary={fronteira}")["data"]["id"]


def main():
    k = chave()
    for caminho in sys.argv[1:]:
        sha = hashlib.sha256(open(caminho, "rb").read()).hexdigest()
        analise = enviar(caminho, k)
        while True:
            a = pedir(f"{API}/analyses/{analise}", k)["data"]["attributes"]
            if a["status"] == "completed":
                break
            time.sleep(20)
        s = a["stats"]
        print(json.dumps({"arquivo": os.path.basename(caminho), "sha256": sha,
                          "deteccoes": s["malicious"] + s["suspicious"],
                          "motores": sum(s.values()), "link": f"https://www.virustotal.com/gui/file/{sha}"}))


if __name__ == "__main__":
    main()
