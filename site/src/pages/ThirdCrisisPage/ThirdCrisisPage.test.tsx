import { fireEvent, render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { AGE_STORAGE_KEY } from '@/hooks/useAgeVerification';
import { ThirdCrisisPage } from './ThirdCrisisPage';

async function submitBirthDate(birthDate: string) {
  const user = userEvent.setup();
  fireEvent.change(screen.getByLabelText('Sua data de nascimento'), { target: { value: birthDate } });
  await user.click(screen.getByRole('checkbox'));
  await user.click(screen.getByRole('button', { name: 'Entrar' }));
}

describe('ThirdCrisisPage', () => {
  it('hides the content behind the age gate', () => {
    render(<ThirdCrisisPage />);
    expect(screen.getByRole('dialog')).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: 'Third Crisis' })).not.toBeInTheDocument();
    expect(document.body.style.overflow).toBe('hidden');
  });

  it('shows the content to adults, without a download link', async () => {
    render(<ThirdCrisisPage />);
    await submitBirthDate('1990-01-01');
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
    expect(screen.getByRole('heading', { name: 'Third Crisis' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Download em breve/ })).toBeDisabled();
    expect(document.body.style.overflow).toBe('');
  });

  it('blocks minors', async () => {
    render(<ThirdCrisisPage />);
    await submitBirthDate(`${new Date().getFullYear() - 15}-06-01`);
    expect(screen.getByRole('alert')).toHaveTextContent('maiores de 18');
    expect(screen.getByRole('button', { name: 'Entrar' })).toBeDisabled();
  });

  it('skips the gate for a recent confirmation', () => {
    localStorage.setItem(AGE_STORAGE_KEY, String(Date.now()));
    render(<ThirdCrisisPage />);
    expect(screen.queryByRole('dialog')).not.toBeInTheDocument();
  });
});
