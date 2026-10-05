"""Pacotes de correção: só os itens com problema, com o motivo e as falas vizinhas.

    work/correcoes/correcao_000.json        entrada (um item por linha)
    work/correcoes/correcao_000.saida.json  {"<lote>#<k>": "nova tradução" | "="}

"=" mantém a tradução atual (só vale para avisos; registra a decisão em src/revisao.json).
`aplicar` grava só os IDs do pacote em out/<lote>.json e revalida.
"""
import datetime
import glob
import json
import os
import shutil

from kit.util import carregar_json, salvar_itens, salvar_json
from kit.validar import Regras, analisar_lote, carregar_revisados, checar, registrar_revisados

VIZINHOS_ANTES, VIZINHOS_DEPOIS = 2, 1


def pasta(p):
    return os.path.join(p.work, "correcoes")


def _linha(it, out):
    pt = out.get(it["k"]) if "k" in it else it.get("pt")
    quem = it.get("quem") or it.get("tipo")
    return f"{quem + ': ' if quem else ''}{it['en']} => {pt if pt else '(sem tradução)'}"


def _cena(chunk, i):
    for j in range(i, -1, -1):
        if chunk[j].get("cena"):
            return chunk[j]["cena"]
    return None


def gerar(p, avisos=False, limite_chars=8000):
    """Recria work/correcoes/ com os erros (e, se pedido, os avisos não revisados). Devolve os nomes."""
    d = pasta(p)
    pendentes = glob.glob(os.path.join(d, "*.saida.json"))
    if pendentes:
        raise SystemExit(f"Há saídas de correção não aplicadas: {[os.path.basename(f) for f in pendentes]}. "
                         "Rode 'aplicar' antes de gerar novos pacotes.")
    regras = Regras(p.cfg["validacao"])
    revisados = carregar_revisados(p)
    itens, refazer, limpos = [], [], 0
    for nome in p.lotes():
        chunk, out, problemas, _ = analisar_lote(p, nome, regras, revisados)
        if out is None:
            continue
        if out == "invalido":
            refazer.append(nome)
            continue
        chaves = {it["k"] for it in chunk if "k" in it}
        extras = [k for k in out if k not in chaves]
        if extras:
            for k in extras:
                del out[k]
            salvar_json(os.path.join(p.out, nome + ".json"), out)
            limpos += len(extras)
        pos = {it["k"]: i for i, it in enumerate(chunk) if "k" in it}
        for pr in problemas:
            if pr["k"] is None or not (pr["erros"] or (avisos and pr["avisos"])):
                continue
            i = pos[pr["k"]]
            it = chunk[i]
            item = {"id": f"{nome}#{pr['k']}", "problema": "erro" if pr["erros"] else "aviso",
                    "motivo": "; ".join(pr["erros"] or pr["avisos"])}
            if cena := _cena(chunk, i):
                item["cena"] = cena
            for campo in ("quem", "tipo"):
                if it.get(campo):
                    item[campo] = it[campo]
            item["en"] = it["en"]
            item["pt"] = out.get(pr["k"])
            vizinhos = [_linha(chunk[j], out) for j in range(i - VIZINHOS_ANTES, i + VIZINHOS_DEPOIS + 1)
                        if j != i and 0 <= j < len(chunk)]
            if vizinhos:
                item["contexto"] = vizinhos
            itens.append(item)

    shutil.rmtree(d, ignore_errors=True)
    nomes, cur, tam = [], [], 0
    for item in itens:
        t = len(json.dumps(item, ensure_ascii=False))
        if cur and tam + t > limite_chars:
            nomes.append(_gravar(d, len(nomes), cur))
            cur, tam = [], 0
        cur.append(item)
        tam += t
    if cur:
        nomes.append(_gravar(d, len(nomes), cur))
    if limpos:
        print(f"Chaves extras removidas automaticamente: {limpos}")
    if refazer:
        print(f"Saídas com JSON inválido (traduzir o lote de novo): {', '.join(refazer)}")
    erros = sum(1 for i in itens if i["problema"] == "erro")
    print(f"{len(itens)} itens ({erros} erros, {len(itens) - erros} avisos) em {len(nomes)} pacotes: {', '.join(nomes)}")
    return nomes


def _gravar(d, n, itens):
    nome = f"correcao_{n:03d}"
    salvar_itens(os.path.join(d, nome + ".json"), itens)
    return nome


def itens_do_pacote(p, nome):
    return carregar_json(os.path.join(pasta(p), nome + ".json"), [])


def aplicar(p, nome):
    """Grava as correções do pacote em out/ (só os IDs do pacote) e registra as revisões de avisos."""
    d = pasta(p)
    itens = itens_do_pacote(p, nome)
    saida_path = os.path.join(d, nome + ".saida.json")
    saida = carregar_json(saida_path)
    if not itens or saida is None:
        raise SystemExit(f"Pacote ou saída ausente: {nome}.json / {nome}.saida.json em {d}")
    regras = Regras(p.cfg["validacao"])
    outs, revisoes, sem_resposta, ainda_erro = {}, [], [], []
    for item in itens:
        v = saida.get(item["id"])
        if not isinstance(v, str) or not v.strip():
            sem_resposta.append(item["id"])
            continue
        lote, k = item["id"].split("#")
        if lote not in outs:
            outs[lote] = carregar_json(os.path.join(p.out, lote + ".json"), {})
        if v == "=":
            if item["problema"] == "aviso" and item["pt"]:
                revisoes.append((item["en"], item["pt"], item["motivo"]))
            else:
                ainda_erro.append(item["id"])
            continue
        outs[lote][k] = v
        erros, _ = checar(item["en"], v, regras, item.get("tipo", "fala"))
        if erros:
            ainda_erro.append(f"{item['id']} ({'; '.join(erros)})")
        elif item["problema"] == "aviso":
            revisoes.append((item["en"], v, item["motivo"]))
    for lote, out in outs.items():
        salvar_json(os.path.join(p.out, lote + ".json"), out)
    registrados = registrar_revisados(p, revisoes)
    arquivo = os.path.join(p.work, "historico", "correcoes")
    os.makedirs(arquivo, exist_ok=True)
    carimbo = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    for f in (nome + ".json", nome + ".saida.json"):
        shutil.move(os.path.join(d, f), os.path.join(arquivo, f"{carimbo}_{f}"))
    print(f"{nome}: {len(itens) - len(sem_resposta) - len(ainda_erro)} aplicados, {registrados} avisos revisados, "
          f"{len(sem_resposta)} sem resposta, {len(ainda_erro)} ainda com erro")
    for x in (sem_resposta + ainda_erro)[:10]:
        print("  ", x)
    return not (sem_resposta or ainda_erro)
