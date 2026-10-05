"""Fake game and project fixtures shared by the tests."""
import copy
import os
import tempfile
import unittest
from unittest import mock

from kit import engines
from kit.config import paths
from kit.config.project import Project
from kit.domain.units import TranslationUnit
from kit.engines.base import Engine
from kit.platform.storage import load_json, save_json


def line(n, text, group="g1", speaker="Jenna (F)"):
    return TranslationUnit(text, [f"D|{n}"], "dialogo", group, group, speaker)


class FakeEngine(Engine):
    name = "falsa"
    units = []

    def extract(self):
        return copy.deepcopy(self.units)


class ProjectTestCase(unittest.TestCase):
    """A temporary project "jogo" whose engine returns FakeEngine.units (8 dialogue lines by default)."""

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        save_json(os.path.join(tmp.name, "jogo", "jogo.json"), {"nome": "Jogo", "engine": FakeEngine.name})
        for patcher in (mock.patch.object(paths, "PROJECTS_DIR", tmp.name),
                        mock.patch.dict(engines.ENGINES, {FakeEngine.name: FakeEngine})):
            patcher.start()
            self.addCleanup(patcher.stop)
        FakeEngine.units = [line(i, f"Line number {i}.") for i in range(1, 9)]
        self.project = Project("jogo")

    def chunk(self, batch):
        return load_json(self.project.chunk_path(batch))

    def pending_items(self, batch):
        return [item for item in self.chunk(batch) if "k" in item]

    def translate_all(self, overrides=None):
        for batch in self.project.batches():
            output = {item["k"]: "Fala " + item["en"].split()[-1] for item in self.pending_items(batch)}
            output.update(overrides or {})
            save_json(self.project.output_path(batch), output)
