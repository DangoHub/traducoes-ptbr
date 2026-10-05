"""Glossary consistency and term candidates.

projetos/<game>/glossario.json:
    {"termos": {"Crush Waves": "Ondas de Paixão", ...},   English term -> required Portuguese form
     "trocas":  [["Ondas Crush", "Ondas de Paixão"], ...]} replacements applied by `standardize`
"""
import collections
import re

from kit.platform.storage import load_json, save_json

CAPITALIZED_PHRASE = re.compile(r"\b([A-Z][a-z]+(?:[ -][A-Z][a-z]+)*)\b")
TAG = re.compile(r"<[^<>]+>")
SENTENCE_START = set(".!?(:~-…\"'*[“‘/")
COMMON_WORDS = set("""I The A An And But Or So If Then When What Why How Who Where Yes No Oh Ah Um Uh Hm Hmm Mm Okay Ok Well
Hey Hi Please Thank Thanks Sorry Wait Look Just This That These Those It Its He She We They You My Your Our His Her
Their Me Him Us Them Not Do Does Did Is Are Was Were Be Been Have Has Had Can Could Would Should Will Shall May Might
Must Let Come Go Get Got Now Here There Huh Haha Hehe Ahh Ohh Mmm Fuck Shit Damn God Sir Ma Miss Mr Mrs Ms""".split())
MIN_TERM_COUNT = 3
EXAMPLE_CHARS = 140


def load_glossary(project):
    return load_json(project.glossary_path, {"termos": {}, "trocas": []})


def _replace_all(text, replacements):
    for wrong, right in replacements:
        text = text.replace(wrong, right)
    return text


def standardize(project):
    """Apply the glossary replacements to out/ and to the consolidated bank."""
    replacements = load_glossary(project)["trocas"]
    if not replacements:
        print("glossario.json sem 'trocas'.")
        return
    in_outputs = 0
    for batch in project.batches():
        output = project.load_output(batch)
        if not output:
            continue
        changed = 0
        for key, text in output.items():
            fixed = _replace_all(text, replacements)
            if fixed != text:
                output[key] = fixed
                changed += 1
        if changed:
            save_json(project.output_path(batch), output)
            in_outputs += changed
    bank = load_json(project.translations_path, {})
    in_bank = 0
    for target, (en, pt) in bank.items():
        fixed = _replace_all(pt, replacements)
        if fixed != pt:
            bank[target] = [en, fixed]
            in_bank += 1
    if in_bank:
        save_json(project.translations_path, bank, indent=0)
    print(f"Trocas aplicadas: {in_outputs} em out/, {in_bank} em src/traducoes.json")


def _translated_pairs(project):
    """[(reference, english, portuguese)] from the current outputs and the consolidated bank."""
    pairs = []
    for batch in project.batches():
        output = project.load_output(batch, {})
        pairs += [(f"{batch}#{item['k']}", item["en"], output[item["k"]])
                  for item in project.load_chunk(batch) if item.get("k") in output]
    pairs += [(target, en, pt) for target, (en, pt) in load_json(project.translations_path, {}).items()]
    return pairs


def check_terms(project, examples=2):
    """Items where a glossary term was not translated with the agreed form."""
    terms = load_glossary(project)["termos"]
    pairs = _translated_pairs(project)
    failures = collections.defaultdict(list)
    for term_en, term_pt in terms.items():
        pattern = re.compile(r"\b" + re.escape(term_en) + r"\b", re.I)
        for ref, en, pt in pairs:
            if pattern.search(en) and term_pt.lower() not in pt.lower():
                failures[term_en].append((ref, pt))
    for term_en, entries in sorted(failures.items(), key=lambda x: -len(x[1])):
        print(f"{terms[term_en]!r} ({term_en}): {len(entries)} sem a forma do glossário")
        for ref, pt in entries[:examples]:
            print(f"   {ref}: {pt[:120]}")
    if not failures:
        print("Glossário seguido em todos os itens.")
    return failures


def term_candidates(project, limit=150):
    """Print proper names and recurring terms of the batches, with a count and an example."""
    counts, example = collections.Counter(), {}
    for batch in project.batches():
        for item in project.load_chunk(batch):
            if "k" not in item:
                continue
            text = TAG.sub("", item["en"])
            for match in CAPITALIZED_PHRASE.finditer(text):
                term = match.group(1)
                before = text[:match.start()].rstrip()
                if term.split()[0] in COMMON_WORDS or not before or before[-1] in SENTENCE_START:
                    continue
                counts[term] += 1
                example.setdefault(term, text.strip()[:EXAMPLE_CHARS])
    for term, n in counts.most_common(limit):
        if n < MIN_TERM_COUNT:
            break
        print(f"{n:5d}  {term}  —  {example[term]}")
