"""Subagent prompts: the orchestrator pastes them as they are."""
from kit.application import corrections, metrics
from kit.application.context import write_context
from kit.config.paths import REPO_ROOT
from kit.platform.storage import read_text
from kit.platform.tokens import count_tokens

TRANSLATION_PROMPT = """Você é tradutor(a) de jogos para português do Brasil. Traduza os lotes abaixo do jogo {jogo}.

1. Numa única rodada de chamadas paralelas, leia:
   - {contexto}  (regras, formato e o guia deste pacote)
{leituras}
2. Numa única rodada de chamadas paralelas, grave cada saída inteira de uma vez:
{gravacoes}
   Cada saída é um objeto JSON {{"k": "tradução"}} com as chaves "k" do lote. Itens sem "k" são referência: não devolva.
3. Rode uma vez, na pasta {repo}:  python -m kit validar {slug} {lotes}
   Se houver ERRO, corrija só os itens apontados (edição pontual, sem regravar o arquivo) e rode mais uma vez.
   O que ainda sobrar vira pacote de correção; não insista. Avisos não exigem ação.

Não leia outros arquivos, não explore o repositório e não use lista de tarefas.
Ao terminar, responda só uma linha por lote: "<lote>: N textos, E erros" e, se houver, dúvidas de glossário (máximo 5 linhas)."""

CORRECTION_PROMPT = """Você revisa traduções para português do Brasil do jogo {jogo}.

1. Numa única rodada de chamadas paralelas, leia:
   - {contexto}  (regras e o guia deste pacote)
{leituras}
2. Cada item traz id, motivo, original (en), tradução atual (pt) e falas vizinhas. Numa única rodada de chamadas
   paralelas, grave para cada pacote um objeto JSON {{"<id>": "texto"}} com todos os ids:
{gravacoes}
   problema "erro": devolva a tradução corrigida.
   problema "aviso": devolva "=" se a tradução atual estiver certa ou a nova tradução se não estiver.
3. Rode uma vez, na pasta {repo}:  python -m kit aplicar {slug} {lotes}

Não leia outros arquivos e não use lista de tarefas. Ao terminar, responda só com a linha que o comando aplicar imprimir."""


def _translation_job(project, names):
    inputs = [project.chunk_path(n) for n in names]
    outputs = [project.output_path(n) for n in names]
    items = [item for n in names for item in project.load_chunk(n)]
    return TRANSLATION_PROMPT, "traducao", inputs, outputs, items


def _correction_job(project, names):
    inputs = [corrections.package_path(project, n) for n in names]
    outputs = [corrections.package_output_path(project, n) for n in names]
    items = [item for n in names for item in corrections.load_package(project, n)]
    return CORRECTION_PROMPT, "correcao", inputs, outputs, items


def _bullets(paths):
    return "\n".join(f"   - {p}" for p in paths)


def render_prompt(project, names):
    """Write the package context, record its metrics and return the subagent prompt."""
    packages = [n for n in names if corrections.is_package(n)]
    if packages and len(packages) != len(names):
        raise SystemExit("Não misture lotes e pacotes de correção no mesmo prompt.")
    job = _correction_job if packages else _translation_job
    template, kind, inputs, outputs, items = job(project, names)
    if not items:
        raise SystemExit(f"Nada encontrado para: {', '.join(names)}")
    path, full_guide, context = write_context(project, names, items)
    metrics.record(project, kind, names,
                   tokens_itens=sum(count_tokens(read_text(p)) for p in inputs),
                   tokens_contexto=count_tokens(context),
                   tokens_guia_inteiro=count_tokens(full_guide))
    return template.format(jogo=project.name, slug=project.slug, repo=REPO_ROOT, lotes=" ".join(names),
                           contexto=path, leituras=_bullets(inputs), gravacoes=_bullets(outputs))
