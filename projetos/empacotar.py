"""Compatibilidade para os builds antigos (garden-of-witches, the-wolf-among-us).

A implementação está em kit/platform/packaging.py.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from kit.platform.packaging import package_linux, package_windows  # noqa: E402


def empacotar(root, app, jogo, versao, dados, fontes, zip_name, steam_build, script=None, dados_extra=()):
    return package_windows(root, app, jogo, versao, dados, fontes, zip_name, steam_build, script, dados_extra)


def empacotar_linux(root, app, jogo, versao, conf, arquivos, zip_name, steam_build, lista=()):
    return package_linux(root, app, jogo, versao, conf, arquivos, zip_name, steam_build, lista)
