import type { Game, GameRelease, TranslationProgress } from '@/models/game';
import { releaseAssetUrl, releaseTagUrl, steamCoverUrl, virusTotalUrl } from '@/utils/links';

const COMPLETE: TranslationProgress[] = [
  { label: 'Diálogos', percent: 100 },
  { label: 'Interface', percent: 100 },
];

function githubRelease(tag: string, zipBaseName: string, sha256: string): GameRelease {
  return {
    windowsUrl: releaseAssetUrl(tag, `${zipBaseName}.zip`),
    linuxUrl: releaseAssetUrl(tag, `${zipBaseName}_SteamDeck-Linux.zip`),
    notesUrl: releaseTagUrl(tag),
    virusTotalUrl: virusTotalUrl(sha256),
  };
}

export const publishedGames: Game[] = [
  {
    slug: 'the-wolf-among-us',
    title: 'The Wolf Among Us',
    studio: 'Telltale Games',
    steamBuild: '319083',
    coverUrl: steamCoverUrl(250320),
    badge: { label: '✔ Testado em jogo', tone: 'success' },
    description: 'Os 5 episódios completos, menus, conquistas e a Fablespedia. Mais de 34 mil falas únicas traduzidas.',
    progress: COMPLETE,
    release: githubRelease(
      'the-wolf-among-us-v1.1',
      'The_Wolf_Among_Us_Traducao_PTBR',
      '7691ec3eee4168965751e73d40feb93bf9251397a759b96a20b24423b4afb24f'
    ),
  },
  {
    slug: 'garden-of-witches',
    title: 'Garden of Witches',
    studio: 'Unity',
    steamBuild: '25225196',
    coverUrl: steamCoverUrl(2530470),
    badge: { label: '✔ Completo', tone: 'success' },
    description: (
      <>
        História inteira (4.017 falas) e toda a interface. Depois de instalar, escolha <b>English</b> no menu de idioma.
      </>
    ),
    progress: COMPLETE,
    release: githubRelease(
      'garden-of-witches-v1.1',
      'Garden_of_Witches_Traducao_PTBR',
      'd63040d97f6ea695fcdfc83a9cc06257ff2774957e9374a1b9f8dd049e603c66'
    ),
  },
];

export const thirdCrisis: Game = {
  slug: 'third-crisis',
  title: 'Third Crisis',
  studio: 'Anduo Games · Unity',
  steamBuild: '18412641',
  coverUrl: steamCoverUrl(1260820),
  badge: { label: '18+', tone: 'adult' },
  description:
    'Mais de 29 mil textos traduzidos: diálogos, escolhas, missões, diário, itens, habilidades e interface. ' +
    'O conteúdo adulto foi traduzido com a mesma intensidade do original, sem suavizar nem exagerar.',
  progress: COMPLETE,
};
