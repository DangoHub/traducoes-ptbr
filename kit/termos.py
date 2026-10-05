"""Candidatos a glossário: nomes próprios e termos recorrentes dos lotes, com contagem e um exemplo."""
import collections
import json
import os
import re

PALAVRA_MAIUSCULA = re.compile(r"\b([A-Z][a-z]+(?:[ -][A-Z][a-z]+)*)\b")
INICIO_DE_FRASE = set(".!?(:~-…\"'*[“‘/")
COMUNS = set("""I The A An And But Or So If Then When What Why How Who Where Yes No Oh Ah Um Uh Hm Hmm Mm Okay Ok Well
Hey Hi Please Thank Thanks Sorry Wait Look Just This That These Those It Its He She We They You My Your Our His Her
Their Me Him Us Them Not Do Does Did Is Are Was Were Be Been Have Has Had Can Could Would Should Will Shall May Might
Must Let Come Go Get Got Now Here There Huh Haha Hehe Ahh Ohh Mmm Fuck Shit Damn God Sir Ma Miss Mr Mrs Ms""".split())


def termos(p, limite=150):
    cont, exemplo = collections.Counter(), {}
    for nome in p.lotes():
        for it in json.load(open(os.path.join(p.chunks, nome + ".json"), encoding="utf-8")):
            if "k" not in it:
                continue
            texto = re.sub(r"<[^<>]+>", "", it["en"])
            for m in PALAVRA_MAIUSCULA.finditer(texto):
                t = m.group(1)
                antes = texto[:m.start()].rstrip()
                if t.split()[0] in COMUNS or not antes or antes[-1] in INICIO_DE_FRASE:
                    continue
                cont[t] += 1
                exemplo.setdefault(t, texto.strip()[:140])
    for t, n in cont.most_common(limite):
        if n < 3:
            break
        print(f"{n:5d}  {t}  —  {exemplo[t]}")
