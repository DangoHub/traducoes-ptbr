"""Junta as traduções, gera o instalador .exe e o .zip de distribuição.
Uso: python build.py [--json-only] [--steam-build=319083]"""
import json, os, shutil, subprocess, sys, zipfile
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from validate import check

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

exe_name = "Instalador_Traducao_PTBR_The_Wolf_Among_Us"
data = [os.path.join(ROOT, "src", f) + ";." for f in ("traducao_ptbr.json", "landb_index.json")]
subprocess.check_call([
    "pyinstaller", "--noconfirm", "--onefile", "--windowed", "--uac-admin", "--clean",
    "--name", exe_name, "--add-data", data[0], "--add-data", data[1],
    "--distpath", os.path.join(ROOT, "dist"), "--workpath", os.path.join(ROOT, "build"),
    "--specpath", os.path.join(ROOT, "build"),
    "--paths", os.path.join(ROOT, "src"), os.path.join(ROOT, "src", "instalador.py"),
])

STEAM_BUILD = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--steam-build=")), "319083")
release = os.path.join(ROOT, "releases", f"steam-build-{STEAM_BUILD}")
os.makedirs(release, exist_ok=True)
exe = os.path.join("dist", exe_name + ".exe")
shutil.copy(exe, release)
zpath = os.path.join(release, "The_Wolf_Among_Us_Traducao_PTBR.zip")
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(exe, exe_name + ".exe")
    z.write("LEIA-ME.txt", "LEIA-ME.txt")
    for f in ("traducao_ptbr.json", "landb_index.json", "wolf_patch.py", "telltale.py", "landb.py", "bf_const.py", "instalador.py"):
        z.write(os.path.join("src", f), "fonte/" + f)
    z.write("GUIA_TRADUCAO.md", "fonte/GUIA_TRADUCAO.md")
print("OK:", exe, "|", zpath, os.path.getsize(zpath) // 1024, "KB")
