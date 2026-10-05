import { describe, expect, it } from 'vitest';
import { calculateAge } from './age';

const TODAY = new Date(2026, 9, 4);

describe('calculateAge', () => {
  it('counts full years only after the birthday', () => {
    expect(calculateAge('2008-10-04', TODAY)).toBe(18);
    expect(calculateAge('2008-10-05', TODAY)).toBe(17);
    expect(calculateAge('2008-11-01', TODAY)).toBe(17);
  });

  it('rejects empty, future and implausible dates', () => {
    expect(calculateAge('', TODAY)).toBeNull();
    expect(calculateAge('2030-01-01', TODAY)).toBeNull();
    expect(calculateAge('1800-01-01', TODAY)).toBeNull();
  });
});
