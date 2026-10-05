"""Métricas de tokens por etapa.

O kit não vê o consumo real do Cursor (cada chamada de ferramenta do agente reenvia o contexto inteiro),
mas mede o material que cada etapa entrega ao agente. Cada `prompt` registra uma linha em
work/metricas.jsonl; `metricas` resume esse histórico e mede os lotes atuais.
"""
import collections
import datetime
import json
import os

from kit.util import carregar_json, tokens


def _log(p):
    return os.path.join(p.work, "metricas.jsonl")


def registrar(p, tipo, nomes, **medidas):
    os.makedirs(p.work, exist_ok=True)
    linha = {"quando": datetime.datetime.now().isoformat(timespec="seconds"), "tipo": tipo, "pacotes": nomes, **medidas}
    with open(_log(p), "a", encoding="utf-8") as f:
        f.write(json.dumps(linha, ensure_ascii=False) + "\n")


def medir_lote(p, nome):
    """Tokens do arquivo do lote, separados em texto a traduzir, referência e estrutura."""
    path = os.path.join(p.chunks, nome + ".json")
    bruto = open(path, encoding="utf-8").read()
    itens = carregar_json(path, [])
    texto = sum(tokens(it["en"]) for it in itens if "k" in it)
    ref = sum(tokens(it["en"]) + tokens(it.get("pt", "")) for it in itens if "k" not in it)
    rascunho = sum(tokens(it.get("rascunho", "")) for it in itens)
    total = tokens(bruto)
    return {"total": total, "texto": texto, "referencia": ref, "rascunho": rascunho,
            "estrutura": total - texto - ref - rascunho}


def resumo(p):
    soma = collections.Counter()
    for nome in p.lotes():
        soma.update(medir_lote(p, nome))
    print(f"Lotes atuais ({len(p.lotes())}): {soma['total']} tokens de entrada")
    for chave in ("texto", "referencia", "rascunho", "estrutura"):
        pct = 100 * soma[chave] / soma["total"] if soma["total"] else 0
        print(f"  {chave:<11} {soma[chave]:>9}  ({pct:.0f}%)")
    if not os.path.isfile(_log(p)):
        print("Sem histórico de prompts (work/metricas.jsonl).")
        return
    por_tipo = collections.defaultdict(collections.Counter)
    for linha in open(_log(p), encoding="utf-8"):
        m = json.loads(linha)
        c = por_tipo[m["tipo"]]
        c["agentes"] += 1
        c["pacotes"] += len(m["pacotes"])
        for k, v in m.items():
            if isinstance(v, int):
                c[k] += v
    for tipo, c in por_tipo.items():
        print(f"{tipo}: {c['agentes']} agentes, {c['pacotes']} pacotes | itens {c['tokens_itens']} | "
              f"contexto {c['tokens_contexto']} (guia inteiro seria {c['tokens_guia_inteiro']})")
    print("Para o custo real, compare o painel do Cursor por onda com estes números: "
          "cada chamada de ferramenta do agente reenvia contexto + itens já lidos.")
