import os, sys, json, collections, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")
import telltale as tt
import landb as lb
PACK = r"C:\Program Files (x86)\Steam\steamapps\common\The Wolf Among Us\Pack"
HERE = os.path.dirname(os.path.abspath(__file__))
idx = json.load(open(os.path.join(HERE, "landb_index.json")))
arcs = {}

def load(v):
    a = arcs.setdefault(v["archive"], tt.TTArchive2(os.path.join(PACK, v["archive"])))
    return a.read(next(x for x in a.entries if x["name"] == v["name"]))

eng = [v for v in idx if v["name"].endswith("_english.landb")]
same = sum(load(v) == load(next(x for x in idx if x["group"] == v["group"] and x["name"] == v["name"].replace("english", "french"))) for v in eng)
print("arquivos english:", len(eng), "| idênticos ao french:", same)

uniq = {}
recs = empty = 0
actors = collections.Counter()
samples = []
for v in eng:
    L = lb.Landb(load(v))
    for r in L.records:
        recs += 1
        s = L.text(r, "speech")
        if not s.strip():
            empty += 1
            continue
        uniq.setdefault(s, 0)
        uniq[s] += 1
        actors[L.text(r, "actor")] += 1
        if len(samples) < 40 and v["name"].startswith("env_bigbyapartment"):
            samples.append((L.text(r, "actor"), s))
print("registros:", recs, "vazios:", empty, "falas únicas:", len(uniq), "chars únicos:", sum(len(s) for s in uniq))
print("atores:", actors.most_common(40))
for a, s in samples:
    print("  ", a, "|", s[:140])
tags = collections.Counter()
for s in uniq:
    for m in re.findall(r"<[^>]*>|\{[^}]*\}|\[[^\]]*\]|\\[a-z]", s):
        tags[re.sub(r"\d+", "#", m)[:30]] += 1
print("tags:", tags.most_common(30))
nonascii = collections.Counter(c for s in uniq for c in s if ord(c) > 126)
print("não-ASCII:", nonascii.most_common(30))
