"""Translation unit: one source text and every place in the game where its translation goes.

Category and kind values are written to the batch files read by the agents, so they stay in Portuguese.
"""
from dataclasses import dataclass, field

CATEGORY_DIALOGUE = "dialogo"
CATEGORY_TEXTS = "textos"
CATEGORY_INTERFACE = "interface"
CATEGORY_ORDER = (CATEGORY_DIALOGUE, CATEGORY_TEXTS, CATEGORY_INTERFACE)

KIND_LINE = "fala"
KIND_CHOICE = "escolha"
KIND_UI = "ui"
IMPLICIT_KINDS = (KIND_LINE, KIND_UI)


@dataclass
class TranslationUnit:
    """
    text          original text
    targets       ids where the translation is written; more than one = deduplicated text.
                  Each id must be unique in the final file, even when the game repeats internal ids.
    category      batch prefix (CATEGORY_*)
    group         conversation/screen id; batches never split a group if it fits
    scene         readable label of the group (dialogue name, mission...)
    speaker       who speaks, e.g. "Jenna (F)"
    kind          KIND_* or a free description ("nome de item", "descricao de missao"...)
    translatable  False for texts shipped as they are (numbers, placeholders)
    """

    text: str
    targets: list = field(default_factory=list)
    category: str = CATEGORY_DIALOGUE
    group: str | None = None
    scene: str | None = None
    speaker: str | None = None
    kind: str = KIND_LINE
    translatable: bool = True

    @property
    def primary_target(self):
        return self.targets[0]
