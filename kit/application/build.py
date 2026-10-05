"""Build: consolidate out/ into src/traducoes.json, generate the game files and package them with the
generic installers."""
import os
import shutil

from kit.application.batches import consolidate
from kit.application.review import analyze_batch, rules_for
from kit.config.paths import ENGINES_DIR, INSTALLER_PATH
from kit.platform.packaging import package_linux, package_windows
from kit.platform.storage import save_json

MAX_PROBLEMS_SHOWN = 20


def verify(project):
    """Problems that block the final package: batches without output, with errors or with invalid JSON."""
    rules = rules_for(project)
    problems = []
    for batch in project.batches():
        analysis = analyze_batch(project, batch, rules)
        total = analysis.item_count
        if analysis.output is None:
            problems.append(f"{batch}: sem saída ({total} textos)")
        elif len(analysis.valid) < total or analysis.has_errors:
            problems.append(f"{batch}: {total - len(analysis.valid)} de {total} textos sem tradução válida")
    return problems


def _ensure_complete(project):
    problems = verify(project)
    if problems:
        print("\n".join(problems[:MAX_PROBLEMS_SHOWN]))
        raise SystemExit(f"Pacote final bloqueado: {len(problems)} lotes incompletos. "
                         "Use 'correcoes'/'aplicar' ou 'montar --parcial' para um pacote de teste.")


def _write_package_manifest(project, package_dir, files, check_path):
    """pacote.json read by the Windows installer (keys are part of the installer format)."""
    save_json(os.path.join(package_dir, "pacote.json"), {
        "jogo": project.name, "pasta_steam": project.steam_folder, "versao": project.version,
        "verificar": check_path, "aviso": project.post_install_notice,
        "arquivos": [{"origem": "arquivos/" + os.path.basename(f), "destino": rel} for f, rel in files],
    })


def build(project, json_only=False, steam_build=None, linux_only=False, partial=False):
    """Generate the translated files (json_only) or the release zips. Return the files or the Linux zip path."""
    if not json_only and not partial:
        _ensure_complete(project)
    bank, changed = consolidate(project)
    print(f"Traduções consolidadas: {len(bank)} destinos ({changed} novos/alterados).")
    if partial or json_only:
        incomplete = len(verify(project))
        if incomplete:
            print(f"Montagem parcial: {incomplete} lotes incompletos; esses textos ficam em inglês.")
    engine = project.engine()
    package_dir = project.path("build", "pacote")
    shutil.rmtree(package_dir, ignore_errors=True)
    files = engine.build(bank, os.path.join(package_dir, "arquivos"))
    if json_only:
        return files

    steam_build = steam_build or project.steam_build
    app = "Traducao_PTBR_" + project.name.replace(" ", "_")
    check_path = engine.check_path().replace("\\", "/")
    engine_file = project.engine_name + ".py"
    if not linux_only:
        _write_package_manifest(project, package_dir, files, check_path)
        package_windows(
            project.root, app, project.name, project.version, [],
            [(INSTALLER_PATH, "instalador.py"), (os.path.join(ENGINES_DIR, engine_file), engine_file)],
            f"{app}_v{project.version}.zip", steam_build,
            script=INSTALLER_PATH,
            extra_data=[(os.path.join(package_dir, "pacote.json"), "."),
                        (os.path.join(package_dir, "arquivos"), "arquivos")],
        )
    names = ["arquivos/" + os.path.basename(f) for f, _ in files]
    return package_linux(
        project.root, app, project.name, project.version,
        {"PASTA_STEAM": project.steam_folder, "VERIFICAR": check_path, "AVISO": project.post_install_notice},
        [(f, name) for (f, _), name in zip(files, names)],
        f"{app}_v{project.version}_SteamDeck-Linux.zip", steam_build,
        copy_list=[(name, rel.replace(os.sep, "/")) for name, (_, rel) in zip(names, files)],
    )


def install_for_testing(project):
    """Build the translated files and copy them straight into the installed game."""
    for file, rel in build(project, json_only=True):
        destination = os.path.join(project.game_dir, rel)
        shutil.copyfile(file, destination)
        print("copiado:", destination)
