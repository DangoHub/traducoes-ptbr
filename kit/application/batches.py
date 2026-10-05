"""Batches: split units per conversation, consolidate translations and report progress.

Text states:
    pendente   in a batch, without output yet
    com erro   has output that fails validation (kept in src/rascunhos.json when preparing again)
    validado   passed validation and is in src/traducoes.json
    revisado   warning checked and recorded in src/revisao.json
"""
import collections
import os
import shutil

from kit.application.review import analyze_batch, load_reviewed, rules_for
from kit.domain.batching import group_units, pending_excerpt, split_into_batches
from kit.domain.units import CATEGORY_ORDER, IMPLICIT_KINDS
from kit.platform.storage import load_json, save_items, save_json, timestamp


def consolidate(project):
    """Merge valid outputs from out/ into src/traducoes.json ({target: [en, pt]}); return (bank, changed).

    Outputs that fail validation go to src/rascunhos.json so they are not lost.
    """
    bank = load_json(project.translations_path, {})
    drafts = load_json(project.drafts_path, {})
    index = load_json(project.index_path, {})
    rules = rules_for(project)
    changed = 0
    for batch in project.batches():
        analysis = analyze_batch(project, batch, rules)
        output = analysis.output
        if not isinstance(output, dict):
            continue
        errors = {problem.key: problem.errors for problem in analysis.problems if problem.errors}
        for key, entry in index.get(batch, {}).items():
            for target in entry["alvos"]:
                if key in analysis.valid:
                    drafts.pop(target, None)
                    record = [entry["en"], analysis.valid[key]]
                    if bank.get(target) != record:
                        bank[target] = record
                        changed += 1
                elif isinstance(output.get(key), str) and output[key].strip():
                    drafts[target] = {"en": entry["en"], "pt": output[key], "erros": errors.get(key, [])}
    save_json(project.translations_path, bank, indent=0)
    save_json(project.drafts_path, drafts, indent=0)
    return bank, changed


def archive_batches(project):
    """Copy the current chunks/, out/ and index to work/historico/<timestamp>/ before rebuilding them."""
    destination = os.path.join(project.work_dir, "historico", timestamp())
    for source in (project.chunks_dir, project.out_dir):
        if os.path.isdir(source):
            shutil.copytree(source, os.path.join(destination, os.path.basename(source)))
    if os.path.isfile(project.index_path):
        shutil.copyfile(project.index_path, os.path.join(destination, "indice.json"))
    return destination


def _reset_dir(path):
    shutil.rmtree(path, ignore_errors=True)
    os.makedirs(path)


def _build_batch(entries, bank, drafts, stats):
    """Batch file items and their index ({k: {"en", "alvos"}})."""
    items, index = [], {}
    for unit, is_reference, starts_excerpt in entries:
        item = {} if is_reference else {"k": str(len(index) + 1)}
        if starts_excerpt and unit.scene:
            item["cena"] = unit.scene
        if unit.speaker:
            item["quem"] = unit.speaker
        if unit.kind not in IMPLICIT_KINDS:
            item["tipo"] = unit.kind
        item["en"] = unit.text
        if is_reference:
            item["pt"] = bank[unit.primary_target][1]
            stats["references"] += 1
        else:
            draft = drafts.get(unit.primary_target)
            if draft and draft["en"] == unit.text:
                item["rascunho"] = draft["pt"]
                if draft["erros"]:
                    item["erro"] = "; ".join(draft["erros"])
                stats["drafts"] += 1
            index[item["k"]] = {"en": unit.text, "alvos": unit.targets}
        items.append(item)
    return items, index


def prepare(project):
    """Extract from the game and rebuild chunks/ and out/ without losing work.

    First consolidates the outputs (valid ones into the bank, invalid ones into drafts) and archives the
    current batches. Texts whose English was already validated do not come back; drafts come back with
    their item to be fixed.
    """
    if project.batches():
        _, changed = consolidate(project)
        print(f"Saídas atuais consolidadas ({changed} novas); lotes anteriores arquivados em {archive_batches(project)}")
    bank = load_json(project.translations_path, {})
    drafts = load_json(project.drafts_path, {})
    units = [unit for unit in project.engine().extract() if unit.translatable]

    def is_done(unit):
        return all(bank.get(target, [None])[0] == unit.text for target in unit.targets)

    def weight(unit, is_reference):
        return len(unit.text) + (len(bank[unit.primary_target][1]) if is_reference else 0)

    _reset_dir(project.chunks_dir)
    _reset_dir(project.out_dir)

    index, stats = {}, collections.Counter()
    for category in CATEGORY_ORDER:
        groups = group_units([unit for unit in units if unit.category == category])
        excerpts = [excerpt for group in groups if (excerpt := pending_excerpt(group, is_done))]
        for n, entries in enumerate(split_into_batches(excerpts, project.batch_max_chars, weight)):
            name = f"{category}_{n:03d}"
            items, index[name] = _build_batch(entries, bank, drafts, stats)
            save_items(project.chunk_path(name), items)

    live_targets = {target for batch in index.values() for entry in batch.values() for target in entry["alvos"]}
    save_json(project.drafts_path, {t: d for t, d in drafts.items() if t in live_targets}, indent=0)
    save_json(project.index_path, index, indent=0)
    pending = sum(len(batch) for batch in index.values())
    done = sum(1 for unit in units if is_done(unit))
    save_json(project.summary_path, {"para_traduzir": len(units), "ja_traduzidas": done})
    print(f"Unidades para traduzir: {len(units)} ({done} já validadas, {pending} nos lotes, "
          f"{stats['references']} falas de referência, {stats['drafts']} com rascunho a corrigir).")
    for category in CATEGORY_ORDER:
        names = [name for name in index if name.startswith(category)]
        if names:
            print(f"  {category}: {len(names)} lotes, {sum(len(index[n]) for n in names)} textos")


def status(project, detailed=False):
    """Print progress by state and return the batches still pending (no output or with errors)."""
    rules = rules_for(project)
    reviewed = load_reviewed(project)
    totals = collections.Counter()
    pending = []
    for batch in project.batches():
        analysis = analyze_batch(project, batch, rules, reviewed)
        errors = sum(len(problem.errors) for problem in analysis.problems)
        totals["items"] += analysis.item_count
        totals["valid"] += len(analysis.valid)
        totals["warnings"] += sum(len(problem.warnings) for problem in analysis.problems)
        if analysis.output is None:
            totals["without_output"] += 1
            pending.append(batch)
        elif errors:
            totals["with_errors"] += 1
            totals["items_with_errors"] += sum(1 for problem in analysis.problems if problem.errors and problem.key)
            pending.append(batch)
        if detailed:
            print(f"{batch}: {len(analysis.valid)}/{analysis.item_count}" + (f"  {errors} erros" if errors else ""))
    summary = load_json(project.summary_path, {})
    overall = summary.get("para_traduzir", totals["items"])
    validated = summary.get("ja_traduzidas", 0) + totals["valid"]
    percent = 100 * validated / overall if overall else 0
    print(f"{project.slug}: {validated}/{overall} textos ({percent:.1f}%) | lotes: {len(project.batches())}, "
          f"sem saída: {totals['without_output']}, com erro: {totals['with_errors']}")
    still_pending = totals["items"] - totals["valid"] - totals["items_with_errors"]
    print(f"  validados: {validated} | com erro: {totals['items_with_errors']} | pendentes: {still_pending} | "
          f"avisos a revisar: {totals['warnings']} | revisados: {len(reviewed)}")
    return pending
