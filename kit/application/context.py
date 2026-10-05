"""Per-package context file: AGENTE.md plus the game guide filtered for the texts received."""
import os

from kit.config import paths
from kit.domain.guide import filter_guide, relevance_text
from kit.platform.storage import read_text, write_text


def context_path(project, names):
    label = names[0] if len(names) == 1 else f"{names[0]}+{len(names) - 1}"
    return os.path.join(project.work_dir, "contexto", label + ".md")


def write_context(project, names, items):
    """Write work/contexto/<package>.md and return (path, full guide text, generated text)."""
    agent_guide = read_text(paths.AGENT_GUIDE_PATH).strip()
    guide = read_text(project.guide_path)
    filtered = filter_guide(guide, relevance_text(items))
    text = (f"{agent_guide}\n\n---\n\n# Guia deste pacote: {project.name}\n\n"
            f"Trechos do guia do jogo que valem para os textos que você recebeu.\n\n{filtered}")
    path = context_path(project, names)
    write_text(path, text)
    return path, agent_guide + "\n" + guide, text
