"""Montagem: consolida out/ -> src/traducoes.json, gera os arquivos do jogo e empacota com os instaladores genéricos."""
import os
import shutil
import sys

from kit.lotes import consolidar
from kit.util import REPO, salvar_json
from kit.validar import Regras, analisar_lote

sys.path.insert(0, os.path.join(REPO, "projetos"))
from empacotar import empacotar, empacotar_linux  # noqa: E402

INSTALADOR = os.path.join(REPO, "kit", "instalador.py")


def verificar(p):
    """Problemas que impedem o pacote final: lotes sem saída, com erro ou com JSON inválido."""
    regras = Regras(p.cfg["validacao"])
    problemas = []
    for nome in p.lotes():
        chunk, out, probs, validas = analisar_lote(p, nome, regras)
        n = sum(1 for it in chunk if "k" in it)
        if out is None:
            problemas.append(f"{nome}: sem saída ({n} textos)")
        elif len(validas) < n or any(pr["erros"] for pr in probs):
            problemas.append(f"{nome}: {n - len(validas)} de {n} textos sem tradução válida")
    return problemas


def montar(p, json_only=False, steam_build=None, so_linux=False, parcial=False):
    if not json_only and not parcial:
        problemas = verificar(p)
        if problemas:
            print("\n".join(problemas[:20]))
            raise SystemExit(f"Pacote final bloqueado: {len(problemas)} lotes incompletos. "
                             "Use 'correcoes'/'aplicar' ou 'montar --parcial' para um pacote de teste.")
    banco, novos = consolidar(p)
    print(f"Traduções consolidadas: {len(banco)} destinos ({novos} novos/alterados).")
    if parcial or json_only:
        faltam = len(verificar(p))
        if faltam:
            print(f"Montagem parcial: {faltam} lotes incompletos; esses textos ficam em inglês.")
    pacote = p.caminho("build", "pacote")
    shutil.rmtree(pacote, ignore_errors=True)
    arquivos = p.engine().montar(banco, os.path.join(pacote, "arquivos"))
    if json_only:
        return arquivos

    cfg = p.cfg
    build = steam_build or cfg["steam_build"]
    app = "Traducao_PTBR_" + cfg["nome"].replace(" ", "_")
    marcador = p.engine().arquivo_de_verificacao().replace("\\", "/")
    aviso = cfg.get("aviso_pos_instalacao", "")
    if not so_linux:
        salvar_json(os.path.join(pacote, "pacote.json"), {
            "jogo": cfg["nome"], "pasta_steam": cfg["pasta_steam"], "versao": cfg["versao"],
            "verificar": marcador, "aviso": aviso,
            "arquivos": [{"origem": "arquivos/" + os.path.basename(a), "destino": rel} for a, rel in arquivos],
        })
        empacotar(p.root, app, cfg["nome"], cfg["versao"], [], [
            (INSTALADOR, "instalador.py"),
            (os.path.join(REPO, "kit", "engines", cfg["engine"] + ".py"), cfg["engine"] + ".py"),
        ], f"{app}_v{cfg['versao']}.zip", build,
            script=INSTALADOR, dados_extra=[(os.path.join(pacote, "pacote.json"), "."),
                                             (os.path.join(pacote, "arquivos"), "arquivos")])
    nomes = ["arquivos/" + os.path.basename(a) for a, _ in arquivos]
    return empacotar_linux(
        p.root, app, cfg["nome"], cfg["versao"],
        {"PASTA_STEAM": cfg["pasta_steam"], "VERIFICAR": marcador, "AVISO": aviso},
        [(a, n) for (a, _), n in zip(arquivos, nomes)],
        f"{app}_v{cfg['versao']}_SteamDeck-Linux.zip", build,
        lista=[(n, rel.replace(os.sep, "/")) for n, (_, rel) in zip(nomes, arquivos)])
