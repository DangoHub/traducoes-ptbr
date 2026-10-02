"""Extrai as falas únicas (inglês) em lotes ordenados por episódio/cena."""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")
import telltale as tt
from landb import Landb

PACK = r"C:\Program Files (x86)\Steam\steamapps\common\The Wolf Among Us\Pack"
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
CHUNKS = os.path.join(ROOT, "chunks")
LIMIT = 14000
os.makedirs(CHUNKS, exist_ok=True)

ORDER = ["<Boot>", "<Menu>", "<Project>", "<Fables101>", "<Fables102>", "<Fables103>", "<Fables104>", "<Fables105>"]
index = [x for x in json.load(open(os.path.join(HERE, "landb_index.json"))) if x["name"].endswith("_english.landb")]
index.sort(key=lambda x: (ORDER.index(x["group"]), x["name"].startswith("ui_"), x["name"]))

seen = {}
lines = []
actors = {}
arcs = {}
for item in index:
    a = arcs.setdefault(item["archive"], tt.TTArchive2(os.path.join(PACK, item["archive"])))
    e = next(x for x in a.entries if x["name"] == item["name"])
    lb = Landb(a.read(e))
    ctx = item["group"].strip("<>") + "/" + item["name"][:-len("_english.landb")]
    for r in lb.records:
        en = lb.text(r, "speech")
        who = lb.text(r, "actor")
        if who:
            actors[who] = actors.get(who, 0) + 1
        if not en.strip() or en in seen:
            continue
        seen[en] = len(lines)
        lines.append({"k": str(len(lines)), "who": who, "ctx": ctx, "en": en})
for a in arcs.values():
    a.close()

json.dump({l["k"]: l["en"] for l in lines}, open(os.path.join(ROOT, "work", "lines_en.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
json.dump(dict(sorted(actors.items(), key=lambda x: -x[1])), open(os.path.join(ROOT, "work", "actors.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)

chunk, size, n = [], 0, 0
def flush():
    global chunk, size, n
    if chunk:
        json.dump(chunk, open(os.path.join(CHUNKS, f"lote_{n:03d}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
        n += 1
    chunk, size = [], 0

for l in lines:
    if size + len(l["en"]) > LIMIT:
        flush()
    chunk.append(l)
    size += len(l["en"])
flush()
print("falas únicas:", len(lines), "chars:", sum(len(l["en"]) for l in lines), "lotes:", n, "personagens:", len(actors))
