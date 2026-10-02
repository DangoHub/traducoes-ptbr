"""Resolve a versão efetiva de cada .landb (maior prioridade) e testa o parser com roundtrip."""
import os, sys, json, collections
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")
import telltale as tt
import landb as lb
PACK = r"C:\Program Files (x86)\Steam\steamapps\common\The Wolf Among Us\Pack"
HERE = os.path.dirname(os.path.abspath(__file__))

sets = json.load(open(os.path.join(HERE, "resdesc.json")))
effective = {}
for s in sets:
    group = s["logicalDestination"] if s.get("logicalDestination") not in (None, "<>") else s["logicalName"]
    for arc in s["archives"]:
        a = tt.TTArchive2(os.path.join(PACK, arc))
        for e in a.entries:
            if e["name"].lower().endswith(".landb"):
                key = (group, e["name"].lower())
                if key not in effective or s["priority"] > effective[key]["priority"]:
                    effective[key] = {"group": group, "name": e["name"], "archive": arc, "priority": s["priority"]}
        a.close()

print("landb efetivos:", len(effective), collections.Counter(v["group"] for v in effective.values()))
ok = bad = 0
stats = collections.Counter()
open_arcs = {}
for v in sorted(effective.values(), key=lambda x: (x["group"], x["name"])):
    a = open_arcs.setdefault(v["archive"], tt.TTArchive2(os.path.join(PACK, v["archive"])))
    e = next(x for x in a.entries if x["name"] == v["name"])
    data = a.read(e)
    try:
        L = lb.Landb(data)
        rt = L.build() == data
        v["records"] = len(L.records)
        v["chars"] = sum(len(r["speech"]) for r in L.records)
        v["magic"] = L.magic.decode("latin-1")
        v["has_crc"], v["unicode"] = L.has_crc, L.unicode
        stats[(v["magic"], L.has_crc, L.unicode)] += 1
        if rt:
            ok += 1
        else:
            bad += 1
            print("ROUNDTRIP DIFERENTE:", v["group"], v["name"])
    except Exception as ex:
        bad += 1
        print("ERRO:", v["group"], v["name"], ex)
print("roundtrip ok", ok, "falhas", bad, dict(stats))
print("falas:", sum(v.get("records", 0) for v in effective.values()), "chars:", sum(v.get("chars", 0) for v in effective.values()))
json.dump(sorted(effective.values(), key=lambda x: (x["group"], x["name"])),
          open(os.path.join(HERE, "landb_index.json"), "w"), indent=1)
