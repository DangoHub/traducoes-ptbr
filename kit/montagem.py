"""Montagem: consolida out/ -> src/traducoes.json, gera os arquivos do jogo e empacota com o instalador genérico."""
import os
import shutil
import sys

from kit.lotes import consolidar
from kit.util import REPO, salvar_json

sys.path.insert(0, os.path.join(REPO, "projetos"))
from empacotar import empacotar  # noqa: E402

INSTALADOR = os.path.join(REPO, "kit", "instalador.py")


def montar(p, json_only=False, steam_build=None):
    banco, novos = consolidar(p)
    print(f"Traduções consolidadas: {len(banco)} destinos ({novos} novos/alterados).")
    pacote = p.caminho("build", "pacote")
    shutil.rmtree(pacote, ignore_errors=True)
    arquivos = p.engine().montar({a: v[1] for a, v in banco.items()}, os.path.join(pacote, "arquivos"))
    if json_only:
        return arquivos

    cfg = p.cfg
    salvar_json(os.path.join(pacote, "pacote.json"), {
        "jogo": cfg["nome"], "pasta_steam": cfg["pasta_steam"], "versao": cfg["versao"],
        "verificar": p.engine().arquivo_de_verificacao().replace("\\", "/"),
        "aviso": cfg.get("aviso_pos_instalacao", ""),
        "arquivos": [{"origem": "arquivos/" + os.path.basename(a), "destino": rel} for a, rel in arquivos],
    })
    app = "Traducao_PTBR_" + cfg["nome"].replace(" ", "_")
    return empacotar(p.root, app, cfg["nome"], cfg["versao"], [], [
        (INSTALADOR, "instalador.py"),
        (os.path.join(REPO, "kit", "engines", cfg["engine"] + ".py"), cfg["engine"] + ".py"),
    ], f"{app}_v{cfg['versao']}.zip", steam_build or cfg["steam_build"],
        script=INSTALADOR, dados_extra=[(os.path.join(pacote, "pacote.json"), "."),
                                         (os.path.join(pacote, "arquivos"), "arquivos")])
