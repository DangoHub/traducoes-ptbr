import type { FaqItem, Step } from '@/models/content';

export const thirdCrisisSteps: Step[] = [
  {
    title: 'Baixe o zip',
    description: 'Windows ou Steam Deck / Linux, quando a tradução for publicada aqui.',
  },
  {
    title: 'Rode o instalador',
    description: 'Ele acha o jogo na Steam e guarda um backup do que mudar.',
  },
  {
    title: 'Escolha o idioma',
    description: (
      <>
        Abra o jogo e escolha <b>Custom Português (Brasil)</b> em <b>Settings &gt; Game &gt; Language</b>.
      </>
    ),
  },
];

export const thirdCrisisFaq: FaqItem[] = [
  {
    question: 'Preciso ter o jogo original?',
    answer: 'Sim. A tradução só acrescenta um idioma e não inclui nenhum arquivo do jogo. Funciona com a versão da Steam indicada no card.',
  },
  {
    question: 'Por que esta página é separada?',
    answer: 'Porque o jogo é adulto. A página principal do DangoHub é para todos os públicos, e esta fica restrita a maiores de 18 anos.',
  },
  {
    question: 'O jogo atualizou. A tradução continua funcionando?',
    answer: 'Sim. Textos novos aparecem em inglês até sair uma versão nova da tradução.',
  },
];
