"""Junta as traduções, gera o instalador e o .zip de distribuição.
Uso: python build.py [--json-only] [--steam-build=319083]"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, os.path.dirname(ROOT))
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from validate import check
from empacotar import empacotar
from wolf_patch import MOD_VERSION

lines, missing, bad = {}, 0, 0
for fn in sorted(os.listdir("chunks")):
    chunk = json.load(open(os.path.join("chunks", fn), encoding="utf-8"))
    out_path = os.path.join("out", fn)
    out = json.load(open(out_path, encoding="utf-8")) if os.path.isfile(out_path) else {}
    for item in chunk:
        pt = out.get(item["k"])
        if not pt:
            missing += 1
        elif check(item["en"], pt):
            bad += 1
        else:
            lines[item["en"]] = pt
print(f"Falas traduzidas: {len(lines)} | faltando: {missing} | inválidas (ignoradas): {bad}")
json.dump({"lines": lines}, open("src/traducao_ptbr.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

index = [{"group": x["group"], "name": x["name"], "archive": x["archive"]}
         for x in json.load(open("tools/landb_index.json")) if x["name"].endswith("_english.landb") and x["records"]]
json.dump(index, open("src/landb_index.json", "w"), indent=0)
print("Arquivos de texto do jogo:", len(index))

if "--json-only" in sys.argv:
    sys.exit(0)

STEAM_BUILD = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--steam-build=")), "319083")
empacotar(
    ROOT, "Traducao_PTBR_The_Wolf_Among_Us", "The Wolf Among Us", MOD_VERSION,
    dados=["traducao_ptbr.json", "landb_index.json"],
    fontes=[("src/" + f, f) for f in ("traducao_ptbr.json", "landb_index.json", "wolf_patch.py", "telltale.py",
                                      "landb.py", "bf_const.py", "instalador.py")]
           + [("GUIA_TRADUCAO.md", "GUIA_TRADUCAO.md")],
    zip_name="The_Wolf_Among_Us_Traducao_PTBR.zip", steam_build=STEAM_BUILD,
)