"""Batch planning: keeps conversations together and adds approved neighbours as reference."""
from typing import NamedTuple

REFERENCE_BEFORE, REFERENCE_AFTER = 3, 1


class BatchEntry(NamedTuple):
    unit: object
    is_reference: bool
    starts_excerpt: bool


def group_units(units):
    """Consecutive units of the same group; units without a group stand alone."""
    groups, current_key = [], object()
    for unit in units:
        key = unit.group or id(unit)
        if not groups or key != current_key:
            groups.append([])
            current_key = key
        groups[-1].append(unit)
    return groups


def pending_excerpt(units, is_done):
    """[(unit, is_reference)] of a group that goes into a batch.

    Whole group pending: all of it. Only part pending: the pending units plus, as reference,
    up to REFERENCE_BEFORE approved units before and REFERENCE_AFTER after each one.
    """
    pending = [i for i, unit in enumerate(units) if not is_done(unit)]
    if not pending:
        return []
    if len(pending) == len(units):
        return [(unit, False) for unit in units]
    included = set()
    for i in pending:
        included.update(range(max(0, i - REFERENCE_BEFORE), min(len(units), i + REFERENCE_AFTER + 1)))
    return [(units[i], is_done(units[i])) for i in sorted(included)]


def split_into_batches(excerpts, limit, weight):
    """Pack excerpts into batches of up to `limit` weight; batches with only references are dropped."""
    batches, current, size = [], [], 0
    for excerpt in excerpts:
        excerpt_size = sum(weight(unit, ref) for unit, ref in excerpt)
        if current and size + excerpt_size > limit:
            batches.append(current)
            current, size = [], 0
        for i, (unit, ref) in enumerate(excerpt):
            if current and size + weight(unit, ref) > limit and size >= limit // 2:
                batches.append(current)
                current, size = [], 0
            current.append(BatchEntry(unit, ref, i == 0 or not current))
            size += weight(unit, ref)
    if current:
        batches.append(current)
    return [batch for batch in batches if any(not entry.is_reference for entry in batch)]
