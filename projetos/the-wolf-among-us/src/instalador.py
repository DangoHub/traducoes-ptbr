import json
import os
import re
import sys
import threading
try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext
except ImportError:  # Linux/Steam Deck sem Tk: só o modo --install/--uninstall/--status
    tk = filedialog = messagebox = scrolledtext = None

import wolf_patch as core

TITLE = f"The Wolf Among Us — Tradução PT-BR v{core.MOD_VERSION}"
GAME_FOLDER = "The Wolf Among Us"


def resource(name):
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, name)


def load_json(name):
    with open(resource(name), encoding="utf-8") as f:
        return json.load(f)


def is_game_dir(path):
    return bool(path) and core.is_game_dir(path)


def steam_libraries():
    libs = []
    try:
        import winreg
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
    except ImportError:
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
    candidates += [os.path.join(lib, "steamapps", "common", GAME_FOLDER) for lib in steam_libraries()]
    return next((c for c in candidates if is_game_dir(c)), "")


def friendly_error(exc):
    if isinstance(exc, PermissionError):
        return ("Sem permissão para alterar os arquivos do jogo.\n"
                "Feche o jogo e execute o instalador como administrador.")
    return str(exc)


def install(game_dir, log=print):
    core.install(game_dir, load_json("traducao_ptbr.json"), load_json("landb_index.json"), log)


class App:
    def __init__(self, root):
        self.root = root
        root.title(TITLE)
        root.geometry("640x430")
        root.minsize(560, 380)

        tk.Label(root, text="Tradução em Português do Brasil", font=("Segoe UI", 15, "bold")).pack(pady=(14, 0))
        tk.Label(root, text="Feche o jogo antes de instalar. Legendas precisam estar ativadas nas opções.",
                 font=("Segoe UI", 9)).pack(pady=(2, 10))

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
        elif core.is_installed(p):
            self.log("Status: tradução INSTALADA. Você pode reinstalar ou desinstalar.")
        else:
            self.log("Status: jogo encontrado, tradução não instalada.")

    def browse(self):
        d = filedialog.askdirectory(title="Selecione a pasta 'The Wolf Among Us'")
        if d:
            self.path.set(os.path.normpath(d))
            self.refresh_status()

    def run(self, fn):
        p = self.path.get()
        if not is_game_dir(p):
            messagebox.showerror(TITLE, "Selecione a pasta onde está o 'TheWolfAmongUs.exe'.")
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
        self.log("Gerando arquivos traduzidos a partir do seu jogo...")
        install(p, self.log)
        self.log("Pronto! Abra o jogo normalmente.")

    def do_uninstall(self, p):
        core.uninstall(p, self.log)


def cli(argv):
    action, game_dir = argv[1], (argv[2] if len(argv) > 2 else detect_game_dir())
    if action == "--install":
        install(game_dir)
    elif action == "--uninstall":
        core.uninstall(game_dir)
    elif action == "--status":
        print("instalado" if core.is_installed(game_dir) else "não instalado", game_dir)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        cli(sys.argv)
    else:
        root = tk.Tk()
        App(root)
        root.mainloop()
