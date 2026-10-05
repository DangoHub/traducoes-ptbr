"""Common interface of the engine plugins.

`extract()` returns kit.domain.units.TranslationUnit objects.
"""


class Engine:
    name = "base"

    def __init__(self, project):
        self.project = project

    def extract(self):
        """Read the installed game, save in src/ what the build needs and return the translation units."""
        raise NotImplementedError

    def build(self, translations, destination):
        """Generate the translated files in `destination` from src/ (without the game).

        translations: {target_id: [english, portuguese]}. Use a translation only if its English equals the
        current original (otherwise the game text changed and the translation is stale).
        Return [(generated_file, path_inside_the_game)].
        """
        raise NotImplementedError

    def check_path(self):
        """Relative path that exists in the game folder; the installer uses it to recognise the folder."""
        raise NotImplementedError
