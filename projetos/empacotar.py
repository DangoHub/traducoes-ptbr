"""Empacotamento comum: PyInstaller em modo pasta (sem --onefile e sem --uac-admin) + zip.

O modo pasta zipado é o formato com menos falsos positivos de antivírus (medido no VirusTotal).
"""
import os
import shlex
import shutil
import subprocess
import zipfile

INSTALADOR_LINUX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "kit", "instalador_linux.sh")

LEIA_ME_LINUX = """Tradução PT-BR de {jogo} v{versao} - DangoHub
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


def _script_executavel(z, origem, nome):
    with open(origem, encoding="utf-8") as f:
        texto = f.read().replace("\r\n", "\n")
    info = zipfile.ZipInfo(nome)
    info.create_system = 3
    info.external_attr = 0o100755 << 16
    info.compress_type = zipfile.ZIP_DEFLATED
    z.writestr(info, texto.encode("utf-8"))


def empacotar_linux(root, app, jogo, versao, conf, arquivos, zip_name, steam_build, lista=()):
    """Zip para Steam Deck/Linux com Instalar.sh.

    conf: variáveis de pacote.conf (PASTA_STEAM, VERIFICAR, AVISO e, opcionalmente, PY_INSTALADOR).
    arquivos: [(caminho_local, nome_dentro_da_pasta_do_app)].
    lista: [(origem_no_app, destino_relativo_no_jogo)] para cópia direta (vira arquivos.lst).
    Deve rodar depois de empacotar(), que recria a pasta de release.
    """
    conf = {"JOGO": jogo, "VERSAO": versao, **conf}
    release = os.path.join(root, "releases", f"steam-build-{steam_build}")
    os.makedirs(release, exist_ok=True)
    zpath = os.path.join(release, zip_name)
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        _script_executavel(z, INSTALADOR_LINUX, f"{app}/Instalar.sh")
        z.writestr(f"{app}/pacote.conf", "".join(f"{k}={shlex.quote(str(v))}\n" for k, v in conf.items()))
        z.writestr(f"{app}/arquivos.lst", "".join(f"{o}\t{d}\n" for o, d in lista))
        for local, nome in arquivos:
            z.write(local, f"{app}/{nome}")
        z.writestr(f"{app}/LEIA-ME.txt", LEIA_ME_LINUX.format(jogo=jogo, versao=versao, aviso=conf.get("AVISO", "")))
    print("OK:", zpath, os.path.getsize(zpath) // 1024, "KB")
    return zpath
