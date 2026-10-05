import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJETOS = os.path.join(REPO, "projetos")

try:
    import tiktoken
    _ENC = tiktoken.get_encoding("o200k_base")
except Exception:
    _ENC = None


def carregar_json(path, padrao=None):
    if not os.path.isfile(path):
        return padrao
    with open(path, encoding="utf-8-sig") as f:
        return json.load(f)


def salvar_json(path, data, indent=1):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
    os.replace(tmp, path)


def salvar_itens(path, itens):
    """Lista JSON com um item por linha: legível para o agente e sem o custo da indentação."""
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        f.write("[\n" + ",\n".join(json.dumps(i, ensure_ascii=False) for i in itens) + "\n]\n")
    os.replace(tmp, path)


def tokens(texto):
    """Tokens do texto (tiktoken o200k, se instalado; senão estimativa por caracteres)."""
    if _ENC is not None:
        return len(_ENC.encode(texto, disallowed_special=()))
    return round(len(texto) / 3.6)
