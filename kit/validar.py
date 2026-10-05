"""Validação de traduções: erros bloqueiam o build; avisos só aparecem para revisão.

Itens de lote sem "k" são referência (já traduzidos) e não são validados.
Avisos já revisados ficam em src/revisao.json como pares [inglês, português] e deixam de aparecer.
"""
import collections
import json
import os
import re

from kit.util import carregar_json, salvar_json

TAG_HTML = re.compile(r"<(/?)([A-Za-z]+)(?:=[^<>]*)?>")


class Regras:
    def __init__(self, cfg):
        self.tags = [re.compile(r) for r in cfg["tags"]]
        self.quebras = cfg["quebras_de_linha"]
        self.codificacao = cfg["codificacao"]
        self.proporcao_escolha = cfg["escolha_max_proporcao"]


def _bem_aninhado(texto, fecham):
    pilha = []
    for m in TAG_HTML.finditer(texto):
        fecha, nome = m.group(1), m.group(2).lower()
        if nome not in fecham:
            continue
        if not fecha:
            pilha.append(nome)
        elif not pilha or pilha.pop() != nome:
            return False
    return not pilha


def checar(en, pt, regras, tipo="fala"):
    """Devolve (erros, avisos)."""
    if not isinstance(pt, str) or not pt.strip():
        return ["vazia"], []
    erros, avisos = [], []
    for rx in regras.tags:
        a, b = collections.Counter(rx.findall(en)), collections.Counter(rx.findall(pt))
        if a != b:
            erros.append(f"tags diferentes: faltam {list((a - b).elements())} sobram {list((b - a).elements())}")
    fecham = {n.lower() for n in re.findall(r"</([A-Za-z]+)>", en)}
    if fecham and not erros and _bem_aninhado(en, fecham) and not _bem_aninhado(pt, fecham):
        erros.append("tags fora de ordem (abertura e fechamento cruzados)")
    if regras.quebras and en.count("\n") != pt.count("\n"):
        erros.append(f"quebras de linha {en.count(chr(10))} -> {pt.count(chr(10))}")
    try:
        pt.encode(regras.codificacao)
    except UnicodeEncodeError as ex:
        erros.append(f"caractere fora do {regras.codificacao}: {pt[ex.start:ex.end]!r}")
    if tipo == "escolha" and len(pt) > len(en) * regras.proporcao_escolha + 8:
        avisos.append(f"escolha longa ({len(en)} -> {len(pt)} caracteres)")
    if pt == en and len(_palavras(en)) >= 3:
        avisos.append("igual ao inglês (não traduzida?)")
    return erros, avisos


def _palavras(texto):
    """Palavras de 3+ letras fora de tags que não parecem onomatopeia ("Haaahh", "Nghh", "Mmm")."""
    limpo = re.sub(r"<[^<>]+>|#\w+#|\{[^{}]*\}", "", texto)
    return [w for w in re.findall(r"[A-Za-z]{3,}", limpo)
            if not re.search(r"(.)\1\1|(.)\2$", w.lower()) and not set(w.lower()) <= set("ahmngfuoeiyrsk")]


def revisao_path(p):
    return p.caminho("src", "revisao.json")


def carregar_revisados(p):
    return {(en, pt) for en, pt, *_ in carregar_json(revisao_path(p), [])}


def registrar_revisados(p, pares):
    """pares: [(en, pt, aviso)]. Grava as decisões de revisão; o mesmo par não é revisado de novo."""
    lista = carregar_json(revisao_path(p), [])
    vistos = {(en, pt) for en, pt, *_ in lista}
    novos = [list(par) for par in pares if (par[0], par[1]) not in vistos]
    if novos:
        salvar_json(revisao_path(p), lista + novos, indent=0)
    return len(novos)


def analisar_lote(projeto, nome, regras, revisados=frozenset()):
    """Devolve (chunk, out, problemas, validas).

    out é None sem arquivo de saída e "invalido" se o JSON não abre.
    problemas: [{"k", "erros", "avisos"}]; k None = problema do arquivo inteiro.
    """
    chunk = carregar_json(os.path.join(projeto.chunks, nome + ".json"), [])
    path = os.path.join(projeto.out, nome + ".json")
    if not os.path.isfile(path):
        return chunk, None, [], {}
    try:
        with open(path, encoding="utf-8-sig") as f:
            out = json.load(f)
        if not isinstance(out, dict):
            raise ValueError("a saída precisa ser um objeto {k: tradução}")
    except Exception as ex:
        return chunk, "invalido", [{"k": None, "erros": [f"JSON inválido: {ex}"], "avisos": []}], {}
    problemas, validas = [], {}
    chaves = set()
    for item in chunk:
        k = item.get("k")
        if k is None:
            continue
        chaves.add(k)
        if k not in out:
            problemas.append({"k": k, "erros": ["FALTANDO"], "avisos": []})
            continue
        e, a = checar(item["en"], out[k], regras, item.get("tipo", "fala"))
        if (item["en"], out[k]) in revisados:
            a = []
        if e or a:
            problemas.append({"k": k, "erros": e, "avisos": a})
        if not e:
            validas[k] = out[k]
    extras = sorted(set(out) - chaves)
    if extras:
        problemas.append({"k": None, "erros": [f"chaves que não existem no lote: {extras[:10]}"], "avisos": []})
    return chunk, out, problemas, validas


def validar_lote(projeto, nome, regras, mostrar_avisos=True, revisados=frozenset()):
    """Imprime os problemas do lote e devolve (n_itens, n_traduzidos, n_erros, n_avisos, traducoes_validas)."""
    chunk, out, problemas, validas = analisar_lote(projeto, nome, regras, revisados)
    itens = {it["k"]: it for it in chunk if "k" in it}
    erros = avisos = 0
    for pr in problemas:
        it = itens.get(pr["k"])
        detalhe = f"\n   EN: {it['en']!r}\n   PT: {out.get(pr['k'])!r}" if it and pr["k"] in out else ""
        ref = f"{nome} #{pr['k']}" if pr["k"] else nome
        for msg in pr["erros"]:
            print(f"{ref}: ERRO {msg}{detalhe if msg != 'FALTANDO' else ''}")
        if mostrar_avisos:
            for msg in pr["avisos"]:
                print(f"{ref}: aviso {msg}{detalhe}")
        erros += len(pr["erros"])
        avisos += len(pr["avisos"])
    return len(itens), len(validas), erros, avisos, validas
