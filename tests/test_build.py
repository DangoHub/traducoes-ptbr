from kit.application.batches import prepare
from kit.application.build import verify
from tests.support import ProjectTestCase


class FinalVerificationTest(ProjectTestCase):
    def test_final_build_requires_complete_batches(self):
        prepare(self.project)
        self.assertTrue(verify(self.project))
        self.translate_all()
        self.assertEqual(verify(self.project), [])

    def test_invalid_output_blocks_the_build(self):
        prepare(self.project)
        self.translate_all({"2": "<b>sem fechar"})
        self.assertEqual(verify(self.project), ["dialogo_000: 1 de 8 textos sem tradução válida"])
