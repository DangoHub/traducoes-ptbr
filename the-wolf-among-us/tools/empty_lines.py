"""Conta falas sem texto (sem legenda) já nos .landb originais em inglês."""
import os, sys, json, collections
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")
import telltale as tt
from landb import Landb

PACK = r"C:\Program Files (x86)\Steam\steamapps\common\The Wolf Among Us\Pack"
HERE = os.path.dirname(os.path.abspath(__file__))
index = [x for x in json.load(open(os.path.join(HERE, "landb_index.json"))) if x["name"].endswith("_english.landb")]
total = empty = 0
by_file, by_actor = collections.Counter(), collections.Counter()
arcs = {}
for item in index:
    a = arcs.setdefault(item["archive"], tt.TTArchive2(os.path.join(PACK, item["archive"])))
    e = next(x for x in a.entries if x["name"] == item["name"])
    lb = Landb(a.read(e))
    for r in lb.records:
        total += 1
        if not lb.text(r, "speech").strip():
            empty += 1
            by_file[item["group"] + " " + item["name"]] += 1
            by_actor[lb.text(r, "actor") or "(sem nome)"] += 1
for a in arcs.values():
    a.close()
print(f"registros: {total} | sem texto no original: {empty}")
print("por arquivo:", by_file.most_common(12))
print("por personagem:", by_actor.most_common(12))
