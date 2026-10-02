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

MANIFESTO = "DangoHub_PTBR.json"
SUFIXO_BACKUP = ".dangohub-backup"


def resource(*partes):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, *partes)


PACOTE = json.load(open(resource("pacote.json"), encoding="utf-8"))
TITLE = f"{PACOTE['jogo']} — Tradução PT-BR v{PACOTE['versao']}"


def is_game_dir(path):
    return bool(path) and os.path.exists(os.path.join(path, PACOTE["verificar"]))


def is_installed(game_dir):
    return os.path.isfile(os.path.join(game_dir, MANIFESTO))


def install(game_dir, log=print):
    if is_installed(game_dir):
        uninstall(game_dir, log)
    instalados = []
    for item in PACOTE["arquivos"]:
        dest = os.path.join(game_dir, item["destino"])
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        backup = None
        if os.path.exists(dest):
            backup = dest + SUFIXO_BACKUP
            shutil.copy2(dest, backup)
            log(f"Backup: {item['destino']}")
        shutil.copyfile(resource(*item["origem"].split("/")), dest)
        instalados.append({"destino": item["destino"], "backup": bool(backup)})
        log(f"Instalado: {item['destino']}")
    with open(os.path.join(game_dir, MANIFESTO), "w", encoding="utf-8") as f:
        json.dump({"jogo": PACOTE["jogo"], "versao": PACOTE["versao"], "arquivos": instalados}, f, ensure_ascii=False, indent=1)
    log("Tradução instalada.")


def uninstall(game_dir, log=print):
    path = os.path.join(game_dir, MANIFESTO)
    if not os.path.isfile(path):
        log("A tradução não está instalada.")
        return
    manifesto = json.load(open(path, encoding="utf-8"))
    for item in manifesto["arquivos"]:
        dest = os.path.join(game_dir, item["destino"])
        if os.path.exists(dest):
            os.remove(dest)
        if item["backup"] and os.path.exists(dest + SUFIXO_BACKUP):
            os.replace(dest + SUFIXO_BACKUP, dest)
            log(f"Restaurado: {item['destino']}")
        else:
            log(f"Removido: {item['destino']}")
    os.remove(path)
    log("Tradução desinstalada; o jogo voltou ao original.")


def steam_libraries():
    libs = []
    if winreg:
        for hive, key in ((winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
                          (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam")):
            try:
                with winreg.OpenKey(hive, key) as k:
                    for value in ("SteamPath", "InstallPath"):
                        try:
                            libs.append(os.path.normpath(winreg.QueryValueEx(k, value)[0]))
                        except OSError:
                            pass
            except OSError:
                pass
    libs.append(r"C:\Program Files (x86)\Steam")
    for steam in list(libs):
        vdf = os.path.join(steam, "steamapps", "libraryfolders.vdf")
        if os.path.exists(vdf):
            text = open(vdf, encoding="utf-8", errors="ignore").read()
            libs += [os.path.normpath(p.replace("\\\\", "\\")) for p in re.findall(r'"path"\s+"([^"]+)"', text)]
    return list(dict.fromkeys(libs))


def detect_game_dir():
    here = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
    candidates = [here, os.path.dirname(here)]
    candidates += [os.path.join(lib, "steamapps", "common", PACOTE["pasta_steam"]) for lib in steam_libraries()]
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

        tk.Label(root, text="Tradução em Português do Brasil", font=("Segoe UI", 15, "bold")).pack(pady=(14, 0))
        tk.Label(root, text=PACOTE.get("aviso", ""), font=("Segoe UI", 9), wraplength=600).pack(pady=(2, 10))

        row = tk.Frame(root)
        row.pack(fill="x", padx=14)
        tk.Label(row, text="Pasta do jogo:", font=("Segoe UI", 9)).pack(side="left")
        self.path = tk.StringVar(value=detect_game_dir())
        tk.Entry(row, textvariable=self.path).pack(side="left", fill="x", expand=True, padx=6)
        tk.Button(row, text="Procurar...", command=self.browse).pack(side="left")

        btns = tk.Frame(root)
        btns.pack(pady=12)
        self.btn_install = tk.Button(btns, text="Instalar tradução", width=20, bg="#3a7d44", fg="white",
                                     font=("Segoe UI", 10, "bold"), command=lambda: self.run(self.do_install))
        self.btn_install.pack(side="left", padx=6)
        self.btn_uninstall = tk.Button(btns, text="Desinstalar", width=14,
                                       command=lambda: self.run(self.do_uninstall))
        self.btn_uninstall.pack(side="left", padx=6)

        self.log_box = scrolledtext.ScrolledText(root, height=12, font=("Consolas", 9), state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=14, pady=(0, 14))
        self.refresh_status()

    def log(self, msg):
        def append():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", msg + "\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.root.after(0, append)

    def refresh_status(self):
        p = self.path.get()
        if not is_game_dir(p):
            self.log("Pasta do jogo não encontrada automaticamente. Clique em \"Procurar...\".")
        elif is_installed(p):
            self.log("Status: tradução INSTALADA. Você pode reinstalar ou desinstalar.")
        else:
            self.log("Status: jogo encontrado, tradução não instalada.")

    def browse(self):
        d = filedialog.askdirectory(title=f"Selecione a pasta '{PACOTE['pasta_steam']}'")
        if d:
            self.path.set(os.path.normpath(d))
            self.refresh_status()

    def run(self, fn):
        p = self.path.get()
        if not is_game_dir(p):
            messagebox.showerror(TITLE, f"Selecione a pasta de instalação do '{PACOTE['jogo']}'.")
            return
        for b in (self.btn_install, self.btn_uninstall):
            b.configure(state="disabled")
        threading.Thread(target=self._worker, args=(fn, p), daemon=True).start()

    def _worker(self, fn, p):
        try:
            fn(p)
            ok, msg = True, None
        except Exception as e:
            ok, msg = False, friendly_error(e)
            self.log("ERRO: " + msg)

        def done():
            for b in (self.btn_install, self.btn_uninstall):
                b.configure(state="normal")
            if ok:
                messagebox.showinfo(TITLE, "Concluído!")
            else:
                messagebox.showerror(TITLE, msg)
        self.root.after(0, done)

    def do_install(self, p):
        install(p, self.log)
        if PACOTE.get("aviso"):
            self.log(PACOTE["aviso"])

    def do_uninstall(self, p):
        uninstall(p, self.log)


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
