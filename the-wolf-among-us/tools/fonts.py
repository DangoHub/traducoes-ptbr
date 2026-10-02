import os, sys, json, struct
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")
import telltale as tt
PACK = r"C:\Program Files (x86)\Steam\steamapps\common\The Wolf Among Us\Pack"
OUT = os.path.join(os.path.dirname(__file__), "..", "work", "fonts")
os.makedirs(OUT, exist_ok=True)
best = {}
sets = json.load(open(os.path.join(os.path.dirname(__file__), "resdesc.json")))
for s in sets:
    for arc in s["archives"]:
        if "Project" not in arc and "Menu" not in arc and "Boot" not in arc:
            continue
        a = tt.TTArchive2(os.path.join(PACK, arc))
        for e in a.entries:
            if e["name"].endswith(".font"):
                if e["name"] not in best or s["priority"] > best[e["name"]][0]:
                    best[e["name"]] = (s["priority"], arc, a.read(e))
        a.close()
for name, (prio, arc, data) in sorted(best.items()):
    open(os.path.join(OUT, name), "wb").write(data)
    print(name, len(data), arc, prio, data[:4])
