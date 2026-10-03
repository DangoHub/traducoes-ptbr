"""Consistência de glossário.

projetos/<jogo>/glossario.json:
    {"termos": {"Crush Waves": "Ondas de Paixão", ...},   termo em inglês -> forma obrigatória em PT
     "trocas":  [["Ondas Crush", "Ondas de Paixão"], ...]} correções aplicadas por `padronizar`
"""
import collections
import json
import os
import re

from kit.lotes import traducoes_path
from kit.util import carregar_json, salvar_json


def _glossario(p):
    return carregar_json(p.caminho("glossario.json"), {"termos": {}, "trocas": []})


def padronizar(p):
    trocas = _glossario(p)["trocas"]
    if not trocas:
        print("glossario.json sem 'trocas'.")
        return
    total = 0
    for nome in p.lotes():
        path = os.path.join(p.out, nome + ".json")
        out = carregar_json(path)
        if not out:
            continue
        n = 0
        for k, v in out.items():
            w = v
            for errado, certo in trocas:
                w = w.replace(errado, certo)
            if w != v:
                out[k] = w
                n += 1
        if n:
            salvar_json(path, out)
            total += n
    banco = carregar_json(traducoes_path(p), {})
    nb = 0
    for alvo, (en, pt) in banco.items():
        w = pt
        for errado, certo in trocas:
            w = w.replace(errado, certo)
        if w != pt:
            banco[alvo] = [en, w]
            nb += 1
    if nb:
        salvar_json(traducoes_path(p), banco, indent=0)
    print(f"Trocas aplicadas: {total} em out/, {nb} em src/traducoes.json")


def checar_termos(p, exemplos=2):
    termos = _glossario(p)["termos"]
    pares = []
    for nome in p.lotes():
        chunk = carregar_json(os.path.join(p.chunks, nome + ".json"), [])
        out = carregar_json(os.path.join(p.out, nome + ".json"), {})
        pares += [(f"{nome}#{it['k']}", it["en"], out[it["k"]]) for it in chunk if it["k"] in out]
    pares += [(alvo, en, pt) for alvo, (en, pt) in carregar_json(traducoes_path(p), {}).items()]
    falhas = collections.defaultdict(list)
    for termo_en, termo_pt in termos.items():
        rx = re.compile(r"\b" + re.escape(termo_en) + r"\b", re.I)
        for ref, en, pt in pares:
            if rx.search(en) and termo_pt.lower() not in pt.lower():
                falhas[termo_en].append((ref, pt))
    for termo_en, lista in sorted(falhas.items(), key=lambda x: -len(x[1])):
        print(f"{termos[termo_en]!r} ({termo_en}): {len(lista)} sem a forma do glossário")
        for ref, pt in lista[:exemplos]:
            print(f"   {ref}: {pt[:120]}")
    if not falhas:
        print("Glossário seguido em todos os itens.")
    return falhas
