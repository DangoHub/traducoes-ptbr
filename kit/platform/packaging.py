"""Release packaging: PyInstaller in folder mode (no --onefile, no --uac-admin) + zip, and the Linux zip.

The zipped folder mode is the format with the fewest antivirus false positives (measured on VirusTotal).
"""
import os
import shlex
import shutil
import subprocess
import zipfile

from kit.config.paths import LINUX_INSTALLER_PATH

LINUX_README = """Tradução PT-BR de {jogo} v{versao} - DangoHub
Instalação no Steam Deck / Linux
================================

1. No Steam Deck, entre no Modo Desktop (botão Steam > Ligar/Desligar > Mudar para a área de trabalho).
2. Extraia este .zip (clique com o botão direito > Extrair > Extrair aqui).
3. Abra a pasta extraída, dê dois cliques em "Instalar.sh" e escolha "Executar".
   Se abrir como texto: botão direito em "Instalar.sh" > "Executar no Konsole".
4. Escolha "Instalar / atualizar a tradução". O jogo é localizado sozinho
   (memória interna ou cartão SD); se não for, selecione a pasta do jogo.
5. Feche o jogo antes de instalar e volte ao Modo de Jogo no final.

{aviso}

Para remover: rode "Instalar.sh" de novo e escolha "Desinstalar" (os arquivos originais são restaurados).

Pelo terminal: ./Instalar.sh --install | --uninstall | --status  [pasta do jogo]
"""
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


def release_dir(root, steam_build):
    return os.path.join(root, "releases", f"steam-build-{steam_build}")


def _version_tuple(version):
    return (tuple(int(x) for x in version.split(".")) + (0, 0, 0, 0))[:4]


def package_windows(root, app, game, version, data_files, sources, zip_name, steam_build, script=None, extra_data=()):
    """Build the installer with PyInstaller and zip it with LEIA-ME.txt and the sources (fonte/).

    data_files: files of <root>/src bundled next to the executable.
    sources: [(path relative to root, name inside fonte/)].
    extra_data: [(local path, destination inside the bundle)].
    Recreates the release folder.
    """
    build = os.path.join(root, "build")
    dist = os.path.join(root, "dist")
    os.makedirs(build, exist_ok=True)
    version_file = os.path.join(build, "version.txt")
    with open(version_file, "w", encoding="utf-8") as f:
        f.write(VERSION_TEMPLATE.format(t=_version_tuple(version), jogo=game, v=version, app=app))

    cmd = ["pyinstaller", "--noconfirm", "--onedir", "--windowed", "--clean", "--name", app,
           "--version-file", version_file, "--distpath", dist, "--workpath", build, "--specpath", build,
           "--paths", os.path.join(root, "src")]
    for name in data_files:
        cmd += ["--add-data", os.path.join(root, "src", name) + ";."]
    for source, destination in extra_data:
        cmd += ["--add-data", f"{source};{destination}"]
    subprocess.check_call(cmd + [script or os.path.join(root, "src", "instalador.py")])

    release = release_dir(root, steam_build)
    shutil.rmtree(release, ignore_errors=True)
    os.makedirs(release)
    app_dir = os.path.join(dist, app)
    zip_path = os.path.join(release, zip_name)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for base, _, files in os.walk(app_dir):
            for name in files:
                full = os.path.join(base, name)
                z.write(full, os.path.join(app, os.path.relpath(full, app_dir)))
        z.write(os.path.join(root, "LEIA-ME.txt"), "LEIA-ME.txt")
        for source, destination in sources:
            z.write(os.path.join(root, source), "fonte/" + destination)
    print("OK:", zip_path, os.path.getsize(zip_path) // 1024, "KB")
    return zip_path


def _write_executable(z, source, name):
    with open(source, encoding="utf-8") as f:
        text = f.read().replace("\r\n", "\n")
    info = zipfile.ZipInfo(name)
    info.create_system = 3
    info.external_attr = 0o100755 << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(info, text.encode("utf-8"))


def package_linux(root, app, game, version, conf, files, zip_name, steam_build, copy_list=()):
    """Steam Deck/Linux zip with Instalar.sh.

    conf: pacote.conf variables (PASTA_STEAM, VERIFICAR, AVISO and, optionally, PY_INSTALADOR).
    files: [(local path, name inside the app folder)].
    copy_list: [(source inside the app, destination relative to the game)] for direct copy (arquivos.lst).
    Must run after package_windows(), which recreates the release folder.
    """
    conf = {"JOGO": game, "VERSAO": version, **conf}
    release = release_dir(root, steam_build)
    os.makedirs(release, exist_ok=True)
    zip_path = os.path.join(release, zip_name)
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        _write_executable(z, LINUX_INSTALLER_PATH, f"{app}/Instalar.sh")
        z.writestr(f"{app}/pacote.conf", "".join(f"{k}={shlex.quote(str(v))}\n" for k, v in conf.items()))
        z.writestr(f"{app}/arquivos.lst", "".join(f"{source}\t{destination}\n" for source, destination in copy_list))
        for local, name in files:
            z.write(local, f"{app}/{name}")
        z.writestr(f"{app}/LEIA-ME.txt", LINUX_README.format(jogo=game, versao=version, aviso=conf.get("AVISO", "")))
    print("OK:", zip_path, os.path.getsize(zip_path) // 1024, "KB")
    return zip_path
