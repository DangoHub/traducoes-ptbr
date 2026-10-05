# 🍡 DangoHub Traduções — jogos em PT-BR, de graça

Traduções de fãs para português do Brasil, com foco em localização (nada de tradução literal).
Cada jogo tem instalador com um clique, desinstalação limpa e código 100% aberto.

**Site:** https://dangohub.github.io/traducoes-ptbr/

## Baixar

| Jogo | Versão Steam compatível | Download |
|---|---|---|
| The Wolf Among Us | build 319083 | [Baixar .zip](https://github.com/DangoHub/traducoes-ptbr/releases/download/the-wolf-among-us-v1.1/The_Wolf_Among_Us_Traducao_PTBR.zip) · [notas e SHA-256](https://github.com/DangoHub/traducoes-ptbr/releases/tag/the-wolf-among-us-v1.1) |
| Garden of Witches | build 25225196 | [Baixar .zip](https://github.com/DangoHub/traducoes-ptbr/releases/download/garden-of-witches-v1.1/Garden_of_Witches_Traducao_PTBR.zip) · [notas e SHA-256](https://github.com/DangoHub/traducoes-ptbr/releases/tag/garden-of-witches-v1.1) |

Todas as versões: [Releases](https://github.com/DangoHub/traducoes-ptbr/releases).

## É seguro?

Os executáveis são gerados pelo GitHub Actions direto deste código, com hash SHA-256, atestação de
origem assinada e análise no VirusTotal. Veja como conferir em [VERIFICAR.md](VERIFICAR.md).

## Estrutura do repositório

```
site/                     site (Vite + React + TypeScript), publicado no GitHub Pages
  src/data/               jogos, links das releases, textos das páginas
  src/components/         componentes por área (ui, layout, games, home, age-gate)
  src/pages/              páginas: início e Third Crisis (+18, com verificação de idade)
kit/                      kit de tradução em Python (veja kit/README.md)
tests/                    testes do kit
projetos/<jogo>/          tudo que gera a tradução de cada jogo
  GUIA_TRADUCAO.md        guia de estilo + glossário PT-BR
  chunks/  out/           texto original em lotes / traduções por lote
  src/                    instalador e patcher
  build.py                junta traduções e gera o .zip (via projetos/empacotar.py)
.github/workflows/
  release.yml             build + publicação de releases
  pages.yml               lint, testes, build e deploy do site
```

## Site

```
cd site
npm install
npm run dev        # servidor local
npm run lint       # oxlint
npm test           # vitest
npm run build      # gera site/dist
```

Todo push em `main` que mexe em `site/` publica o site pelo workflow `pages.yml`.

## Publicar uma versão

No GitHub: **Actions → Release de tradução → Run workflow**, escolha o jogo, a versão (ex.: `v1.1`) e o
Steam build. O workflow gera o instalador numa máquina limpa do GitHub, calcula o SHA-256, cria a
atestação, envia ao VirusTotal (se o secret `VT_API_KEY` existir) e publica a release
`<jogo>-<versão>`.

Ao lançar uma versão nova, atualize a versão e os SHA-256 em `site/src/data/games.tsx` e os links
neste README.

## Aviso

Projeto não oficial, sem fins lucrativos e sem afiliação com os desenvolvedores dos jogos.
Requer o jogo original; nenhum arquivo do jogo é distribuído.
