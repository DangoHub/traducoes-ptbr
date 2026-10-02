"""Lotes: divide as unidades por conversa, consolida traduções e mostra o progresso."""
import contextlib
import io
import os
import shutil

from kit.util import carregar_json, salvar_json
from kit.validar import Regras, validar_lote

ORDEM_CAT = ("dialogo", "textos", "interface")


def traducoes_path(p):
    return p.caminho("src", "traducoes.json")


def consolidar(p):
    """Junta as saídas válidas de out/ em src/traducoes.json ({alvo: [en, pt]}) e devolve o dicionário."""
    banco = carregar_json(traducoes_path(p), {})
    indice = carregar_json(p.indice_path, {})
    regras = Regras(p.cfg["validacao"])
    novos = 0
    for nome in p.lotes():
        _, _, _, _, validas = _quieto(p, nome, regras)
        for k, pt in validas.items():
            item = indice.get(nome, {}).get(k)
            if not item:
                continue
            for alvo in item["alvos"]:
                if banco.get(alvo) != [item["en"], pt]:
                    banco[alvo] = [item["en"], pt]
                    novos += 1
    salvar_json(traducoes_path(p), banco, indent=0)
    return banco, novos


def _quieto(p, nome, regras):
    with contextlib.redirect_stdout(io.StringIO()):
        return validar_lote(p, nome, regras, mostrar_avisos=False)


def preparar(p, forcar=False):
    """Extrai do jogo e recria chunks/. Traduções já consolidadas com o mesmo inglês são mantidas."""
    if p.lotes() and not forcar:
        banco, novos = consolidar(p)
        print(f"Saídas atuais consolidadas em src/traducoes.json ({novos} novas).")
    banco = carregar_json(traducoes_path(p), {})

    unidades = p.engine().extrair()
    pendentes = [u for u in unidades if u["traduzir"]
                 and not all(banco.get(a, [None])[0] == u["en"] for a in u["alvos"])]
    limite = p.cfg["lote_max_chars"]

    for d in (p.chunks, p.out):
        if os.path.isdir(d):
            shutil.rmtree(d)
    os.makedirs(p.chunks)
    os.makedirs(p.out)

    indice = {}
    for cat in ORDEM_CAT:
        grupos, atual = [], None
        for u in (u for u in pendentes if u["cat"] == cat):
            chave = u["grupo"] or id(u)
            if atual is None or atual[0] != chave:
                atual = (chave, [])
                grupos.append(atual)
            atual[1].append(u)

        lotes, cur, tam = [], [], 0
        for _, us in grupos:
            g_tam = sum(len(u["en"]) for u in us)
            if cur and tam + g_tam > limite:
                lotes.append(cur)
                cur, tam = [], 0
            for i, u in enumerate(us):
                if cur and tam + len(u["en"]) > limite and tam >= limite // 2:
                    lotes.append(cur)
                    cur, tam = [], 0
                cur.append((u, i == 0 or not cur))
                tam += len(u["en"])
        if cur:
            lotes.append(cur)

        for n, itens in enumerate(lotes):
            nome = f"{cat}_{n:03d}"
            chunk, idx = [], {}
            for k, (u, inicio) in enumerate(itens, 1):
                item = {"k": str(k)}
                if inicio and u["cena"]:
                    item["cena"] = u["cena"]
                if u["quem"]:
                    item["quem"] = u["quem"]
                if u["tipo"] not in ("fala", "ui"):
                    item["tipo"] = u["tipo"]
                item["en"] = u["en"]
                chunk.append(item)
                idx[str(k)] = {"en": u["en"], "alvos": u["alvos"]}
            salvar_json(os.path.join(p.chunks, nome + ".json"), chunk)
            indice[nome] = idx

    salvar_json(p.indice_path, indice, indent=0)
    total = len([u for u in unidades if u["traduzir"]])
    salvar_json(p.caminho("src", "resumo.json"), {"para_traduzir": total, "ja_traduzidas": total - len(pendentes)})
    print(f"Unidades: {len(unidades)} ({total} para traduzir, {total - len(pendentes)} já traduzidas).")
    for cat in ORDEM_CAT:
        ls = [n for n in indice if n.startswith(cat)]
        if ls:
            print(f"  {cat}: {len(ls)} lotes, {sum(len(indice[n]) for n in ls)} textos")


def status(p, detalhe=False):
    regras = Regras(p.cfg["validacao"])
    tot = feitos = com_erro = sem_saida = 0
    pendentes = []
    for nome in p.lotes():
        n, ok, erros, _, _ = _quieto(p, nome, regras)
        tot += n
        feitos += ok
        if not os.path.isfile(os.path.join(p.out, nome + ".json")):
            sem_saida += 1
            pendentes.append(nome)
        elif erros:
            com_erro += 1
            pendentes.append(nome)
        if detalhe:
            print(f"{nome}: {ok}/{n}" + (f"  {erros} erros" if erros else ""))
    resumo = carregar_json(p.caminho("src", "resumo.json"), {})
    geral, antes = resumo.get("para_traduzir", tot), resumo.get("ja_traduzidas", 0)
    pct = 100 * (antes + feitos) / geral if geral else 0
    print(f"{p.slug}: {antes + feitos}/{geral} textos ({pct:.1f}%) | nos lotes atuais: {feitos}/{tot} | "
          f"lotes: {len(p.lotes())}, sem saída: {sem_saida}, com erro: {com_erro}")
    return pendentes
