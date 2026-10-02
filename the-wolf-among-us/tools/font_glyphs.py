import os, sys, struct
sys.stdout.reconfigure(encoding="utf-8")
D = os.path.join(os.path.dirname(__file__), "..", "work", "fonts")
NEED = "áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ"


def glyph_table(d):
    for q in range(100, len(d) - 200):
        if struct.unpack_from("<I", d, q)[0] == 32 and struct.unpack_from("<I", d, q + 48)[0] == 33:
            for k in range(0, 40):
                p = q - 48 * k - 4
                n = struct.unpack_from("<I", d, p)[0]
                if 50 < n < 70000 and p + 4 + 48 * n <= len(d):
                    codes = [struct.unpack_from("<I", d, p + 4 + 48 * i)[0] for i in range(n)]
                    if all(a < b for a, b in zip(codes, codes[1:])):
                        return p, n
    return None, 0


for fn in sorted(os.listdir(D)):
    d = open(os.path.join(D, fn), "rb").read()
    p, n = glyph_table(d)
    if p is None:
        print(fn, "tabela não encontrada"); continue
    codes = {}
    for i in range(n):
        code = struct.unpack_from("<I", d, p + 4 + 48 * i)[0]
        rect = struct.unpack_from("<4f", d, p + 4 + 48 * i + 12)
        codes[code] = rect
    present = "".join(c for c in NEED if c.encode("cp1252")[0] in codes)
    missing = "".join(c for c in NEED if c.encode("cp1252")[0] not in codes)
    ext = "".join(chr(c) if c < 256 else "?" for c in sorted(codes) if c > 126)
    print(f"{fn:38} glifos={n:4} tem=[{present}] falta=[{missing}]")
    print(f"{'':38} extras: {bytes(c for c in sorted(codes) if 126 < c < 256).decode('cp1252', 'replace')}")
