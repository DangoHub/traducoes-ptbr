"""Instalador genérico das traduções DangoHub.

Lê pacote.json (embutido pelo build): copia os arquivos traduzidos para a pasta do jogo, guardando backup
do que já existia, e registra tudo em DangoHub_PTBR.json para desinstalar depois.
Uso sem janela: instalador.exe --install|--uninstall|--status [pasta do jogo]
"""
import json
import os
import re
import shutil
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

try:
    import winreg
except ImportError:
    winreg = None

MANIFEST_NAME = "DangoHub_PTBR.json"
BACKUP_SUFFIX = ".dangohub-backup"
DEFAULT_STEAM_DIR = r"C:\Program Files (x86)\Steam"
STEAM_REGISTRY_KEYS = ((r"Software\Valve\Steam", "HKEY_CURRENT_USER"),
                       (r"SOFTWARE\WOW6432Node\Valve\Steam", "HKEY_LOCAL_MACHINE"))
FONT = "Segoe UI"


def resource(*parts):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *parts)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


PACKAGE = read_json(resource("pacote.json"))
TITLE = f"{PACKAGE['jogo']} — Tradução PT-BR v{PACKAGE['versao']}"


def is_game_dir(path):
    return bool(path) and os.path.exists(os.path.join(path, PACKAGE["verificar"]))


def manifest_path(game_dir):
    return os.path.join(game_dir, MANIFEST_NAME)


def is_installed(game_dir):
    return os.path.isfile(manifest_path(game_dir))


def install(game_dir, log=print):
    if is_installed(game_dir):
        uninstall(game_dir, log)
    installed = []
    for item in PACKAGE["arquivos"]:
        destination = os.path.join(game_dir, item["destino"])
        os.makedirs(os.path.dirname(destination), exist_ok=True)
        has_backup = os.path.exists(destination)
        if has_backup:
            shutil.copy2(destination, destination + BACKUP_SUFFIX)
            log(f"Backup: {item['destino']}")
        shutil.copyfile(resource(*item["origem"].split("/")), destination)
        installed.append({"destino": item["destino"], "backup": has_backup})
        log(f"Instalado: {item['destino']}")
    with open(manifest_path(game_dir), "w", encoding="utf-8") as f:
        json.dump({"jogo": PACKAGE["jogo"], "versao": PACKAGE["versao"], "arquivos": installed}, f,
                  ensure_ascii=False, indent=1)
    log("Tradução instalada.")


def uninstall(game_dir, log=print):
    path = manifest_path(game_dir)
    if not os.path.isfile(path):
        log("A tradução não está instalada.")
        return
    for item in read_json(path)["arquivos"]:
        destination = os.path.join(game_dir, item["destino"])
        backup = destination + BACKUP_SUFFIX
        if os.path.exists(destination):
            os.remove(destination)
        if item["backup"] and os.path.exists(backup):
            os.replace(backup, destination)
            log(f"Restaurado: {item['destino']}")
        else:
            log(f"Removido: {item['destino']}")
    os.remove(path)
    log("Tradução desinstalada; o jogo voltou ao original.")


def _registry_steam_dirs():
    if not winreg:
        return []
    found = []
    for key, hive_name in STEAM_REGISTRY_KEYS:
        try:
            with winreg.OpenKey(getattr(winreg, hive_name), key) as handle:
                for value in ("SteamPath", "InstallPath"):
                    try:
                        found.append(os.path.normpath(winreg.QueryValueEx(handle, value)[0]))
                    except OSError:
                        pass
        except OSError:
            pass
    return found


def steam_libraries():
    libraries = _registry_steam_dirs() + [DEFAULT_STEAM_DIR]
    for steam in list(libraries):
        vdf = os.path.join(steam, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf):
            with open(vdf, encoding="utf-8", errors="ignore") as f:
                text = f.read()
            libraries += [os.path.normpath(p.replace("\\\\", "\\")) for p in re.findall(r'"path"\s+"([^"]+)"', text)]
    return list(dict.fromkeys(libraries))


def detect_game_dir():
    here = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
    candidates = [here, os.path.dirname(here)]
    candidates += [os.path.join(lib, "steamapps", "common", PACKAGE["pasta_steam"]) for lib in steam_libraries()]
    return next((c for c in candidates if is_game_dir(c)), "")


def friendly_error(exc):
    if isinstance(exc, PermissionError):
        return ("Sem permissão para alterar os arquivos do jogo.\n"
                "Feche o jogo e execute o instalador como administrador.")
    return str(exc)


class App:
    def __init__(self, root):
        self.root = root
        root.title(TITLE)
        root.geometry("640x430")
        root.minsize(560, 380)

        tk.Label(root, text="Tradução em Português do Brasil", font=(FONT, 15, "bold")).pack(pady=(14, 0))
        tk.Label(root, text=PACKAGE.get("aviso", ""), font=(FONT, 9), wraplength=600).pack(pady=(2, 10))

        row = tk.Frame(root)
        row.pack(fill="x", padx=14)
        tk.Label(row, text="Pasta do jogo:", font=(FONT, 9)).pack(side="left")
        self.path = tk.StringVar(value=detect_game_dir())
        tk.Entry(row, textvariable=self.path).pack(side="left", fill="x", expand=True, padx=6)
        tk.Button(row, text="Procurar...", command=self.browse).pack(side="left")

        buttons = tk.Frame(root)
        buttons.pack(pady=12)
        self.install_button = tk.Button(buttons, text="Instalar tradução", width=20, bg="#3a7d44", fg="white",
                                        font=(FONT, 10, "bold"), command=lambda: self.run(self.do_install))
        self.install_button.pack(side="left", padx=6)
        self.uninstall_button = tk.Button(buttons, text="Desinstalar", width=14,
                                          command=lambda: self.run(self.do_uninstall))
        self.uninstall_button.pack(side="left", padx=6)

        self.log_box = scrolledtext.ScrolledText(root, height=12, font=("Consolas", 9), state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.refresh_status()

    @property
    def buttons(self):
        return (self.install_button, self.uninstall_button)

    def log(self, message):
        def append():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", message + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.root.after(0, append)

    def refresh_status(self):
        game_dir = self.path.get()
        if not is_game_dir(game_dir):
            self.log("Pasta do jogo não encontrada automaticamente. Clique em \"Procurar...\".")
        elif is_installed(game_dir):
            self.log("Status: tradução INSTALADA. Você pode reinstalar ou desinstalar.")
        else:
            self.log("Status: jogo encontrado, tradução não instalada.")

    def browse(self):
        selected = filedialog.askdirectory(title=f"Selecione a pasta '{PACKAGE['pasta_steam']}'")
        if selected:
            self.path.set(os.path.normpath(selected))
            self.refresh_status()

    def run(self, action):
        game_dir = self.path.get()
        if not is_game_dir(game_dir):
            messagebox.showerror(TITLE, f"Selecione a pasta de instalação do '{PACKAGE['jogo']}'.")
            return
        for button in self.buttons:
            button.configure(state="disabled")
        threading.Thread(target=self._worker, args=(action, game_dir), daemon=True).start()

    def _worker(self, action, game_dir):
        try:
            action(game_dir)
            ok, message = True, None
        except Exception as e:
            ok, message = False, friendly_error(e)
            self.log("ERRO: " + message)

        def done():
            for button in self.buttons:
                button.configure(state="normal")
            if ok:
                messagebox.showinfo(TITLE, "Concluído!")
            else:
                messagebox.showerror(TITLE, message)
        self.root.after(0, done)

    def do_install(self, game_dir):
        install(game_dir, self.log)
        if PACKAGE.get("aviso"):
            self.log(PACKAGE["aviso"])

    def do_uninstall(self, game_dir):
        uninstall(game_dir, self.log)


def cli(argv):
    action, game_dir = argv[1], (argv[2] if len(argv) > 2 else detect_game_dir())
    if action == "--install":
        install(game_dir)
    elif action == "--uninstall":
        uninstall(game_dir)
    elif action == "--status":
        print("instalado" if is_installed(game_dir) else "não instalado", game_dir)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli(sys.argv)
    else:
        root = tk.Tk()
        App(root)
        root.mainloop()
