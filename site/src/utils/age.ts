export const MINIMUM_AGE = 18;
export const MAXIMUM_AGE = 120;

/** Age in full years for an ISO date ("YYYY-MM-DD"), or null when the date is invalid. */
export function calculateAge(birthDate: string, today: Date = new Date()): number | null {
  const [year, month, day] = birthDate.split('-').map(Number);
  if (!year || !month || !day) {
    return null;
  }
  const birthdayPending = today.getMonth() + 1 < month || (today.getMonth() + 1 === month && today.getDate() < day);
  const age = today.getFullYear() - year - (birthdayPending ? 1 : 0);
  return age < 0 || age > MAXIMUM_AGE ? null : age;
}
