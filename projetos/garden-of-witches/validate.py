"""Uso: python validate.py <nome_do_lote>   ex.: python validate.py story_03
Compara chunks/<lote>.json com out/<lote>.json e lista problemas."""
import json, re, sys, os
sys.stdout.reconfigure(encoding="utf-8")
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def check(name):
    src = json.load(open(f"chunks/{name}.json", encoding="utf-8"))
    p = f"out/{name}.json"
    if not os.path.exists(p):
        return [f"{name}: arquivo de saída ausente"]
    try:
        out = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        return [f"{name}: JSON inválido: {e}"]
    errs = []
    for it in src:
        k, en = it["k"], it["en"]
        pt = out.get(k)
        if pt is None or (not pt.strip() and en.strip()):
            errs.append(f"[FALTANDO] {k}"); continue
        if sorted(re.findall(r"\{[^{}]*\}", en)) != sorted(re.findall(r"\{[^{}]*\}", pt)):
            errs.append(f"[PLACEHOLDER] {k}: {re.findall(r'{[^{}]*}', en)} vs {re.findall(r'{[^{}]*}', pt)}")
        if sorted(re.findall(r"<[^<>]*>", en)) != sorted(re.findall(r"<[^<>]*>", pt)):
            errs.append(f"[TAG] {k}")
        if en.count("`") != pt.count("`"):
            errs.append(f"[CRASE] {k}: en={en.count('`')} pt={pt.count('`')}")
        if en.count("\n") != pt.count("\n"):
            errs.append(f"[QUEBRA] {k}: en={en.count(chr(10))} pt={pt.count(chr(10))}")
    extra = set(out) - {it["k"] for it in src}
    if extra:
        errs.append(f"[CHAVES EXTRAS] {list(extra)[:5]}")
    return errs

names = sys.argv[1:] or sorted(f[:-5] for f in os.listdir("chunks"))
total = 0
for n in names:
    e = check(n)
    total += len(e)
    print(f"{n}: {'OK' if not e else str(len(e)) + ' problema(s)'}")
    for x in e[:40]:
        print("  ", x)
sys.exit(1 if total else 0)
