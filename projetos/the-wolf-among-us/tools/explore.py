import os, sys, collections
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")
import telltale as tt
PACK = r"C:\Program Files (x86)\Steam\steamapps\common\The Wolf Among Us\Pack"

mode = sys.argv[1]
if mode == "lenc":
    for fn in sys.argv[2:]:
        dec = tt.decrypt_lenc(open(os.path.join(PACK, fn), "rb").read())
        print("=====", fn)
        print(dec.decode("latin-1"))
elif mode == "list":
    for fn in sys.argv[2:]:
        a = tt.TTArchive2(os.path.join(PACK, fn))
        exts = collections.Counter(os.path.splitext(e["name"])[1] for e in a.entries)
        print(fn, a.magic, a.version, len(a.entries), dict(exts))
        a.close()
elif mode == "names":
    a = tt.TTArchive2(os.path.join(PACK, sys.argv[2]))
    pat = sys.argv[3] if len(sys.argv) > 3 else ""
    for e in a.entries:
        if pat in e["name"]:
            print(e["name"], e["size"], "crc ok" if tt.crc64(e["name"]) == e["crc"] else "CRC MISMATCH")
