from kit.application import corrections
from kit.application.batches import prepare
from kit.application.review import load_reviewed, report_batch, rules_for
from kit.platform.storage import save_json
from tests.support import FakeEngine, ProjectTestCase


class CorrectionPackageTest(ProjectTestCase):
    def test_fixes_only_package_ids_and_records_review(self):
        FakeEngine.units[1].text = "Jenna Wright arrives today."
        prepare(self.project)
        self.translate_all({"1": "", "2": "Jenna Wright arrives today."})
        names = corrections.generate(self.project, include_warnings=True)
        items = corrections.load_package(self.project, names[0])
        self.assertEqual({i["id"]: i["problema"] for i in items},
                         {"dialogo_000#1": "erro", "dialogo_000#2": "aviso"})
        self.assertIn("contexto", items[0])

        save_json(corrections.package_output_path(self.project, names[0]),
                  {"dialogo_000#1": "Fala 1.", "dialogo_000#2": "="})
        self.assertTrue(corrections.apply_package(self.project, names[0]))
        report = report_batch(self.project, "dialogo_000", rules_for(self.project), load_reviewed(self.project),
                              show_warnings=False)
        self.assertEqual((report.translated, report.errors, report.warnings), (8, 0, 0))

    def test_refuses_new_packages_while_an_answer_is_pending(self):
        prepare(self.project)
        self.translate_all({"1": ""})
        names = corrections.generate(self.project)
        save_json(corrections.package_output_path(self.project, names[0]), {})
        with self.assertRaises(SystemExit):
            corrections.generate(self.project)

    def test_extra_keys_are_removed(self):
        prepare(self.project)
        self.translate_all({"99": "sobra"})
        corrections.generate(self.project)
        self.assertNotIn("99", self.project.load_output("dialogo_000"))
