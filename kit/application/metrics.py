"""Token metrics per step.

The kit does not see Cursor's real usage (each agent tool call re-sends the whole context), but it
measures what each step hands to the agent. Each `prompt` appends a line to work/metricas.jsonl;
`metricas` summarises that history and measures the current batches.
"""
import collections
import datetime
import os

from kit.platform.storage import append_jsonl, load_json, read_jsonl, read_text
from kit.platform.tokens import count_tokens

BATCH_PARTS = ("texto", "referencia", "rascunho", "estrutura")


def log_path(project):
    return os.path.join(project.work_dir, "metricas.jsonl")


def record(project, kind, names, **measures):
    append_jsonl(log_path(project), {
        "quando": datetime.datetime.now().isoformat(timespec="seconds"),
        "tipo": kind,
        "pacotes": names,
        **measures,
    })


def measure_batch(project, batch):
    """Tokens of the batch file split into text to translate, references, drafts and structure."""
    path = project.chunk_path(batch)
    items = load_json(path, [])
    text = sum(count_tokens(item["en"]) for item in items if "k" in item)
    references = sum(count_tokens(item["en"]) + count_tokens(item.get("pt", "")) for item in items if "k" not in item)
    drafts = sum(count_tokens(item.get("rascunho", "")) for item in items)
    total = count_tokens(read_text(path))
    return {"total": total, "texto": text, "referencia": references, "rascunho": drafts,
            "estrutura": total - text - references - drafts}


def print_summary(project):
    totals = collections.Counter()
    batches = project.batches()
    for batch in batches:
        totals.update(measure_batch(project, batch))
    print(f"Lotes atuais ({len(batches)}): {totals['total']} tokens de entrada")
    for part in BATCH_PARTS:
        percent = 100 * totals[part] / totals["total"] if totals["total"] else 0
        print(f"  {part:<11} {totals[part]:>9}  ({percent:.0f}%)")
    history = read_jsonl(log_path(project))
    if not history:
        print("Sem histórico de prompts (work/metricas.jsonl).")
        return
    by_kind = collections.defaultdict(collections.Counter)
    for entry in history:
        counter = by_kind[entry["tipo"]]
        counter["agentes"] += 1
        counter["pacotes"] += len(entry["pacotes"])
        counter.update({k: v for k, v in entry.items() if isinstance(v, int)})
    for kind, counter in by_kind.items():
        print(f"{kind}: {counter['agentes']} agentes, {counter['pacotes']} pacotes | itens {counter['tokens_itens']} | "
              f"contexto {counter['tokens_contexto']} (guia inteiro seria {counter['tokens_guia_inteiro']})")
    print("Para o custo real, compare o painel do Cursor por onda com estes números: "
          "cada chamada de ferramenta do agente reenvia contexto + itens já lidos.")
