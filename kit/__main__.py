"""Kit de tradução DangoHub.

    python -m kit detectar "<pasta do jogo>"
    python -m kit preparar <jogo> [--forcar]
    python -m kit status <jogo> [--detalhe]
    python -m kit proximos <jogo> [-n 6]
    python -m kit prompt <jogo> <lote> [<lote> ...]
    python -m kit validar <jogo> [<lote> ...]
    python -m kit montar <jogo> [--json-only] [--steam-build=N]
    python -m kit instalar-teste <jogo>
    python -m kit termos <jogo> [-n 150]
    python -m kit amostra <jogo> <lote> [-n 30] [--de 0]
    python -m kit termos-check <jogo>     (glossario.json "termos")
    python -m kit padronizar <jogo>       (glossario.json "trocas")
"""
import argparse
import json
import os
import shutil
import sys

from kit import montagem
from kit.consistencia import checar_termos, padronizar
from kit.detectar import detectar
from kit.lotes import preparar, status
from kit.projeto import Projeto
from kit.termos import termos
from kit.util import REPO, carregar_json
from kit.validar import Regras, validar_lote

PROMPT = """Você é tradutor(a) de jogos para português do Brasil. Traduza os lotes abaixo do jogo {jogo}.

Leia, nesta ordem e uma única vez:
1. {agente}  (regras gerais e formato; obrigatório)
2. {guia}  (tom, personagens e glossário deste jogo)

Para cada lote:
- entrada: {chunks}\\<lote>.json
- saída:   {out}\\<lote>.json   (objeto JSON {{"k": "tradução"}} com TODAS as chaves do lote)
- depois de gravar, rode: python -m kit validar {slug} <lote>   (na pasta {repo})
  e corrija até aparecer "0 erros". Avisos são para você conferir, não bloqueiam.

Lotes: {lotes}

Não leia outros arquivos do repositório nem a pasta do jogo. Ao terminar, responda só com uma linha por lote:
"<lote>: N textos, 0 erros" e, se houver, dúvidas de glossário (máximo 5 linhas)."""


def main(argv):
    ap = argparse.ArgumentParser(prog="python -m kit")
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("detectar"); a.add_argument("pasta")
    a = sub.add_parser("preparar"); a.add_argument("jogo"); a.add_argument("--forcar", action="store_true")
    a = sub.add_parser("status"); a.add_argument("jogo"); a.add_argument("--detalhe", action="store_true")
    a = sub.add_parser("proximos"); a.add_argument("jogo"); a.add_argument("-n", type=int, default=6)
    a = sub.add_parser("prompt"); a.add_argument("jogo"); a.add_argument("lotes", nargs="+")
    a = sub.add_parser("validar"); a.add_argument("jogo"); a.add_argument("lotes", nargs="*")
    a = sub.add_parser("montar"); a.add_argument("jogo"); a.add_argument("--json-only", action="store_true")
    a.add_argument("--steam-build", default=None)
    a = sub.add_parser("instalar-teste"); a.add_argument("jogo")
    a = sub.add_parser("termos"); a.add_argument("jogo"); a.add_argument("-n", type=int, default=150)
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
        preparar(p, args.forcar)
    elif args.cmd == "status":
        status(p, args.detalhe)
    elif args.cmd == "proximos":
        print("\n".join(status(p)[:args.n]))
    elif args.cmd == "prompt":
        print(PROMPT.format(jogo=p.cfg["nome"], slug=p.slug, repo=REPO, lotes=", ".join(args.lotes),
                            agente=os.path.join(REPO, "kit", "AGENTE.md"), guia=p.caminho("GUIA_TRADUCAO.md"),
                            chunks=p.chunks, out=p.out))
    elif args.cmd == "validar":
        regras = Regras(p.cfg["validacao"])
        nomes = args.lotes or [n for n in p.lotes() if os.path.isfile(os.path.join(p.out, n + ".json"))]
        total = 0
        for nome in nomes:
            n, ok, erros, avisos, _ = validar_lote(p, nome, regras)
            print(f"{nome}: {ok}/{n} traduzidos, {erros} erros, {avisos} avisos")
            total += erros
        return 1 if total else 0
    elif args.cmd == "montar":
        montagem.montar(p, json_only=args.json_only, steam_build=args.steam_build)
    elif args.cmd == "termos":
        termos(p, args.n)
    elif args.cmd == "padronizar":
        padronizar(p)
    elif args.cmd == "termos-check":
        checar_termos(p)
    elif args.cmd == "amostra":
        chunk = carregar_json(os.path.join(p.chunks, args.lote + ".json"), [])
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
