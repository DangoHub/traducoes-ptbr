import contextlib
import io

from kit.commands.cli import build_parser, run
from tests.support import ProjectTestCase


class ParserTest(ProjectTestCase):
    def test_keeps_portuguese_command_names_and_flags(self):
        args = build_parser().parse_args(["montar", "jogo", "--parcial", "--so-linux", "--steam-build=1"])
        self.assertEqual((args.command, args.game, args.partial, args.linux_only, args.steam_build),
                         ("montar", "jogo", True, True, "1"))

    def test_validate_exit_code_follows_errors(self):
        with contextlib.redirect_stdout(io.StringIO()):
            run(["preparar", "jogo"])
            self.translate_all({"1": ""})
            self.assertEqual(run(["validar", "jogo"]), 1)
            self.translate_all()
            self.assertEqual(run(["validar", "jogo"]), 0)

    def test_prompt_writes_filtered_context(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            run(["preparar", "jogo"])
            run(["prompt", "jogo", "dialogo_000"])
        self.assertIn("python -m kit validar jogo dialogo_000", out.getvalue())
