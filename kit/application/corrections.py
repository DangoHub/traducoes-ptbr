"""Correction packages: only the items with problems, with the reason and the neighbouring lines.

    work/correcoes/correcao_000.json        input (one item per line)
    work/correcoes/correcao_000.saida.json  {"<batch>#<k>": "new translation" | "="}

"=" keeps the current translation (only valid for warnings; records the decision in src/revisao.json).
`apply_package` writes only the package ids into out/<batch>.json and validates them again.
"""
import glob
import json
import os
import shutil

from kit.application.review import INVALID_OUTPUT, analyze_batch, load_reviewed, record_reviewed, rules_for
from kit.domain.units import KIND_LINE
from kit.domain.validation import check_translation
from kit.platform.storage import load_json, save_items, save_json, timestamp

PACKAGE_PREFIX = "correcao_"
OUTPUT_SUFFIX = ".saida.json"
KEEP_CURRENT = "="
NEIGHBOURS_BEFORE, NEIGHBOURS_AFTER = 2, 1
PACKAGE_MAX_CHARS = 8000
PROBLEM_ERROR, PROBLEM_WARNING = "erro", "aviso"


def corrections_dir(project):
    return os.path.join(project.work_dir, "correcoes")


def package_path(project, name):
    return os.path.join(corrections_dir(project), name + ".json")


def package_output_path(project, name):
    return os.path.join(corrections_dir(project), name + OUTPUT_SUFFIX)


def is_package(name):
    return name.startswith(PACKAGE_PREFIX)


def load_package(project, name):
    return load_json(package_path(project, name), [])


def _context_line(item, output):
    pt = output.get(item["k"]) if "k" in item else item.get("pt")
    speaker = item.get("quem") or item.get("tipo")
    return f"{speaker + ': ' if speaker else ''}{item['en']} => {pt if pt else '(sem tradução)'}"


def _scene_at(chunk, index):
    for j in range(index, -1, -1):
        if chunk[j].get("cena"):
            return chunk[j]["cena"]
    return None


def _drop_extra_keys(project, batch, chunk, output):
    keys = {item["k"] for item in chunk if "k" in item}
    extra = [key for key in output if key not in keys]
    for key in extra:
        del output[key]
    if extra:
        save_json(project.output_path(batch), output)
    return len(extra)


def _correction_item(batch, chunk, index, problem, output):
    item = chunk[index]
    entry = {
        "id": f"{batch}#{problem.key}",
        "problema": PROBLEM_ERROR if problem.errors else PROBLEM_WARNING,
        "motivo": "; ".join(problem.errors or problem.warnings),
    }
    if scene := _scene_at(chunk, index):
        entry["cena"] = scene
    for field in ("quem", "tipo"):
        if item.get(field):
            entry[field] = item[field]
    entry["en"] = item["en"]
    entry["pt"] = output.get(problem.key)
    neighbours = [
        _context_line(chunk[j], output)
        for j in range(index - NEIGHBOURS_BEFORE, index + NEIGHBOURS_AFTER + 1)
        if j != index and 0 <= j < len(chunk)
    ]
    if neighbours:
        entry["contexto"] = neighbours
    return entry


def _split_packages(items, limit):
    packages, current, size = [], [], 0
    for item in items:
        item_size = len(json.dumps(item, ensure_ascii=False))
        if current and size + item_size > limit:
            packages.append(current)
            current, size = [], 0
        current.append(item)
        size += item_size
    if current:
        packages.append(current)
    return packages


def generate(project, include_warnings=False, limit_chars=PACKAGE_MAX_CHARS):
    """Rebuild work/correcoes/ with the errors (and, if asked, unreviewed warnings). Return the names."""
    directory = corrections_dir(project)
    unapplied = glob.glob(os.path.join(directory, "*" + OUTPUT_SUFFIX))
    if unapplied:
        raise SystemExit(f"Há saídas de correção não aplicadas: {[os.path.basename(f) for f in unapplied]}. "
                         "Rode 'aplicar' antes de gerar novos pacotes.")
    rules = rules_for(project)
    reviewed = load_reviewed(project)
    items, redo, cleaned = [], [], 0
    for batch in project.batches():
        analysis = analyze_batch(project, batch, rules, reviewed)
        if analysis.output is None:
            continue
        if analysis.output == INVALID_OUTPUT:
            redo.append(batch)
            continue
        cleaned += _drop_extra_keys(project, batch, analysis.chunk, analysis.output)
        positions = {item["k"]: i for i, item in enumerate(analysis.chunk) if "k" in item}
        for problem in analysis.problems:
            if problem.key is None or not (problem.errors or (include_warnings and problem.warnings)):
                continue
            items.append(_correction_item(batch, analysis.chunk, positions[problem.key], problem, analysis.output))

    shutil.rmtree(directory, ignore_errors=True)
    names = []
    for n, package in enumerate(_split_packages(items, limit_chars)):
        names.append(f"{PACKAGE_PREFIX}{n:03d}")
        save_items(package_path(project, names[-1]), package)
    if cleaned:
        print(f"Chaves extras removidas automaticamente: {cleaned}")
    if redo:
        print(f"Saídas com JSON inválido (traduzir o lote de novo): {', '.join(redo)}")
    errors = sum(1 for item in items if item["problema"] == PROBLEM_ERROR)
    print(f"{len(items)} itens ({errors} erros, {len(items) - errors} avisos) em {len(names)} pacotes: {', '.join(names)}")
    return names


def _archive_package(project, name):
    archive = os.path.join(project.work_dir, "historico", "correcoes")
    os.makedirs(archive, exist_ok=True)
    stamp = timestamp()
    for path in (package_path(project, name), package_output_path(project, name)):
        shutil.move(path, os.path.join(archive, f"{stamp}_{os.path.basename(path)}"))


def apply_package(project, name):
    """Write the package corrections into out/ (package ids only) and record the reviewed warnings."""
    items = load_package(project, name)
    answers = load_json(package_output_path(project, name))
    if not items or answers is None:
        raise SystemExit(f"Pacote ou saída ausente: {name}.json / {name}{OUTPUT_SUFFIX} em {corrections_dir(project)}")
    rules = rules_for(project)
    outputs, reviews, unanswered, still_wrong = {}, [], [], []
    for item in items:
        answer = answers.get(item["id"])
        if not isinstance(answer, str) or not answer.strip():
            unanswered.append(item["id"])
            continue
        batch, key = item["id"].split("#")
        if batch not in outputs:
            outputs[batch] = project.load_output(batch, {})
        if answer == KEEP_CURRENT:
            if item["problema"] == PROBLEM_WARNING and item["pt"]:
                reviews.append((item["en"], item["pt"], item["motivo"]))
            else:
                still_wrong.append(item["id"])
            continue
        outputs[batch][key] = answer
        errors, _ = check_translation(item["en"], answer, rules, item.get("tipo", KIND_LINE))
        if errors:
            still_wrong.append(f"{item['id']} ({'; '.join(errors)})")
        elif item["problema"] == PROBLEM_WARNING:
            reviews.append((item["en"], answer, item["motivo"]))
    for batch, output in outputs.items():
        save_json(project.output_path(batch), output)
    recorded = record_reviewed(project, reviews)
    _archive_package(project, name)
    applied = len(items) - len(unanswered) - len(still_wrong)
    print(f"{name}: {applied} aplicados, {recorded} avisos revisados, "
          f"{len(unanswered)} sem resposta, {len(still_wrong)} ainda com erro")
    for entry in (unanswered + still_wrong)[:10]:
        print("  ", entry)
    return not (unanswered or still_wrong)
