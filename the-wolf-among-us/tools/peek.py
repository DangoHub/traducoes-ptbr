import os, sys
PACK = r"C:\Program Files (x86)\Steam\steamapps\common\The Wolf Among Us\Pack"
for fn in sys.argv[1:]:
    p = os.path.join(PACK, fn)
    with open(p, "rb") as f:
        h = f.read(96)
    print(fn, os.path.getsize(p))
    print("  ", h[:48].hex(" "))
    print("  ", h[:48])
