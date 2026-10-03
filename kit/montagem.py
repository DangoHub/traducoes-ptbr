"""Montagem: consolida out/ -> src/traducoes.json, gera os arquivos do jogo e empacota com os instaladores genéricos."""
import os
import shlex
import shutil
import sys
import zipfile

from kit.lotes import consolidar
from kit.util import REPO, salvar_json

sys.path.insert(0, os.path.join(REPO, "projetos"))
from empacotar import empacotar  # noqa: E402

INSTALADOR = os.path.join(REPO, "kit", "instalador.py")
INSTALADOR_LINUX = os.path.join(REPO, "kit", "instalador_linux.sh")

LEIA_ME_LINUX = """Tradução PT-BR de {jogo} v{versao} - DangoHub
Instalação no Steam Deck / Linux
================================

1. No Steam Deck, entre no Modo Desktop (botão Steam > Ligar/Desligar > Mudar para a área de trabalho).
2. Extraia este .zip (clique com o botão direito > Extrair > Extrair aqui).
3. Abra a pasta extraída e dê dois cliques em "Instalar.sh" e escolha "Executar".
   Se abrir como texto: botão direito em "Instalar.sh" > "Executar no Konsole".
4. Escolha "Instalar / atualizar a tradução". O jogo é localizado sozinho
   (memória interna ou cartão SD); se não for, selecione a pasta do jogo.
5. Volte ao Modo de Jogo.

{aviso}

Para remover: rode "Instalar.sh" de novo e escolha "Desinstalar" (os arquivos originais são restaurados).

Pelo terminal: ./Instalar.sh --install | --uninstall | --status  [pasta do jogo]
"""


def _escrever_lf(z, origem, nome):
    with open(origem, encoding="utf-8") as f:
        texto = f.read().replace("\r\n", "\n")
    info = zipfile.ZipInfo(nome)
    info.create_system = 3
    info.external_attr = 0o100755 << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(info, texto.encode("utf-8"))


def empacotar_linux(p, arquivos, release):
    cfg = p.cfg
    app = "Traducao_PTBR_" + cfg["nome"].replace(" ", "_")
    conf = {
        "JOGO": cfg["nome"], "PASTA_STEAM": cfg["pasta_steam"], "VERSAO": cfg["versao"],
        "VERIFICAR": p.engine().arquivo_de_verificacao().replace("\\", "/"),
        "AVISO": cfg.get("aviso_pos_instalacao", ""),
    }
    os.makedirs(release, exist_ok=True)
    zpath = os.path.join(release, f"{app}_v{cfg['versao']}_SteamDeck-Linux.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        _escrever_lf(z, INSTALADOR_LINUX, f"{app}/Instalar.sh")
        z.writestr(f"{app}/pacote.conf", "".join(f"{k}={shlex.quote(v)}\n" for k, v in conf.items()))
        z.writestr(f"{app}/arquivos.lst",
                   "".join(f"arquivos/{os.path.basename(a)}\t{rel.replace(os.sep, '/')}\n" for a, rel in arquivos))
        for a, _ in arquivos:
            z.write(a, f"{app}/arquivos/{os.path.basename(a)}")
        z.writestr(f"{app}/LEIA-ME.txt", LEIA_ME_LINUX.format(
            jogo=cfg["nome"], versao=cfg["versao"], aviso=conf["AVISO"]))
    print("OK:", zpath, os.path.getsize(zpath) // 1024, "KB")
    return zpath


def montar(p, json_only=False, steam_build=None, so_linux=False):
    banco, novos = consolidar(p)
    print(f"Traduções consolidadas: {len(banco)} destinos ({novos} novos/alterados).")
    pacote = p.caminho("build", "pacote")
    shutil.rmtree(pacote, ignore_errors=True)
    arquivos = p.engine().montar({a: v[1] for a, v in banco.items()}, os.path.join(pacote, "arquivos"))
    if json_only:
        return arquivos

    cfg = p.cfg
    build = steam_build or cfg["steam_build"]
    release = os.path.join(p.root, "releases", f"steam-build-{build}")
    if not so_linux:
        salvar_json(os.path.join(pacote, "pacote.json"), {
            "jogo": cfg["nome"], "pasta_steam": cfg["pasta_steam"], "versao": cfg["versao"],
            "verificar": p.engine().arquivo_de_verificacao().replace("\\", "/"),
            "aviso": cfg.get("aviso_pos_instalacao", ""),
            "arquivos": [{"origem": "arquivos/" + os.path.basename(a), "destino": rel} for a, rel in arquivos],
        })
        app = "Traducao_PTBR_" + cfg["nome"].replace(" ", "_")
        empacotar(p.root, app, cfg["nome"], cfg["versao"], [], [
            (INSTALADOR, "instalador.py"),
            (os.path.join(REPO, "kit", "engines", cfg["engine"] + ".py"), cfg["engine"] + ".py"),
        ], f"{app}_v{cfg['versao']}.zip", build,
            script=INSTALADOR, dados_extra=[(os.path.join(pacote, "pacote.json"), "."),
                                             (os.path.join(pacote, "arquivos"), "arquivos")])
    return empacotar_linux(p, arquivos, release)
