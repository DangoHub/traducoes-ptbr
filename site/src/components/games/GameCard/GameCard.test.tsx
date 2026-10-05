import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { publishedGames, thirdCrisis } from '@/data/games';
import { GameCard } from './GameCard';

describe('GameCard', () => {
  it('links the Windows and Linux downloads of a published game', () => {
    const [game] = publishedGames;
    render(<GameCard game={game} />);
    expect(screen.getByRole('link', { name: /Windows/ })).toHaveAttribute('href', game.release?.windowsUrl);
    expect(screen.getByRole('link', { name: /Steam Deck/ })).toHaveAttribute('href', game.release?.linuxUrl);
    expect(screen.getByRole('link', { name: /VirusTotal/ })).toHaveAttribute('target', '_blank');
  });

  it('shows a disabled button and no download link before the release', () => {
    render(<GameCard game={thirdCrisis} />);
    expect(screen.getByRole('button', { name: /Download em breve/ })).toBeDisabled();
    expect(screen.queryByRole('link')).not.toBeInTheDocument();
  });
});
