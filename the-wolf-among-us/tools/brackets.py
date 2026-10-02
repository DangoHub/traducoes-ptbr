"""Opções inteiras entre colchetes que ficaram em inglês.
python brackets.py export  -> work/colchetes_en.json  {"lote_NNN#k": en}
python brackets.py import  <- work/colchetes_pt.json  {"lote_NNN#k": pt} aplicado nos out/"""
import os, sys, json
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from validate import is_bracket_choice, check
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CH, OUT, WORK = (os.path.join(ROOT, d) for d in ("chunks", "out", "work"))

if sys.argv[1] == "export":
    todo = {}
    for f in sorted(os.listdir(OUT)):
        chunk = json.load(open(os.path.join(CH, f), encoding="utf-8"))
        out = json.load(open(os.path.join(OUT, f), encoding="utf-8"))
        for x in chunk:
            if is_bracket_choice(x["en"]) and out.get(x["k"]) == x["en"]:
                todo[f"{f[:-5]}#{x['k']}"] = x["en"]
    json.dump(todo, open(os.path.join(WORK, "colchetes_en.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("pendentes:", len(todo))
else:
    pt = json.load(open(os.path.join(WORK, "colchetes_pt.json"), encoding="utf-8"))
    en = json.load(open(os.path.join(WORK, "colchetes_en.json"), encoding="utf-8"))
    by_lote = {}
    for key, val in pt.items():
        lote, k = key.split("#")
        by_lote.setdefault(lote, {})[k] = val
    ok = bad = 0
    for lote, items in by_lote.items():
        path = os.path.join(OUT, lote + ".json")
        out = json.load(open(path, encoding="utf-8"))
        for k, val in items.items():
            errs = check(en[f"{lote}#{k}"], val)
            if errs:
                print(lote, k, errs, val); bad += 1
            else:
                out[k] = val; ok += 1
        json.dump(out, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print("aplicadas:", ok, "rejeitadas:", bad)
