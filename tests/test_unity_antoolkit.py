import os
import tempfile
import unittest
from unittest import mock

from kit.domain.units import TranslationUnit
from kit.engines.unity_antoolkit import UnityANToolkit
from kit.platform.storage import load_json, save_json

GAME_DATA = {
    "Dialogues": [{"guid": "g", "Lines": [{"LineId": "l", "originalText": "Hi", "Choices": [
        {"choiceId": "", "originalText": "Show the lights."}, {"choiceId": "", "originalText": "Give supplies."}]}]}],
    "UILocalizations": [], "LocalizedStrings": [], "Missions": [], "JournalEntries": [], "SceneNames": [],
    "Items": [{"Id": "x", "Name": "Holy Armor", "Description": "d1"},
              {"Id": "x", "Name": "Elven Leather", "Description": "d2"}],
    "Abilities": [],
}


def ui(target, text, scene):
    return TranslationUnit(text, [target], "interface", None, scene, None, "ui")


class InterfaceDeduplicationTest(unittest.TestCase):
    def test_equal_texts_merge_only_within_the_same_role(self):
        result = UnityANToolkit.deduplicate_interface([
            ui("S|Settings.TextureQuality.High", "High", "Settings.TextureQuality.High"),
            ui("S|Settings.GrassDetail.High", "High", "Settings.GrassDetail.High"),
            ui("S|Settings.ControlsTab", "Controls", "Settings.ControlsTab"),
            ui("S|Settings.ControlsTab", "Controls", "Settings.ControlsTab"),
            ui("U|a", "Back", None), ui("U|b", "Back", None),
        ])
        self.assertEqual([(u.text, len(u.targets)) for u in result],
                         [("High", 1), ("High", 1), ("Controls", 1), ("Back", 2)])


class UniqueTargetsTest(unittest.TestCase):
    def test_repeated_game_id_gets_its_own_target(self):
        targets = [target for target, *_ in UnityANToolkit.fields(GAME_DATA)]
        self.assertEqual(len(targets), len(set(targets)))
        self.assertIn("C|g|l|~1", targets)
        self.assertIn("I|x|Name~1", targets)

    def test_translation_of_another_text_is_not_used(self):
        with tempfile.TemporaryDirectory() as tmp:
            save_json(os.path.join(tmp, "src", "esqueleto.json"), GAME_DATA)
            project = mock.Mock(path=lambda *parts: os.path.join(tmp, *parts),
                                config={"nome_idioma": "PT", "pasta_dados": "D"})
            output, _ = UnityANToolkit(project).build({"I|x|Name": ["Holy Armor", "Armadura Sagrada"],
                                                       "I|x|Name~1": ["Old text", "Texto velho"]}, tmp)[0]
            items = load_json(output)["Items"]
            self.assertEqual([i["TranslatedName"] for i in items], ["Armadura Sagrada", "Elven Leather"])
