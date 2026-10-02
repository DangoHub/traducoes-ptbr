import json
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJETOS = os.path.join(REPO, "projetos")


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
