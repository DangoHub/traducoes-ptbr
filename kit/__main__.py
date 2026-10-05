"""Kit de tradução DangoHub.

    python -m kit detectar "<pasta do jogo>"
    python -m kit preparar <jogo>
    python -m kit status <jogo> [--detalhe]
    python -m kit proximos <jogo> [-n 6]
    python -m kit prompt <jogo> <lote|correcao_NNN> [...]
    python -m kit validar <jogo> [<lote> ...]
    python -m kit correcoes <jogo> [--avisos]
    python -m kit aplicar <jogo> <correcao_NNN> [...]
    python -m kit verificar <jogo>
    python -m kit metricas <jogo>
    python -m kit montar <jogo> [--parcial] [--json-only] [--so-linux] [--steam-build=N]
    python -m kit instalar-teste <jogo>
    python -m kit termos <jogo> [-n 150]
    python -m kit amostra <jogo> <lote> [-n 30] [--de 0]
    python -m kit buscar <jogo> "<texto>" [-n 20]
    python -m kit termos-check <jogo>     (glossario.json "termos")
    python -m kit padronizar <jogo>       (glossario.json "trocas")
"""
import argparse
import json
import os
import shutil
import sys

from kit import correcoes, metricas, montagem
from kit.consistencia import buscar, checar_termos, padronizar
from kit.contexto import montar_contexto
from kit.detectar import detectar
from kit.lotes import preparar, status
from kit.projeto import Projeto
from kit.termos import termos
from kit.util import REPO, carregar_json, tokens
from kit.validar import Regras, carregar_revisados, validar_lote

PROMPT = """Você é tradutor(a) de jogos para português do Brasil. Traduza os lotes abaixo do jogo {jogo}.

1. Numa única rodada de chamadas paralelas, leia:
   - {contexto}  (regras, formato e o guia deste pacote)
{leituras}
2. Numa única rodada de chamadas paralelas, grave cada saída inteira de uma vez:
{gravacoes}
   Cada saída é um objeto JSON {{"k": "tradução"}} com as chaves "k" do lote. Itens sem "k" são referência: não devolva.
3. Rode uma vez, na pasta {repo}:  python -m kit validar {slug} {lotes}
   Se houver ERRO, corrija só os itens apontados (edição pontual, sem regravar o arquivo) e rode mais uma vez.
   O que ainda sobrar vira pacote de correção; não insista. Avisos não exigem ação.

Não leia outros arquivos, não explore o repositório e não use lista de tarefas.
Ao terminar, responda só uma linha por lote: "<lote>: N textos, E erros" e, se houver, dúvidas de glossário (máximo 5 linhas)."""

PROMPT_CORRECAO = """Você revisa traduções para português do Brasil do jogo {jogo}.

1. Numa única rodada de chamadas paralelas, leia:
   - {contexto}  (regras e o guia deste pacote)
{leituras}
2. Cada item traz id, motivo, original (en), tradução atual (pt) e falas vizinhas. Numa única rodada de chamadas
   paralelas, grave para cada pacote um objeto JSON {{"<id>": "texto"}} com todos os ids:
{gravacoes}
   problema "erro": devolva a tradução corrigida.
   problema "aviso": devolva "=" se a tradução atual estiver certa ou a nova tradução se não estiver.
3. Rode uma vez, na pasta {repo}:  python -m kit aplicar {slug} {lotes}

Não leia outros arquivos e não use lista de tarefas. Ao terminar, responda só com a linha que o comando aplicar imprimir."""


def _prompt(p, nomes):
    corr = [n for n in nomes if n.startswith("correcao_")]
    if corr and len(corr) != len(nomes):
        raise SystemExit("Não misture lotes e pacotes de correção no mesmo prompt.")
    if corr:
        d = correcoes.pasta(p)
        itens = [it for n in nomes for it in correcoes.itens_do_pacote(p, n)]
        entradas = [os.path.join(d, n + ".json") for n in nomes]
        saidas = [os.path.join(d, n + ".saida.json") for n in nomes]
        modelo = PROMPT_CORRECAO
    else:
        itens = [it for n in nomes for it in carregar_json(os.path.join(p.chunks, n + ".json"), [])]
        entradas = [os.path.join(p.chunks, n + ".json") for n in nomes]
        saidas = [os.path.join(p.out, n + ".json") for n in nomes]
        modelo = PROMPT
    if not itens:
        raise SystemExit(f"Nada encontrado para: {', '.join(nomes)}")
    path, guia_inteiro, contexto = montar_contexto(p, nomes, itens)
    metricas.registrar(p, "correcao" if corr else "traducao", nomes,
                       tokens_itens=sum(tokens(open(e, encoding="utf-8").read()) for e in entradas),
                       tokens_contexto=tokens(contexto), tokens_guia_inteiro=tokens(guia_inteiro))
    return modelo.format(jogo=p.cfg["nome"], slug=p.slug, repo=REPO, lotes=" ".join(nomes), contexto=path,
                         leituras="\n".join(f"   - {e}" for e in entradas),
                         gravacoes="\n".join(f"   - {s}" for s in saidas))


def main(argv):
    ap = argparse.ArgumentParser(prog="python -m kit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("detectar"); a.add_argument("pasta")
    a = sub.add_parser("preparar"); a.add_argument("jogo")
    a = sub.add_parser("status"); a.add_argument("jogo"); a.add_argument("--detalhe", action="store_true")
    a = sub.add_parser("proximos"); a.add_argument("jogo"); a.add_argument("-n", type=int, default=6)
    a = sub.add_parser("prompt"); a.add_argument("jogo"); a.add_argument("lotes", nargs="+")
    a = sub.add_parser("validar"); a.add_argument("jogo"); a.add_argument("lotes", nargs="*")
    a = sub.add_parser("correcoes"); a.add_argument("jogo")
    a.add_argument("--avisos", action="store_true", help="inclui avisos ainda não revisados")
    a = sub.add_parser("aplicar"); a.add_argument("jogo"); a.add_argument("pacotes", nargs="+")
    a = sub.add_parser("verificar"); a.add_argument("jogo")
    a = sub.add_parser("metricas"); a.add_argument("jogo")
    a = sub.add_parser("montar"); a.add_argument("jogo"); a.add_argument("--json-only", action="store_true")
    a.add_argument("--parcial", action="store_true", help="monta mesmo com lotes incompletos (só para teste)")
    a.add_argument("--steam-build", default=None)
    a.add_argument("--so-linux", action="store_true", help="só o zip do Steam Deck/Linux (sem PyInstaller)")
    a = sub.add_parser("instalar-teste"); a.add_argument("jogo")
    a = sub.add_parser("termos"); a.add_argument("jogo"); a.add_argument("-n", type=int, default=150)
    a = sub.add_parser("buscar"); a.add_argument("jogo"); a.add_argument("texto"); a.add_argument("-n", type=int, default=20)
    a = sub.add_parser("padronizar"); a.add_argument("jogo")
    a = sub.add_parser("termos-check"); a.add_argument("jogo")
    a = sub.add_parser("amostra"); a.add_argument("jogo"); a.add_argument("lote")
    a.add_argument("-n", type=int, default=30); a.add_argument("--de", type=int, default=0)
    args = ap.parse_args(argv)

    if args.cmd == "detectar":
        print(json.dumps(detectar(args.pasta), ensure_ascii=False, indent=1))
        return 0

    p = Projeto(args.jogo)
    if args.cmd == "preparar":
        preparar(p)
    elif args.cmd == "status":
        status(p, args.detalhe)
    elif args.cmd == "proximos":
        print("\n".join(status(p)[:args.n]))
    elif args.cmd == "prompt":
        print(_prompt(p, args.lotes))
    elif args.cmd == "validar":
        regras = Regras(p.cfg["validacao"])
        revisados = carregar_revisados(p)
        nomes = args.lotes or [n for n in p.lotes() if os.path.isfile(os.path.join(p.out, n + ".json"))]
        total = 0
        for nome in nomes:
            n, ok, erros, avisos, _ = validar_lote(p, nome, regras, revisados=revisados)
            print(f"{nome}: {ok}/{n} traduzidos, {erros} erros, {avisos} avisos")
            total += erros
        return 1 if total else 0
    elif args.cmd == "correcoes":
        correcoes.gerar(p, avisos=args.avisos)
    elif args.cmd == "aplicar":
        ok = [correcoes.aplicar(p, n) for n in args.pacotes]
        return 0 if all(ok) else 1
    elif args.cmd == "verificar":
        problemas = montagem.verificar(p)
        print("\n".join(problemas) if problemas else "Pronto para o pacote final: todos os lotes completos e sem erros.")
        return 1 if problemas else 0
    elif args.cmd == "metricas":
        metricas.resumo(p)
    elif args.cmd == "montar":
        montagem.montar(p, json_only=args.json_only, steam_build=args.steam_build, so_linux=args.so_linux,
                        parcial=args.parcial)
    elif args.cmd == "termos":
        termos(p, args.n)
    elif args.cmd == "buscar":
        buscar(p, args.texto, args.n)
    elif args.cmd == "padronizar":
        padronizar(p)
    elif args.cmd == "termos-check":
        checar_termos(p)
    elif args.cmd == "amostra":
        chunk = [it for it in carregar_json(os.path.join(p.chunks, args.lote + ".json"), []) if "k" in it]
        out = carregar_json(os.path.join(p.out, args.lote + ".json"), {})
        for it in chunk[args.de:args.de + args.n]:
            if it.get("cena"):
                print(f"== {it['cena']}")
            print(f"[{it['k']}] {it.get('quem') or it.get('tipo', '')}: {it['en']}\n     -> {out.get(it['k'], '(sem tradução)')}")
    elif args.cmd == "instalar-teste":
        for arq, rel in montagem.montar(p, json_only=True):
            dest = os.path.join(p.pasta_jogo, rel)
            shutil.copyfile(arq, dest)
            print("copiado:", dest)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
