# 🍡 DangoHub Traduções — jogos em PT-BR, de graça

Traduções de fãs para português do Brasil, com foco em localização (nada de tradução literal).
Cada jogo tem instalador com um clique, desinstalação limpa e código 100% aberto.

**Site:** https://dangohub.github.io/traducoes-ptbr/

## Baixar

| Jogo | Versão Steam compatível | Download |
|---|---|---|
| The Wolf Among Us | build 319083 | [Instalador .exe](https://github.com/DangoHub/traducoes-ptbr/releases/download/the-wolf-among-us-v1.0/Instalador_Traducao_PTBR_The_Wolf_Among_Us.exe) · [.zip](https://github.com/DangoHub/traducoes-ptbr/releases/download/the-wolf-among-us-v1.0/The_Wolf_Among_Us_Traducao_PTBR.zip) · [notas e SHA-256](https://github.com/DangoHub/traducoes-ptbr/releases/tag/the-wolf-among-us-v1.0) |
| Garden of Witches | build 25225196 | [Instalador .exe](https://github.com/DangoHub/traducoes-ptbr/releases/download/garden-of-witches-v1.0/Instalador_Traducao_PTBR_Garden_of_Witches.exe) · [.zip](https://github.com/DangoHub/traducoes-ptbr/releases/download/garden-of-witches-v1.0/Garden_of_Witches_Traducao_PTBR.zip) · [notas e SHA-256](https://github.com/DangoHub/traducoes-ptbr/releases/tag/garden-of-witches-v1.0) |

Todas as versões: [Releases](https://github.com/DangoHub/traducoes-ptbr/releases).

## É seguro?

Os executáveis são gerados pelo GitHub Actions direto deste código, com hash SHA-256, atestação de
origem assinada e análise no VirusTotal. Veja como conferir em [VERIFICAR.md](VERIFICAR.md).

## Estrutura do repositório

```
docs/                     site (GitHub Pages)
projetos/<jogo>/          tudo que gera a tradução de cada jogo
  GUIA_TRADUCAO.md        guia de estilo + glossário PT-BR
  chunks/  out/           texto original em lotes / traduções por lote
  src/                    instalador e patcher
  build.py                junta traduções, gera .exe e .zip
.github/workflows/release.yml   build + publicação de releases
```

## Publicar uma versão

No GitHub: **Actions → Release de tradução → Run workflow**, escolha o jogo, a versão (ex.: `v1.1`) e o
Steam build. O workflow gera o instalador numa máquina limpa do GitHub, calcula o SHA-256, cria a
atestação, envia ao VirusTotal (se o secret `VT_API_KEY` existir) e publica a release
`<jogo>-<versão>`.

Ao lançar uma versão nova, atualize os links em `docs/index.html` e neste README.

## Aviso

Projeto não oficial, sem fins lucrativos e sem afiliação com os desenvolvedores dos jogos.
Requer o jogo original; nenhum arquivo do jogo é distribuído.
