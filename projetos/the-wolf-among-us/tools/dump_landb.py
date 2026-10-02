import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")
import telltale as tt
from landb import Landb
PACK = r"C:\Program Files (x86)\Steam\steamapps\common\The Wolf Among Us\Pack"
arc, name = sys.argv[1], sys.argv[2]
limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
a = tt.TTArchive2(os.path.join(PACK, arc))
e = next(x for x in a.entries if x["name"] == name)
lb = Landb(a.read(e))
a.close()
for r in lb.records[:limit]:
    print(r["id"], "|", lb.text(r, "actor"), "|", lb.text(r, "speech"))
