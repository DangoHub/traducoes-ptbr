"""Validação de traduções: erros bloqueiam o build; avisos só aparecem para revisão."""
import collections
import json
import os
import re

from kit.util import carregar_json


class Regras:
    def __init__(self, cfg):
        self.tags = [re.compile(r) for r in cfg["tags"]]
        self.quebras = cfg["quebras_de_linha"]
        self.codificacao = cfg["codificacao"]
        self.proporcao_escolha = cfg["escolha_max_proporcao"]


def checar(en, pt, regras, tipo="fala"):
    """Devolve (erros, avisos)."""
    if not isinstance(pt, str) or not pt.strip():
        return ["vazia"], []
    erros, avisos = [], []
    for rx in regras.tags:
        a, b = collections.Counter(rx.findall(en)), collections.Counter(rx.findall(pt))
        if a != b:
            erros.append(f"tags diferentes: faltam {list((a - b).elements())} sobram {list((b - a).elements())}")
    if regras.quebras and en.count("\n") != pt.count("\n"):
        erros.append(f"quebras de linha {en.count(chr(10))} -> {pt.count(chr(10))}")
    try:
        pt.encode(regras.codificacao)
    except UnicodeEncodeError as ex:
        erros.append(f"caractere fora do {regras.codificacao}: {pt[ex.start:ex.end]!r}")
    if tipo == "escolha" and len(pt) > len(en) * regras.proporcao_escolha + 8:
        avisos.append(f"escolha longa ({len(en)} -> {len(pt)} caracteres)")
    if pt == en and len(re.findall(r"[A-Za-z]{3,}", en)) >= 3:
        avisos.append("igual ao inglês (não traduzida?)")
    return erros, avisos


def validar_lote(projeto, nome, regras, mostrar_avisos=True):
    """Imprime os problemas do lote e devolve (n_itens, n_traduzidos, n_erros, n_avisos, traducoes_validas)."""
    chunk = carregar_json(os.path.join(projeto.chunks, nome + ".json"), [])
    path = os.path.join(projeto.out, nome + ".json")
    if not os.path.isfile(path):
        return len(chunk), 0, 0, 0, {}
    try:
        out = json.load(open(path, encoding="utf-8-sig"))
    except Exception as ex:
        print(f"{nome}: JSON inválido: {ex}")
        return len(chunk), 0, 1, 0, {}
    erros = avisos = 0
    validas = {}
    for item in chunk:
        k = item["k"]
        if k not in out:
            print(f"{nome} #{k}: FALTANDO")
            erros += 1
            continue
        e, a = checar(item["en"], out[k], regras, item.get("tipo", "fala"))
        for msg in e:
            print(f"{nome} #{k}: ERRO {msg}\n   EN: {item['en']!r}\n   PT: {out[k]!r}")
        if mostrar_avisos:
            for msg in a:
                print(f"{nome} #{k}: aviso {msg}\n   EN: {item['en']!r}\n   PT: {out[k]!r}")
        erros += len(e)
        avisos += len(a)
        if not e:
            validas[k] = out[k]
    extras = set(out) - {i["k"] for i in chunk}
    if extras:
        print(f"{nome}: chaves que não existem no lote: {sorted(extras)[:10]}")
        erros += len(extras)
    return len(chunk), len(validas), erros, avisos, validas
