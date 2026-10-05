import { act, renderHook } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { AGE_MESSAGES, AGE_STORAGE_KEY, VERIFICATION_TTL_MS, useAgeVerification } from './useAgeVerification';

describe('useAgeVerification', () => {
  it('asks for the birth date and the declaration before checking the age', () => {
    const { result } = renderHook(() => useAgeVerification());
    act(() => result.current.verify('', true));
    expect(result.current.error).toBe(AGE_MESSAGES.missingBirthDate);
    act(() => result.current.verify('1990-01-01', false));
    expect(result.current.error).toBe(AGE_MESSAGES.missingDeclaration);
    expect(result.current.status).toBe('pending');
  });

  it('verifies adults and remembers them', () => {
    const { result } = renderHook(() => useAgeVerification());
    act(() => result.current.verify('1990-01-01', true));
    expect(result.current.status).toBe('verified');
    expect(renderHook(() => useAgeVerification()).result.current.status).toBe('verified');
  });

  it('denies minors for the rest of the session', () => {
    const { result } = renderHook(() => useAgeVerification());
    act(() => result.current.verify(`${new Date().getFullYear() - 10}-01-01`, true));
    expect(result.current.status).toBe('denied');
    const next = renderHook(() => useAgeVerification()).result.current;
    expect(next.status).toBe('denied');
    expect(next.error).toBe(AGE_MESSAGES.underage);
  });

  it('expires the confirmation after the validity period', () => {
    localStorage.setItem(AGE_STORAGE_KEY, String(Date.now() - VERIFICATION_TTL_MS - 1));
    expect(renderHook(() => useAgeVerification()).result.current.status).toBe('pending');
  });
});
