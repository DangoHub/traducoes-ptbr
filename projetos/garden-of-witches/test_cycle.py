import sys, hashlib, os
sys.path.insert(0, r"C:\gow_mod\src")
sys.stdout.reconfigure(encoding="utf-8")
import gow_ptbr_core as core
GAME = r"C:\Program Files (x86)\Steam\steamapps\common\Garden of Witches"
AP = core.game_assets_path(GAME)

def sha():
    h = hashlib.sha256()
    with open(AP, "rb") as f:
        for b in iter(lambda: f.read(8 << 20), b""):
            h.update(b)
    return h.hexdigest()

h0, s0 = sha(), os.path.getsize(AP)
print("orig", h0[:16], s0)
tr = {"System": {"ChapterInfo||Title.Chapter.0": "Capítulo 1 — ação ç ã õ"},
      "Story": {"Chapter0_HomeOpening.000": "Ufa, finalmente terminei!"}}
core.install(GAME, tr)
print("installed?", core.is_installed(GAME), os.path.getsize(AP))
story = core.read_current_text(GAME, "Story").decode("utf-8")
system = core.read_current_text(GAME, "System").decode("utf-8")
print("story ok", "Ufa, finalmente terminei!" in story, "system ok", "Capítulo 1 — ação ç ã õ" in system)
core.install(GAME, tr)
print("reinstall size", os.path.getsize(AP))
core.uninstall(GAME)
h1 = sha()
print("restored identical", h1 == h0, os.path.getsize(AP) == s0)
