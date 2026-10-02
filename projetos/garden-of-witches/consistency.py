import json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(os.path.dirname(os.path.abspath(__file__)))
src = {}
for fn in os.listdir("chunks"):
    for it in json.load(open(f"chunks/{fn}", encoding="utf-8")):
        src[it["k"]] = it["en"]
out = {}
for fn in os.listdir("out"):
    if fn.endswith(".json"):
        out.update(json.load(open(f"out/{fn}", encoding="utf-8")))

checks = [
    (r"\brealms?\b", r"\breinos?\b", "realm traduzido como reino"),
    (r"Blood Witch", r"Bruxa de Sangue", "Blood Witch -> 'de Sangue'"),
    (r"\bTea Party\b|\btea party\b", r"[Cc]há da [Tt]arde|[Pp]arty", "tea party fora do glossário"),
    (r"\bCooldown\b", r"[Cc]ooldown|[Tt]empo de [Rr]ecarga", "Cooldown fora do glossário"),
    (r"\bwitch", r"\bfeiticeira", "witch -> feiticeira"),
    (r"\bGarden\b|\bgarden\b", r"\b[Gg]arden\b", "garden não traduzido"),
]
for en_pat, pt_pat, label in checks:
    hits = [k for k, pt in out.items() if re.search(en_pat, src.get(k, "")) and re.search(pt_pat, pt)]
    print(f"{label}: {len(hits)}")
    for k in hits[:8]:
        print("   ", k, "|", out[k][:120])

same = [k for k, pt in out.items() if pt == src.get(k) and re.search(r"[a-z]{4,} [a-z]{3,}", pt)]
print("linhas idênticas ao inglês:", len(same))
for k in same[:20]:
    print("   ", k, "|", out[k][:100])
