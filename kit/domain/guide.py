"""Per-package excerpt of GUIA_TRADUCAO.md.

- prose (outside tables) is always kept: universe, tone and general rules;
- a table row is kept only if a term of its first column appears in the lines, speakers or scenes;
- under "## Personagens", each "### Name / Alias" is kept only if the character speaks or is mentioned.
"""
import re

CHARACTERS_SECTION = "personagens"
TERM_STRIP = " .!?:;\"'“”"


def cell_terms(cell):
    text = re.sub(r"\([^)]*\)", "", cell).replace("**", "").replace("`", "")
    return [t for t in (x.strip(TERM_STRIP) for x in re.split(r"[/,]", text)) if len(t) >= 2]


def mentions_any(terms, text):
    return any(re.search(r"(?<![\w])" + re.escape(t) + r"(?![\w])", text, re.I) for t in terms)


def _sections(text):
    """[[heading line | None, level, body lines]] split on markdown headings."""
    sections = [[None, 0, []]]
    for line in text.splitlines():
        match = re.match(r"^(#+)\s", line)
        if match:
            sections.append([line, len(match.group(1)), []])
        else:
            sections[-1][2].append(line)
    return sections


def _is_table_row(line):
    return line.lstrip().startswith("|")


def _filter_tables(lines, text):
    kept, table = [], []

    def flush():
        if len(table) > 2:
            kept.extend(table)
        table.clear()

    for line in lines:
        if not _is_table_row(line):
            flush()
            kept.append(line)
            continue
        if len(table) < 2:
            table.append(line)
            continue
        first_cell = line.strip().strip("|").split("|")[0]
        if mentions_any(cell_terms(first_cell), text):
            table.append(line)
    flush()
    return kept


def filter_guide(guide, text):
    """The guide with only the parts relevant to `text` (lines, speakers and scenes joined)."""
    kept, in_characters = [], False
    for heading, level, lines in _sections(guide):
        if level == 1:
            continue
        title = heading.lstrip("# ") if heading else ""
        if level == 2:
            in_characters = title.lower().startswith(CHARACTERS_SECTION)
        elif level == 3 and in_characters and not mentions_any(cell_terms(title), text):
            continue
        body = _filter_tables(lines, text)
        had_table = any(_is_table_row(line) for line in lines)
        if had_table and not any(line.strip() for line in body):
            continue
        if heading:
            kept.append(heading)
        kept.extend(body)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(kept)).strip() + "\n"


def relevance_text(items):
    """Everything in the package that can mention a guide entry."""
    parts = []
    for item in items:
        parts += [item.get("en") or "", item.get("quem") or "", item.get("cena") or ""]
        parts += item.get("contexto", [])
    return "\n".join(parts)
