import csv, io, json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
os.makedirs("chunks", exist_ok=True)
os.makedirs("out", exist_ok=True)

def rows_of(fn):
    return list(csv.reader(io.StringIO(open(fn, encoding="utf-8").read(), newline="")))

def emit(prefix, items, limit):
    chunks, cur, size = [], [], 0
    for it in items:
        if cur and size + len(it["en"]) > limit and it.get("brk", True):
            chunks.append(cur); cur, size = [], 0
        cur.append({k: v for k, v in it.items() if k != "brk"}); size += len(it["en"])
    if cur:
        chunks.append(cur)
    for i, c in enumerate(chunks):
        name = f"{prefix}_{i:02d}"
        json.dump(c, open(f"chunks/{name}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(name, len(c), sum(len(x["en"]) for x in c), c[0]["k"], "->", c[-1]["k"])

sysr = rows_of("ta/System__16811.txt")
en = sysr[0].index("en")
items, prev = [], None
for r in sysr[1:]:
    if r[en].strip():
        items.append({"k": f"{r[0]}||{r[1]}", "en": r[en], "brk": r[0] != prev})
    prev = r[0]
emit("system", items, 13500)

st = rows_of("ta/Story__16979.txt")
en = st[0].index("en")
items, prev = [], None
for r in st[1:]:
    scene = r[0].split(".")[0]
    if r[en].strip():
        items.append({"k": r[0], "en": r[en], "brk": scene != prev})
    prev = scene
emit("story", items, 12500)
