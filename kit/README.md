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
| `python -m kit preparar <jogo>` | Extrai do jogo e recria `chunks/` e `out/`. Antes, consolida o que já foi traduzido em `src/traducoes.json`, e textos com o mesmo inglês não voltam para a fila. |
| `python -m kit termos <jogo>` | Nomes e termos mais frequentes, com um exemplo cada, para montar o glossário. |
| `python -m kit status <jogo> [--detalhe]` | Progresso e lotes sem saída ou com erro. |
| `python -m kit proximos <jogo> [-n 6]` | Próximos lotes pendentes. |
| `python -m kit prompt <jogo> <lotes...>` | Prompt pronto para passar ao subagente. |
| `python -m kit validar <jogo> [<lotes...>]` | Erros e avisos por item. |
| `python -m kit montar <jogo> [--json-only]` | Consolida, gera os arquivos traduzidos e o zip com o instalador. |
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
   de `prompt` sem acrescentar nada.
6. Entre as ondas, rode só `status`. **Não leia lotes nem saídas por conta própria**, porque isso gasta
   tokens. Leia apenas os erros que `validar` apontar.
7. `instalar-teste`, depois testar no jogo, `montar` e fazer o release pelo workflow `Release de tradução`.

## Atualização do jogo

Rode `preparar` de novo. Só os textos novos ou alterados voltam para os lotes. O resto vem de
`src/traducoes.json`.

## Estrutura de um projeto

```
projetos/<jogo>/
  jogo.json            configuração: engine, pasta, nome do idioma, regras de validação
  GUIA_TRADUCAO.md     tom, personagens e glossário (lido pelos subagentes)
  personagens.json     gênero de cada personagem: "F", "M" ou "?" (desconhecido/varia). Gerado; edite o que vier null
  chunks/  out/        lotes de entrada e saída dos subagentes
  src/indice.json      de cada item do lote para os destinos no jogo
  src/esqueleto.json   estrutura do arquivo final; permite montar sem o jogo, inclusive no CI
  src/traducoes.json   banco consolidado {destino: [inglês, português]}
```

## Plugin de engine

Herde de `kit/engines/base.py` e registre a classe em `kit/engines/__init__.py`. Implemente:

- `extrair()`: lê o jogo, grava em `src/` o que for preciso para montar sem o jogo e devolve as
  unidades, no formato descrito em `base.py`. Agrupe por conversa (`grupo`, `cena`) e informe `quem`
  sempre que der.
- `montar(traducoes, destino)`: gera os arquivos traduzidos e devolve `[(arquivo, caminho_no_jogo)]`.
  O instalador genérico (`kit/instalador.py`) copia esses arquivos, guarda backup do original e
  desinstala.
- `arquivo_de_verificacao()`: caminho que existe na pasta do jogo.

Plugins disponíveis: `unity_antoolkit` (Third Crisis).
