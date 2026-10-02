# Traduções PT-BR de jogos

Traduções de fãs para português do Brasil, feitas com foco em localização (não tradução literal): guia de estilo e glossário por jogo, tradução em lotes paralelos, validação automática de placeholders/tags e instalador com backup/desinstalação.

| Jogo | Engine | Pasta | Versão suportada (Steam build) | Status |
|---|---|---|---|---|
| Garden of Witches | Unity 2022.3 (IL2CPP) | [`garden-of-witches/`](garden-of-witches/) | 25225196 | Completo (história + interface) |
| The Wolf Among Us | Telltale Tool | [`the-wolf-among-us/`](the-wolf-among-us/) | 319083 | Completo (5 episódios + menus + Fablespedia), aguardando teste em jogo |

## Estrutura de cada jogo

```
<jogo>/
  GUIA_TRADUCAO.md     guia de estilo + glossário PT-BR
  chunks/              texto original dividido em lotes (entrada)
  out/                 traduções por lote (saída)
  src/                 instalador e patcher
  validate.py          valida placeholders, tags, crases e quebras de linha
  build.py             junta traduções, gera .exe e .zip
  releases/steam-build-<id>/   executável e zip prontos para essa versão do jogo
```
