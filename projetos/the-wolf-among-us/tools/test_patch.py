"""Instala um patch mínimo (menu + abertura do ep. 1) para validar o mecanismo no jogo.
Uso: python test_patch.py [install|uninstall]"""
import os, sys, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")
import telltale as tt
import wolf_patch as wp
from landb import Landb

GAME = r"C:\Program Files (x86)\Steam\steamapps\common\The Wolf Among Us"
HERE = os.path.dirname(os.path.abspath(__file__))

TR = {"lines": {
    "Continue": "Continuar",
    "New Game": "Novo Jogo",
    "Quit": "Sair",
    "Save & Load": "Salvar e Carregar",
    "Help & Settings": "Ajuda e Configurações",
    "Return to Game": "Voltar ao Jogo",
    "You want to start a new game?": "Quer começar um jogo novo?",
    "Are you sure you want to quit?": "Tem certeza de que quer sair?",
    "Oops, no!": "Opa, não!",
    "Yes, I do!": "Sim, quero!",
    "[annoyed, defensive] What?": "[annoyed, defensive] Que foi?",
    "Fuckin' hell...": "Puta que pariu...",
    "[annoyed] {flustereda} I called you {annoyeda} twenty minutes ago.":
        "[annoyed] {flustereda} Eu te liguei {annoyeda} faz vinte minutos.",
}}

if sys.argv[1:] == ["uninstall"]:
    wp.uninstall(GAME)
    sys.exit()

index = [x for x in json.load(open(os.path.join(HERE, "landb_index.json")))
         if x["name"].endswith("_english.landb") and x["group"] in ("<Menu>", "<Fables101>")]
wp.install(GAME, TR, index)

for f in sorted(wp.mod_files(GAME)):
    if f.endswith(".lenc"):
        dec = tt.decrypt_lenc(open(f, "rb").read())
        assert dec.startswith(b"local set"), f
        print("ok lenc", os.path.basename(f))
    else:
        a = tt.TTArchive2(f)
        for e in a.entries:
            assert tt.crc64(e["name"]) == e["crc"]
            Landb(a.read(e))
        print("ok arquivo", os.path.basename(f), a.version, len(a.entries))
        a.close()

orig = open(os.path.join(GAME, "Pack", "_resourcedescriptions_500_Menu.lenc"), "rb").read()
assert tt.encrypt_lenc(tt.decrypt_lenc(orig)) == orig
print("roundtrip blowfish ok")
