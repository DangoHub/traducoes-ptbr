import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { publishedGames } from '@/data/games';
import { HomePage } from './HomePage';

describe('HomePage', () => {
  it('lists every published game and the navigation sections', () => {
    const { container } = render(<HomePage />);
    for (const game of publishedGames) {
      expect(screen.getByRole('heading', { name: game.title })).toBeInTheDocument();
    }
    for (const id of ['jogos', 'instalar', 'seguranca', 'apoie', 'faq']) {
      expect(container.querySelector(`#${id}`)).toBeInTheDocument();
    }
  });

  it('never links to the adult page', () => {
    render(<HomePage />);
    const hrefs = screen.getAllByRole('link').map((link) => link.getAttribute('href') ?? '');
    expect(hrefs.some((href) => href.includes('third-crisis'))).toBe(false);
  });
});
