"""Kit de tradução DangoHub.

    python -m kit detectar "<pasta do jogo>"
    python -m kit preparar <jogo>
    python -m kit status <jogo> [--detalhe]
    python -m kit proximos <jogo> [-n 6]
    python -m kit prompt <jogo> <lote|correcao_NNN> [...]
    python -m kit validar <jogo> [<lote> ...]
    python -m kit correcoes <jogo> [--avisos]
    python -m kit aplicar <jogo> <correcao_NNN> [...]
    python -m kit verificar <jogo>
    python -m kit metricas <jogo>
    python -m kit montar <jogo> [--parcial] [--json-only] [--so-linux] [--steam-build=N]
    python -m kit instalar-teste <jogo>
    python -m kit termos <jogo> [-n 150]
    python -m kit amostra <jogo> <lote> [-n 30] [--de 0]
    python -m kit buscar <jogo> "<texto>" [-n 20]
    python -m kit termos-check <jogo>     (glossario.json "termos")
    python -m kit padronizar <jogo>       (glossario.json "trocas")
"""
import argparse
import json
import os

from kit.application import batches, build, corrections, glossary, inspection, metrics
from kit.application.detection import detect
from kit.application.review import load_reviewed, report_batch, rules_for
from kit.commands.prompts import render_prompt
from kit.config.project import Project


def _detect(args):
    print(json.dumps(detect(args.game_dir), ensure_ascii=False, indent=1))


def _prepare(project, args):
    batches.prepare(project)


def _status(project, args):
    batches.status(project, args.detailed)


def _next_batches(project, args):
    print("\n".join(batches.status(project)[:args.count]))


def _prompt(project, args):
    print(render_prompt(project, args.names))


def _validate(project, args):
    rules = rules_for(project)
    reviewed = load_reviewed(project)
    names = args.names or [n for n in project.batches() if os.path.isfile(project.output_path(n))]
    total_errors = 0
    for name in names:
        report = report_batch(project, name, rules, reviewed)
        print(f"{name}: {report.translated}/{report.total} traduzidos, {report.errors} erros, {report.warnings} avisos")
        total_errors += report.errors
    return 1 if total_errors else 0


def _corrections(project, args):
    corrections.generate(project, include_warnings=args.include_warnings)


def _apply(project, args):
    results = [corrections.apply_package(project, name) for name in args.packages]
    return 0 if all(results) else 1


def _verify(project, args):
    problems = build.verify(project)
    print("\n".join(problems) if problems else "Pronto para o pacote final: todos os lotes completos e sem erros.")
    return 1 if problems else 0


def _metrics(project, args):
    metrics.print_summary(project)


def _build(project, args):
    build.build(project, json_only=args.json_only, steam_build=args.steam_build, linux_only=args.linux_only,
                partial=args.partial)


def _install_for_testing(project, args):
    build.install_for_testing(project)


def _terms(project, args):
    glossary.term_candidates(project, args.count)


def _search(project, args):
    inspection.search(project, args.text, args.count)


def _standardize(project, args):
    glossary.standardize(project)


def _check_terms(project, args):
    glossary.check_terms(project)


def _sample(project, args):
    inspection.print_sample(project, args.batch, args.count, args.start)


PROJECT_COMMANDS = {
    "preparar": _prepare,
    "status": _status,
    "proximos": _next_batches,
    "prompt": _prompt,
    "validar": _validate,
    "correcoes": _corrections,
    "aplicar": _apply,
    "verificar": _verify,
    "metricas": _metrics,
    "montar": _build,
    "instalar-teste": _install_for_testing,
    "termos": _terms,
    "buscar": _search,
    "padronizar": _standardize,
    "termos-check": _check_terms,
    "amostra": _sample,
}


def build_parser():
    parser = argparse.ArgumentParser(prog="python -m kit", description="Kit de tradução DangoHub")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("detectar").add_argument("game_dir", metavar="pasta")

    def project_command(name, **kwargs):
        command = sub.add_parser(name, **kwargs)
        command.add_argument("game", metavar="jogo")
        return command

    project_command("preparar")
    project_command("status").add_argument("--detalhe", dest="detailed", action="store_true")
    project_command("proximos").add_argument("-n", dest="count", type=int, default=6)
    project_command("prompt").add_argument("names", metavar="lotes", nargs="+")
    project_command("validar").add_argument("names", metavar="lotes", nargs="*")
    project_command("correcoes").add_argument("--avisos", dest="include_warnings", action="store_true",
                                              help="inclui avisos ainda não revisados")
    project_command("aplicar").add_argument("packages", metavar="pacotes", nargs="+")
    project_command("verificar")
    project_command("metricas")
    command = project_command("montar")
    command.add_argument("--json-only", action="store_true")
    command.add_argument("--parcial", dest="partial", action="store_true",
                         help="monta mesmo com lotes incompletos (só para teste)")
    command.add_argument("--steam-build", default=None)
    command.add_argument("--so-linux", dest="linux_only", action="store_true",
                         help="só o zip do Steam Deck/Linux (sem PyInstaller)")
    project_command("instalar-teste")
    project_command("termos").add_argument("-n", dest="count", type=int, default=150)
    command = project_command("buscar")
    command.add_argument("text", metavar="texto")
    command.add_argument("-n", dest="count", type=int, default=20)
    project_command("padronizar")
    project_command("termos-check")
    command = project_command("amostra")
    command.add_argument("batch", metavar="lote")
    command.add_argument("-n", dest="count", type=int, default=30)
    command.add_argument("--de", dest="start", type=int, default=0)
    return parser


def run(argv):
    args = build_parser().parse_args(argv)
    if args.command == "detectar":
        _detect(args)
        return 0
    return PROJECT_COMMANDS[args.command](Project(args.game), args) or 0
