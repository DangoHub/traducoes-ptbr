"""Unity + ANToolkit (Anduo Games, e.g. Third Crisis).

The game loads StreamingAssets/Languages/customtranslated_<name>.json and shows "Custom <name>" in the menu.
The file follows the official translations format (translated_es_translation.json): lines indexed by
dialogue guid + LineId, interface by guid etc. A missing entry shows as empty text in the game, so the final
file is always complete, with the English as fallback.

Speakers are not in the JSON: they come from the Dialogue/Character assets (read with UnityPy + the DLL
typetree).
"""
import copy
import os
import re
import sys

from kit.domain.units import (CATEGORY_DIALOGUE, CATEGORY_INTERFACE, CATEGORY_TEXTS, KIND_CHOICE, KIND_LINE,
                              KIND_UI, TranslationUnit)
from kit.engines.base import Engine
from kit.platform.storage import load_json, save_json

try:
    import UnityPy
    from UnityPy.helpers.TypeTreeGenerator import TypeTreeGenerator
except ImportError:
    UnityPy = None

TRANSLATED_FIELDS = ("text", "TranslatedName", "TranslatedDescription", "TranslatedDisplayName",
                     "TranslatedContents", "TranslatedToolTip")
SYMBOLS_ONLY = re.compile(r"^[^A-Za-z]*$")
WHOLE_TOKEN = re.compile(r"^#\w+#$")
NARRATOR = "Narrator"
NARRATOR_PT = "Narrador"
GENDERS = ("M", "F")
MAX_INTERFACE_CONTEXTS = 5
ASSET_CLASSES = {"Dialogue": "Asuna.Dialogues.Dialogue", "Character": "Asuna.CharManagement.Character"}


def _natural_key(text):
    return [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", text)]


class UnityANToolkit(Engine):
    name = "unity_antoolkit"

    @property
    def data_dir(self):
        return self.project.config["pasta_dados"]

    @property
    def languages_dir(self):
        return os.path.join(self.data_dir, "StreamingAssets", "Languages")

    @property
    def output_name(self):
        return f"customtranslated_{self.project.config['nome_idioma']}.json"

    @property
    def skeleton_path(self):
        return self.project.path("src", "esqueleto.json")

    def check_path(self):
        return self.languages_dir

    # ---------- extraction ----------

    def extract(self):
        game_dir = self.project.game_dir
        template = load_json(os.path.join(game_dir, self.languages_dir, self.project.config["modelo"]))
        if template is None:
            raise SystemExit(f"Modelo não encontrado em {os.path.join(game_dir, self.languages_dir)}")

        skeleton = copy.deepcopy(template)
        self._clear_translations(skeleton)
        save_json(self.skeleton_path, skeleton, indent=None)

        speakers = self._read_speakers(game_dir)
        keep_as_is = set(self.project.config.get("nao_traduzir", []))
        targets = {(id(obj), field): target for target, obj, field, _ in self.fields(template)}
        units = []

        def add(obj, field, category, group=None, scene=None, speaker=None, kind=KIND_LINE):
            text = obj[field]
            if not isinstance(text, str) or not text.strip():
                return
            translatable = not (SYMBOLS_ONLY.match(text) or WHOLE_TOKEN.match(text.strip()) or text in keep_as_is)
            units.append(TranslationUnit(text, [targets[id(obj), field]], category, group, scene, speaker, kind,
                                         translatable))

        for dialogue in sorted(template["Dialogues"], key=lambda d: _natural_key(d["name"])):
            line_speakers = speakers.get(dialogue["guid"], {})
            for line in dialogue["Lines"]:
                add(line, "originalText", CATEGORY_DIALOGUE, dialogue["guid"], dialogue["name"],
                    line_speakers.get(line["LineId"]))
                for choice in line["Choices"]:
                    add(choice, "originalText", CATEGORY_DIALOGUE, dialogue["guid"], dialogue["name"], None,
                        KIND_CHOICE)

        for mission in template["Missions"]:
            group = "M:" + mission["Id"]
            add(mission, "Name", CATEGORY_TEXTS, group, mission["Name"], kind="titulo de missao")
            add(mission, "Description", CATEGORY_TEXTS, group, mission["Name"], kind="descricao de missao")
            for task in mission["Tasks"]:
                add(task, "DisplayName", CATEGORY_TEXTS, group, mission["Name"], kind="tarefa de missao")
        for entry in template["JournalEntries"]:
            group = "J:" + entry["Id"]
            add(entry, "Name", CATEGORY_TEXTS, group, entry["Name"], kind="titulo do diario")
            add(entry, "Contents", CATEGORY_TEXTS, group, entry["Name"], kind="texto do diario")
        for item in template["Items"]:
            group = "I:" + item["Id"]
            add(item, "Name", CATEGORY_TEXTS, group, item["Name"], kind="nome de item")
            add(item, "Description", CATEGORY_TEXTS, group, item["Name"], kind="descricao de item")
        for ability in template["Abilities"]:
            group = "A:" + ability["Id"]
            add(ability, "Name", CATEGORY_TEXTS, group, ability["Name"], kind="nome de habilidade")
            add(ability, "Tooltip", CATEGORY_TEXTS, group, ability["Name"], kind="descricao de habilidade")
        for scene in template["SceneNames"]:
            add(scene, "Name", CATEGORY_TEXTS, "lugares", "Nomes de lugares", kind="nome de lugar")

        for string in template["LocalizedStrings"]:
            add(string, "originalText", CATEGORY_INTERFACE, scene=string["Identifier"], kind=KIND_UI)
        for ui in template["UILocalizations"]:
            add(ui, "originalText", CATEGORY_INTERFACE, kind=KIND_UI)
        return self.deduplicate_interface(units)

    @staticmethod
    def fields(data):
        """(target, object, original field, translated field) of each text, in file order.

        The game repeats ids (empty choiceId, item Id, interface guid) for different texts. Each distinct
        text under the same id gets "~n" from the 2nd one on, so it has its own translation; repetitions of
        the same text keep the same target.
        """
        targets_by_id = {}

        def field(base_target, obj, original, translated):
            by_text = targets_by_id.setdefault(base_target, {})
            if obj[original] not in by_text:
                n = len(by_text)
                by_text[obj[original]] = base_target if n == 0 else f"{base_target}~{n}"
            return by_text[obj[original]], obj, original, translated

        for d in data["Dialogues"]:
            for line in d["Lines"]:
                yield field(f"D|{d['guid']}|{line['LineId']}", line, "originalText", "text")
                for choice in line["Choices"]:
                    yield field(f"C|{d['guid']}|{line['LineId']}|{choice['choiceId']}", choice, "originalText", "text")
        for ui in data["UILocalizations"]:
            yield field(f"U|{ui['guid']}", ui, "originalText", "text")
        for string in data["LocalizedStrings"]:
            yield field(f"S|{string['Identifier']}", string, "originalText", "text")
        for mission in data["Missions"]:
            yield field(f"M|{mission['Id']}|Name", mission, "Name", "TranslatedName")
            yield field(f"M|{mission['Id']}|Description", mission, "Description", "TranslatedDescription")
            for task in mission["Tasks"]:
                yield field(f"T|{mission['Id']}|{task['Id']}", task, "DisplayName", "TranslatedDisplayName")
        for entry in data["JournalEntries"]:
            yield field(f"J|{entry['Id']}|Name", entry, "Name", "TranslatedName")
            yield field(f"J|{entry['Id']}|Contents", entry, "Contents", "TranslatedContents")
        for item in data["Items"]:
            yield field(f"I|{item['Id']}|Name", item, "Name", "TranslatedName")
            yield field(f"I|{item['Id']}|Description", item, "Description", "TranslatedDescription")
        for ability in data["Abilities"]:
            yield field(f"A|{ability['Id']}|Name", ability, "Name", "TranslatedName")
            yield field(f"A|{ability['Id']}|Tooltip", ability, "Tooltip", "TranslatedToolTip")
        for scene in data["SceneNames"]:
            yield field(f"N|{scene['Id']}", scene, "Name", "TranslatedName")

    @staticmethod
    def _clear_translations(skeleton):
        def walk(node):
            if isinstance(node, dict):
                for key, value in node.items():
                    if key in TRANSLATED_FIELDS and isinstance(value, str):
                        node[key] = ""
                    else:
                        walk(value)
            elif isinstance(node, list):
                for child in node:
                    walk(child)
        walk(skeleton)

    @staticmethod
    def interface_role(unit):
        """Where the text is used. LocalizedStrings: identifier group ("Settings.TextureQuality.High" ->
        "Settings.TextureQuality"). UILocalizations only have a guid, so equal texts count as the same role."""
        target = unit.primary_target.split("~")[0]
        if target.startswith("S|"):
            return target[2:].rsplit(".", 1)[0]
        return target.split("|", 1)[0]

    @classmethod
    def deduplicate_interface(cls, units, max_contexts=MAX_INTERFACE_CONTEXTS):
        """Merge equal interface texts only within the same role, keeping the identifiers of every target."""
        result, by_key, contexts, seen = [], {}, {}, {}
        for unit in units:
            if unit.category != CATEGORY_INTERFACE:
                result.append(unit)
                continue
            key = (unit.text, cls.interface_role(unit))
            if key in by_key:
                new = [t for t in unit.targets if t not in seen[key]]
                by_key[key].targets += new
                seen[key].update(new)
            else:
                by_key[key] = unit
                seen[key] = set(unit.targets)
                contexts[id(unit)] = []
                result.append(unit)
            scenes = contexts[id(by_key[key])]
            if unit.scene and unit.scene not in scenes:
                scenes.append(unit.scene)
        for unit in result:
            scenes = contexts.get(id(unit))
            if scenes:
                extra = f" (+{len(scenes) - max_contexts})" if len(scenes) > max_contexts else ""
                unit.scene = ", ".join(scenes[:max_contexts]) + extra
        return result

    # ---------- speakers (assets) ----------

    def _read_assets(self, data):
        """Raw Dialogue and Character assets: ({guid: dialogue}, {asset_ref: character})."""
        files = sorted(f for f in os.listdir(data) if f.endswith(".assets") or f.startswith("level"))
        generator, nodes = None, {}
        dialogues, characters = {}, {}
        for file in files:
            env = UnityPy.load(os.path.join(data, file))
            for obj in env.objects:
                if obj.type.name != "MonoBehaviour":
                    continue
                try:
                    base = obj.read(check_read=False)
                    class_name = base.m_Script.read().m_ClassName
                except Exception:
                    continue
                if class_name not in ASSET_CLASSES:
                    continue
                if generator is None:
                    generator = TypeTreeGenerator(obj.assets_file.unity_version)
                    generator.load_local_dll_folder(os.path.join(data, "Managed"))
                if class_name not in nodes:
                    nodes[class_name] = generator.get_nodes_up("Assembly-CSharp", ASSET_CLASSES[class_name])
                ref = f"{file}:{obj.path_id}"
                try:
                    tree = obj.read_typetree(nodes[class_name])
                except Exception:
                    if class_name == "Character":
                        characters[ref] = {"nome": base.m_Name, "genero": None}
                    continue
                if class_name == "Character":
                    characters[ref] = {"nome": tree.get("Name") or tree["m_Name"],
                                       "genero": GENDERS[tree.get("Gender", 0)]}
                    continue
                externals = [os.path.basename(e.path) for e in obj.assets_file.externals]

                def asset_ref(pointer, file=file, externals=externals):
                    if not pointer["m_PathID"]:
                        return None
                    origin = file if pointer["m_FileID"] == 0 else externals[pointer["m_FileID"] - 1]
                    return f"{origin}:{pointer['m_PathID']}"
                dialogues[tree["Guid"]] = {"nome": tree["m_Name"], "linhas": {
                    line["LineID"]: {"speaker": line["Speaker"], "override": line["NameOverride"],
                                     "char": asset_ref(line["Character"]),
                                     "preset": (line.get("PresetLocation", ""), line.get("PresetID", ""))}
                    for line in tree["Lines"]}}
        return dialogues, characters

    def _read_speakers(self, game_dir):
        """{guid: {lineId: "Name (F)"}} from the Dialogue/Character assets."""
        if UnityPy is None:
            print("AVISO: UnityPy/TypeTreeGeneratorAPI ausentes; lotes sairão sem 'quem fala'.")
            return {}
        dialogues, characters = self._read_assets(os.path.join(game_dir, self.data_dir))
        presets = {d["nome"]: d for d in dialogues.values()}
        speakers = {}
        for guid, dialogue in dialogues.items():
            speakers[guid] = {}
            for line_id, line in dialogue["linhas"].items():
                location, preset_id = line["preset"]
                if preset_id:
                    preset = presets.get(location.split("/")[-1], {}).get("linhas", {}).get(preset_id)
                    if preset:
                        line = {**line, "speaker": preset["speaker"], "override": preset["override"],
                                "char": preset["char"]}
                speakers[guid][line_id] = self._speaker(line, characters)

        genders = self._genders(characters, speakers)
        labels = {guid: {line_id: self._label(s, genders) for line_id, s in lines.items()}
                  for guid, lines in speakers.items()}
        print(f"Quem fala: {len(dialogues)} diálogos e {len(characters)} personagens lidos dos assets.")
        return labels

    @staticmethod
    def _speaker(line, characters):
        """(name shown in the game, asset gender or None), following the game's DialoguePopulateInfo."""
        character = characters.get(line["char"]) if line["char"] else None
        name = (line["override"] or character["nome"]) if character else line["speaker"]
        return (name or "").strip(), (character["genero"] if character else None)

    def _genders(self, characters, speakers):
        """Gender per displayed name. The project's personagens.json (editable) fills what the assets miss."""
        path = self.project.path("personagens.json")
        manual = load_json(path, {})
        detected = {}
        for character in characters.values():
            if character["nome"] and character["genero"]:
                detected.setdefault(character["nome"], character["genero"])
        counts = {}
        for lines in speakers.values():
            for name, gender in lines.values():
                if name and name != NARRATOR:
                    counts[name] = counts.get(name, 0) + 1
                    if gender:
                        detected.setdefault(name, gender)
        names = sorted(counts, key=lambda n: -counts[n])
        save_json(path, {n: manual.get(n, detected.get(n)) for n in names}
                  | {n: g for n, g in manual.items() if n not in counts})
        return {**detected, **{n: g for n, g in manual.items() if g}}

    @staticmethod
    def _label(speaker, genders):
        name = speaker[0]
        if not name:
            return None
        if name == NARRATOR:
            return NARRATOR_PT
        gender = genders.get(name)
        return f"{name} ({gender})" if gender in GENDERS else name

    # ---------- build ----------

    def build(self, translations, destination):
        skeleton = load_json(self.skeleton_path)
        if skeleton is None:
            raise SystemExit("src/esqueleto.json não existe; rode 'python -m kit preparar' primeiro.")
        used = 0
        # tokens the game expands from English lists inside the assets
        token_replacements = self.project.config.get("substituir_tokens", {})

        def translated(target, original):
            nonlocal used
            source, text = translations.get(target, (None, None))
            if text and source == original:
                used += 1
            else:
                text = original
            for token, replacement in token_replacements.items():
                text = text.replace(token, replacement)
            return text

        for target, obj, original, translated_field in list(self.fields(skeleton)):
            obj[translated_field] = translated(target, obj[original])

        os.makedirs(destination, exist_ok=True)
        output = os.path.join(destination, self.output_name)
        save_json(output, skeleton, indent=None)
        print(f"{self.output_name}: {used} campos traduzidos", file=sys.stderr)
        return [(output, os.path.join(self.languages_dir, self.output_name).replace("\\", "/"))]
