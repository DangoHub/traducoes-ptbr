# Garden of Witches — Tradução PT-BR

- Engine: Unity 2022.3.62f3, IL2CPP, sem typetrees.
- Texto: TextAssets `System` (interface, 1.098 linhas) e `Story` (diálogos, 4.017 linhas) dentro de `resources.assets`, em CSV com colunas `ko,en,ja,...`.
- Estratégia: a coluna `en` é substituída pelo PT-BR (o jogador escolhe "English").
- Patcher (`src/gow_ptbr_core.py`): lê apenas a tabela de objetos do SerializedFile, grava os TextAssets novos no fim do arquivo e redireciona os ponteiros. Backup em `Garden of Witches_Data/ptbr_mod_backup.json`; desinstalação restaura o arquivo byte a byte.

## Releases

| Steam build | Arquivos |
|---|---|
| 25225196 | [`releases/steam-build-25225196/`](releases/steam-build-25225196/) |

## Fluxo

1. `python dump_ta.py` e `python prepare.py` — extrai e divide o texto em `chunks/`.
2. Tradução dos lotes em `out/` seguindo `GUIA_TRADUCAO.md`.
3. `python validate.py`, `python consistency.py`, `python normalize.py`.
4. `python build.py --steam-build=<id>` — gera o `.exe` e o `.zip` em `releases/`.
