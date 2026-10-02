# The Wolf Among Us — Tradução PT-BR

- **Versão do jogo:** Steam build 319083 (app 250320)
- **Conteúdo:** 34.480 falas únicas (52.507 no total) — episódios 1 a 5, menus, conquistas, Fablespedia, créditos
- **Release:** [`the-wolf-among-us-v1.0`](https://github.com/DangoHub/traducoes-ptbr/releases/tag/the-wolf-among-us-v1.0)

## Limitações conhecidas

- **Algumas falas narradas não exibem legenda.** São 756 falas (de 53.263) que já vêm **sem texto no
  jogo original em inglês** — só existe o áudio, então não há o que traduzir/exibir. Concentram-se em
  `previouslyon_*` / `nexttimeon_*` ("Anteriormente em..." / "Na próxima...") e em algumas cenas do
  Episódio 2 (cela do Lenhador, Pudding & Pie). Para conferir: `python tools/empty_lines.py`.
  Legendá-las exigiria transcrever o áudio e criar os textos do zero.

## Como funciona

O Telltale Tool carrega conteúdo por *resource descriptions* (`Pack/_resourcedescriptions_*.lenc`, Lua
criptografado com Blowfish modificado). O instalador:

1. Lê os `.landb` (banco de falas) efetivos direto dos `.ttarch2` do jogo instalado (`src/landb_index.json`).
2. Substitui as falas pelo texto de `src/traducao_ptbr.json` (chave = fala original em inglês).
3. Grava um `Fables_pc_PTBR_<grupo>.ttarch2` (TTCN/TTA3) por grupo lógico (`<Boot>`, `<Menu>`, `<Project>`, `<Fables101..105>`).
4. Grava `_resourcedescriptions_500_PTBR_<grupo>.lenc` com prioridade 100 (acima de todos os updates oficiais).

Nenhum arquivo original é alterado; desinstalar = apagar os arquivos `*PTBR*` da pasta `Pack`.
Nenhum dado do jogo é distribuído — só o texto traduzido.

## Estrutura

```
src/telltale.py      Blowfish v7 (.lenc), leitor/escritor .ttarch2, CRC64
src/landb.py         parser/escritor de .landb (roundtrip byte a byte validado nos 410 arquivos)
src/wolf_patch.py    gera/instala/remove o patch
src/instalador.py    GUI Tkinter + CLI (--install / --uninstall / --status)
tools/extract.py     extrai falas únicas em lotes (chunks/)
tools/validate.py    valida tags {..}, notas [..], <<marcadores, quebras de linha, cp1252
tools/brackets.py    passada para opções do jogador inteiras entre colchetes
tools/font_glyphs.py confere glifos acentuados nas fontes do jogo
build.py             consolida out/ -> src/traducao_ptbr.json e gera .exe + .zip
```

Requisitos para gerar: Python 3 + PyInstaller. `python build.py --steam-build=319083`.
