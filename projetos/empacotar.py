"""Empacotamento comum: PyInstaller em modo pasta (sem --onefile e sem --uac-admin) + zip.

O modo pasta zipado é o formato com menos falsos positivos de antivírus (medido no VirusTotal).
"""
import os
import shutil
import subprocess
import zipfile

VERSION_TEMPLATE = """VSVersionInfo(
  ffi=FixedFileInfo(filevers={t}, prodvers={t}, mask=0x3f, flags=0x0, OS=0x40004, fileType=0x1, subtype=0x0, date=(0, 0)),
  kids=[
    StringFileInfo([StringTable('041604B0', [
      StringStruct('CompanyName', 'DangoHub'),
      StringStruct('FileDescription', 'Tradução PT-BR de {jogo}'),
      StringStruct('FileVersion', '{v}'),
      StringStruct('InternalName', '{app}'),
      StringStruct('LegalCopyright', 'DangoHub - tradução de fãs, código aberto'),
      StringStruct('OriginalFilename', '{app}.exe'),
      StringStruct('ProductName', 'DangoHub Traduções - {jogo} PT-BR'),
      StringStruct('ProductVersion', '{v}')])]),
    VarFileInfo([VarStruct('Translation', [0x0416, 1200])])
  ]
)
"""


def empacotar(root, app, jogo, versao, dados, fontes, zip_name, steam_build, script=None, dados_extra=()):
    build = os.path.join(root, "build")
    dist = os.path.join(root, "dist")
    os.makedirs(build, exist_ok=True)
    parts = (tuple(int(x) for x in versao.split(".")) + (0, 0, 0, 0))[:4]
    version_file = os.path.join(build, "version.txt")
    with open(version_file, "w", encoding="utf-8") as f:
        f.write(VERSION_TEMPLATE.format(t=parts, jogo=jogo, v=versao, app=app))

    cmd = ["pyinstaller", "--noconfirm", "--onedir", "--windowed", "--clean", "--name", app,
           "--version-file", version_file, "--distpath", dist, "--workpath", build, "--specpath", build,
           "--paths", os.path.join(root, "src")]
    for d in dados:
        cmd += ["--add-data", os.path.join(root, "src", d) + ";."]
    for origem, destino in dados_extra:
        cmd += ["--add-data", f"{origem};{destino}"]
    subprocess.check_call(cmd + [script or os.path.join(root, "src", "instalador.py")])

    release = os.path.join(root, "releases", f"steam-build-{steam_build}")
    shutil.rmtree(release, ignore_errors=True)
    os.makedirs(release)
    app_dir = os.path.join(dist, app)
    zpath = os.path.join(release, zip_name)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(app_dir):
            for fn in files:
                full = os.path.join(base, fn)
                z.write(full, os.path.join(app, os.path.relpath(full, app_dir)))
        z.write(os.path.join(root, "LEIA-ME.txt"), "LEIA-ME.txt")
        for src, dst in fontes:
            z.write(os.path.join(root, src), "fonte/" + dst)
    print("OK:", zpath, os.path.getsize(zpath) // 1024, "KB")
    return zpath
