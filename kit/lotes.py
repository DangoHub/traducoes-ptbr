"""Lotes: divide as unidades por conversa, consolida traduções e mostra o progresso.

Estados de um texto:
    pendente   está num lote e ainda não tem saída
    com erro   tem saída que não passa na validação (guardada em src/rascunhos.json ao repreparar)
    validado   passou na validação e está em src/traducoes.json
    revisado   aviso conferido e registrado em src/revisao.json
"""
import datetime
import os
import shutil

from kit.util import carregar_json, salvar_itens, salvar_json
from kit.validar import Regras, analisar_lote, carregar_revisados

ORDEM_CAT = ("dialogo", "textos", "interface")
REF_ANTES, REF_DEPOIS = 3, 1


def traducoes_path(p):
    return p.caminho("src", "traducoes.json")


def rascunhos_path(p):
    return p.caminho("src", "rascunhos.json")


def consolidar(p):
    """Junta as saídas válidas de out/ em src/traducoes.json ({alvo: [en, pt]}) e devolve o dicionário.

    Saídas que não passam na validação vão para src/rascunhos.json, para não se perderem.
    """
    banco = carregar_json(traducoes_path(p), {})
    rascunhos = carregar_json(rascunhos_path(p), {})
    indice = carregar_json(p.indice_path, {})
    regras = Regras(p.cfg["validacao"])
    novos = 0
    for nome in p.lotes():
        _, out, problemas, validas = analisar_lote(p, nome, regras)
        if not isinstance(out, dict):
            continue
        erros = {pr["k"]: pr["erros"] for pr in problemas if pr["erros"]}
        for k, item in indice.get(nome, {}).items():
            for alvo in item["alvos"]:
                if k in validas:
                    rascunhos.pop(alvo, None)
                    if banco.get(alvo) != [item["en"], validas[k]]:
                        banco[alvo] = [item["en"], validas[k]]
                        novos += 1
                elif isinstance(out.get(k), str) and out[k].strip():
                    rascunhos[alvo] = {"en": item["en"], "pt": out[k], "erros": erros.get(k, [])}
    salvar_json(traducoes_path(p), banco, indent=0)
    salvar_json(rascunhos_path(p), rascunhos, indent=0)
    return banco, novos


def _arquivar(p):
    """Copia chunks/, out/ e o índice atuais para work/historico/<data>/ antes de recriar os lotes."""
    destino = os.path.join(p.work, "historico", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
    for origem in (p.chunks, p.out):
        if os.path.isdir(origem):
            shutil.copytree(origem, os.path.join(destino, os.path.basename(origem)))
    if os.path.isfile(p.indice_path):
        shutil.copyfile(p.indice_path, os.path.join(destino, "indice.json"))
    return destino


def _grupos(unidades):
    grupos, atual = [], None
    for u in unidades:
        chave = u["grupo"] or id(u)
        if atual is None or atual[0] != chave:
            atual = (chave, [])
            grupos.append(atual)
        atual[1].append(u)
    return [us for _, us in grupos]


def _trecho(us, feita):
    """Itens de um grupo que vão para o lote: [(unidade, é_referência)].

    Grupo todo pendente: vai inteiro. Só parte pendente: vão as pendentes e, como referência,
    até REF_ANTES falas aprovadas antes e REF_DEPOIS depois de cada uma.
    """
    pend = [i for i, u in enumerate(us) if not feita(u)]
    if not pend:
        return []
    if len(pend) == len(us):
        return [(u, False) for u in us]
    incluir = set()
    for i in pend:
        incluir.update(range(max(0, i - REF_ANTES), min(len(us), i + REF_DEPOIS + 1)))
    return [(us[i], feita(us[i])) for i in sorted(incluir)]


def _dividir(trechos, limite, peso):
    lotes, cur, tam = [], [], 0
    for itens in trechos:
        g_tam = sum(peso(u, ref) for u, ref in itens)
        if cur and tam + g_tam > limite:
            lotes.append(cur)
            cur, tam = [], 0
        for i, (u, ref) in enumerate(itens):
            if cur and tam + peso(u, ref) > limite and tam >= limite // 2:
                lotes.append(cur)
                cur, tam = [], 0
            cur.append((u, ref, i == 0 or not cur))
            tam += peso(u, ref)
    if cur:
        lotes.append(cur)
    return [lote for lote in lotes if any(not ref for _, ref, _ in lote)]


def preparar(p):
    """Extrai do jogo e recria chunks/ e out/ sem perder trabalho.

    Antes: consolida as saídas (válidas no banco, inválidas em rascunhos) e arquiva os lotes atuais.
    Textos com o mesmo inglês já validado não voltam; rascunhos voltam junto do item para correção.
    """
    if p.lotes():
        _, novos = consolidar(p)
        print(f"Saídas atuais consolidadas ({novos} novas); lotes anteriores arquivados em {_arquivar(p)}")
    banco = carregar_json(traducoes_path(p), {})
    rascunhos = carregar_json(rascunhos_path(p), {})

    unidades = [u for u in p.engine().extrair() if u["traduzir"]]

    def feita(u):
        return all(banco.get(a, [None])[0] == u["en"] for a in u["alvos"])

    def peso(u, ref):
        return len(u["en"]) + (len(banco[u["alvos"][0]][1]) if ref else 0)

    for d in (p.chunks, p.out):
        shutil.rmtree(d, ignore_errors=True)
        os.makedirs(d)

    indice, refs, com_rascunho = {}, 0, 0
    vivos = set()
    for cat in ORDEM_CAT:
        trechos = [t for us in _grupos([u for u in unidades if u["cat"] == cat]) if (t := _trecho(us, feita))]
        for n, itens in enumerate(_dividir(trechos, p.cfg["lote_max_chars"], peso)):
            nome = f"{cat}_{n:03d}"
            chunk, idx = [], {}
            for u, ref, inicio in itens:
                item = {} if ref else {"k": str(len(idx) + 1)}
                if inicio and u["cena"]:
                    item["cena"] = u["cena"]
                if u["quem"]:
                    item["quem"] = u["quem"]
                if u["tipo"] not in ("fala", "ui"):
                    item["tipo"] = u["tipo"]
                item["en"] = u["en"]
                if ref:
                    item["pt"] = banco[u["alvos"][0]][1]
                    refs += 1
                else:
                    r = rascunhos.get(u["alvos"][0])
                    if r and r["en"] == u["en"]:
                        item["rascunho"] = r["pt"]
                        if r["erros"]:
                            item["erro"] = "; ".join(r["erros"])
                        com_rascunho += 1
                    idx[item["k"]] = {"en": u["en"], "alvos": u["alvos"]}
                    vivos.update(u["alvos"])
                chunk.append(item)
            salvar_itens(os.path.join(p.chunks, nome + ".json"), chunk)
            indice[nome] = idx

    salvar_json(rascunhos_path(p), {a: r for a, r in rascunhos.items() if a in vivos}, indent=0)
    salvar_json(p.indice_path, indice, indent=0)
    pendentes = sum(len(i) for i in indice.values())
    total = len(unidades)
    ja = sum(1 for u in unidades if feita(u))
    salvar_json(p.caminho("src", "resumo.json"), {"para_traduzir": total, "ja_traduzidas": ja})
    print(f"Unidades para traduzir: {total} ({ja} já validadas, {pendentes} nos lotes, "
          f"{refs} falas de referência, {com_rascunho} com rascunho a corrigir).")
    for cat in ORDEM_CAT:
        ls = [n for n in indice if n.startswith(cat)]
        if ls:
            print(f"  {cat}: {len(ls)} lotes, {sum(len(indice[n]) for n in ls)} textos")


def status(p, detalhe=False):
    regras = Regras(p.cfg["validacao"])
    revisados = carregar_revisados(p)
    tot = feitos = com_erro = sem_saida = itens_erro = avisos = 0
    pendentes = []
    for nome in p.lotes():
        chunk, out, problemas, validas = analisar_lote(p, nome, regras, revisados)
        n = sum(1 for it in chunk if "k" in it)
        erros = sum(len(pr["erros"]) for pr in problemas)
        tot += n
        feitos += len(validas)
        avisos += sum(len(pr["avisos"]) for pr in problemas)
        if out is None:
            sem_saida += 1
            pendentes.append(nome)
        elif erros:
            com_erro += 1
            itens_erro += sum(1 for pr in problemas if pr["erros"] and pr["k"])
            pendentes.append(nome)
        if detalhe:
            print(f"{nome}: {len(validas)}/{n}" + (f"  {erros} erros" if erros else ""))
    resumo = carregar_json(p.caminho("src", "resumo.json"), {})
    geral, antes = resumo.get("para_traduzir", tot), resumo.get("ja_traduzidas", 0)
    pct = 100 * (antes + feitos) / geral if geral else 0
    print(f"{p.slug}: {antes + feitos}/{geral} textos ({pct:.1f}%) | lotes: {len(p.lotes())}, "
          f"sem saída: {sem_saida}, com erro: {com_erro}")
    print(f"  validados: {antes + feitos} | com erro: {itens_erro} | pendentes: {tot - feitos - itens_erro} | "
          f"avisos a revisar: {avisos} | revisados: {len(revisados)}")
    return pendentes
