import { useCallback, useState } from 'react';
import { MINIMUM_AGE, calculateAge } from '@/utils/age';

export type AgeStatus = 'pending' | 'verified' | 'denied';

/** Storage values kept from the first version of the page so existing confirmations stay valid. */
export const AGE_STORAGE_KEY = 'dangohub_maior18';
const DENIED_VALUE = 'negado';
export const VERIFICATION_TTL_MS = 30 * 24 * 60 * 60 * 1000;

export const AGE_MESSAGES = {
  missingBirthDate: 'Informe a sua data de nascimento.',
  missingDeclaration: 'Marque a declaração para continuar.',
  invalidBirthDate: 'Data de nascimento inválida.',
  underage: 'Esta página é só para maiores de 18 anos.',
} as const;

function safely<T>(read: () => T, fallback: T): T {
  try {
    return read();
  } catch {
    return fallback;
  }
}

function readInitialStatus(): AgeStatus {
  const verifiedAt = safely(() => Number(localStorage.getItem(AGE_STORAGE_KEY)), 0);
  if (verifiedAt && Date.now() - verifiedAt < VERIFICATION_TTL_MS) {
    return 'verified';
  }
  return safely(() => sessionStorage.getItem(AGE_STORAGE_KEY), null) === DENIED_VALUE ? 'denied' : 'pending';
}

export function useAgeVerification() {
  const [status, setStatus] = useState<AgeStatus>(readInitialStatus);
  const [error, setError] = useState<string | null>(() => (status === 'denied' ? AGE_MESSAGES.underage : null));

  const verify = useCallback((birthDate: string, declared: boolean) => {
    if (!birthDate) {
      return setError(AGE_MESSAGES.missingBirthDate);
    }
    if (!declared) {
      return setError(AGE_MESSAGES.missingDeclaration);
    }
    const age = calculateAge(birthDate);
    if (age === null) {
      return setError(AGE_MESSAGES.invalidBirthDate);
    }
    if (age < MINIMUM_AGE) {
      safely(() => sessionStorage.setItem(AGE_STORAGE_KEY, DENIED_VALUE), undefined);
      setStatus('denied');
      return setError(AGE_MESSAGES.underage);
    }
    safely(() => localStorage.setItem(AGE_STORAGE_KEY, String(Date.now())), undefined);
    setError(null);
    setStatus('verified');
  }, []);

  return { status, error, verify };
}
