"""Mapeia os conjuntos de recursos (resdesc) e descobre a versão efetiva de cada .landb."""
import os, re, sys, struct, json, collections
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
sys.stdout.reconfigure(encoding="utf-8")
import telltale as tt
PACK = r"C:\Program Files (x86)\Steam\steamapps\common\The Wolf Among Us\Pack"


def lua_consts(blob):
    """Extrai a sequência de constantes (strings/números/bool) de um chunk Lua 5.1 de forma heurística."""
    out = []
    i = 0
    while i < len(blob) - 9:
        t = blob[i]
        if t == 4:
            (n,) = struct.unpack_from("<I", blob, i + 1)
            if 1 <= n < 300 and i + 5 + n <= len(blob) and blob[i + 4 + n] == 0:
                s = blob[i + 5:i + 4 + n]
                if all(32 <= c < 127 for c in s):
                    out.append(s.decode())
                    i += 5 + n
                    continue
        if t == 3 and out and isinstance(out[-1], str) and out[-1] in ("priority", "descriptionPriority", "gameDataPriority"):
            out.append(struct.unpack_from("<f", blob, i + 1)[0])
            i += 5
            continue
        i += 1
    return out


sets = []
for fn in sorted(os.listdir(PACK)):
    if not fn.endswith(".lenc"):
        continue
    c = lua_consts(tt.decrypt_lenc(open(os.path.join(PACK, fn), "rb").read()))
    d = {"file": fn}
    for k in ("name", "logicalName", "logicalDestination", "priority", "descriptionPriority", "gameDataPriority", "enableMode", "version"):
        if k in c:
            j = c.index(k)
            d[k] = c[j + 1] if j + 1 < len(c) else None
    d["archives"] = [x for x in c if isinstance(x, str) and x.endswith(".ttarch2")]
    sets.append(d)

for d in sets:
    print(f'{d.get("logicalName","?"):45} -> {d.get("logicalDestination","?"):14} prio={d.get("priority")} gdp={d.get("gameDataPriority")} {d.get("enableMode","")} {d["archives"]}')

json.dump(sets, open(os.path.join(os.path.dirname(__file__), "resdesc.json"), "w"), indent=1)
