import { useEffect, useRef, useState, type FormEvent } from 'react';
import { Button } from '@/components/ui/Button/Button';
import { HOME_PAGE } from '@/data/navigation';
import styles from './AgeGate.module.css';

interface AgeGateProps {
  gameTitle: string;
  error: string | null;
  denied: boolean;
  onSubmit: (birthDate: string, declared: boolean) => void;
}

export function AgeGate({ gameTitle, error, denied, onSubmit }: AgeGateProps) {
  const [birthDate, setBirthDate] = useState('');
  const [declared, setDeclared] = useState(false);

  const dialogRef = useRef<HTMLDialogElement>(null);

  useEffect(() => {
    const dialog = dialogRef.current;
    if (dialog && !dialog.open) {
      if (typeof dialog.showModal === 'function') {
        dialog.showModal();
      } else {
        dialog.setAttribute('open', '');
      }
    }
    const previous = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = previous;
    };
  }, []);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    onSubmit(birthDate, declared);
  }

  return (
    <dialog ref={dialogRef} className={styles.overlay} aria-labelledby="age-gate-title" onCancel={(event) => event.preventDefault()}>
      <form className={styles.box} onSubmit={handleSubmit} noValidate>
        <span className={styles.badge} aria-hidden="true">
          18+
        </span>
        <h1 id="age-gate-title">Conteúdo adulto</h1>
        <p>
          Esta página é sobre a tradução de <b>{gameTitle}</b>, um jogo com conteúdo sexual explícito. Ela é restrita a maiores de 18 anos.
        </p>
        <label className={styles.field}>
          <span>Sua data de nascimento</span>
          <input type="date" required value={birthDate} onChange={(event) => setBirthDate(event.target.value)} />
        </label>
        <label className={styles.declaration}>
          <input type="checkbox" required checked={declared} onChange={(event) => setDeclared(event.target.checked)} />
          <span>Declaro que tenho 18 anos ou mais e que acessar conteúdo adulto é permitido onde estou.</span>
        </label>
        {error && (
          <p className={styles.error} role="alert">
            {error}
          </p>
        )}
        <div className={styles.actions}>
          <Button variant="start" type="submit" disabled={denied}>
            Entrar
          </Button>
          <Button variant="ghost" href={HOME_PAGE}>
            Sair
          </Button>
        </div>
      </form>
    </dialog>
  );
}
