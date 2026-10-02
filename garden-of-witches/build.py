"""Junta as traduções, gera o instalador .exe e o .zip de distribuição."""
import json, os, shutil, subprocess, sys, zipfile
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.dirname(os.path.abspath(__file__))
os.chdir(ROOT)

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

exe_name = "Instalador_Traducao_PTBR_Garden_of_Witches"
subprocess.check_call([
    "pyinstaller", "--noconfirm", "--onefile", "--windowed", "--uac-admin", "--clean",
    "--name", exe_name, "--add-data", os.path.join(ROOT, "src", "traducao_ptbr.json") + ";.",
    "--distpath", os.path.join(ROOT, "dist"), "--workpath", os.path.join(ROOT, "build"),
    "--specpath", os.path.join(ROOT, "build"),
    "--paths", os.path.join(ROOT, "src"), os.path.join(ROOT, "src", "instalador.py"),
])

STEAM_BUILD = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--steam-build=")), "25225196")
release = os.path.join(ROOT, "releases", f"steam-build-{STEAM_BUILD}")
os.makedirs(release, exist_ok=True)
exe = os.path.join("dist", exe_name + ".exe")
shutil.copy(exe, release)
zpath = os.path.join(release, "Garden_of_Witches_Traducao_PTBR.zip")
with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(exe, exe_name + ".exe")
    z.write("LEIA-ME.txt", "LEIA-ME.txt")
    z.write("src/traducao_ptbr.json", "fonte/traducao_ptbr.json")
    z.write("src/gow_ptbr_core.py", "fonte/gow_ptbr_core.py")
    z.write("src/instalador.py", "fonte/instalador.py")
    z.write("GUIA_TRADUCAO.md", "fonte/GUIA_TRADUCAO.md")
print("OK:", exe, "|", zpath, os.path.getsize(zpath) // 1024, "KB")
