import unittest

from kit.config.project import DEFAULTS
from kit.domain.validation import ValidationRules, check_translation


class CheckTranslationTest(unittest.TestCase):
    def setUp(self):
        self.rules = ValidationRules(DEFAULTS["validacao"])

    def test_empty_translation_is_an_error(self):
        self.assertEqual(check_translation("Hello", "  ", self.rules), (["vazia"], []))

    def test_crossed_tags_are_an_error(self):
        errors, _ = check_translation("<b><i>Hello</i></b>", "<b><i>Olá</b></i>", self.rules)
        self.assertTrue(any("fora de ordem" in e for e in errors))
        self.assertEqual(check_translation("<b><i>Hello</i></b>", "<b><i>Olá</i></b>", self.rules)[0], [])

    def test_missing_placeholder_and_line_break_are_errors(self):
        errors, _ = check_translation("Hi {name}\nBye", "Oi", self.rules)
        self.assertEqual(len(errors), 2)

    def test_long_choice_is_a_warning(self):
        _, warnings = check_translation("Yes", "Sim, com certeza absoluta", self.rules, "escolha")
        self.assertTrue(warnings)

    def test_identical_onomatopoeia_has_no_warning(self):
        same = "<i>Haaahh... Nghh... Mmmf...</i>"
        self.assertEqual(check_translation(same, same, self.rules)[1], [])
        self.assertTrue(check_translation("Lorem ipsum dolor sit", "Lorem ipsum dolor sit", self.rules)[1])
