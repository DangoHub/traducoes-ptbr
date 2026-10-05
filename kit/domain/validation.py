"""Translation checks: errors block the build; warnings only show up for review."""
import collections
import re

from kit.domain.units import KIND_CHOICE, KIND_LINE

HTML_TAG = re.compile(r"<(/?)([A-Za-z]+)(?:=[^<>]*)?>")
CLOSING_TAG = re.compile(r"</([A-Za-z]+)>")
MARKUP = re.compile(r"<[^<>]+>|#\w+#|\{[^{}]*\}")
WORD = re.compile(r"[A-Za-z]{3,}")
ONOMATOPOEIA_PATTERN = re.compile(r"(.)\1\1|(.)\2$")
ONOMATOPOEIA_LETTERS = set("ahmngfuoeiyrsk")
MIN_WORDS_FOR_UNTRANSLATED = 3
CHOICE_EXTRA_CHARS = 8


class ValidationRules:
    """Validation settings from the "validacao" block of jogo.json."""

    def __init__(self, config):
        self.tag_patterns = [re.compile(r) for r in config["tags"]]
        self.check_line_breaks = config["quebras_de_linha"]
        self.encoding = config["codificacao"]
        self.choice_max_ratio = config["escolha_max_proporcao"]


def is_well_nested(text, closable_tags):
    stack = []
    for match in HTML_TAG.finditer(text):
        closing, name = match.group(1), match.group(2).lower()
        if name not in closable_tags:
            continue
        if not closing:
            stack.append(name)
        elif not stack or stack.pop() != name:
            return False
    return not stack


def content_words(text):
    """Words with 3+ letters outside markup that do not look like onomatopoeia ("Haaahh", "Nghh", "Mmm")."""
    plain = MARKUP.sub("", text)
    return [
        word for word in WORD.findall(plain)
        if not ONOMATOPOEIA_PATTERN.search(word.lower()) and not set(word.lower()) <= ONOMATOPOEIA_LETTERS
    ]


def check_translation(source, translation, rules, kind=KIND_LINE):
    """Return (errors, warnings) for one translated text."""
    if not isinstance(translation, str) or not translation.strip():
        return ["vazia"], []
    errors, warnings = [], []
    for pattern in rules.tag_patterns:
        expected = collections.Counter(pattern.findall(source))
        found = collections.Counter(pattern.findall(translation))
        if expected != found:
            missing, extra = list((expected - found).elements()), list((found - expected).elements())
            errors.append(f"tags diferentes: faltam {missing} sobram {extra}")
    closable = {name.lower() for name in CLOSING_TAG.findall(source)}
    if closable and not errors and is_well_nested(source, closable) and not is_well_nested(translation, closable):
        errors.append("tags fora de ordem (abertura e fechamento cruzados)")
    if rules.check_line_breaks and source.count("\n") != translation.count("\n"):
        errors.append(f"quebras de linha {source.count(chr(10))} -> {translation.count(chr(10))}")
    try:
        translation.encode(rules.encoding)
    except UnicodeEncodeError as ex:
        errors.append(f"caractere fora do {rules.encoding}: {translation[ex.start:ex.end]!r}")
    if kind == KIND_CHOICE and len(translation) > len(source) * rules.choice_max_ratio + CHOICE_EXTRA_CHARS:
        warnings.append(f"escolha longa ({len(source)} -> {len(translation)} caracteres)")
    if translation == source and len(content_words(source)) >= MIN_WORDS_FOR_UNTRANSLATED:
        warnings.append("igual ao inglês (não traduzida?)")
    return errors, warnings
