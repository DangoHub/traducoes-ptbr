"""Valida traduções: python validate.py [lote_000 lote_001 ...] (sem argumentos = todos os lotes com saída)."""
import os, sys, json, re, collections
sys.stdout.reconfigure(encoding="utf-8")
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
CHUNKS, OUT = os.path.join(ROOT, "chunks"), os.path.join(ROOT, "out")

TAG_CURLY = re.compile(r"\{[^{}]*\}")
TAG_SQUARE = re.compile(r"\[[^\[\]]*\]")
TAG_DEV = re.compile(r"<<[A-Za-z]+")


def is_bracket_choice(text):
    """Opção de ação inteira entre colchetes, ex.: '[Choke him]' — é exibida e deve ser traduzida."""
    t = TAG_CURLY.sub("", text).strip()
    return t.startswith("[") and t.endswith("]") and len(TAG_SQUARE.findall(t)) == 1


def check(en, pt):
    errs = []
    if not isinstance(pt, str) or not pt.strip():
        return ["vazia"]
    rules = [("{}", TAG_CURLY), ("<<", TAG_DEV)]
    if is_bracket_choice(en):
        if not is_bracket_choice(pt):
            errs.append("opção entre colchetes deve continuar inteira entre colchetes")
    else:
        rules.append(("[]", TAG_SQUARE))
    for name, rx in rules:
        a, b = collections.Counter(rx.findall(en)), collections.Counter(rx.findall(pt))
        if a != b:
            errs.append(f"tags {name} diferentes: faltam {list((a - b).elements())} sobram {list((b - a).elements())}")
    if en.count("\n") != pt.count("\n"):
        errs.append(f"quebras de linha {en.count(chr(10))} -> {pt.count(chr(10))}")
    try:
        pt.encode("cp1252")
    except UnicodeEncodeError as ex:
        errs.append(f"caractere fora do cp1252: {pt[ex.start:ex.end]!r}")
    return errs


def main(names):
    if not names:
        names = sorted(f[:-5] for f in os.listdir(OUT) if f.endswith(".json")) if os.path.isdir(OUT) else []
    total_err = 0
    for name in names:
        chunk = json.load(open(os.path.join(CHUNKS, name + ".json"), encoding="utf-8"))
        path = os.path.join(OUT, name + ".json")
        if not os.path.isfile(path):
            print(f"{name}: SEM SAÍDA"); total_err += 1; continue
        try:
            out = json.load(open(path, encoding="utf-8"))
        except Exception as ex:
            print(f"{name}: JSON inválido: {ex}"); total_err += 1; continue
        errs = 0
        for item in chunk:
            k = item["k"]
            if k not in out:
                print(f"{name} #{k}: FALTANDO"); errs += 1; continue
            for e in check(item["en"], out[k]):
                print(f"{name} #{k}: {e}\n   EN: {item['en']!r}\n   PT: {out[k]!r}"); errs += 1
        extra = set(out) - {i["k"] for i in chunk}
        if extra:
            print(f"{name}: chaves extras {sorted(extra)[:10]}"); errs += len(extra)
        print(f"{name}: {len(chunk)} falas, {errs} problemas")
        total_err += errs
    print("TOTAL DE PROBLEMAS:", total_err)
    return total_err


if __name__ == "__main__":
    sys.exit(1 if main(sys.argv[1:]) else 0)
