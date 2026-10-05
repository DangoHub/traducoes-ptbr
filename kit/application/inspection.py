"""Quick read-only views of the batches for the orchestrator."""


def _translatable_items(project, batch):
    return [item for item in project.load_chunk(batch) if "k" in item]


def search(project, text, limit=20):
    """Find `text` (case-insensitive) in the English and the translation of every batch."""
    needle = text.lower()
    found = 0
    for batch in project.batches():
        output = project.load_output(batch, {})
        for item in _translatable_items(project, batch):
            pt = output.get(item["k"], "")
            if needle not in item["en"].lower() and needle not in pt.lower():
                continue
            found += 1
            if found <= limit:
                speaker = f" {item['quem']}:" if item.get("quem") else ""
                print(f"out/{batch}.json  \"{item['k']}\"{speaker}")
                print(f"   EN: {item['en']}")
                print(f"   PT: {pt}")
    extra = f" (mostrando {limit})" if found > limit else ""
    print(f"{found} resultado(s){extra}")


def print_sample(project, batch, count=30, start=0):
    """English and Portuguese side by side for a quick review."""
    output = project.load_output(batch, {})
    for item in _translatable_items(project, batch)[start:start + count]:
        if item.get("cena"):
            print(f"== {item['cena']}")
        label = item.get("quem") or item.get("tipo", "")
        print(f"[{item['k']}] {label}: {item['en']}\n     -> {output.get(item['k'], '(sem tradução)')}")
