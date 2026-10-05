# Kit de tradução DangoHub

Scripts fazem todo o trabalho previsível: detectar a engine, extrair o texto, montar lotes com
contexto, validar, gerar os arquivos do jogo e empacotar. Os agentes só traduzem.

Requisitos: Python 3.12+, `pip install UnityPy TypeTreeGeneratorAPI pyinstaller` (UnityPy só para
jogos Unity).

## Comandos

Rode sempre da raiz do repositório:

| Comando | O que faz |
|---|---|
| `python -m kit detectar "<pasta do jogo>"` | Relatório curto: engine, pistas e arquivos de texto. Diz qual plugin usar. |
| `python -m kit preparar <jogo>` | Extrai do jogo e recria `chunks/` e `out/` sem perder trabalho: consolida as saídas válidas em `src/traducoes.json`, guarda as inválidas em `src/rascunhos.json` e arquiva os lotes anteriores em `work/historico/`. Textos com o mesmo inglês já validado não voltam; falas novas de uma conversa já traduzida vêm com as vizinhas aprovadas como referência. |
| `python -m kit termos <jogo>` | Nomes e termos mais frequentes, com um exemplo cada, para montar o glossário. |
| `python -m kit status <jogo> [--detalhe]` | Progresso por estado: validados, com erro, pendentes, avisos a revisar e revisados. |
| `python -m kit proximos <jogo> [-n 6]` | Próximos lotes pendentes. |
| `python -m kit prompt <jogo> <lotes...>` | Gera `work/contexto/<pacote>.md` (regras + guia filtrado para esses lotes) e imprime o prompt do subagente. Com `correcao_NNN`, gera o prompt de correção. |
| `python -m kit validar <jogo> [<lotes...>]` | Erros e avisos por item. |
| `python -m kit correcoes <jogo> [--avisos]` | Pacotes `work/correcoes/correcao_NNN.json` só com os itens com erro (e avisos não revisados), com motivo, cena, quem fala e falas vizinhas. Remove chaves extras sozinho. |
| `python -m kit aplicar <jogo> <correcao_NNN...>` | Grava em `out/` só os IDs do pacote, revalida e registra os avisos revisados em `src/revisao.json`. |
| `python -m kit verificar <jogo>` | Diz se todos os lotes estão completos e sem erro (exigido pelo `montar` final). |
| `python -m kit metricas <jogo>` | Tokens dos lotes (texto, referência, rascunho, estrutura) e do contexto entregue em cada prompt. |
| `python -m kit amostra <jogo> <lote> [-n 30]` | Inglês e português lado a lado, para revisão rápida. |
| `python -m kit buscar <jogo> "<texto>"` | Acha uma frase (inglês ou português) e mostra arquivo, número, original e tradução. |
| `python -m kit termos-check <jogo>` | Itens em que um termo de `glossario.json` ("termos") não foi traduzido como combinado. |
| `python -m kit padronizar <jogo>` | Aplica as correções de `glossario.json` ("trocas") em `out/` e no banco consolidado. |
| `python -m kit montar <jogo> --so-linux` | Só o zip do Steam Deck/Linux (`Instalar.sh` + arquivos), sem PyInstaller. O `montar` normal gera os dois zips. |
| `python -m kit montar <jogo> [--json-only]` | Consolida, gera os arquivos traduzidos e o zip com o instalador. Recusa se `verificar` apontar lotes incompletos. |
| `python -m kit montar <jogo> --parcial` | Pacote de teste mesmo com lotes incompletos (esses textos ficam em inglês). |
| `python -m kit instalar-teste <jogo>` | Monta e copia direto para a pasta do jogo, para testar. |

## Roteiro para um jogo novo (agente orquestrador)

1. `detectar` na pasta do jogo. Se houver plugin compatível, siga em frente. Se não houver, escreva um
   novo em `kit/engines/` (veja abaixo). Essa é a única etapa de exploração.
2. Crie `projetos/<jogo>/jogo.json`, copiando o de um jogo da mesma engine.
3. `preparar`, depois `termos`. Escreva `projetos/<jogo>/GUIA_TRADUCAO.md` com o tom, os personagens e
   o glossário. Complete os gêneros em `personagens.json`, se o plugin gerar esse arquivo.
4. **Lote piloto:** um subagente traduz 1 ou 2 lotes, e você revisa uma amostra e ajusta o guia. Só
   depois libere o resto.
5. **Ondas:** `proximos -n 12` e depois até 4 subagentes em paralelo, cada um com 3 lotes. Use o texto
   de `prompt` sem acrescentar nada. O prompt pede leitura e gravação em rodadas paralelas e no máximo
   uma correção: cada chamada de ferramenta do agente reenvia todo o contexto, então menos rodadas é o
   que mais economiza.
6. Entre as ondas, rode só `status`. **Não leia lotes nem saídas por conta própria**, porque isso gasta
   tokens.
7. **Correções:** `correcoes` (com `--avisos` na revisão final), um subagente por até 3 pacotes com o
   texto de `prompt <jogo> correcao_000 ...`, e ele mesmo roda `aplicar`. Avisos aceitos não voltam.
8. `verificar`, `instalar-teste`, testar no jogo, `montar` e fazer o release pelo workflow
   `Release de tradução`.

## Atualização do jogo

Rode `preparar` de novo. Só os textos novos ou alterados voltam para os lotes, acompanhados das falas
aprovadas vizinhas como referência (itens sem `k`). O resto vem de `src/traducoes.json`. Se o texto de um
destino mudou e ainda não foi retraduzido, a montagem usa o inglês, e não a tradução antiga.

## Guia do jogo e contexto por pacote

O `GUIA_TRADUCAO.md` não é lido inteiro pelos agentes. O `prompt` monta um contexto por pacote:

- texto corrido (universo, tom, regras) entra sempre;
- linhas de tabela entram só se algum termo da 1ª coluna (separados por `/` ou `,`; parênteses são
  notas) aparece nas falas, em quem fala ou na cena;
- em `## Personagens`, cada `### Nome / Apelido` entra só se o personagem fala ou é citado. Coloque
  ali personalidade, relações e jeito de falar.

## Estrutura de um projeto

```
projetos/<jogo>/
  jogo.json            configuração: engine, pasta, nome do idioma, regras de validação
  GUIA_TRADUCAO.md     tom, personagens e glossário (lido pelos subagentes)
  personagens.json     gênero de cada personagem: "F", "M" ou "?" (desconhecido/varia). Gerado; edite o que vier null
  chunks/  out/        lotes de entrada e saída dos subagentes
  src/indice.json      de cada item do lote para os destinos no jogo
  src/esqueleto.json   estrutura do arquivo final; permite montar sem o jogo, inclusive no CI
  src/traducoes.json   banco consolidado {destino: [inglês, português]} (validados)
  src/rascunhos.json   saídas que falharam na validação; voltam no lote como "rascunho"
  src/revisao.json     avisos revisados ([inglês, português, aviso]); não aparecem de novo
  work/                local, fora do git: contexto/, correcoes/, historico/, metricas.jsonl
```

## Organização do código

O código usa nomes em inglês; comandos, flags, chaves JSON e nomes de arquivo continuam em português.

```
kit/
  platform/      E/S: JSON e arquivos (gravação atômica), contagem de tokens, empacotamento dos zips
  config/        caminhos do repositório e Project (jogo.json + pastas de um projeto)
  domain/        regras puras: unidades de tradução, validação, divisão em lotes, filtro do guia
  application/   casos de uso: lotes, revisão, correções, contexto, glossário, montagem, detecção
  commands/      CLI (argparse) e textos dos prompts dos subagentes
  engines/       plugins de engine
  installer/     instalador genérico (Windows) e Instalar.sh (Steam Deck/Linux)
tests/           testes com um jogo falso
```

## Plugin de engine

Herde de `kit/engines/base.py` e registre a classe em `kit/engines/__init__.py`. Implemente:

- `extract()`: lê o jogo, grava em `src/` o que for preciso para montar sem o jogo e devolve uma lista
  de `TranslationUnit` (`kit/domain/units.py`). Agrupe por conversa (`group`, `scene`) e informe
  `speaker` sempre que der. Cada destino precisa ser único: jogos repetem ids internos, e a extração e
  a montagem devem gerar os destinos pela mesma função.
- `build(translations, destination)`: gera os arquivos traduzidos e devolve
  `[(arquivo, caminho_no_jogo)]`. O instalador genérico (`kit/installer/installer.py`) copia esses
  arquivos, guarda backup do original e desinstala.
- `check_path()`: caminho que existe na pasta do jogo.

Plugins disponíveis: `unity_antoolkit` (Third Crisis).

Testes (com um jogo falso): `python -m unittest discover -s tests -t .`
