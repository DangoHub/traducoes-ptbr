import os

from kit.application.batches import prepare, status
from kit.platform.storage import load_json
from tests.support import FakeEngine, ProjectTestCase


class IncrementalTranslationTest(ProjectTestCase):
    def test_changed_line_comes_with_approved_references(self):
        prepare(self.project)
        self.translate_all()
        FakeEngine.units[5].text = "Changed line."
        prepare(self.project)
        items = self.chunk("dialogo_000")
        references = [item for item in items if "k" not in item]
        self.assertEqual([item["en"] for item in self.pending_items("dialogo_000")], ["Changed line."])
        self.assertEqual(len(references), 4)
        self.assertTrue(all("pt" in r for r in references))
        self.assertEqual(items[0].get("cena"), "g1")

    def test_fully_translated_game_has_no_batches(self):
        prepare(self.project)
        self.translate_all()
        prepare(self.project)
        self.assertEqual(self.project.batches(), [])


class SafeResumeTest(ProjectTestCase):
    def test_invalid_output_becomes_draft_and_batches_are_archived(self):
        prepare(self.project)
        self.translate_all({"3": ""})
        prepare(self.project)
        self.assertEqual(len(self.pending_items("dialogo_000")), 1)
        self.assertEqual(len(load_json(self.project.translations_path)), 7)
        self.assertTrue(os.path.isdir(os.path.join(self.project.work_dir, "historico")))

    def test_draft_comes_back_with_the_reason(self):
        FakeEngine.units[2].text = "<b><i>Hi</i></b> there."
        prepare(self.project)
        self.translate_all({"3": "<b><i>Oi</b></i> aí."})
        prepare(self.project)
        item = self.pending_items("dialogo_000")[0]
        self.assertEqual(item["rascunho"], "<b><i>Oi</b></i> aí.")
        self.assertIn("fora de ordem", item["erro"])


class StatusTest(ProjectTestCase):
    def test_lists_batches_without_output_or_with_errors(self):
        prepare(self.project)
        self.assertEqual(status(self.project), ["dialogo_000"])
        self.translate_all()
        self.assertEqual(status(self.project), [])
