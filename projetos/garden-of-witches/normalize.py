import json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = {}
for fn in os.listdir("chunks"):
    for it in json.load(open(f"chunks/{fn}", encoding="utf-8")):
        src[it["k"]] = it["en"]

REPL = [("reinos", "domínios"), ("Reinos", "Domínios"), ("reino", "domínio"), ("Reino", "Domínio")]
changed = 0
for fn in os.listdir("out"):
    if not fn.endswith(".json"):
        continue
    p = f"out/{fn}"
    data = json.load(open(p, encoding="utf-8"))
    for k, pt in data.items():
        new = pt
        if re.search(r"\brealms?\b", src.get(k, ""), re.I):
            for a, b in REPL:
                new = re.sub(rf"\b{a}\b", b, new)
        new = new.replace("Bruxa de Sangue", "Bruxa do Sangue")
        if new != pt:
            data[k] = new
            changed += 1
    json.dump(data, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("linhas ajustadas:", changed)
