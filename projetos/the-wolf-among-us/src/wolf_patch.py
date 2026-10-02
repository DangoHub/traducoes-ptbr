"""Gera e instala o patch PT-BR de The Wolf Among Us.

Os .landb originais são lidos do próprio jogo instalado, traduzidos em memória
e gravados em arquivos .ttarch2 novos, registrados por resource descriptions
próprias com prioridade acima de todos os updates oficiais. Nenhum arquivo
original é alterado: desinstalar = apagar os arquivos com o prefixo do mod.
"""
import os

import telltale as tt
from landb import Landb

MOD_VERSION = "1.1.0"
MOD_TAG = "PTBR"
PRIORITY = 100
LANGS = ("english", "french", "german", "italian", "spanish")
ARCHIVE_FMT = "Fables_pc_" + MOD_TAG + "_{group}.ttarch2"
RESDESC_FMT = "_resourcedescriptions_500_" + MOD_TAG + "_{group}.lenc"

RESDESC_LUA = """local set = {{}}
set.name = "{tag}_{group}"
set.setName = "{tag}_{group}"
set.descriptionFilenameOverride = ""
set.logicalName = "<{tag}_{group}>"
set.logicalDestination = "<{group}>"
set.priority = {priority}
set.localDir = _currentDirectory
set.enableMode = "constant"
set.version = "trunk"
set.descriptionPriority = 0
set.gameDataName = "{tag}_{group} Game Data"
set.gameDataPriority = 0
set.gameDataEnableMode = "constant"
set.localDirIncludeBase = true
set.localDirRecurse = false
set.localDirIncludeOnly = nil
set.localDirExclude = {{ "_dev/" }}
set.gameDataArchives = {{ _currentDirectory .. "{archive}" }}
RegisterSetDescription(set)
"""


def pack_dir(game_dir):
    return os.path.join(game_dir, "Pack")


def mod_files(game_dir):
    p = pack_dir(game_dir)
    if not os.path.isdir(p):
        return []
    return [os.path.join(p, f) for f in os.listdir(p)
            if f.startswith("Fables_pc_" + MOD_TAG + "_") or f.startswith("_resourcedescriptions_500_" + MOD_TAG + "_")]


def is_installed(game_dir):
    return bool(mod_files(game_dir))


def is_game_dir(game_dir):
    return os.path.isfile(os.path.join(game_dir, "TheWolfAmongUs.exe")) and os.path.isdir(pack_dir(game_dir))


def translate_landb(data, landb_name, tr):
    """tr = {"lines": {en: pt}, "actors": {en: pt}, "by_id": {"arquivo#id": pt}}"""
    lb = Landb(data)
    lines, actors, by_id = tr.get("lines", {}), tr.get("actors", {}), tr.get("by_id", {})
    done = total = 0
    for rec in lb.records:
        speech = lb.text(rec, "speech")
        if speech.strip():
            total += 1
            pt = by_id.get(f"{landb_name}#{rec['id']}") or lines.get(speech)
            if pt:
                lb.set_text(rec, "speech", pt)
                done += 1
        actor = lb.text(rec, "actor")
        if actor in actors:
            lb.set_text(rec, "actor", actors[actor])
    return lb.build(), done, total


def install(game_dir, translations, index, log=print):
    """index = [{"group", "name", "archive"}] apenas dos arquivos *_english.landb efetivos."""
    if not is_game_dir(game_dir):
        raise RuntimeError("Pasta do jogo inválida (TheWolfAmongUs.exe/Pack não encontrados).")
    uninstall(game_dir, log=lambda *_: None)
    pack = pack_dir(game_dir)
    by_group = {}
    for item in index:
        by_group.setdefault(item["group"], []).append(item)
    done_all = total_all = 0
    for group, items in sorted(by_group.items()):
        gname = group.strip("<>")
        files = []
        archives = {}
        for item in items:
            a = archives.get(item["archive"])
            if a is None:
                path = os.path.join(pack, item["archive"])
                if not os.path.isfile(path):
                    raise RuntimeError(f"Arquivo do jogo não encontrado: {item['archive']}")
                a = archives[item["archive"]] = tt.TTArchive2(path)
            entry = next((e for e in a.entries if e["name"] == item["name"]), None)
            if entry is None:
                raise RuntimeError(f"{item['name']} não encontrado em {item['archive']}")
            base = item["name"][:-len("_english.landb")]
            new, done, total = translate_landb(a.read(entry), base, translations)
            done_all += done
            total_all += total
            for lang in LANGS:
                files.append((f"{base}_{lang}.landb", new))
        for a in archives.values():
            a.close()
        archive = ARCHIVE_FMT.format(group=gname)
        tt.write_ttarch2_ttcn(os.path.join(pack, archive), files)
        lua = RESDESC_LUA.format(tag=MOD_TAG, group=gname, priority=PRIORITY, archive=archive)
        with open(os.path.join(pack, RESDESC_FMT.format(group=gname)), "wb") as f:
            f.write(tt.encrypt_lenc(lua.encode("ascii")))
        log(f"  {group}: {len(items)} arquivos de texto")
    log(f"Falas traduzidas: {done_all}/{total_all}")
    return done_all, total_all


def uninstall(game_dir, log=print):
    files = mod_files(game_dir)
    for f in files:
        os.remove(f)
    log(f"Removidos {len(files)} arquivos do mod." if files else "Nenhum arquivo do mod encontrado.")
    return len(files)
