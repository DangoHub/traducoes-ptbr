import unittest

from kit.domain.guide import filter_guide, relevance_text

GUIDE = """# Guia
## O jogo
Universo.
## Personagens
### Rida
- Fala quebrado.
### Ray / Lumber Rats
- Sotaque caipira.
## Glossário
| Inglês | PT |
|---|---|
| Crush Waves (laser) | Ondas de Paixão |
| Townhall | Prefeitura |
"""


class FilterGuideTest(unittest.TestCase):
    def test_keeps_prose_and_only_mentioned_characters_and_terms(self):
        text = filter_guide(GUIDE, "Rida (F)\nThe Crush Waves hit me.")
        self.assertIn("Universo.", text)
        self.assertIn("Fala quebrado.", text)
        self.assertIn("Ondas de Paixão", text)
        self.assertNotIn("Sotaque caipira", text)
        self.assertNotIn("Prefeitura", text)

    def test_drops_table_sections_without_matches(self):
        self.assertNotIn("## Glossário", filter_guide(GUIDE, "Nothing relevant."))

    def test_relevance_text_includes_speaker_scene_and_context(self):
        text = relevance_text([{"en": "Hi", "quem": "Ray", "cena": "Bar", "contexto": ["Rida: Yo => E aí"]}])
        self.assertEqual(text.split("\n"), ["Hi", "Ray", "Bar", "Rida: Yo => E aí"])
