"""Identify the engine and where the text probably is, reading only file names and small excerpts."""
import os
import re

from kit.engines import ENGINES

DLL_SIGNATURES = {
    "unity_antoolkit": [b"c\x00u\x00s\x00t\x00o\x00m\x00t\x00r\x00a\x00n\x00s\x00l\x00a\x00t\x00e\x00d\x00_\x00"],
    "i2_localization": [b"I2.Loc"],
    "unity_localization": [b"UnityEngine.Localization"],
}
TEXT_EXTENSIONS = (".json", ".csv", ".txt", ".xml", ".po", ".tsv", ".yaml", ".yml")
DIALOGUE_DLL = re.compile(r"I2|Locali[sz]|Yarn|Ink|Naninovel|Fungus|PixelCrushers|Dialogue")
UNITY_VERSION = re.compile(rb"20\d\d\.\d+\.\d+[abfp]\d+")
MAX_TEXT_FILES = 20
DLL_READ_BYTES = 64 * 1024 * 1024


def _read_head(path, size=DLL_READ_BYTES):
    with open(path, "rb") as f:
        return f.read(size)


def _inspect_unity(game_dir, data_dir, report):
    data = os.path.join(game_dir, data_dir)
    app_info = os.path.join(data, "app.info")
    if os.path.isfile(app_info):
        with open(app_info, encoding="utf-8", errors="ignore") as f:
            report["pistas"].append("app.info: " + " / ".join(f.read().split("\n")))
    managers = os.path.join(data, "globalgamemanagers")
    if os.path.isfile(managers):
        match = UNITY_VERSION.search(_read_head(managers, 4096))
        if match:
            report["pistas"].append("Unity " + match.group().decode())
    assembly = os.path.join(data, "Managed", "Assembly-CSharp.dll")
    if os.path.isfile(assembly):
        content = _read_head(assembly)
        for plugin, signatures in DLL_SIGNATURES.items():
            if any(s in content for s in signatures):
                report["pistas"].append(f"Assembly-CSharp contém marca de {plugin}")
                if plugin in ENGINES and not report["plugin"]:
                    report["plugin"] = plugin
        managed = os.listdir(os.path.join(data, "Managed"))
        report["pistas"] += [f"DLL: {name}" for name in managed if DIALOGUE_DLL.search(name)]
    streaming = os.path.join(data, "StreamingAssets")
    if os.path.isdir(streaming):
        for base, _, files in os.walk(streaming):
            for name in files:
                if name.lower().endswith(TEXT_EXTENSIONS):
                    full = os.path.join(base, name)
                    report["arquivos_de_texto"].append([os.path.relpath(full, game_dir), os.path.getsize(full)])


def _is_renpy(game_dir):
    if os.path.isdir(os.path.join(game_dir, "renpy")):
        return True
    game = os.path.join(game_dir, "game")
    return os.path.isdir(game) and any(f.endswith((".rpa", ".rpyc")) for f in os.listdir(game))


def _find_unreal_pak(game_dir):
    for base, _, files in os.walk(game_dir):
        if any(f.endswith(".pak") for f in files) and "Content" in base:
            return base
    return None


def detect(game_dir):
    """Short report (keys in Portuguese, printed as JSON): engine, hints, text files and kit plugin."""
    game_dir = os.path.abspath(game_dir)
    names = os.listdir(game_dir)
    report = {"pasta": game_dir, "engine": "desconhecida", "pistas": [], "arquivos_de_texto": [], "plugin": None}

    data_dir = next((n for n in names if n.endswith("_Data") and os.path.isdir(os.path.join(game_dir, n))), None)
    if data_dir:
        report["engine"] = "unity-il2cpp" if "GameAssembly.dll" in names else "unity-mono"
        _inspect_unity(game_dir, data_dir, report)
    elif any(n.endswith(".ttarch2") for n in names) or os.path.isdir(os.path.join(game_dir, "Archives")):
        report["engine"] = "telltale"
    elif _is_renpy(game_dir):
        report["engine"] = "renpy"
    elif os.path.isdir(os.path.join(game_dir, "www", "data")) or any(n.endswith((".rgss3a", ".rgssad")) for n in names):
        report["engine"] = "rpgmaker"
    elif "data.win" in names:
        report["engine"] = "gamemaker"
    elif any(n.endswith(".pck") for n in names):
        report["engine"] = "godot"
    elif pak_dir := _find_unreal_pak(game_dir):
        report["engine"] = "unreal"
        report["pistas"].append("pak em " + os.path.relpath(pak_dir, game_dir))

    report["arquivos_de_texto"] = sorted(report["arquivos_de_texto"], key=lambda x: -x[1])[:MAX_TEXT_FILES]
    return report
