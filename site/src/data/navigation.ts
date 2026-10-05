import type { NavLink } from '@/models/content';

export const HOME_PAGE = 'index.html';

export const homeNavigation: NavLink[] = [
  { label: 'Jogos', href: '#jogos' },
  { label: 'Como instalar', href: '#instalar' },
  { label: 'Segurança', href: '#seguranca' },
  { label: 'FAQ', href: '#faq' },
  { label: '☕ Café pro dev', href: '#apoie', highlighted: true },
];

export const thirdCrisisNavigation: NavLink[] = [
  { label: 'Início', href: HOME_PAGE },
  { label: 'Como instalar', href: '#instalar' },
  { label: 'FAQ', href: '#faq' },
];

export const DEFAULT_DISCLAIMER =
  'Projeto não oficial e sem afiliação com os desenvolvedores ou distribuidores dos jogos. ' +
  'Todas as marcas e imagens pertencem aos seus respectivos donos.';

export const ADULT_DISCLAIMER =
  'Conteúdo destinado exclusivamente a maiores de 18 anos. Projeto não oficial e sem afiliação com os desenvolvedores ' +
  'ou distribuidores do jogo. Todas as marcas e imagens pertencem aos seus respectivos donos.';
