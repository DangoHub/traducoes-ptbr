import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { donation } from '@/data/donation';
import { PixCard } from './PixCard';

describe('PixCard', () => {
  it('copies the Pix code and confirms it', async () => {
    const user = userEvent.setup();
    render(<PixCard />);
    await user.click(screen.getByRole('button', { name: /Copiar código Pix/ }));
    expect(await navigator.clipboard.readText()).toBe(donation.pixCode);
    expect(screen.getByRole('button', { name: /copiado/ })).toBeInTheDocument();
  });
});
