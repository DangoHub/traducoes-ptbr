"""Batch review: validates agent outputs against their batch and keeps the warning review log.

Batch items without "k" are references (already translated) and are not validated.
Reviewed warnings live in src/revisao.json as [english, portuguese, warning] and stop showing up.
"""
import os
from dataclasses import dataclass
from typing import NamedTuple

from kit.domain.units import KIND_LINE
from kit.domain.validation import ValidationRules, check_translation
from kit.platform.storage import load_json, save_json

INVALID_OUTPUT = "invalido"
MISSING = "FALTANDO"


@dataclass
class Problem:
    key: str | None
    """Batch item key; None means a problem with the whole output file."""
    errors: list
    warnings: list


class BatchAnalysis(NamedTuple):
    chunk: list
    output: dict | str | None
    """None without an output file, INVALID_OUTPUT when the JSON does not parse."""
    problems: list
    valid: dict

    @property
    def item_count(self):
        return sum(1 for item in self.chunk if "k" in item)

    @property
    def has_errors(self):
        return any(problem.errors for problem in self.problems)


class BatchReport(NamedTuple):
    total: int
    translated: int
    errors: int
    warnings: int


def rules_for(project):
    return ValidationRules(project.validation)


def load_reviewed(project):
    return {(en, pt) for en, pt, *_ in load_json(project.reviewed_path, [])}


def record_reviewed(project, entries):
    """entries: [(english, portuguese, warning)]. The same pair is never reviewed twice."""
    log = load_json(project.reviewed_path, [])
    seen = {(en, pt) for en, pt, *_ in log}
    new = [list(entry) for entry in entries if (entry[0], entry[1]) not in seen]
    if new:
        save_json(project.reviewed_path, log + new, indent=0)
    return len(new)


def analyze_batch(project, batch, rules, reviewed=frozenset()):
    chunk = project.load_chunk(batch)
    path = project.output_path(batch)
    if not os.path.isfile(path):
        return BatchAnalysis(chunk, None, [], {})
    try:
        output = load_json(path)
        if not isinstance(output, dict):
            raise ValueError("a saída precisa ser um objeto {k: tradução}")
    except Exception as ex:
        return BatchAnalysis(chunk, INVALID_OUTPUT, [Problem(None, [f"JSON inválido: {ex}"], [])], {})

    problems, valid, keys = [], {}, set()
    for item in chunk:
        key = item.get("k")
        if key is None:
            continue
        keys.add(key)
        if key not in output:
            problems.append(Problem(key, [MISSING], []))
            continue
        errors, warnings = check_translation(item["en"], output[key], rules, item.get("tipo", KIND_LINE))
        if (item["en"], output[key]) in reviewed:
            warnings = []
        if errors or warnings:
            problems.append(Problem(key, errors, warnings))
        if not errors:
            valid[key] = output[key]
    extra = sorted(set(output) - keys)
    if extra:
        problems.append(Problem(None, [f"chaves que não existem no lote: {extra[:10]}"], []))
    return BatchAnalysis(chunk, output, problems, valid)


def report_batch(project, batch, rules, reviewed=frozenset(), show_warnings=True):
    """Print the batch problems and return the counters."""
    analysis = analyze_batch(project, batch, rules, reviewed)
    items = {item["k"]: item for item in analysis.chunk if "k" in item}
    output = analysis.output if isinstance(analysis.output, dict) else {}
    errors = warnings = 0
    for problem in analysis.problems:
        item = items.get(problem.key)
        detail = f"\n   EN: {item['en']!r}\n   PT: {output.get(problem.key)!r}" if item and problem.key in output else ""
        ref = f"{batch} #{problem.key}" if problem.key else batch
        for message in problem.errors:
            print(f"{ref}: ERRO {message}{detail if message != MISSING else ''}")
        if show_warnings:
            for message in problem.warnings:
                print(f"{ref}: aviso {message}{detail}")
        errors += len(problem.errors)
        warnings += len(problem.warnings)
    return BatchReport(len(items), len(analysis.valid), errors, warnings)
