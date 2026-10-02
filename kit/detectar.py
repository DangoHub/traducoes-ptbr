"""Identifica a engine e onde provavelmente está o texto, lendo só nomes de arquivos e trechos pequenos."""
import os
import re

from kit.engines import ENGINES

ASSINATURAS_DLL = {
    "unity_antoolkit": [b"c\x00u\x00s\x00t\x00o\x00m\x00t\x00r\x00a\x00n\x00s\x00l\x00a\x00t\x00e\x00d\x00_\x00"],
    "i2_localization": [b"I2.Loc"],
    "unity_localization": [b"UnityEngine.Localization"],
}
EXT_TEXTO = (".json", ".csv", ".txt", ".xml", ".po", ".tsv", ".yaml", ".yml")


def _ler_inicio(path, n=64 * 1024 * 1024):
    with open(path, "rb") as f:
        return f.read(n)


def detectar(pasta):
    pasta = os.path.abspath(pasta)
    nomes = os.listdir(pasta)
    rel = {"pasta": pasta, "engine": "desconhecida", "pistas": [], "arquivos_de_texto": [], "plugin": None}

    dados = next((n for n in nomes if n.endswith("_Data") and os.path.isdir(os.path.join(pasta, n))), None)
    if dados:
        d = os.path.join(pasta, dados)
        il2cpp = "GameAssembly.dll" in nomes
        rel["engine"] = "unity-il2cpp" if il2cpp else "unity-mono"
        app = os.path.join(d, "app.info")
        if os.path.isfile(app):
            rel["pistas"].append("app.info: " + " / ".join(open(app, encoding="utf-8", errors="ignore").read().split("\n")))
        ggm = os.path.join(d, "globalgamemanagers")
        if os.path.isfile(ggm):
            m = re.search(rb"20\d\d\.\d+\.\d+[abfp]\d+", _ler_inicio(ggm, 4096))
            if m:
                rel["pistas"].append("Unity " + m.group().decode())
        asm = os.path.join(d, "Managed", "Assembly-CSharp.dll")
        if os.path.isfile(asm):
            b = _ler_inicio(asm)
            for plugin, sigs in ASSINATURAS_DLL.items():
                if any(s in b for s in sigs):
                    rel["pistas"].append(f"Assembly-CSharp contém marca de {plugin}")
                    if plugin in ENGINES and not rel["plugin"]:
                        rel["plugin"] = plugin
            managed = os.listdir(os.path.join(d, "Managed"))
            rel["pistas"] += [f"DLL: {x}" for x in managed if re.search(r"I2|Locali[sz]|Yarn|Ink|Naninovel|Fungus|PixelCrushers|Dialogue", x)]
        sa = os.path.join(d, "StreamingAssets")
        if os.path.isdir(sa):
            for base, _, fs in os.walk(sa):
                for f in fs:
                    if f.lower().endswith(EXT_TEXTO):
                        full = os.path.join(base, f)
                        rel["arquivos_de_texto"].append([os.path.relpath(full, pasta), os.path.getsize(full)])
    elif any(n.endswith(".ttarch2") for n in nomes) or os.path.isdir(os.path.join(pasta, "Archives")):
        rel["engine"] = "telltale"
    elif os.path.isdir(os.path.join(pasta, "renpy")) or os.path.isdir(os.path.join(pasta, "game")) and any(
            f.endswith((".rpa", ".rpyc")) for f in os.listdir(os.path.join(pasta, "game"))):
        rel["engine"] = "renpy"
    elif os.path.isdir(os.path.join(pasta, "www", "data")) or any(n.endswith((".rgss3a", ".rgssad")) for n in nomes):
        rel["engine"] = "rpgmaker"
    elif "data.win" in nomes:
        rel["engine"] = "gamemaker"
    elif any(n.endswith(".pck") for n in nomes):
        rel["engine"] = "godot"
    else:
        for base, _, fs in os.walk(pasta):
            if any(f.endswith(".pak") for f in fs) and "Content" in base:
                rel["engine"] = "unreal"
                rel["pistas"].append("pak em " + os.path.relpath(base, pasta))
                break

    rel["arquivos_de_texto"] = sorted(rel["arquivos_de_texto"], key=lambda x: -x[1])[:20]
    return rel
