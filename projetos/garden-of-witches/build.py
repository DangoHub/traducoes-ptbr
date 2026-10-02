"""Junta as traduções, gera o instalador e o .zip de distribuição.
Uso: python build.py [--json-only] [--steam-build=25225196]"""
import json, os, sys
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, os.path.dirname(ROOT))
sys.path.insert(0, os.path.join(ROOT, "src"))
from empacotar import empacotar
from gow_ptbr_core import MOD_VERSION

trans = {"System": {}, "Story": {}}
for fn in sorted(os.listdir("out")):
    if not fn.endswith(".json"):
        continue
    data = json.load(open(os.path.join("out", fn), encoding="utf-8"))
    trans["System" if fn.startswith("system") else "Story"].update(data)
print("System:", len(trans["System"]), "Story:", len(trans["Story"]))
json.dump(trans, open("src/traducao_ptbr.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)

if "--json-only" in sys.argv:
    sys.exit(0)

STEAM_BUILD = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--steam-build=")), "25225196")
empacotar(
    ROOT, "Traducao_PTBR_Garden_of_Witches", "Garden of Witches", MOD_VERSION,
    dados=["traducao_ptbr.json"],
    fontes=[("src/traducao_ptbr.json", "traducao_ptbr.json"), ("src/gow_ptbr_core.py", "gow_ptbr_core.py"),
            ("src/instalador.py", "instalador.py"), ("GUIA_TRADUCAO.md", "GUIA_TRADUCAO.md")],
    zip_name="Garden_of_Witches_Traducao_PTBR.zip", steam_build=STEAM_BUILD,
)
